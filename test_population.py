#!/usr/bin/env python3
"""Test GHSL population data processing."""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from cosmic_neighborhoods.population import build_population_cdf, population_percentile

def main() -> None:
    """Load GHSL data and verify population distribution."""
    # Path to GHSL GeoTIFF
    data_path = Path("cosmic_neighborhoods/data/population/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif")
    
    print(f"\nProcessing GHSL population data from: {data_path}")
    print("(This may take a few minutes on first run...)")
    
    # Load and bin the data
    df = build_population_cdf(data_path, source_type="ghsl")
    
    # Print some statistics
    total_pop = df["population"].sum()
    print(f"\nTotal population: {total_pop:,.0f}")
    
    # Test some key latitudes
    test_lats = [-60, -30, 0, 30, 60]
    print("\nPopulation distribution:")
    for lat in test_lats:
        p = population_percentile(lat, df)
        print(f"  {lat:3d}°: {p*100:5.1f}% of population lives south of this latitude")
    
    # Look at specific 40-40.1° band
    lat_band = df[
        (df["lat_bin_center"] >= 40.0) & 
        (df["lat_bin_center"] < 40.1)
    ]
    band_pop = lat_band["population"].sum()
    band_percent = (band_pop / total_pop) * 100
    print(f"\nPopulation between 40.0° and 40.1°N:")
    print(f"  Count: {band_pop:,.0f}")
    print(f"  Percentage: {band_percent:.3f}% of global population")
    
    # Create a simple plot
    plt.figure(figsize=(12, 6))
    
    # Population by latitude
    plt.subplot(1, 2, 1)
    plt.plot(df["lat_bin_center"], df["population"])
    plt.xlabel("Latitude (degrees)")
    plt.ylabel("Population")
    plt.title("Population Distribution by Latitude")
    plt.grid(True)
    
    # Cumulative distribution
    plt.subplot(1, 2, 2)
    plt.plot(df["lat_bin_center"], df["cum_frac"])
    plt.xlabel("Latitude (degrees)")
    plt.ylabel("Cumulative Fraction")
    plt.title("Cumulative Population Distribution")
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("population_distribution.png")
    print("\nPlot saved as population_distribution.png")

if __name__ == "__main__":
    main()