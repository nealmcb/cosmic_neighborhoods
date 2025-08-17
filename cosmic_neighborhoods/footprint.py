"""Functions for handling the Rubin Observatory footprint."""

from pathlib import Path
import random
import sqlite3
from typing import Tuple, Dict, Optional, List, Set

import numpy as np
import pandas as pd
from astropy_healpix import HEALPix
from astropy.coordinates import ICRS, SkyCoord
import astropy.units as u

# Standard HEALPix parameters
NSIDE = 128  # Order 7

# Rubin field parameters
FIELD_WIDTH = 3.5  # degrees, full width
FIELD_HEIGHT = 3.5  # degrees, full height
FIELD_DIAGONAL = np.sqrt(FIELD_WIDTH**2 + FIELD_HEIGHT**2)  # For initial cone search

def get_pixels_in_field(
    ra: float,
    dec: float,
    rotator_angle: float = 0.0,  # Ignored in simple version
    nside: int = NSIDE,
) -> np.ndarray:
    """Get HEALPix pixels that approximately overlap with a Rubin field pointing.
    
    This is a simplified version that treats the field as a circle with radius
    equal to the field width/2. This is good enough for our use case since:
    1. We're using NSIDE=128 (order 7) where pixels are ~0.5° across
    2. The Rubin field is 3.5° × 3.5°
    3. Small inaccuracies at field edges won't impact visit statistics much
    
    Args:
        ra: Right ascension of field center in degrees [0, 360)
        dec: Declination of field center in degrees [-90, 90]
        rotator_angle: Ignored in this simple version
        nside: HEALPix nside parameter (power of 2)
    
    Returns:
        Array of HEALPix pixel indices (nested scheme)
    """
    hp = HEALPix(nside=nside, order="nested", frame=ICRS())
    
    # Use circle with radius = field width/2
    # This will miss some corner pixels but include some extra edge pixels
    # The differences roughly cancel out for visit statistics
    return hp.cone_search_lonlat(
        lon=ra * u.deg,
        lat=dec * u.deg,
        radius=FIELD_WIDTH/2 * u.deg
    )


def count_pixel_visits(db_path: Path, cache_path: Optional[Path] = None) -> pd.Series:
    """Count the number of visits to each HEALPix pixel.
    
    This efficiently processes the OpSim database to count how many times each
    HEALPix pixel is observed, taking into account the field of view size.
    Results can optionally be cached for faster reuse.
    
    Args:
        db_path: Path to OpSim SQLite database
        cache_path: Optional path to cache results as parquet
    
    Returns:
        Series indexed by healpix pixel number containing visit counts
    """
    # Check cache first
    if cache_path is not None and cache_path.exists():
        return pd.read_parquet(cache_path)["visits"]
    
    print("\nCounting visits per HEALPix pixel...")
    visit_counts = {}  # pixel -> count
    
    with sqlite3.connect(db_path) as conn:
        # Process in chunks to avoid loading entire database
        chunk_size = 10000
        offset = 0
        
        while True:
            # Get a chunk of pointings
            query = f"""
            SELECT fieldRA, fieldDec, rotSkyPos
            FROM observations
            LIMIT {chunk_size} OFFSET {offset}
            """
            chunk = pd.read_sql_query(query, conn)
            if len(chunk) == 0:
                break
                
            if offset == 0:
                print(f"Processing pointings in chunks of {chunk_size:,}...")
            
            # Process each pointing
            for _, row in chunk.iterrows():
                # Get all pixels covered by this pointing
                pixels = get_pixels_in_field(
                    row["fieldRA"],
                    row["fieldDec"],
                    rotator_angle=row["rotSkyPos"]
                )
                
                # Update counts
                for pixel in pixels:
                    visit_counts[pixel] = visit_counts.get(pixel, 0) + 1
            
            offset += chunk_size
            if offset % 100000 == 0:
                print(f"  Processed {offset:,} pointings...")
    
    # Convert to Series
    visits = pd.Series(visit_counts, name="visits")
    visits.index.name = "healpix"
    
    # Cache if requested
    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        visits.to_frame().to_parquet(cache_path)
        print(f"\nVisit counts cached to {cache_path}")
    
    return visits


def build_observation_cache(db_path: Path, cache_path: Path) -> None:
    """Build and save cache mapping observation times to affected HEALPix pixels.
    
    This creates a mapping between HEALPix pixels and their observation times from
    the OpSim database. Each pointing in the database affects multiple pixels due
    to the field of view size.
    
    Args:
        db_path: Path to OpSim SQLite database
        cache_path: Path where to save the parquet cache file
    """
    import time
    print("\nBuilding pixel observation cache...")
    
    with sqlite3.connect(db_path) as conn:
        # Get total count first
        total = pd.read_sql_query("SELECT COUNT(*) as n FROM observations", conn).iloc[0]["n"]
        print(f"Total observations to process: {total:,}")
        
        # Process in chunks to avoid loading entire database
        chunk_size = 10000
        offset = 0
        start_time = time.time()
        total_pixels = 0
        
        while True:
            chunk_start = time.time()
            
            # Get a chunk of pointings
            query = f"""
            SELECT fieldRA, fieldDec, rotSkyPos, observationStartMJD
            FROM observations
            ORDER BY observationStartMJD
            LIMIT {chunk_size} OFFSET {offset}
            """
            chunk = pd.read_sql_query(query, conn)
            if len(chunk) == 0:
                break
            
            if offset == 0:
                print(f"Processing pointings in chunks of {chunk_size:,}...")
            
            # Process each pointing
            all_pixels = []  # HEALPix pixel numbers
            all_mjds = []    # Corresponding observation times
            
            for _, row in chunk.iterrows():
                # Get all pixels covered by this pointing
                pixels = get_pixels_in_field(
                    row["fieldRA"],
                    row["fieldDec"],
                    rotator_angle=row["rotSkyPos"]
                )
                
                # Add an entry for each pixel
                all_pixels.extend(pixels)
                all_mjds.extend([row["observationStartMJD"]] * len(pixels))
            
            # Create DataFrame for this chunk
            chunk_df = pd.DataFrame({
                "healpix": all_pixels,
                "mjd": all_mjds
            })
            
            # Accumulate chunks in memory
            if offset == 0:
                full_df = chunk_df
            else:
                full_df = pd.concat([full_df, chunk_df], ignore_index=True)
            
            # Update progress
            offset += chunk_size
            total_pixels += len(chunk_df)
            chunk_time = time.time() - chunk_start
            
            # Show basic progress every 1000 observations
            if offset % 1000 == 0:
                elapsed = time.time() - start_time
                obs_per_sec = offset / elapsed if elapsed > 0 else 0
                remaining = (total - offset) / obs_per_sec if obs_per_sec > 0 else 0
                
                print(
                    f"Progress: {offset:,}/{total:,} obs "
                    f"({offset/total:.1%}), "
                    f"Speed: {obs_per_sec:.1f} obs/sec, "
                    f"ETA: {remaining/60:.1f}m",
                    flush=True  # Force output
                )
            
            # Show detailed stats every 100k observations
            if offset % 100000 == 0:
                print(
                    f"\nGenerated {total_pixels:,} pixel-observation pairs "
                    f"({total_pixels/offset:.1f} pixels/pointing avg)"
                )
                print(
                    f"Memory used: {full_df.memory_usage(deep=True).sum()/1e9:.1f} GB"
                )
    
    print("\nSaving cache...")
    full_df.to_parquet(cache_path)
    print(f"Cache saved to {cache_path}")


def load_observation_cache(cache_path: Path) -> pd.DataFrame:
    """Load the pixel observation cache.
    
    Args:
        cache_path: Path to the parquet cache file
    
    Returns:
        DataFrame with columns:
            - healpix: HEALPix pixel index (nested scheme)
            - mjd: Modified Julian Date of observation
    
    Raises:
        FileNotFoundError: If cache file doesn't exist
    """
    if not cache_path.exists():
        raise FileNotFoundError(
            f"Cache file not found at {cache_path}. "
            "Run build_observation_cache() first."
        )
    
    return pd.read_parquet(cache_path)


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

    # Update northern boundary (adding field radius)
    for ra, dec in max_decs.items():
        idx = int(ra * 10)  # Convert RA to array index
        if idx < len(dec_north):
            dec_north[idx] = dec + FIELD_HEIGHT/2  # Add half field height

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