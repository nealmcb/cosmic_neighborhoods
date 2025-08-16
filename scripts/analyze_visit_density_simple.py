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

def plot_visit_density(pixels_df: pd.DataFrame, filename: str) -> None:
    """Plot visit density across the footprint."""
    # Define visit thresholds focusing on key ranges
    visit_bounds = [0, 1, 2, 5, 7, 10, 15, 20, 25, 30, 50, 80, 100, 150]
    
    # Define colors for each range - high contrast for deuteranopia
    colors = [
        '#000033',  # Darkest blue for 0-1
        '#000099',  # Very dark blue for 1-2
        '#0000FF',  # Pure blue for 2-5
        '#0099FF',  # Sky blue for 5-7
        '#00CCFF',  # Light blue for 7-10
        '#00FFFF',  # Cyan for 10-15
        '#FFFFFF',  # White for 15-20
        '#FFCC00',  # Gold for 20-25
        '#FF9900',  # Orange for 25-30
        '#FF6600',  # Dark orange for 30-50
        '#FF3300',  # Red-orange for 50-80
        '#FF0000',  # Pure red for 80-100
        '#CC0000',  # Dark red for 100-150
        '#990000',  # Very dark red for 150+
    ]
    
    # Create figure with Mollweide projection
    plt.figure(figsize=(15, 10))
    ax = plt.subplot(111, projection='mollweide')
    
    # Convert coordinates to radians for Mollweide projection
    ra_rad = np.deg2rad(pixels_df["ra"] - 180)  # Shift RA range from [0,360] to [-180,180]
    dec_rad = np.deg2rad(pixels_df["dec"])
    
    # Create colormap and normalize
    custom_cmap = ListedColormap(colors)
    norm = BoundaryNorm(visit_bounds, len(colors))
    
    # Plot points with smaller size
    scatter = ax.scatter(
        ra_rad,
        dec_rad,
        c=pixels_df["visits"],
        norm=norm,
        cmap=custom_cmap,
        s=8,  # Much smaller points
        alpha=1.0  # Full opacity
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
    # Convert RA to [-180,180] range and to radians
    ecl_ra = np.deg2rad(np.mod(icrs.ra.deg + 180, 360) - 180)
    ecl_dec = icrs.dec.rad
    ax.plot(ecl_ra, ecl_dec, 'r--', alpha=0.3, linewidth=1, label='Ecliptic plane')
    
    # Add colorbar with explicit labels
    cbar = plt.colorbar(scatter, label="Number of visits", 
                       ticks=visit_bounds,
                       boundaries=visit_bounds,
                       extend='max')
    cbar.ax.set_yticklabels([f"{int(b)}" for b in visit_bounds[:-1]] + [f"{visit_bounds[-1]}+"])
    
    # Add grid and title
    plt.grid(True, alpha=0.3)
    plt.title("Rubin Visit Density (nside=64)")
    
    # Save figure
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def analyze_visit_density(db_path: Path) -> None:
    """Analyze and visualize visit density across the footprint."""
    print("\nAnalyzing visit density across the Rubin footprint...")
    
    # Read all pointings
    with sqlite3.connect(db_path) as conn:
        query = "SELECT fieldRA, fieldDec FROM observations"
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
    
    # Print distribution for key thresholds
    print("\nPixels by visit count:")
    thresholds = [1, 2, 5, 7, 10, 15, 20, 25, 30, 50, 80, 100, 150]
    for i, threshold in enumerate(thresholds):
        count = (pixels_df["visits"] >= threshold).sum()
        print(f"  Above {threshold:3d} visits: {count:6,} pixels")
    
    # Create main plot
    plot_visit_density(pixels_df, "visit_density.png")
    
    # Create histogram for 1-150 visits range
    plt.figure(figsize=(12, 6))
    plt.hist(pixels_df[pixels_df["visits"] <= 150]["visits"], 
             bins=50, edgecolor='black')
    plt.xlabel("Number of visits")
    plt.ylabel("Number of pixels")
    plt.title("Visit Count Distribution (1-150 visits)")
    plt.grid(True, alpha=0.3)
    plt.savefig("visit_histogram_detail.png", dpi=300, bbox_inches='tight')
    plt.close()

def main() -> None:
    """Main entry point."""
    db_path = Path("cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db")
    if not db_path.exists():
        print(f"Error: OpSim database not found at {db_path}")
        return
    
    analyze_visit_density(db_path)

if __name__ == "__main__":
    main()
