"""Functions for handling the Rubin Observatory footprint."""

from pathlib import Path
import random
from typing import List, Tuple, Optional, Dict

import numpy as np
import pandas as pd
from astropy_healpix import HEALPix
from astropy.coordinates import SkyCoord
import astropy.units as u

def extract_boundary(db_path: str | Path) -> Dict[int, float]:
    """Extract maximum declination per RA degree from OpSim.
    
    For each integer degree of RA, find the maximum declination of any pointing
    and add 1.75 degrees to account for the field radius.
    
    Args:
        db_path: Path to OpSim SQLite database
    
    Returns:
        Dictionary mapping RA degree (0-359) to max declination + field radius
    """
    # Read all unique pointings
    db_uri = f"sqlite:///{db_path}"
    query = """
    SELECT DISTINCT fieldRA, fieldDec 
    FROM observations
    """
    pointings = pd.read_sql_query(query, db_uri)
    
    # Round RA to nearest degree (0-359)
    pointings['ra_deg'] = pointings['fieldRA'].round().astype(int) % 360
    
    # Find max dec for each RA degree and add field radius
    boundary = pointings.groupby('ra_deg')['fieldDec'].max() + 1.75
    
    return boundary.to_dict()

def get_rubin_pixels(
    boundary: Dict[int, float],
    nside: int = 128
) -> List[int]:
    """Get all HEALPix pixels below the OpSim boundary.
    
    Args:
        boundary: Dictionary mapping RA degree to max declination
        nside: HEALPix nside parameter
    
    Returns:
        List of HEALPix pixel indices
    """
    hp = HEALPix(nside=nside, order='nested')
    
    # Get all pixel centers
    npix = hp.npix
    pixels = np.arange(npix)
    lon, lat = hp.healpix_to_lonlat(pixels)
    
    # Convert to degrees
    ra = lon.to_value(u.deg)
    dec = lat.to_value(u.deg)
    
    # Round RA to nearest degree for boundary lookup
    ra_deg = np.round(ra).astype(int) % 360
    
    # Create mask based on the boundary
    mask = np.zeros_like(pixels, dtype=bool)
    for i, (ra_i, dec_i) in enumerate(zip(ra_deg, dec)):
        max_dec = boundary.get(ra_i, 2.0)  # Default to +2° if no data
        mask[i] = dec_i <= max_dec
    
    # Return sorted list of pixels that match the mask
    return sorted(pixels[mask])

def pixel_to_radec(pixel: int, nside: int = 128) -> Tuple[float, float]:
    """Convert HEALPix pixel to (RA, Dec) of pixel center.
    
    Args:
        pixel: HEALPix pixel index
        nside: HEALPix nside parameter
    
    Returns:
        Tuple of (RA, Dec) in degrees
    """
    hp = HEALPix(nside=nside, order='nested')
    
    # Get longitude and latitude of pixel center
    lon, lat = hp.healpix_to_lonlat(pixel)
    
    # Convert to degrees
    ra = lon.to_value(u.deg)
    dec = lat.to_value(u.deg)
    
    return ra, dec