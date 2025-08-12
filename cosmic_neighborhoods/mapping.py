"""Functions for mapping between population latitude and Rubin declination."""

from typing import Tuple

import numpy as np
import pandas as pd
from astropy_healpix import HEALPix
from astropy.coordinates import SkyCoord, ICRS
import astropy.units as u

from cosmic_neighborhoods.footprint import get_dec_range_at_ra

def map_latitude_to_declination(
    lat_deg: float,
    ra_deg: float,
    pop_cdf: pd.DataFrame,
    footprint_boundary: dict,
) -> float:
    """Map latitude to declination at specific RA using population percentile.
    
    For a given latitude φ and RA:
    1. Find what percentile φ is in global population distribution
    2. Get available declination range [δ_s, δ_n] at that RA
    3. Map percentile to that range
    
    Args:
        lat_deg: Input latitude in degrees [-90, 90]
        ra_deg: Right ascension in degrees [0, 360)
        pop_cdf: Population CDF DataFrame with columns:
                - lat_bin_center: Latitude bin center in degrees
                - cum_frac: Cumulative fraction of population south of latitude
        footprint_boundary: Dictionary with footprint boundaries from
                          extract_boundary() or load_footprint_cache()
    
    Returns:
        Declination in degrees that matches the input latitude's population percentile
        within the available range at the given RA
    
    Raises:
        ValueError: If latitude is outside valid range [-90, 90]
        ValueError: If RA is outside valid range [0, 360)
        ValueError: If CDF is not properly normalized or not monotonic
    """
    # Validate inputs
    if not -90 <= lat_deg <= 90:
        raise ValueError(f"Latitude {lat_deg}° must be between -90° and 90°")
    if not 0 <= ra_deg < 360:
        raise ValueError(f"RA {ra_deg}° must be in [0, 360)")
    
    # Validate CDF properties
    max_frac = pop_cdf['cum_frac'].max()
    if not 0.99 <= max_frac <= 1.01:
        raise ValueError(f"Population CDF not normalized: max = {max_frac:.3f}")
    if not (pop_cdf['cum_frac'].diff().dropna() >= 0).all():
        raise ValueError("Population CDF is not monotonically increasing")
    
    # Sort population data from south to north
    pop_sorted = pop_cdf.sort_values('lat_bin_center')
    
    # Get population percentile for input latitude
    pop_percentile = np.interp(
        lat_deg,
        pop_sorted['lat_bin_center'],
        pop_sorted['cum_frac'],
        left=0.0,  # South pole
        right=1.0  # North pole
    )
    
    # Get declination range at this RA
    dec_south, dec_north = get_dec_range_at_ra(ra_deg, footprint_boundary)
    
    # Map percentile to available declination range
    assigned_dec = dec_south + pop_percentile * (dec_north - dec_south)
    
    return assigned_dec

def assign_healpix_tile(
    ra_deg: float,
    dec_deg: float,
    nside: int = 128,
) -> int:
    """Return HEALPix nested pixel id containing (ra, dec).
    
    Args:
        ra_deg: Right ascension in degrees [0, 360)
        dec_deg: Declination in degrees [-90, 90]
        nside: HEALPix nside parameter (power of 2)
    
    Returns:
        HEALPix pixel index (nested scheme)
    
    Raises:
        ValueError: If RA/Dec out of valid ranges
        ValueError: If nside not a power of 2
    """
    # Validate inputs
    if not 0 <= ra_deg < 360:
        raise ValueError(f"RA {ra_deg}° must be in [0, 360)")
    if not -90 <= dec_deg <= 90:
        raise ValueError(f"Dec {dec_deg}° must be in [-90, 90]")
    if not (nside & (nside - 1) == 0):  # Power of 2 check
        raise ValueError(f"nside {nside} must be a power of 2")
    
    # Create HEALPix object (ICRS frame)
    hp = HEALPix(nside=nside, order='nested', frame=ICRS())
    
    # Create SkyCoord object
    coords = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame='icrs')
    
    # Convert to pixel index
    pixel = hp.skycoord_to_healpix(coords)
    
    return pixel