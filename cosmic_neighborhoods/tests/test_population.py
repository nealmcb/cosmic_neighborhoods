"""Tests for population distribution calculations."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cosmic_neighborhoods.population import build_population_cdf, population_percentile


def test_build_population_cdf_toy() -> None:
    """Test CDF construction from toy data."""
    toy_path = Path(__file__).parent.parent / "data" / "population" / "toy_popcdf.csv"

    df = build_population_cdf(toy_path, source_type="toy")

    # Check dataframe structure
    assert all(col in df.columns for col in ["lat_bin_center", "population", "cum_frac"])
    assert len(df) > 0

    # Check sorting and value ranges
    assert df["lat_bin_center"].is_monotonic_increasing
    assert (df["population"] >= 0).all()
    assert (0 <= df["cum_frac"]).all() and (df["cum_frac"] <= 1).all()
    assert df["cum_frac"].is_monotonic_increasing

    # Check normalization
    assert np.isclose(df["cum_frac"].iloc[-1], 1.0)


def test_build_population_cdf_missing_file() -> None:
    """Test error handling for missing data file."""
    with pytest.raises(FileNotFoundError):
        build_population_cdf("nonexistent.csv", source_type="toy")


def test_build_population_cdf_invalid_source() -> None:
    """Test error handling for invalid source type."""
    with pytest.raises(ValueError):
        build_population_cdf("dummy.csv", source_type="invalid")  # type: ignore


def test_population_percentile() -> None:
    """Test latitude to percentile mapping."""
    # Create simple test data
    test_data = pd.DataFrame(
        {
            "lat_bin_center": [-50, -25, 0, 25, 50],
            "population": [1000, 2000, 4000, 2000, 1000],
        }
    )

    # Compute CDF
    total_pop = test_data["population"].sum()
    test_data["cum_frac"] = test_data["population"].cumsum() / total_pop

    # Test interpolation
    assert population_percentile(-90, test_data) == 0.0  # Below minimum
    assert population_percentile(90, test_data) == 1.0  # Above maximum
    assert np.isclose(population_percentile(0, test_data), 0.7)  # Middle value

    # Test monotonicity
    lats = np.linspace(-90, 90, 100)
    percentiles = [population_percentile(lat, test_data) for lat in lats]
    assert np.all(np.diff(percentiles) >= 0)


def test_population_percentile_errors() -> None:
    """Test error handling in percentile calculation."""
    test_data = pd.DataFrame(
        {
            "lat_bin_center": [-50, 0, 50],
            "cum_frac": [0.2, 0.5, 1.0],
        }
    )

    # Invalid latitude
    with pytest.raises(ValueError):
        population_percentile(-100, test_data)

    with pytest.raises(ValueError):
        population_percentile(100, test_data)

    # Invalid dataframe
    bad_data = pd.DataFrame({"wrong_column": [1, 2, 3]})
    with pytest.raises(ValueError):
        population_percentile(0, bad_data)
