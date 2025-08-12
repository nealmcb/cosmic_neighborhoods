#!/usr/bin/env python3
"""Test cosmic neighborhood assignments with small variations."""

import warnings
# Suppress all warnings at the start
warnings.filterwarnings('ignore')

from cosmic_neighborhoods.mapping import map_latitude_to_declination, assign_healpix_tile
from cosmic_neighborhoods.population import build_population_cdf
from cosmic_neighborhoods.footprint import extract_boundary, get_rubin_pixels
from cosmic_neighborhoods.ephemeris import sun_ra_deg
from test_mapping import create_declination_cdf

def format_assignment(lat: float, date: str, ra: float, dec: float, pixel: int, nside: int = 128) -> str:
    """Format assignment in standard output format."""
    return (f"neighborhood for {lat:.6f} N, {date} RA {ra:.6f}, "
            f"Dec {dec:.6f}, in HEALPix {pixel} (nside={nside}).")

def main():
    """Test assignments with small variations."""
    # Load data
    print("\nLoading data...")
    pop_cdf = build_population_cdf("cosmic_neighborhoods/data/population/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif")
    
    opsim_db = "cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db"
    boundary = extract_boundary(opsim_db)
    
    # Test different nside values
    print("\nTesting different nside values for 40°N, 2024-03-14:")
    base_lat = 40.0
    base_date = "2024-03-14"
    for nside in [32, 64, 128]:
        pixels = get_rubin_pixels(boundary, nside=nside)
        dec_cdf = create_declination_cdf(pixels, nside)
        
        sun_ra = sun_ra_deg(base_date)
        assigned_ra = (sun_ra + 180.0) % 360.0
        dec = map_latitude_to_declination(base_lat, pop_cdf, dec_cdf)
        pixel = assign_healpix_tile(assigned_ra, dec, nside)
        
        print(format_assignment(base_lat, base_date, assigned_ra, dec, pixel, nside))
    
    # Reset to nside=128 for remaining tests
    pixels = get_rubin_pixels(boundary)
    dec_cdf = create_declination_cdf(pixels)
    
    print("\nTesting latitude variations around 40°N:")
    base_lat = 40.0
    deltas = [0.01, 0.1, 0.5, 1.0]
    test_lats = [base_lat + delta for delta in deltas]
    
    sun_ra = sun_ra_deg(base_date)
    assigned_ra = (sun_ra + 180.0) % 360.0
    
    for lat in test_lats:
        dec = map_latitude_to_declination(lat, pop_cdf, dec_cdf)
        pixel = assign_healpix_tile(assigned_ra, dec)
        print(format_assignment(lat, base_date, assigned_ra, dec, pixel))
    
    print("\nTesting latitude variations around 25°N:")
    base_lat = 25.0
    deltas = [0.01, 0.1, 0.5]
    test_lats = [base_lat + delta for delta in deltas]
    
    for lat in test_lats:
        dec = map_latitude_to_declination(lat, pop_cdf, dec_cdf)
        pixel = assign_healpix_tile(assigned_ra, dec)
        print(format_assignment(lat, base_date, assigned_ra, dec, pixel))
    
    print("\nTesting notable birthdays at 40°N:")
    notable_dates = [
        ("1928-07-23", "Vera Rubin"),
        ("1929-01-15", "Martin Luther King Jr."),
        ("1869-10-02", "Mahatma Gandhi"),
    ]
    
    base_lat = 40.0
    for date, person in notable_dates:
        sun_ra = sun_ra_deg(date)
        assigned_ra = (sun_ra + 180.0) % 360.0
        dec = map_latitude_to_declination(base_lat, pop_cdf, dec_cdf)
        pixel = assign_healpix_tile(assigned_ra, dec)
        print(f"\n# {person} (note: pre-1900 dates have reduced ephemeris accuracy)")
        print(format_assignment(base_lat, date, assigned_ra, dec, pixel))

if __name__ == "__main__":
    main()