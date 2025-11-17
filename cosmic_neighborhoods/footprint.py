"""Functions for handling the Rubin Observatory footprint."""

from pathlib import Path
import random
from typing import Tuple, Dict, Optional, List

import numpy as np
import pandas as pd
from astropy_healpix import HEALPix
from astropy.coordinates import ICRS, SkyCoord
import astropy.units as u
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import warnings

warnings.filterwarnings("ignore")  # Suppress astropy/ERFA warnings

# Standard HEALPix parameters for footprint visualization
NSIDE_VIZ = 64  # Order 6, 49,152 pixels total (12 * 64^2)

# Rubin field parameters
FIELD_WIDTH = 3.5  # degrees, full width
FIELD_HEIGHT = 3.5  # degrees, full height
FIELD_DIAGONAL = np.sqrt(FIELD_WIDTH**2 + FIELD_HEIGHT**2)  # For initial cone search

import healpy as hp


def extract_boundary(db_path: str | Path) -> Dict[str, np.ndarray]:
    """Extract RA-based declination boundaries from OpSim database.

    Creates a compact representation of the footprint as declination
    boundaries for each RA slice (every 0.1 degrees).

    Args:
        db_path: Path to OpSim SQLite database

    Returns:
        Dictionary with:
            'ra': Array of RA values (0 to 359.9, step 0.1)
            'dec_south': Array of southern boundaries
            'dec_north': Array of northern boundaries
    """
    # Read all unique pointings
    db_uri = f"sqlite:///{db_path}"
    query = """
    SELECT DISTINCT fieldRA, fieldDec 
    FROM observations
    """
    pointings = pd.read_sql_query(query, db_uri)

    # Create RA grid (0 to 359.9, step 0.1)
    ra_grid = np.arange(0, 360, 0.1)

    # Initialize boundary arrays
    dec_south = np.full_like(ra_grid, -90.0)  # For now, always -90
    dec_north = np.full_like(ra_grid, -90.0)  # Will update with real values

    # Round RAs to nearest 0.1°
    pointings["ra_bin"] = (pointings["fieldRA"] / 0.1).round() * 0.1

    # Find maximum declination for each RA bin
    max_decs = pointings.groupby("ra_bin")["fieldDec"].max()

    # Update northern boundary (adding field radius of 1.75°)
    for ra, dec in max_decs.items():
        idx = int(ra * 10)  # Convert RA to array index
        if idx < len(dec_north):
            dec_north[idx] = dec + 1.75  # Add field radius

    # Interpolate any gaps
    mask = dec_north > -90
    if np.any(mask):
        x = np.where(mask)[0]
        y = dec_north[mask]
        dec_north = np.interp(np.arange(len(dec_north)), x, y)

    return {
        "ra": ra_grid,
        "dec_south": dec_south,
        "dec_north": dec_north,
    }


def save_footprint_cache(
    boundary: Dict[str, np.ndarray],
    cache_file: str | Path,
) -> None:
    """Save footprint boundary data to cache file.

    Args:
        boundary: Dictionary from extract_boundary()
        cache_file: Path to save cache (will be .npz)
    """
    np.savez_compressed(
        cache_file,
        ra=boundary["ra"],
        dec_south=boundary["dec_south"],
        dec_north=boundary["dec_north"],
    )


def load_footprint_cache(cache_file: str | Path) -> Dict[str, np.ndarray]:
    """Load footprint boundary data from cache file.

    Args:
        cache_file: Path to .npz cache file

    Returns:
        Dictionary with ra, dec_south, dec_north arrays
    """
    with np.load(cache_file) as data:
        return {
            "ra": data["ra"],
            "dec_south": data["dec_south"],
            "dec_north": data["dec_north"],
        }


def get_dec_range_at_ra(
    ra_deg: float,
    boundary: Dict[str, np.ndarray],
) -> Tuple[float, float]:
    """Get declination range at a specific RA.

    Args:
        ra_deg: Right ascension in degrees [0, 360)
        boundary: Dictionary from extract_boundary() or load_footprint_cache()

    Returns:
        Tuple of (south_dec, north_dec) in degrees
    """
    # Normalize RA to [0, 360)
    ra = ra_deg % 360

    # Find nearest RA bin
    idx = int(round(ra * 10))  # Convert RA to array index
    if idx >= len(boundary["ra"]):
        idx = 0  # Wrap around at 360°

    return (boundary["dec_south"][idx], boundary["dec_north"][idx])


# Keep these for reference/testing but not using them for main footprint
def extract_opsim_pointings(
    db_path: str | Path, sample_size: Optional[int] = None, random_seed: Optional[int] = None
) -> pd.DataFrame:
    """Extract unique pointings from OpSim database.

    Args:
        db_path: Path to OpSim SQLite database
        sample_size: If provided, return this many random pointings
        random_seed: Random seed for reproducible sampling

    Returns:
        DataFrame with columns 'fieldRA' and 'fieldDec'
    """
    # Read all unique pointings
    db_uri = f"sqlite:///{db_path}"
    query = """
    SELECT DISTINCT fieldRA, fieldDec 
    FROM observations
    """
    pointings = pd.read_sql_query(query, db_uri)

    if sample_size is not None:
        if random_seed is not None:
            random.seed(random_seed)
        pointings = pointings.sample(n=min(sample_size, len(pointings)), random_state=random_seed)

    return pointings


def get_healpix_indices(ra: np.ndarray, dec: np.ndarray, nside: int = NSIDE_VIZ) -> np.ndarray:
    """Convert arrays of (RA, Dec) to HEALPix pixel indices (nested scheme)."""
    hp = HEALPix(nside=nside, order="nested", frame=ICRS())
    return hp.lonlat_to_healpix(ra * u.deg, dec * u.deg)

def get_pixel_centers(pixels: np.ndarray, nside: int = NSIDE_VIZ) -> tuple[np.ndarray, np.ndarray]:
    """Get (RA, Dec) of multiple HEALPix pixel centers at once."""
    hp = HEALPix(nside=nside, order="nested", frame=ICRS())
    lon, lat = hp.healpix_to_lonlat(pixels)
    return lon.deg, lat.deg

def plot_visit_density(pixels_df: pd.DataFrame, filename: str) -> None:
    """Plot visit density across the footprint.

    This visualization uses a deuteranopia-friendly color scheme.
    """
    # Define visit thresholds focusing on key ranges
    visit_bounds = [0, 1, 2, 5, 7, 10, 15, 20, 25, 30, 50, 80, 100, 150]
    
    # Define colors for each range - high contrast for deuteranopia
    # Blue-white-orange-red progression
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
    plt.title(f"Rubin Visit Density (nside={NSIDE_VIZ})")
    
    # Save figure
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def visualize_visit_density(db_path: Path, output_filename: str = "visit_density.png") -> None:
    """Visualize visit density across the Rubin footprint.

    Args:
        db_path: Path to OpSim SQLite database.
        output_filename: Name of the output image file.
    """
    import sqlite3 # Moved inside function to avoid circular dependency
    from astropy.coordinates import GeocentricTrueEcliptic # Moved inside function
    
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
        pointings["fieldDec"].values,
        nside=NSIDE_VIZ
    )
    
    # Count visits per pixel
    unique_pixels, visit_counts = np.unique(healpix_indices, return_counts=True)
    print(f"\nFound {len(unique_pixels):,} unique HEALPix pixels")
    
    # Get centers for all pixels at once
    ra_centers, dec_centers = get_pixel_centers(unique_pixels, nside=NSIDE_VIZ)
    
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
    plot_visit_density(pixels_df, output_filename)
    print(f"Visit density visualization saved to {output_filename}")
    
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
    print("Visit count histogram saved to visit_histogram_detail.png")
