"""Functions for handling the Rubin Observatory footprint."""

from pathlib import Path
import random
from typing import Tuple, Dict, Optional

import numpy as np
import pandas as pd


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
