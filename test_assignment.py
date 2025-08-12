#!/usr/bin/env python3
"""Test cosmic neighborhood assignments with small variations."""

import warnings
warnings.filterwarnings('ignore')

from cosmic_neighborhoods.mapping import map_latitude_to_declination, assign_healpix_tile
from cosmic_neighborhoods.population import build_population_cdf
from cosmic_neighborhoods.footprint import extract_boundary, load_footprint_cache
from cosmic_neighborhoods.ephemeris import sun_ra_deg

def format_assignment(lat: float, date: str, ra: float, dec: float, pixel: int, nside: int = 128) -> str:
    """Format assignment in standard output format."""
    return (f"neighborhood for {lat:.6f} N, {date} RA {ra:.6f}, "
            f"Dec {dec:.6f}, in HEALPix {pixel} (nside={nside}).")

def main():
    """Test assignments with small variations."""
    # Load data
    print("\nLoading data...")
    pop_cdf = build_population_cdf("cosmic_neighborhoods/data/population/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif")
    
    # Load footprint boundary
    try:
        boundary = load_footprint_cache("cosmic_neighborhoods/data/footprint/boundary_nside128.npz")
    except FileNotFoundError:
        print("Extracting footprint boundary...")
        opsim_db = "cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db"
        boundary = extract_boundary(opsim_db)
    
    # Test different nside values
    print("\nTesting different nside values for 40°N, 2024-03-14:")
    base_lat = 40.0
    base_date = "2024-03-14"
    sun_ra = sun_ra_deg(base_date)
    assigned_ra = (sun_ra + 180.0) % 360.0
    
    for nside in [32, 64, 128]:
        dec = map_latitude_to_declination(base_lat, assigned_ra, pop_cdf, boundary)
        pixel = assign_healpix_tile(assigned_ra, dec, nside)
        print(format_assignment(base_lat, base_date, assigned_ra, dec, pixel, nside))
    
    # Test latitude variations around 40°N
    print("\nTesting latitude variations around 40°N:")
    base_lat = 40.0
    deltas = [0.01, 0.1, 0.5, 1.0]
    test_lats = [base_lat + delta for delta in deltas]
    
    sun_ra = sun_ra_deg(base_date)
    assigned_ra = (sun_ra + 180.0) % 360.0
    
    for lat in test_lats:
        dec = map_latitude_to_declination(lat, assigned_ra, pop_cdf, boundary)
        pixel = assign_healpix_tile(assigned_ra, dec)
        print(format_assignment(lat, base_date, assigned_ra, dec, pixel))
    
    # Test latitude variations around 25°N
    print("\nTesting latitude variations around 25°N:")
    base_lat = 25.0
    deltas = [0.01, 0.1, 0.5]
    test_lats = [base_lat + delta for delta in deltas]
    
    for lat in test_lats:
        dec = map_latitude_to_declination(lat, assigned_ra, pop_cdf, boundary)
        pixel = assign_healpix_tile(assigned_ra, dec)
        print(format_assignment(lat, base_date, assigned_ra, dec, pixel))
    
    # Test notable birthdays at 40°N
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
        dec = map_latitude_to_declination(base_lat, assigned_ra, pop_cdf, boundary)
        pixel = assign_healpix_tile(assigned_ra, dec)
        print(f"\n# {person}")
        print(format_assignment(base_lat, date, assigned_ra, dec, pixel))

if __name__ == "__main__":
    main()