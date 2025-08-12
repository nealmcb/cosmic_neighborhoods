"""Functions for mapping between population latitude and Rubin declination."""

from typing import Tuple

import numpy as np
import pandas as pd
from astropy_healpix import HEALPix
from astropy.coordinates import SkyCoord, ICRS
import astropy.units as u

def map_latitude_to_declination(
    lat_deg: float,
    pop_cdf: pd.DataFrame,
    dec_cdf: pd.DataFrame,
) -> float:
    """Find declination δ such that F_r(δ) = F_h(φ).
    
    Maps northern latitudes to northern declinations by matching percentiles:
    - For latitude φ, find what percentile it is in population distribution
    - Find the declination δ at the same percentile in Rubin footprint
    
    Args:
        lat_deg: Input latitude in degrees
        pop_cdf: Population CDF DataFrame with columns:
                - lat_bin_center: Latitude bin center in degrees
                - cum_frac: Cumulative fraction of population south of latitude
        dec_cdf: Declination CDF DataFrame with columns:
                - dec_bin_center: Declination bin center in degrees
                - cum_frac: Cumulative fraction of pixels south of declination
    
    Returns:
        Declination in degrees that matches the input latitude's population percentile
    
    Raises:
        ValueError: If latitude is outside valid range [-90, 90]
        ValueError: If CDFs are not properly normalized or not monotonic
    """
    # Validate input latitude
    if not -90 <= lat_deg <= 90:
        raise ValueError(f"Latitude {lat_deg}° must be between -90° and 90°")
    
    # Validate CDF properties
    for cdf, name in [(pop_cdf, "Population"), (dec_cdf, "Declination")]:
        # Check normalization (allowing for small numerical errors)
        max_frac = cdf['cum_frac'].max()
        if not 0.99 <= max_frac <= 1.01:
            raise ValueError(f"{name} CDF not normalized: max = {max_frac:.3f}")
        
        # Check monotonicity
        if not (cdf['cum_frac'].diff().dropna() >= 0).all():
            raise ValueError(f"{name} CDF is not monotonically increasing")
    
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
    
    # Sort declination data from south to north
    dec_sorted = dec_cdf.sort_values('dec_bin_center')
    
    # Find matching declination at same percentile
    assigned_dec = np.interp(
        pop_percentile,
        dec_sorted['cum_frac'],
        dec_sorted['dec_bin_center'],
        left=dec_sorted['dec_bin_center'].min(),  # Southern limit
        right=dec_sorted['dec_bin_center'].max()  # Northern limit
    )
    
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