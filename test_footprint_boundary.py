#!/usr/bin/env python3
"""Test extraction and visualization of Rubin footprint boundaries."""

import numpy as np
import matplotlib.pyplot as plt

from cosmic_neighborhoods.footprint import (
    extract_boundary,
    save_footprint_cache,
    load_footprint_cache,
    get_dec_range_at_ra,
)

def main():
    """Extract and visualize footprint boundaries."""
    print("\nExtracting footprint boundaries...")
    opsim_db = "cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db"
    boundary = extract_boundary(opsim_db)
    
    # Save to cache
    cache_file = "cosmic_neighborhoods/data/footprint/boundary_nside128.npz"
    save_footprint_cache(boundary, cache_file)
    
    # Test loading from cache
    print("\nLoading from cache...")
    loaded = load_footprint_cache(cache_file)
    
    # Create visualization
    plt.figure(figsize=(15, 10))
    
    # Plot boundaries
    plt.subplot(2, 1, 1)
    plt.plot(boundary['ra'], boundary['dec_north'], 'b-', label='Northern boundary')
    plt.plot(boundary['ra'], boundary['dec_south'], 'r-', label='Southern boundary')
    plt.grid(True, alpha=0.3)
    plt.xlabel('Right Ascension (degrees)')
    plt.ylabel('Declination (degrees)')
    plt.title('Rubin Observatory Footprint Boundaries')
    plt.legend()
    
    # Test some specific RAs
    test_ras = [0, 90, 180, 270]
    print("\nTesting specific RAs:")
    for ra in test_ras:
        south, north = get_dec_range_at_ra(ra, boundary)
        print(f"RA {ra:3d}°: Dec range [{south:6.1f}°, {north:6.1f}°]")
        plt.plot([ra, ra], [south, north], 'g-', alpha=0.5)
    
    # Plot in Mollweide projection
    plt.subplot(2, 1, 2, projection='mollweide')
    
    # Convert to radians and handle Mollweide convention
    ra_rad = np.radians(boundary['ra'] - 180)
    dec_north_rad = np.radians(boundary['dec_north'])
    dec_south_rad = np.radians(boundary['dec_south'])
    
    plt.plot(ra_rad, dec_north_rad, 'b-', label='Northern boundary')
    plt.plot(ra_rad, dec_south_rad, 'r-', label='Southern boundary')
    
    # Add grid
    for ra_line in range(-180, 181, 30):
        plt.axvline(np.radians(ra_line), color='gray', alpha=0.2, linestyle=':')
    for dec_line in range(-90, 91, 15):
        plt.axhline(np.radians(dec_line), color='gray', alpha=0.2, linestyle=':')
    
    # Customize labels
    ra_ticks = np.array([-150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150])
    plt.xticks(np.radians(ra_ticks), [f"{(t + 180) % 360}°" for t in ra_ticks])
    dec_ticks = np.array([-75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75])
    plt.yticks(np.radians(dec_ticks), [f"{t}°" for t in dec_ticks])
    
    plt.title('Rubin Observatory Footprint (Mollweide projection)')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('footprint_boundary.png', dpi=150)
    print("\nPlot saved as footprint_boundary.png")

if __name__ == "__main__":
    main()

