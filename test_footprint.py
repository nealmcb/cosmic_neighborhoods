#!/usr/bin/env python3
"""Test Rubin footprint extraction from OpSim."""

from pathlib import Path
import time

import matplotlib.pyplot as plt
import numpy as np

from cosmic_neighborhoods.footprint import (
    extract_boundary,
    get_rubin_pixels,
    pixel_to_radec,
)

def timeit(func):
    """Simple timing decorator."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"  Took {end - start:.1f} seconds")
        return result
    return wrapper

@timeit
def get_boundary(db_path):
    """Extract the northern boundary from OpSim."""
    return extract_boundary(db_path)

@timeit
def get_pixels(boundary):
    """Get all pixels in the Rubin footprint."""
    return get_rubin_pixels(boundary, nside=128)

@timeit
def convert_to_radec(pixels):
    """Convert pixels to RA/Dec."""
    return [pixel_to_radec(p) for p in pixels]

def main() -> None:
    """Extract and visualize the Rubin footprint."""
    # Paths
    opsim_db = "cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db"
    
    # Extract the northern boundary
    print("\nExtracting northern boundary from OpSim database...")
    boundary = get_boundary(opsim_db)
    print(f"Found max declination for {len(boundary)} RA degrees")
    
    # Plot the boundary itself
    ra = sorted(boundary.keys())
    dec = [boundary[r] for r in ra]
    
    # Get all pixels below the boundary
    print("\nGetting all HEALPix pixels (nside=128) below the boundary...")
    pixels = get_pixels(boundary)
    print(f"Found {len(pixels):,} pixels")
    
    # Convert pixels to RA/Dec for visualization
    print("\nConverting pixels to RA/Dec...")
    ra_dec = convert_to_radec(pixels)
    pixel_ra = [r for r, _ in ra_dec]
    pixel_dec = [d for _, d in ra_dec]
    
    # Create plot
    print("\nCreating visualization...")
    plt.figure(figsize=(15, 10))
    
    # Mollweide projection of pixels
    plt.subplot(2, 1, 1)
    
    # Convert RA/Dec to radians and handle Mollweide RA convention
    ra_rad = np.radians([r - 180 for r in pixel_ra])  # Mollweide proj uses -180 to +180
    dec_rad = np.radians(pixel_dec)
    
    # Plot points
    plt.subplot(2, 1, 1, projection='mollweide')
    plt.scatter(ra_rad, dec_rad, s=1, alpha=0.5)  # Small points for density
    
    # Plot the boundary
    boundary_ra_rad = np.radians([r - 180 for r in ra])
    boundary_dec_rad = np.radians(dec)
    plt.plot(boundary_ra_rad, boundary_dec_rad, 'r-', alpha=0.8, label='Northern Boundary')
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Add more detailed grid
    for ra_line in range(-180, 181, 30):
        plt.axvline(np.radians(ra_line), color='gray', alpha=0.2, linestyle=':')
    for dec_line in range(-90, 91, 15):
        plt.axhline(np.radians(dec_line), color='gray', alpha=0.2, linestyle=':')
    
    # Customize labels
    ra_ticks = np.array([-150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150])
    plt.xticks(np.radians(ra_ticks), [f"{(t + 180) % 360}°" for t in ra_ticks])
    dec_ticks = np.array([-75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75])
    plt.yticks(np.radians(dec_ticks), [f"{t}°" for t in dec_ticks])
    
    plt.title("Rubin Observatory Footprint (HEALPix nside=128)")
    plt.legend()
    
    # Plot declination distribution
    plt.subplot(2, 1, 2)
    
    # Create declination bins
    dec_bins = np.arange(-90, 90.1, 0.1)
    dec_centers = (dec_bins[:-1] + dec_bins[1:]) / 2
    
    # Count pixels per bin
    counts, _ = np.histogram(pixel_dec, bins=dec_bins)
    plt.plot(dec_centers, counts)
    
    plt.xlabel("Declination (degrees)")
    plt.ylabel("Pixels per 0.1° bin")
    plt.title("Pixel Distribution vs Declination")
    plt.grid(True)
    
    # Add vertical lines at key declinations
    plt.axvline(-90, color='gray', alpha=0.3, linestyle=':')
    plt.axvline(2, color='gray', alpha=0.3, linestyle=':')
    
    plt.tight_layout()
    plt.savefig("footprint_opsim.png", dpi=150)
    print("\nPlot saved as footprint_opsim.png")
    
    # Print some statistics
    print(f"\nDeclination range: {min(pixel_dec):.1f}° to {max(pixel_dec):.1f}°")
    print(f"Boundary declination range: {min(dec):.1f}° to {max(dec):.1f}°")
    
    # Compute area
    nside = 128
    full_sky_area = 41252.96  # square degrees
    pixel_area = full_sky_area / (12 * nside * nside)
    total_area = len(pixels) * pixel_area
    print(f"Approximate survey area: {total_area:,.0f} deg²")
    
    # Look at the densest regions
    print("\nMost common declination bands:")
    dec_bins = np.arange(-90, 90.1, 1.0)  # 1° bins
    counts, _ = np.histogram(pixel_dec, bins=dec_bins)
    top_indices = np.argsort(counts)[-5:]  # Top 5 bins
    for idx in top_indices[::-1]:
        bin_start = dec_bins[idx]
        bin_end = dec_bins[idx + 1]
        n_points = counts[idx]
        print(f"  {bin_start:4.1f}° to {bin_end:4.1f}°: {n_points:,} pixels")

if __name__ == "__main__":
    main()