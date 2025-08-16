#!/usr/bin/env python3
"""Analyze and visualize visit density across the Rubin footprint."""

import warnings
warnings.filterwarnings("ignore")  # Suppress astropy/ERFA warnings

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.transforms import Affine2D
from astropy_healpix import HEALPix
from astropy.coordinates import SkyCoord, ICRS, GeocentricTrueEcliptic
import astropy.units as u

# HEALPix resolution for binning
NSIDE = 64  # 49,152 pixels total (12 * 64^2)

def get_healpix_indices(ra: np.ndarray, dec: np.ndarray, nside: int = NSIDE) -> np.ndarray:
    """Convert arrays of (RA, Dec) to HEALPix pixel indices (nested scheme)."""
    hp = HEALPix(nside=nside, order="nested", frame=ICRS())
    return hp.lonlat_to_healpix(ra * u.deg, dec * u.deg)

def get_pixel_centers(pixels: np.ndarray, nside: int = NSIDE) -> tuple[np.ndarray, np.ndarray]:
    """Get (RA, Dec) of multiple HEALPix pixel centers at once."""
    hp = HEALPix(nside=nside, order="nested", frame=ICRS())
    lon, lat = hp.healpix_to_lonlat(pixels)
    return lon.deg, lat.deg

def get_pixel_area(nside: int = NSIDE) -> float:
    """Get area of a single HEALPix pixel in square degrees."""
    return 41252.96 / (12 * nside * nside)

def plot_region(pixels_df: pd.DataFrame, dec_min: float, dec_max: float, 
                norm: BoundaryNorm, cmap: ListedColormap, 
                visit_bounds: list[int], filename: str) -> None:
    """Plot a specific declination region with vertical stretching."""
    # Create figure in landscape format
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111, projection='mollweide')
    
    # Filter data for this region
    mask = (pixels_df["dec"] >= dec_min) & (pixels_df["dec"] <= dec_max)
    region_data = pixels_df[mask]
    
    # Convert coordinates to radians
    ra_rad = -np.deg2rad(region_data["ra"])  # Negate for east-left convention
    dec_rad = np.deg2rad(region_data["dec"])
    
    # Plot points
    scatter = ax.scatter(
        ra_rad,
        dec_rad,
        c=region_data["visits"],
        norm=norm,
        cmap=cmap,
        s=40,
        alpha=0.9
    )
    
    # Add ecliptic plane
    ecl_lon = np.linspace(-180, 180, 360)
    ecl_lat = np.zeros_like(ecl_lon)
    coords = SkyCoord(
        lon=ecl_lon * u.deg,
        lat=ecl_lat * u.deg,
        frame=GeocentricTrueEcliptic
    )
    icrs = coords.transform_to(ICRS())
    ecl_ra = -icrs.ra.rad  # Negate for east-left convention
    ecl_dec = icrs.dec.rad
    
    # Only plot ecliptic within the region
    ecl_mask = (np.rad2deg(ecl_dec) >= dec_min) & (np.rad2deg(ecl_dec) <= dec_max)
    if any(ecl_mask):
        ax.plot(ecl_ra[ecl_mask], ecl_dec[ecl_mask], 'r--', alpha=0.5, label='Ecliptic plane')
        ax.legend()
    
    # Add region labels from MAF notebook
    if dec_min >= 0:
        # Northern region labels
        plt.figtext(0.51, 0.45, 'Low-dust\nWFD', fontsize='x-large', fontweight='bold', color='white')
        plt.figtext(0.28, 0.6, 'NES', fontsize='x-large', fontweight='bold', color='white')
        plt.figtext(0.71, 0.41, 'GP\nWFD', fontsize='x-large', fontweight='bold', color='white')
        plt.figtext(0.36, 0.38, 'DDFs', fontsize='x-large', fontweight='bold', color='white')
        plt.figtext(0.9, 0.63, "Virgo", fontsize='x-large', fontweight='bold', color='white')
    else:
        # Southern region labels
        plt.figtext(0.55, 0.26, 'SCP', fontsize='x-large', fontweight='bold', color='white')
        plt.figtext(0.18, 0.4, 'Dusty\nPlane', fontsize='x-large', fontweight='bold', color='white')
    
    # Add colorbar and labels
    plt.colorbar(scatter, label="Number of visits", ticks=visit_bounds)
    plt.grid(True, alpha=0.3)
    plt.title(f"Visit Density ({dec_min}° to {dec_max}° Dec)")
    
    # Adjust figure size and point size based on region
    if dec_min >= 0:
        # For northern region (0° to 40°), use wider aspect ratio
        fig.set_size_inches(24, 6)
        point_size = 80
    else:
        # For southern region (-90° to -60°), use more square aspect ratio
        fig.set_size_inches(20, 10)
        point_size = 60
    
    # Make points larger for better visibility
    for collection in ax.collections:
        collection.set_sizes([point_size])
    
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def analyze_visit_density(db_path: Path) -> None:
    """Analyze and visualize visit density across the footprint."""
    print("\nAnalyzing visit density across the Rubin footprint...")
    
    # Read all pointings
    with sqlite3.connect(db_path) as conn:
        # First, check what's in the database
        tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = pd.read_sql_query(tables_query, conn)
        print("\nDatabase tables:", ", ".join(tables["name"]))
        
        # Check observation counts with and without DISTINCT
        count_queries = [
            "SELECT COUNT(*) as total FROM observations",
            "SELECT COUNT(*) as unique_fields FROM (SELECT DISTINCT fieldRA, fieldDec FROM observations)",
        ]
        for query in count_queries:
            count = pd.read_sql_query(query, conn).iloc[0, 0]
            print(f"{query}: {count:,}")
        
        # Get all pointings
        query = """
        SELECT fieldRA, fieldDec
        FROM observations
        """
        pointings = pd.read_sql_query(query, conn)
    
    print(f"Found {len(pointings):,} total pointings")
    
    # Convert all pointings to HEALPix at once
    print("\nConverting pointings to HEALPix pixels...")
    healpix_indices = get_healpix_indices(
        pointings["fieldRA"].values,
        pointings["fieldDec"].values
    )
    
    # Count visits per pixel
    unique_pixels, visit_counts = np.unique(healpix_indices, return_counts=True)
    print(f"\nFound {len(unique_pixels):,} unique HEALPix pixels")
    
    # Get centers for all pixels at once
    ra_centers, dec_centers = get_pixel_centers(unique_pixels)
    
    # Create DataFrame
    pixels_df = pd.DataFrame({
        "pixel": unique_pixels,
        "visits": visit_counts,
        "ra": ra_centers,
        "dec": dec_centers,
    })
    
    # Print statistics
    print("\nVisit count statistics:")
    print(f"  Minimum: {pixels_df['visits'].min():,}")
    print(f"  Maximum: {pixels_df['visits'].max():,}")
    print(f"  Mean: {pixels_df['visits'].mean():.1f}")
    print(f"  Median: {pixels_df['visits'].median():.1f}")
    
    # Define visit thresholds based on MAF notebook
    visit_bounds = [0, 10, 50, 100, 200, 300, 500, 750, 1000, 2000, 5000, 7500, 10000]
    
    # Color scheme for visit density
    colors = [
        '#000033',  # Very dark blue for < 10
        '#000099',  # Dark blue for 10-50
        '#0000FF',  # Blue for 50-100
        '#0066FF',  # Light blue for 100-200
        '#00CCFF',  # Sky blue for 200-300
        '#00FFCC',  # Turquoise for 300-500
        '#00FF66',  # Blue-green for 500-750
        '#33FF33',  # Light green for 750-1000
        '#FFFF00',  # Yellow for 1000-2000
        '#FF9900',  # Orange for 2000-5000
        '#FF3300',  # Orange-red for 5000-7500
        '#FF0000',  # Red for 7500-10000
        '#990000',  # Dark red for 10000+
    ]
    
    custom_cmap = ListedColormap(colors)
    norm = BoundaryNorm(visit_bounds, len(visit_bounds) - 1)
    
    # Calculate areas
    pixel_area = get_pixel_area()
    total_area = len(pixels_df) * pixel_area
    
    print("\nArea coverage:")
    print(f"  Total pixels: {len(pixels_df):,} ({total_area:.0f} sq deg)")
    
    for visits in [10, 750, 10000]:
        n_pixels = (pixels_df["visits"] > visits).sum()
        area = n_pixels * pixel_area
        print(f"  Points above {visits:5d} visits: {n_pixels:6,} pixels ({area:.0f} sq deg)")
    
    # Print detailed distribution
    print("\nPixels by visit count:")
    for i in range(len(visit_bounds)):
        min_visits = visit_bounds[i]
        max_visits = visit_bounds[i + 1] if i < len(visit_bounds) - 1 else float("inf")
        count = ((pixels_df["visits"] >= min_visits) & (pixels_df["visits"] < max_visits)).sum()
        area = count * pixel_area
        if i < len(visit_bounds) - 1:
            print(f"  {min_visits:5d}-{max_visits:5d}: {count:6,} pixels ({area:.0f} sq deg)")
        else:
            print(f"  {min_visits:5d}+     : {count:6,} pixels ({area:.0f} sq deg)")
    
    # Plot regions
    plot_region(pixels_df, 0, 40, norm, custom_cmap, visit_bounds, "visit_density_north.png")
    plot_region(pixels_df, -90, -60, norm, custom_cmap, visit_bounds, "visit_density_south.png")

def main() -> None:
    """Main entry point."""
    db_path = Path("cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db")
    if not db_path.exists():
        print(f"Error: OpSim database not found at {db_path}")
        return
    
    analyze_visit_density(db_path)

if __name__ == "__main__":
    main()