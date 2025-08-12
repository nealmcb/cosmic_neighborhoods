#!/usr/bin/env python3
"""Analyze timing of high-declination visits."""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from astropy.time import Time
import astropy.units as u

def mjd_to_datetime(mjd):
    """Convert MJD to datetime."""
    return Time(mjd, format='mjd').datetime

def main():
    """Analyze and visualize visit timing."""
    print("\nAnalyzing timing of high-declination visits...")
    
    # Read all observations above 30°
    db_uri = "sqlite:///cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db"
    query = """
    SELECT fieldRA, fieldDec, observationStartMJD, filter, note
    FROM observations
    WHERE fieldDec > 30
    ORDER BY observationStartMJD
    """
    visits = pd.read_sql_query(query, db_uri)
    
    # Convert MJD to datetime
    visits['datetime'] = [mjd_to_datetime(mjd) for mjd in visits['observationStartMJD']]
    visits['year'] = [d.year for d in visits['datetime']]
    visits['month'] = [d.month for d in visits['datetime']]
    
    # Create figure
    plt.figure(figsize=(20, 15))
    
    # Plot 1: Visits over time
    plt.subplot(311)
    
    # Create scatter plot
    scatter = plt.scatter(visits['observationStartMJD'], visits['fieldDec'],
                         c=visits['fieldRA'], cmap='twilight',
                         s=30, alpha=0.6)
    plt.colorbar(scatter, label='Right Ascension (degrees)')
    
    # Format x-axis with dates
    start_date = mjd_to_datetime(visits['observationStartMJD'].min())
    end_date = mjd_to_datetime(visits['observationStartMJD'].max())
    plt.title(f'High-Declination Visits ({start_date.year} to {end_date.year})')
    plt.xlabel('Time (MJD)')
    plt.ylabel('Declination (degrees)')
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Histogram of visits by year/month
    plt.subplot(312)
    
    # Create year-month strings
    visits['yearmonth'] = [f"{y}-{m:02d}" for y, m in zip(visits['year'], visits['month'])]
    monthly_counts = visits['yearmonth'].value_counts().sort_index()
    
    plt.bar(range(len(monthly_counts)), monthly_counts.values, alpha=0.7)
    plt.xticks(range(len(monthly_counts)), monthly_counts.index,
               rotation=45, ha='right')
    plt.title('Visits per Month')
    plt.ylabel('Number of Visits')
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Visit timing analysis
    plt.subplot(313)
    
    # Group visits by field
    fields = visits.groupby(['fieldRA', 'fieldDec'])
    
    # Calculate time between visits for each field
    time_diffs = []
    n_visits = []
    for _, field_visits in fields:
        if len(field_visits) > 1:
            # Sort by time
            sorted_times = np.sort(field_visits['observationStartMJD'].values)
            # Calculate time differences in days
            diffs = np.diff(sorted_times)
            time_diffs.extend(diffs)
            n_visits.append(len(field_visits))
    
    # Plot histogram of time differences
    if time_diffs:
        plt.hist(time_diffs, bins=50, alpha=0.7)
        plt.xlabel('Time Between Visits (days)')
        plt.ylabel('Number of Visit Pairs')
        plt.title('Distribution of Time Between Visits')
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('high_timing.png', dpi=300)
    print("\nPlot saved as high_timing.png")
    
    # Print timing statistics
    print("\nTiming statistics:")
    print(f"First visit: {start_date}")
    print(f"Last visit: {end_date}")
    print(f"Total duration: {(end_date - start_date).days} days")
    print(f"Total visits: {len(visits):,}")
    
    if time_diffs:
        time_diffs = np.array(time_diffs)
        print("\nTime between visits:")
        print(f"  Minimum: {time_diffs.min():.1f} days")
        print(f"  Maximum: {time_diffs.max():.1f} days")
        print(f"  Median: {np.median(time_diffs):.1f} days")
        print(f"  Mean: {time_diffs.mean():.1f} days")
    
    # Look at visit filters
    print("\nVisits by filter:")
    filter_counts = visits['filter'].value_counts()
    for filter_name, count in filter_counts.items():
        print(f"  {filter_name}: {count:,} visits")
    
    # Check for any notes or special flags
    if 'note' in visits.columns and not visits['note'].isna().all():
        print("\nNotes found in visits:")
        note_counts = visits['note'].value_counts()
        for note, count in note_counts.items():
            print(f"  {note}: {count:,} visits")
    
    # Look for rapid revisits (within 24 hours)
    rapid = time_diffs[time_diffs < 1.0]
    if len(rapid) > 0:
        print(f"\nFound {len(rapid)} rapid revisits (<24 hours):")
        print(f"  Minimum time: {rapid.min():.2f} hours")
        print(f"  Median time: {np.median(rapid):.2f} hours")

if __name__ == "__main__":
    main()
