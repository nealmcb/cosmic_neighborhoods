"""Population distribution and CDF calculations."""

import math
from pathlib import Path
from typing import Literal, Optional, Union

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window


def bin_population_by_latitude(
    geotiff_path: Union[str, Path],
    output_csv: Optional[Union[str, Path]] = None,
    lat_bin_deg: float = 0.1,
) -> pd.DataFrame:
    """Aggregate population data into latitude bins.
    
    This reads a GeoTIFF population grid (e.g., GHSL GHS-POP) and aggregates
    population counts into latitude bins, accounting for:
    1. Cell area changes with latitude (cos(lat) factor)
    2. Missing/NODATA values
    3. Proper bin edge alignment
    
    Args:
        geotiff_path: Path to population GeoTIFF file
        output_csv: Optional path to cache results as CSV
        lat_bin_deg: Latitude bin size in degrees (default 0.1°)
    
    Returns:
        DataFrame with columns:
        - lat_bin_center: Latitude bin center in degrees
        - population: Total population in bin
    """
    with rasterio.open(geotiff_path) as src:
        # Get basic metadata
        height = src.height
        width = src.width
        transform = src.transform
        nodata = src.nodata
        
        # Create latitude bins
        lat_bins = np.arange(-90, 90 + lat_bin_deg, lat_bin_deg)
        lat_centers = (lat_bins[:-1] + lat_bins[1:]) / 2
        bin_populations = np.zeros_like(lat_centers)
        
        # Process in rows to avoid loading entire file
        row_batch = 1000  # Process this many rows at a time
        
        for row_start in range(0, height, row_batch):
            # Read a batch of rows
            row_end = min(row_start + row_batch, height)
            window = Window(0, row_start, width, row_end - row_start)
            data = src.read(1, window=window)
            
            # Get latitudes for this batch
            row_indices = np.arange(row_start, row_end)
            row_coords = transform * (0, row_indices)
            lats = row_coords[1]  # Y coordinates are latitudes
            
            # Handle NODATA values
            if nodata is not None:
                data = np.where(data == nodata, 0, data)
            
            # Account for cell area changes with latitude
            # Each cell's area is proportional to cos(latitude)
            area_factors = np.cos(np.radians(lats))
            data = data * area_factors[:, np.newaxis]
            
            # Bin the data
            for i, (lat_min, lat_max) in enumerate(zip(lat_bins[:-1], lat_bins[1:])):
                mask = (lats >= lat_min) & (lats < lat_max)
                if mask.any():
                    bin_populations[i] += data[mask].sum()
    
    # Create DataFrame
    df = pd.DataFrame({
        "lat_bin_center": lat_centers,
        "population": bin_populations,
    })
    
    # Cache results if requested
    if output_csv is not None:
        df.to_csv(output_csv, index=False)
    
    return df


def build_population_cdf(
    pop_source: Union[str, Path],
    lat_bin_deg: float = 0.1,
    source_type: Literal["ghsl", "toy"] = "ghsl",
) -> pd.DataFrame:
    """Load population data, aggregate by latitude, compute cumulative fraction south of φ.
    
    This function supports multiple population data sources:
    - GHSL (JRC) - GHS-POP R2023A dataset (preferred)
    - toy - Simple synthetic data for testing
    
    Args:
        pop_source: Path to population data file
        lat_bin_deg: Latitude bin size in degrees (default 0.1°)
        source_type: Type of population data source
    
    Returns:
        DataFrame with columns:
        - lat_bin_center: Latitude bin center in degrees
        - population: Total population in bin
        - cum_frac: Cumulative fraction of population south of bin
    
    Raises:
        FileNotFoundError: If population data file not found
        ValueError: If source_type is unknown or data format is invalid
    """
    # Validate source type first
    if source_type not in ["ghsl", "toy"]:
        raise ValueError(f"Unknown population data source type: {source_type}")
    
    pop_path = Path(pop_source)
    if not pop_path.exists():
        raise FileNotFoundError(f"Population data not found at: {pop_path}")
    
    if source_type == "ghsl":
        # Check if we have a cached CSV
        cache_path = pop_path.parent / "binned_population.csv"
        if cache_path.exists():
            df = pd.read_csv(cache_path)
        else:
            # Process GeoTIFF and cache result
            df = bin_population_by_latitude(pop_path, output_csv=cache_path)
    else:  # toy data
        df = pd.read_csv(pop_path)
        if not all(col in df.columns for col in ["lat_bin_center", "population"]):
            raise ValueError("Toy data must have lat_bin_center and population columns")
    
    # Sort by latitude (south to north)
    df = df.sort_values("lat_bin_center")
    
    # Compute cumulative fraction (0 = southernmost, 1 = northernmost)
    total_pop = df["population"].sum()
    df["cum_frac"] = df["population"].cumsum() / total_pop
    
    return df


def population_percentile(lat_deg: float, cdf_df: pd.DataFrame) -> float:
    """Return cumulative population fraction south of given latitude.
    
    This maps a latitude to p ∈ [0,1] representing the fraction of Earth's
    population living south of that latitude. The mapping is based on the
    provided CDF dataframe from build_population_cdf().
    
    Args:
        lat_deg: Latitude in degrees
        cdf_df: Population CDF dataframe from build_population_cdf()
    
    Returns:
        float: Fraction p ∈ [0,1] of population south of lat_deg
    
    Raises:
        ValueError: If latitude is out of range or CDF data is invalid
    """
    if not -90 <= lat_deg <= 90:
        raise ValueError(f"Latitude must be in [-90, 90], got {lat_deg}")
    
    if not all(col in cdf_df.columns for col in ["lat_bin_center", "cum_frac"]):
        raise ValueError("CDF dataframe must have lat_bin_center and cum_frac columns")
    
    # Handle edge cases
    if lat_deg <= cdf_df["lat_bin_center"].min():
        return 0.0
    if lat_deg >= cdf_df["lat_bin_center"].max():
        return 1.0
    
    # Interpolate between bins
    return np.interp(
        lat_deg,
        cdf_df["lat_bin_center"],
        cdf_df["cum_frac"],
    )