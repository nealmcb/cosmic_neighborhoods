"""Analyze which pixels were visited on the day after visits to a target pixel."""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import healpy as hp
from typing import Dict, List, Tuple

from cosmic_neighborhoods.footprint import (
    load_observation_cache,
    get_pixel_coords,
    get_pixel_constellation,
)

# Set up paths
CACHE_PATH = Path("cosmic_neighborhoods/data/footprint/pixel_observations_full.parquet")

# Target pixels: original Cetus pixel + 10 random ones
TARGET_PIXELS = [70397]  # Start with Cetus pixel

# Chile day boundary: Chile Standard Time (CLT) is UTC-3
# So noon Chile time = UTC+3 = MJD + 0.125 days
CHILE_DAY_OFFSET = 0.125

def get_chile_day_boundary(mjd: float) -> int:
    """Get the Chile day number for an MJD.
    
    Chile Standard Time (CLT) is UTC-3
    So noon Chile time = UTC+3 = MJD + 0.125 days
    
    Args:
        mjd: Modified Julian Date
    
    Returns:
        Chile day number (integer)
    """
    return int(mjd + CHILE_DAY_OFFSET)

def build_date_to_pixels_map(df: pd.DataFrame) -> Dict[int, set]:
    """Build a map from Chile date to set of pixels visited on that date.
    
    This is the key optimization: single pass through the cache.
    
    Args:
        df: DataFrame with observation cache
    
    Returns:
        Dictionary mapping Chile date (integer) to set of pixel IDs
    """
    print("Building date-to-pixels map (single pass optimization)...")
    
    date_to_pixels = {}
    
    for pixel_id in df.index:
        mjds_str = df.loc[pixel_id, "mjds"]
        mjds = np.array([float(x) for x in mjds_str.split(",")], dtype=np.float64)
        
        # Group visits by Chile date
        for mjd in mjds:
            chile_date = get_chile_day_boundary(mjd)
            if chile_date not in date_to_pixels:
                date_to_pixels[chile_date] = set()
            date_to_pixels[chile_date].add(pixel_id)
    
    print(f"  Built map for {len(date_to_pixels)} unique Chile dates")
    return date_to_pixels

def find_following_day_visits(df: pd.DataFrame, target_pixel: int, 
                            date_to_pixels: Dict[int, set]) -> Dict[int, int]:
    """Find all pixels visited on the day after visits to target pixel.
    
    Args:
        df: DataFrame with observation cache
        target_pixel: Pixel ID to analyze
        date_to_pixels: Pre-built map from date to pixels
    
    Returns:
        Dictionary mapping pixel_id to count of following-day visits
    """
    # Get constellation for display
    ra, dec = get_pixel_coords(target_pixel)
    const = get_pixel_constellation(ra, dec)
    print(f"Analyzing following-day visits for pixel {target_pixel} ({const})")
    
    # Get target pixel visits
    target_mjds_str = df.loc[target_pixel, "mjds"]
    target_mjds = np.array([float(x) for x in target_mjds_str.split(",")], dtype=np.float64)
    target_visit_count = df.loc[target_pixel, "visit_count"]
    
    print(f"  Target pixel has {target_visit_count} visits")
    
    # Group target visits by Chile date
    target_dates = set()
    for mjd in target_mjds:
        chile_date = get_chile_day_boundary(mjd)
        target_dates.add(chile_date)
    
    print(f"  Target visits span {len(target_dates)} unique Chile dates")
    
    # Find following day visits using the pre-built map
    following_day_stats = {}
    total_following_days = 0
    
    for target_date in target_dates:
        following_date = target_date + 1
        
        # Look up pixels visited on following day (O(1) lookup!)
        if following_date in date_to_pixels:
            following_day_pixels = date_to_pixels[following_date]
            total_following_days += 1
            
            # Count visits to each pixel on following day
            for pixel_id in following_day_pixels:
                if pixel_id not in following_day_stats:
                    following_day_stats[pixel_id] = 0
                following_day_stats[pixel_id] += 1
    
    print(f"  Found {total_following_days} following days with visits")
    print(f"  Unique pixels visited on following days: {len(following_day_stats)}")
    
    return following_day_stats, total_following_days

def create_heatmap(following_day_stats: Dict[int, int], total_following_days: int, 
                   target_pixel: int, save_path: str = None):
    """Create a heatmap visualization of the following-day visit data.
    
    Args:
        following_day_stats: Dictionary mapping pixel_id to count of following-day visits
        total_following_days: Total number of following days analyzed
        target_pixel: Target pixel ID for reference
        save_path: Optional path to save the plot
    """
    nside = 128  # Order 7
    npix = hp.nside2npix(nside)
    
    # Create visit count map
    visit_map = np.zeros(npix)
    
    for pixel_id, visit_count in following_day_stats.items():
        if pixel_id < npix:  # Safety check
            visit_map[pixel_id] = visit_count
    
    # Reshape to 2D for plotting
    visit_map_2d = hp.reorder(visit_map, n2r=True)
    
    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Use mollweide projection for equal-area display
    # Get actual max visits (excluding zeros)
    max_visits = np.max(visit_map)
    title = f"Following Day Visits: Pixel {target_pixel}\nTotal following days: {total_following_days}"
    if max_visits > 0:
        title += f", Max visits: {max_visits:.0f}"
    
    hp.mollview(visit_map_2d, 
                title=title,
                unit="Number of following days visited",
                cmap="viridis")
    
    # Add marker for target pixel
    target_ra, target_dec = get_pixel_coords(target_pixel)
    target_theta = np.radians(90 - target_dec)  # Convert to healpy coordinates
    target_phi = np.radians(target_ra)
    
    # Convert to mollweide projection coordinates
    target_x = target_phi
    target_y = np.arcsin(2 * target_theta / np.pi - 1)
    
    # Plot marker (red cross)
    plt.plot(target_x, target_y, 'rx', markersize=15, markeredgewidth=3, 
             label=f'Target Pixel {target_pixel}')
    
    # Add grid and legend
    hp.graticule()
    plt.legend(loc='upper right')
    
    plt.tight_layout()
    
    # Save the plot without displaying
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  Heatmap saved: {save_path}")
    
    # Close the figure to free memory
    plt.close(fig)

def main():
    """Main analysis function."""
    import random
    
    print("Loading observation cache...")
    df = load_observation_cache(CACHE_PATH)
    print(f"Loaded cache with {len(df)} pixels")
    
    # Add 10 random pixels to the target list
    available_pixels = [p for p in df.index if p != 70397]  # Exclude Cetus pixel
    random_pixels = random.sample(available_pixels, 10)
    TARGET_PIXELS.extend(random_pixels)
    
    print(f"Analyzing {len(TARGET_PIXELS)} target pixels:")
    for i, pixel_id in enumerate(TARGET_PIXELS):
        ra, dec = get_pixel_coords(pixel_id)
        const = get_pixel_constellation(ra, dec)
        if i == 0:
            print(f"  {i+1:2d}. Pixel {pixel_id}: RA: {ra:.2f}°, Dec: {dec:.2f}° ({const}) - Cetus")
        else:
            print(f"  {i+1:2d}. Pixel {pixel_id}: RA: {ra:.2f}°, Dec: {dec:.2f}° ({const})")
    
    # Build date-to-pixels map (single pass optimization)
    date_to_pixels = build_date_to_pixels_map(df)
    
    # Analyze each target pixel
    for i, target_pixel in enumerate(TARGET_PIXELS):
        print(f"\n{'='*60}")
        print(f"ANALYZING PIXEL {i+1}/{len(TARGET_PIXELS)}: {target_pixel}")
        print(f"{'='*60}")
        
        # Find following day visits using the optimized map
        following_day_stats, total_following_days = find_following_day_visits(
            df, target_pixel, date_to_pixels)
        
        # Print summary statistics
        print(f"\nFollowing Day Visit Summary:")
        print(f"  Target pixel visits: {df.loc[target_pixel, 'visit_count']}")
        print(f"  Following days with visits: {total_following_days}")
        print(f"  Unique pixels visited on following days: {len(following_day_stats)}")
        
        if following_day_stats:
            max_visits = max(following_day_stats.values())
            mean_visits = np.mean(list(following_day_stats.values()))
            print(f"  Maximum following-day visits to any pixel: {max_visits}")
            print(f"  Mean following-day visits per pixel: {mean_visits:.1f}")
        
        # Create and save heatmap
        print(f"\nCreating heatmap...")
        filename = f"pixel_{target_pixel}_following_day_heatmap.png"
        create_heatmap(following_day_stats, total_following_days, target_pixel, filename)
        
        print(f"Completed pixel {target_pixel} ({i+1}/{len(TARGET_PIXELS)})")
    
    print(f"\n{'='*60}")
    print(f"ANALYSIS COMPLETE: {len(TARGET_PIXELS)} pixels analyzed")
    print(f"{'='*60}")
    
    # List all generated heatmap files
    print(f"\nGenerated heatmap files:")
    for pixel_id in TARGET_PIXELS:
        filename = f"pixel_{pixel_id}_following_day_heatmap.png"
        print(f"  - {filename}")
    
    print(f"\nAll heatmaps saved successfully!")

if __name__ == "__main__":
    main()
