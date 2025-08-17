"1000""Tests for footprint boundary and visit pattern analysis."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cosmic_neighborhoods.footprint import (
    build_observation_cache,
    load_observation_cache,
    NSIDE,
)


def test_observation_cache_distribution(tmp_path):
    """Test observation cache creation and visit distribution analysis."""
    # Set up paths
    db_path = Path("cosmic_neighborhoods/data/footprint/baseline_v3.2_10yrs.db")
    cache_path = tmp_path / "test_pixel_observations.parquet"
    log_path = tmp_path / "build.log"

    if not db_path.exists():
        pytest.skip("OpSim database not available")

    # Redirect stdout to a file to see progress
    with log_path.open('w') as log:
        # Print initial message that will show in pytest output
        print("\nStarting cache build, watching progress in:", log_path, flush=True)
        
        # Build cache with stdout redirected to file
        import sys
        old_stdout = sys.stdout
        sys.stdout = log
        try:
            build_observation_cache(db_path, cache_path)
        finally:
            sys.stdout = old_stdout
            log.flush()

    # Show progress log in pytest output
    print("\nProgress log:")
    print(log_path.read_text())

    # Load cached data
    observations = load_observation_cache(cache_path)

    # Analyze visit distribution
    visit_counts = observations.groupby("healpix").size()
    
    # Basic statistics
    stats = {
        "n_pixels": len(visit_counts),
        "total_visits": len(observations),
        "min_visits": visit_counts.min(),
        "max_visits": visit_counts.max(),
        "mean_visits": visit_counts.mean(),
        "median_visits": visit_counts.median(),
    }

    # Print statistics for reference
    print("\nVisit distribution statistics:")
    print(f"Total pixels observed: {stats['n_pixels']:,}")
    print(f"Total visits: {stats['total_visits']:,}")
    print(f"Visits per pixel:")
    print(f"  Min: {stats['min_visits']:,}")
    print(f"  Max: {stats['max_visits']:,}")
    print(f"  Mean: {stats['mean_visits']:.1f}")
    print(f"  Median: {stats['median_visits']:.1f}")

    # Calculate visit count percentiles
    percentiles = [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100]
    visit_percentiles = np.percentile(visit_counts, percentiles)
    print("\nVisit count percentiles:")
    for p, v in zip(percentiles, visit_percentiles):
        print(f"  {p:3d}%: {v:7.1f}")

    # Basic sanity checks
    assert stats["n_pixels"] > 0, "No pixels found"
    assert stats["total_visits"] > 0, "No visits found"
    assert stats["min_visits"] > 0, "Found pixels with no visits"
    assert stats["max_visits"] > stats["min_visits"], "All pixels have same visit count"
    assert stats["mean_visits"] > 0, "Invalid mean visit count"
    assert stats["median_visits"] > 0, "Invalid median visit count"

    # Check reasonable ranges based on Rubin's observing strategy
    # Each field should be visited hundreds of times over 10 years
    assert 100 < stats["mean_visits"] < 10000, "Unexpected mean visit count"
    assert stats["max_visits"] < 20000, "Unreasonably high visit count"

    # Save visit distribution for reference
    visit_counts.to_csv("visit_distribution.csv")

    # Return stats for potential future use
    return stats
