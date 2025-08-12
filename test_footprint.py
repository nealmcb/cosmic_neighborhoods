#!/usr/bin/env python3
"""Test Rubin footprint extraction from OpSim."""

import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main() -> None:
    """Extract and visualize the Rubin footprint."""
    # Path to OpSim database
    opsim_db = "cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db"
    
    # Extract unique pointings directly
    print("\nExtracting pointings from OpSim database...")
    conn = sqlite3.connect(opsim_db)
    query = """
    SELECT DISTINCT fieldRA, fieldDec
    FROM observations
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    print(f"Found {len(df):,} unique pointings")
    
    # Create plot
    print("\nCreating visualization...")
    plt.figure(figsize=(15, 10))
    
    # Mollweide projection of pointings
    plt.subplot(2, 1, 1)
    
    # Convert RA/Dec to radians and handle Mollweide RA convention
    ra_rad = np.radians(df.fieldRA - 180)  # Mollweide proj uses -180 to +180
    dec_rad = np.radians(df.fieldDec)
    
    # Plot points
    plt.subplot(2, 1, 1, projection='mollweide')
    plt.scatter(ra_rad, dec_rad, s=0.1, alpha=0.1)  # Smaller points, more transparent
    
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
    
    plt.title("Rubin Observatory Pointings from OpSim v3.2")
    
    # Plot declination distribution
    plt.subplot(2, 1, 2)
    
    # Create declination bins
    dec_bins = np.arange(-90, 90.1, 0.1)
    dec_centers = (dec_bins[:-1] + dec_bins[1:]) / 2
    
    # Count pointings per bin
    counts, _ = np.histogram(df.fieldDec, bins=dec_bins)
    plt.plot(dec_centers, counts)
    
    plt.xlabel("Declination (degrees)")
    plt.ylabel("Pointings per 0.1° bin")
    plt.title("Pointing Distribution vs Declination")
    plt.grid(True)
    
    # Add vertical lines at key declinations
    plt.axvline(-90, color='gray', alpha=0.3, linestyle=':')
    plt.axvline(2, color='gray', alpha=0.3, linestyle=':')
    
    plt.tight_layout()
    plt.savefig("footprint.png", dpi=150)
    print("\nPlot saved as footprint.png")
    
    # Print some statistics
    print(f"\nDeclination range: {df.fieldDec.min():.1f}° to {df.fieldDec.max():.1f}°")
    
    # Look at the densest regions
    print("\nMost common declination bands:")
    dec_bins = np.arange(-90, 90.1, 1.0)  # 1° bins
    counts, _ = np.histogram(df.fieldDec, bins=dec_bins)
    top_indices = np.argsort(counts)[-5:]  # Top 5 bins
    for idx in top_indices[::-1]:
        bin_start = dec_bins[idx]
        bin_end = dec_bins[idx + 1]
        n_points = counts[idx]
        print(f"  {bin_start:4.1f}° to {bin_end:4.1f}°: {n_points:,} pointings")

if __name__ == "__main__":
    main()