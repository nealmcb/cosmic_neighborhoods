"""Visualize all pixels visited on the first day of the Rubin survey."""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import healpy as hp

from cosmic_neighborhoods.footprint import (
    load_observation_cache,
    get_pixel_coords,
)

# Set up paths
CACHE_PATH = Path("cosmic_neighborhoods/data/footprint/pixel_observations_full.parquet")

def find_first_day_pixels(df: pd.DataFrame) -> set:
    """Find all pixels visited on the first day of the survey.
    
    Args:
        df: DataFrame with observation cache
    
    Returns:
        Set of pixel IDs visited on the first day
    """
    print("Finding pixels visited on the first day...")
    
    # Find the earliest MJD across all pixels
    all_mjds = []
    for pixel_id in df.index:
        mjds_str = df.loc[pixel_id, "mjds"]
        mjds = np.array([float(x) for x in mjds_str.split(",")], dtype=np.float64)
        all_mjds.extend(mjds)
    
    first_mjd = min(all_mjds)
    first_day = int(first_mjd)  # Simple integer day boundary
    
    print(f"  First MJD: {first_mjd:.6f}")
    print(f"  First day: {first_day}")
    
    # Find all pixels visited on the first day
    first_day_pixels = set()
    
    for pixel_id in df.index:
        mjds_str = df.loc[pixel_id, "mjds"]
        mjds = np.array([float(x) for x in mjds_str.split(",")], dtype=np.float64)
        
        # Check if any visits fall on the first day
        if np.any(np.floor(mjds) == first_day):
            first_day_pixels.add(pixel_id)
    
    print(f"  Pixels visited on first day: {len(first_day_pixels)}")
    return first_day_pixels

def create_first_day_heatmap(first_day_pixels: set, save_path: str = None):
    """Create a heatmap visualization of the first day visits.
    
    Args:
        first_day_pixels: Set of pixel IDs visited on the first day
        save_path: Optional path to save the plot
    """
    nside = 128  # Order 7
    npix = hp.nside2npix(nside)
    
    # Create visit map (1 for visited, 0 for not visited)
    visit_map = np.zeros(npix)
    
    for pixel_id in first_day_pixels:
        if pixel_id < npix:  # Safety check
            visit_map[pixel_id] = 1
    
    # Reshape to 2D for plotting
    visit_map_2d = hp.reorder(visit_map, n2r=True)
    
    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Use mollweide projection for equal-area display
    hp.mollview(visit_map_2d, 
                title=f"First Day Survey Coverage\n"
                      f"Pixels visited: {len(first_day_pixels):,}",
                unit="Visited (1) / Not Visited (0)",
                cmap="viridis")
    
    # Add grid
    hp.graticule()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    plt.show()

def main():
    """Main analysis function."""
    print("Loading observation cache...")
    df = load_observation_cache(CACHE_PATH)
    print(f"Loaded cache with {len(df)} pixels")
    
    # Find first day pixels
    first_day_pixels = find_first_day_pixels(df)
    
    # Create heatmap
    print("\nCreating first day heatmap...")
    create_first_day_heatmap(first_day_pixels, "first_day_coverage.png")

if __name__ == "__main__":
    main()
