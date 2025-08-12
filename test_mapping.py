#!/usr/bin/env python3
"""Test the mapping between population latitude and Rubin declination."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from cosmic_neighborhoods.mapping import map_latitude_to_declination, assign_healpix_tile
from cosmic_neighborhoods.population import build_population_cdf
from cosmic_neighborhoods.footprint import extract_boundary, get_rubin_pixels, pixel_to_radec

def create_declination_cdf(pixels, nside=128):
    """Create declination CDF from HEALPix pixels."""
    # Get declination for each pixel
    ra_dec = [pixel_to_radec(p, nside) for p in pixels]
    dec = [d for _, d in ra_dec]
    
    # Create bins
    dec_bins = np.arange(-90, 90.1, 0.1)  # 0.1° bins
    dec_centers = (dec_bins[:-1] + dec_bins[1:]) / 2
    
    # Count pixels per bin
    counts, _ = np.histogram(dec, bins=dec_bins)
    cum_counts = np.cumsum(counts)
    cum_frac = cum_counts / cum_counts[-1]
    
    # Create DataFrame
    return pd.DataFrame({
        'dec_bin_center': dec_centers,
        'cum_frac': cum_frac
    })

def find_percentile_value(df: pd.DataFrame, lat_col: str, cum_col: str, percentile: float) -> float:
    """Find the latitude/declination at a given percentile."""
    # Sort by cumulative fraction
    df_sorted = df.sort_values(cum_col)
    
    # Interpolate to find value at percentile
    return np.interp(
        percentile,
        df_sorted[cum_col],
        df_sorted[lat_col]
    )

def main():
    """Test the mapping with real data."""
    print("\nLoading population CDF...")
    pop_cdf = build_population_cdf("cosmic_neighborhoods/data/population/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif")
    
    print("\nExtracting Rubin footprint boundary...")
    opsim_db = "cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db"
    boundary = extract_boundary(opsim_db)
    
    print("\nGetting Rubin pixels...")
    pixels = get_rubin_pixels(boundary, nside=128)
    
    print("\nCreating declination CDF...")
    dec_cdf = create_declination_cdf(pixels)
    
    # Sanity check: Find key percentiles in both distributions
    percentiles = [0.1, 0.25, 0.5, 0.75, 0.9]
    print("\nDistribution percentiles:")
    print("                Population    Rubin")
    print("Percentile    Latitude(°N)   Dec(°)")
    print("-" * 40)
    for p in percentiles:
        pop_lat = find_percentile_value(pop_cdf, 'lat_bin_center', 'cum_frac', p)
        dec_val = find_percentile_value(dec_cdf, 'dec_bin_center', 'cum_frac', p)
        print(f"{p:4.2f}         {pop_lat:8.1f}     {dec_val:8.1f}")
    
    # Test latitudes from north to south
    test_lats = [90, 60, 40, 25, 0, -30, -60, -90]
    print("\nTesting latitude → declination mapping (north to south):")
    for lat in test_lats:
        dec = map_latitude_to_declination(lat, pop_cdf, dec_cdf)
        print(f"  {lat:4d}°N → {dec:5.1f}°")
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # Plot both CDFs
    plt.subplot(2, 1, 1)
    plt.plot(pop_cdf['lat_bin_center'], pop_cdf['cum_frac'],
             label='Population', alpha=0.7)
    plt.plot(dec_cdf['dec_bin_center'], dec_cdf['cum_frac'],
             label='Rubin Footprint', alpha=0.7)
    plt.grid(True, alpha=0.3)
    plt.xlabel('Latitude / Declination (degrees)')
    plt.ylabel('Cumulative Fraction')
    plt.title('Population and Footprint CDFs')
    plt.legend()
    
    # Plot the mapping function
    plt.subplot(2, 1, 2)
    lats = np.linspace(90, -90, 181)  # 1° steps, north to south
    decs = [map_latitude_to_declination(lat, pop_cdf, dec_cdf)
            for lat in lats]
    plt.plot(lats, decs, '-', alpha=0.7)
    plt.plot(lats, lats, ':', color='gray', alpha=0.5,
             label='1:1 line')
    
    # Add test points
    plt.plot(test_lats,
             [map_latitude_to_declination(lat, pop_cdf, dec_cdf)
              for lat in test_lats],
             'o', label='Test points')
    
    plt.grid(True, alpha=0.3)
    plt.xlabel('Input Latitude (degrees)')
    plt.ylabel('Mapped Declination (degrees)')
    plt.title('Latitude → Declination Mapping Function')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('mapping.png', dpi=150)
    print("\nPlot saved as mapping.png")
    
    # Test HEALPix assignment
    print("\nTesting HEALPix assignment:")
    ra = 123.4
    dec = map_latitude_to_declination(40, pop_cdf, dec_cdf)
    pixel = assign_healpix_tile(ra, dec)
    print(f"  RA={ra}°, Dec={dec}° → pixel {pixel}")

if __name__ == "__main__":
    main()