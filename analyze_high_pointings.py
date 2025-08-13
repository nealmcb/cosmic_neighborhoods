#!/usr/bin/env python3
"""Analyze density of pointings at high declinations."""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import pandas as pd
from astropy.coordinates import SkyCoord, GeocentricTrueEcliptic
import astropy.units as u

def main():
    """Analyze and visualize high-declination pointings."""
    print("\nAnalyzing high-declination pointings...")
    
    # Read all pointings
    db_uri = "sqlite:///cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db"
    query = """
    SELECT fieldRA, fieldDec, COUNT(*) as n_visits
    FROM observations
    GROUP BY fieldRA, fieldDec
    """
    pointings = pd.read_sql_query(query, db_uri)
    
    # Focus on high declinations
    high_points = pointings[pointings['fieldDec'] > 30]
    print(f"\nFound {len(high_points):,} unique pointings above +30°")
    
    # Create figure
    plt.figure(figsize=(20, 15))
    
    # Plot 1: Scatter plot colored by number of visits
    plt.subplot(211)
    
    # Get ecliptic curve for reference
    ecl_lon = np.linspace(0, 360, 360)
    ecl_lat = np.zeros_like(ecl_lon)
    coords = SkyCoord(
        lon=ecl_lon * u.deg,
        lat=ecl_lat * u.deg,
        frame=GeocentricTrueEcliptic
    )
    ecl_ra = coords.icrs.ra.deg
    ecl_dec = coords.icrs.dec.deg
    
    # Plot ecliptic
    plt.plot(ecl_ra, ecl_dec, 'r--', alpha=0.5, label='Ecliptic plane')
    
    # Plot pointings
    scatter = plt.scatter(high_points['fieldRA'], high_points['fieldDec'],
                         c=high_points['n_visits'], norm=LogNorm(),
                         s=50, alpha=0.6, cmap='viridis')
    plt.colorbar(scatter, label='Number of visits')
    
    plt.grid(True, alpha=0.3)
    plt.xlabel('Right Ascension (degrees)')
    plt.ylabel('Declination (degrees)')
    plt.title('High-Declination Pointings (>30°)')
    plt.legend()
    
    # Plot 2: Detailed view of RA 70-110°
    plt.subplot(212)
    
    # Create 2D histogram
    ra_bins = np.arange(70, 110.1, 0.2)  # 0.2° bins in RA
    dec_bins = np.arange(30, 40.1, 0.2)  # 0.2° bins in Dec
    
    # Filter points for this region
    region = high_points[
        (high_points['fieldRA'] >= 70) &
        (high_points['fieldRA'] <= 110)
    ]
    
    # Create visit count grid
    grid, _, _ = np.histogram2d(
        region['fieldRA'],
        region['fieldDec'],
        bins=[ra_bins, dec_bins],
        weights=region['n_visits']
    )
    
    # Plot heatmap
    plt.imshow(grid.T, origin='lower', aspect='auto',
               extent=[70, 110, 30, 40],
               norm=LogNorm(),
               cmap='viridis')
    plt.colorbar(label='Number of visits')
    
    # Plot ecliptic in this region
    mask = (ecl_ra >= 70) & (ecl_ra <= 110)
    plt.plot(ecl_ra[mask], ecl_dec[mask], 'r--', alpha=0.5,
             label='Ecliptic plane')
    
    # Add contours for specific visit counts
    levels = [1, 2, 5, 10, 20]
    contours = plt.contour(
        (ra_bins[:-1] + ra_bins[1:]) / 2,
        (dec_bins[:-1] + dec_bins[1:]) / 2,
        grid.T,
        levels=levels,
        colors='white',
        alpha=0.3,
        linewidths=1
    )
    plt.clabel(contours, inline=True, fontsize=8, fmt='%d visits')
    
    plt.grid(True, alpha=0.3)
    plt.xlabel('Right Ascension (degrees)')
    plt.ylabel('Declination (degrees)')
    plt.title('Visit Density in Northern Region')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('high_pointings.png', dpi=300)
    print("\nPlot saved as high_pointings.png")
    
    # Print statistics about visit counts
    print("\nVisit statistics for pointings above 30°:")
    visits = high_points['n_visits']
    print(f"  Minimum visits: {visits.min()}")
    print(f"  Maximum visits: {visits.max()}")
    print(f"  Median visits: {visits.median():.1f}")
    print(f"  Mean visits: {visits.mean():.1f}")
    
    # Count pointings with different visit thresholds
    print("\nNumber of pointings by visit count:")
    thresholds = [1, 2, 5, 10, 20, 50, 100]
    for i in range(len(thresholds)):
        min_visits = thresholds[i]
        max_visits = thresholds[i+1] if i < len(thresholds)-1 else float('inf')
        count = ((visits >= min_visits) & (visits < max_visits)).sum()
        if i < len(thresholds)-1:
            print(f"  {min_visits}-{max_visits-1} visits: {count:,} pointings")
        else:
            print(f"  {min_visits}+ visits: {count:,} pointings")
    
    # Look at highest-visit pointings
    print("\nTop 10 most-visited high-declination pointings:")
    top_10 = high_points.nlargest(10, 'n_visits')
    for _, row in top_10.iterrows():
        print(f"  RA {row['fieldRA']:6.2f}°, Dec {row['fieldDec']:6.2f}°: {row['n_visits']:,} visits")

if __name__ == "__main__":
    main()

