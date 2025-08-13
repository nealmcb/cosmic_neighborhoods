#!/usr/bin/env python3
"""Analyze northern coverage of Rubin footprint around RA 80-100°."""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from cosmic_neighborhoods.boundary import RubinBoundary

def main():
    """Analyze and visualize northern coverage."""
    print("\nAnalyzing northern coverage around RA 80-100°...")
    
    # Load boundary data
    boundary = RubinBoundary.from_cache("cosmic_neighborhoods/data/footprint/boundary_nside128.npz")
    
    # Create detailed RA range
    ra_range = np.arange(70, 110, 0.1)  # Extend a bit on both sides
    dec_north = np.array([boundary.get_dec_range(ra)[1] for ra in ra_range])
    dec_south = np.array([boundary.get_dec_range(ra)[0] for ra in ra_range])
    widths = dec_north - dec_south
    
    # Find maximum
    max_idx = np.argmax(dec_north)
    max_ra = ra_range[max_idx]
    max_dec = dec_north[max_idx]
    
    # Create figure
    fig = plt.figure(figsize=(15, 12))
    gs = GridSpec(3, 1, height_ratios=[2, 1, 1])
    
    # Plot 1: Northern boundary detail
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(ra_range, dec_north, 'b-', label='Northern boundary')
    ax1.axvline(max_ra, color='r', linestyle='--', alpha=0.5,
                label=f'Maximum at RA {max_ra:.1f}°')
    ax1.axhline(max_dec, color='r', linestyle='--', alpha=0.5)
    
    # Add points every 5 degrees
    ra_points = np.arange(75, 105, 5)
    dec_points = [boundary.get_dec_range(ra)[1] for ra in ra_points]
    ax1.plot(ra_points, dec_points, 'ko', markersize=4)
    for ra, dec in zip(ra_points, dec_points):
        ax1.annotate(f'({ra:.0f}°, {dec:.1f}°)',
                    (ra, dec), xytext=(0, 5),
                    textcoords='offset points', ha='center')
    
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Right Ascension (degrees)')
    ax1.set_ylabel('Northern Declination Limit (degrees)')
    ax1.set_title('Northern Boundary Detail')
    ax1.legend()
    
    # Plot 2: Width of coverage
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(ra_range, widths, 'g-', label='Coverage width')
    ax2.axvline(max_ra, color='r', linestyle='--', alpha=0.5)
    
    # Add width at maximum
    max_width = widths[max_idx]
    ax2.annotate(f'Width at RA {max_ra:.1f}°: {max_width:.1f}°',
                 (max_ra, max_width), xytext=(10, -10),
                 textcoords='offset points')
    
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Right Ascension (degrees)')
    ax2.set_ylabel('Coverage Width (degrees)')
    ax2.set_title('Footprint Width')
    
    # Plot 3: Rate of change
    ax3 = fig.add_subplot(gs[2])
    gradient = np.gradient(dec_north, ra_range)
    ax3.plot(ra_range, gradient, 'm-', label='Rate of change')
    ax3.axvline(max_ra, color='r', linestyle='--', alpha=0.5)
    ax3.axhline(0, color='gray', linestyle='-', alpha=0.3)
    
    ax3.grid(True, alpha=0.3)
    ax3.set_xlabel('Right Ascension (degrees)')
    ax3.set_ylabel('dDec/dRA (degrees/degree)')
    ax3.set_title('Rate of Change in Northern Boundary')
    
    plt.tight_layout()
    plt.savefig('northern_coverage.png', dpi=150)
    print("\nPlot saved as northern_coverage.png")
    
    # Print detailed statistics
    print("\nDetailed coverage statistics:")
    print(f"Maximum northern declination: {max_dec:.2f}° at RA {max_ra:.1f}°")
    
    # Look at values around the maximum
    print("\nNorthern declination values:")
    for ra in range(75, 105, 5):
        dec_n = boundary.get_dec_range(ra)[1]
        print(f"RA {ra:3d}°: {dec_n:6.2f}°")
    
    # Look for rapid changes
    gradient_abs = np.abs(gradient)
    steep_points = np.where(gradient_abs > np.percentile(gradient_abs, 95))[0]
    if len(steep_points) > 0:
        print("\nRegions of rapid change:")
        for idx in steep_points:
            ra = ra_range[idx]
            rate = gradient[idx]
            print(f"RA {ra:.1f}°: {rate:+.3f}°/°")

if __name__ == "__main__":
    main()

