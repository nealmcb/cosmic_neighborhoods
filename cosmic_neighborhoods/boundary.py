"""Functions for handling Rubin footprint boundary data.

The footprint boundary is stored in .npz format with three arrays:
- ra: Right Ascension values (0° to 359.9° in 0.1° steps), shape (3600,)
- dec_south: Southern declination limit at each RA, shape (3600,)
- dec_north: Northern declination limit at each RA, shape (3600,)

Example:
    ra[42] = 4.2  # RA = 4.2°
    dec_south[42] = -90.0  # Southern limit at RA 4.2°
    dec_north[42] = 13.5   # Northern limit at RA 4.2°

The boundary data represents the maximum extent of the Rubin footprint
in declination at each RA value. This is used to map population percentiles
to available declination ranges in a way that respects the footprint shape.
"""

from pathlib import Path
from typing import Dict, Tuple, Union

import numpy as np
import pandas as pd


class RubinBoundary:
    """Class for handling Rubin footprint boundary data."""

    def __init__(self, data: Dict[str, np.ndarray]):
        """Initialize with boundary data.

        Args:
            data: Dictionary with arrays:
                - ra: Right Ascension values (0° to 359.9°)
                - dec_south: Southern declination limits
                - dec_north: Northern declination limits
        """
        self._validate_data(data)
        self.ra = data["ra"]
        self.dec_south = data["dec_south"]
        self.dec_north = data["dec_north"]

    @classmethod
    def from_cache(cls, cache_file: Union[str, Path]) -> "RubinBoundary":
        """Load boundary data from .npz cache file.

        Args:
            cache_file: Path to .npz cache file

        Returns:
            RubinBoundary object
        """
        with np.load(cache_file) as data:
            return cls(
                {
                    "ra": data["ra"],
                    "dec_south": data["dec_south"],
                    "dec_north": data["dec_north"],
                }
            )

    @classmethod
    def from_opsim(cls, db_path: Union[str, Path]) -> "RubinBoundary":
        """Create boundary data from OpSim database.

        Args:
            db_path: Path to OpSim SQLite database

        Returns:
            RubinBoundary object
        """
        # Read all unique pointings
        db_uri = f"sqlite:///{db_path}"
        query = """
        SELECT DISTINCT fieldRA, fieldDec 
        FROM observations
        """
        pointings = pd.read_sql_query(query, db_uri)

        # Create RA grid (0 to 359.9, step 0.1)
        ra_grid = np.arange(0, 360, 0.1)

        # Initialize boundary arrays
        dec_south = np.full_like(ra_grid, -90.0)  # For now, always -90
        dec_north = np.full_like(ra_grid, -90.0)  # Will update with real values

        # Round RAs to nearest 0.1°
        pointings["ra_bin"] = (pointings["fieldRA"] / 0.1).round() * 0.1

        # Find maximum declination for each RA bin
        max_decs = pointings.groupby("ra_bin")["fieldDec"].max()

        # Update northern boundary (adding field radius of 1.75°)
        for ra, dec in max_decs.items():
            idx = int(ra * 10)  # Convert RA to array index
            if idx < len(dec_north):
                dec_north[idx] = dec + 1.75  # Add field radius

        # Interpolate any gaps
        mask = dec_north > -90
        if np.any(mask):
            x = np.where(mask)[0]
            y = dec_north[mask]
            dec_north = np.interp(np.arange(len(dec_north)), x, y)

        return cls(
            {
                "ra": ra_grid,
                "dec_south": dec_south,
                "dec_north": dec_north,
            }
        )

    def save(self, cache_file: Union[str, Path]) -> None:
        """Save boundary data to .npz cache file.

        Args:
            cache_file: Path to save cache (will be .npz)
        """
        np.savez_compressed(
            cache_file,
            ra=self.ra,
            dec_south=self.dec_south,
            dec_north=self.dec_north,
        )

    def get_dec_range(self, ra_deg: float) -> Tuple[float, float]:
        """Get declination range at a specific RA.

        Args:
            ra_deg: Right ascension in degrees [0, 360)

        Returns:
            Tuple of (south_dec, north_dec) in degrees

        Raises:
            ValueError: If RA is outside valid range
        """
        if not 0 <= ra_deg < 360:
            raise ValueError(f"RA {ra_deg}° must be in [0, 360)")

        # Normalize RA to [0, 360)
        ra = ra_deg % 360

        # Find nearest RA bin
        idx = int(round(ra * 10))  # Convert RA to array index
        if idx >= len(self.ra):
            idx = 0  # Wrap around at 360°

        return (self.dec_south[idx], self.dec_north[idx])

    def _validate_data(self, data: Dict[str, np.ndarray]) -> None:
        """Validate boundary data format and contents.

        Args:
            data: Dictionary with ra, dec_south, dec_north arrays

        Raises:
            ValueError: If data format is invalid
        """
        required = {"ra", "dec_south", "dec_north"}
        if not all(k in data for k in required):
            raise ValueError(f"Missing required arrays: {required - set(data.keys())}")

        if not all(isinstance(v, np.ndarray) for v in data.values()):
            raise ValueError("All values must be NumPy arrays")

        if not all(len(v) == 3600 for v in data.values()):
            raise ValueError("All arrays must have length 3600 (0 to 359.9 in 0.1° steps)")

        if not np.allclose(data["ra"], np.arange(0, 360, 0.1)):
            raise ValueError("RA array must be 0 to 359.9 in 0.1° steps")

        if not np.all(data["dec_south"] <= data["dec_north"]):
            raise ValueError("Southern boundary must not exceed northern boundary")
