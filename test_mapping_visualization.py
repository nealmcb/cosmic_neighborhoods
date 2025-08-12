#!/usr/bin/env python3
"""Visualize how latitude to declination mapping varies with RA."""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import matplotlib.pyplot as plt

from cosmic_neighborhoods.mapping import map_latitude_to_declination
from cosmic_neighborhoods.population import build_population_cdf
from cosmic_neighborhoods.footprint import extract_boundary, load_footprint_cache

def main():
    """Create visualizations of the mapping."""
    print("\nLoading data...")
    pop_cdf = build_population_cdf("cosmic_neighborhoods/data/population/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif")
    
    # Load footprint boundary
    try:
        boundary = load_footprint_cache("cosmic_neighborhoods/data/footprint/boundary_nside128.npz")
    except FileNotFoundError:
        print("Extracting footprint boundary...")
        opsim_db = "cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db"
        boundary = extract_boundary(opsim_db)
    
    # Create figure
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Mapping at key RAs
    plt.subplot(2, 1, 1)
    test_ras = [0, 90, 180, 270, 330]  # Four cardinal points plus deepest south
    colors = ['b', 'g', 'r', 'c', 'm']
    
    lats = np.linspace(-90, 90, 181)  # 1° steps
    for ra, color in zip(test_ras, colors):
        decs = [map_latitude_to_declination(lat, ra, pop_cdf, boundary)
                for lat in lats]
        plt.plot(lats, decs, color=color, alpha=0.7,
                label=f'RA {ra}°')
    
    plt.plot(lats, lats, ':', color='gray', alpha=0.5,
             label='1:1 line')
    
    plt.grid(True, alpha=0.3)
    plt.xlabel('Input Latitude (degrees)')
    plt.ylabel('Mapped Declination (degrees)')
    plt.title('Latitude → Declination Mapping at Different RAs')
    plt.legend()
    
    # Plot 2: Heatmap of mapping across all RAs
    plt.subplot(2, 1, 2)
    
    # Create grid
    ra_grid = np.arange(0, 360, 10)  # 10° RA steps
    lat_grid = np.arange(-90, 91, 5)  # 5° latitude steps
    dec_grid = np.zeros((len(lat_grid), len(ra_grid)))
    
    # Fill grid
    for i, lat in enumerate(lat_grid):
        for j, ra in enumerate(ra_grid):
            dec_grid[i, j] = map_latitude_to_declination(lat, ra, pop_cdf, boundary)
    
    # Plot heatmap
    plt.imshow(dec_grid, aspect='auto', origin='lower',
               extent=[0, 360, -90, 90],
               cmap='viridis')
    plt.colorbar(label='Mapped Declination (degrees)')
    
    # Add grid
    plt.grid(True, alpha=0.3)
    plt.xlabel('Right Ascension (degrees)')
    plt.ylabel('Input Latitude (degrees)')
    plt.title('Latitude → Declination Mapping Across All RAs')
    
    # Add example points
    example_points = [
        (40.0, 174.1, "March 14"),  # Base test case
        (40.0, 303.1, "Rubin"),
        (40.0, 117.3, "MLK"),
        (25.0, 174.1, "25°N test"),
        (40.0, 330.0, "Deepest South"),  # Added point at RA 330°
    ]
    
    for lat, ra, label in example_points:
        dec = map_latitude_to_declination(lat, ra, pop_cdf, boundary)
        plt.plot(ra, lat, 'r*')
        plt.annotate(f"{label}\n({ra:.1f}°, {lat:.1f}°) → {dec:.1f}°",
                    (ra, lat), xytext=(10, 10),
                    textcoords='offset points',
                    color='white', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('mapping_analysis.png', dpi=150)
    print("\nPlot saved as mapping_analysis.png")
    
    # Print some statistics
    print("\nMapping examples at different RAs:")
    test_lats = [-60, -30, 0, 25, 40, 60]
    print("\nRA      ", end='')
    for lat in test_lats:
        print(f"{lat:8.1f}°N", end='')
    print()
    print("-" * 60)
    
    for ra in test_ras:
        print(f"{ra:3d}° → ", end='')
        for lat in test_lats:
            dec = map_latitude_to_declination(lat, ra, pop_cdf, boundary)
            print(f"{dec:8.1f}°", end='')
        print()

if __name__ == "__main__":
    main()