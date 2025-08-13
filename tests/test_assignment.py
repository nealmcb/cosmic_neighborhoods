"""Test the core assignment functionality."""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from astropy_healpix import HEALPix
from astropy.coordinates import SkyCoord
import astropy.units as u

from cosmic_neighborhoods.boundary import RubinBoundary
from cosmic_neighborhoods.population import build_population_cdf
from cosmic_neighborhoods.mapping import map_latitude_to_declination, assign_healpix_tile
from cosmic_neighborhoods.ephemeris import sun_ra_deg


@pytest.fixture(autouse=True)
def suppress_erfa_warnings():
    """Suppress specific ERFA warnings about historical dates.
    
    ERFA (Essential Routines for Fundamental Astronomy) warns about:
    - "dubious year" before 1800 (Note 6)
    - "dubious year" before 1961 for TAI (Note 3)
    - "dubious year" before 1972 for UTC (Note 4)
    
    These warnings are expected and safe to ignore when testing
    historical dates like Vera Rubin's birth (1928).
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*dubious year.*", module="erfa")
        yield


@pytest.fixture
def test_data_dir() -> Path:
    """Get path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def rubin_boundary(test_data_dir: Path) -> RubinBoundary:
    """Load test Rubin boundary data."""
    # Create test boundary with 4 points
    # We want:
    # - RA=0°: dec_north=30°
    # - RA=90°: dec_north=40° (highest)
    # - RA=180°: dec_north=30°
    # - RA=270°: dec_north=20° (lowest)
    
    # Create arrays with 0.1° spacing
    ra = np.arange(0, 360, 0.1)  # Required 0.1° steps
    dec_south = np.full_like(ra, -90.0)  # Full southern coverage
    
    # Create northern boundary by interpolating between key points
    key_ras = np.array([0, 90, 180, 270, 360])  # Include 360° for wrap
    key_decs = np.array([30, 40, 30, 20, 30])   # Wrap back to start
    dec_north = np.interp(ra, key_ras, key_decs)
    
    boundary = RubinBoundary({
        "ra": ra,
        "dec_south": dec_south,
        "dec_north": dec_north,
    })
    return boundary


@pytest.fixture
def population_cdf(test_data_dir: Path) -> pd.DataFrame:
    """Create test population CDF."""
    # Simple linear CDF from -90° to +90° latitude
    lats = np.arange(-90, 91, 0.1)
    cdfs = (lats + 90) / 180  # Linear mapping from -90° -> 0% to +90° -> 100%
    return pd.DataFrame({
        "lat_bin_center": lats,
        "cum_frac": cdfs,
    })


def test_sun_ra_solstices():
    """Test solar RA calculation at solstices."""
    # Summer solstice (approximate RA)
    ra = sun_ra_deg("2024-06-21")
    assert abs(ra - 90) < 1, "Summer solstice RA should be near 90°"

    # Winter solstice (approximate RA)
    ra = sun_ra_deg("2024-12-21")
    assert abs(ra - 270) < 1, "Winter solstice RA should be near 270°"


def test_map_latitude_to_declination(rubin_boundary, population_cdf):
    """Test latitude to declination mapping at key points."""
    # Test cases: (lat, ra, expected_dec)
    test_cases = [
        # At RA=90° where boundary is highest (40°)
        (90, 90, 40),    # Northernmost latitude -> highest available dec
        (0, 90, -25),    # Equator -> midway between -90° and +40°
        (-90, 90, -90),  # Southernmost latitude -> lowest available dec

        # At RA=270° where boundary is lowest (20°)
        (90, 270, 20),   # Northernmost latitude -> highest available dec
        (0, 270, -35),   # Equator -> midway between -90° and +20°
        (-90, 270, -90), # Southernmost latitude -> lowest available dec
    ]

    for lat, ra, expected_dec in test_cases:
        dec = map_latitude_to_declination(lat, ra, population_cdf, rubin_boundary)
        assert abs(dec - expected_dec) < 1, f"Wrong declination for lat={lat}, ra={ra}"


def test_assign_healpix():
    """Test HEALPix assignment at various resolutions."""
    # Test point: RA=180°, Dec=45° (easy to verify)
    ra, dec = 180, 45

    # Test different resolutions
    test_cases = [
        (0, 12),       # nside=1: 12 pixels total
        (2, 192),      # nside=4: 192 pixels total
        (4, 3072),     # nside=16: 3072 pixels total
    ]

    for resolution, total_pixels in test_cases:
        nside = 2**resolution
        pixel = assign_healpix_tile(ra, dec, nside)
        
        # Verify pixel index is valid
        assert 0 <= pixel < total_pixels, f"Invalid pixel {pixel} for nside={nside}"

        # Verify pixel center is near input coordinates
        hp = HEALPix(nside=nside, order="nested", frame="icrs")
        center = hp.healpix_to_skycoord(pixel)
        
        # Allow some deviation due to pixel size
        assert abs(center.ra.deg - ra) < 360/nside, "Pixel center RA too far from input"
        assert abs(center.dec.deg - dec) < 180/nside, "Pixel center Dec too far from input"


def test_vera_rubin_assignment(rubin_boundary, population_cdf):
    """Test assignment for Vera Rubin's birth."""
    lat = 39.95  # Philadelphia
    date = "1928-07-23"
    nside = 128  # Standard resolution
    
    # Get Sun's RA and add 180° for nighttime visibility
    sun_ra = sun_ra_deg(date)
    expected_sun_ra = 123.595  # Verified with both VSOP87/ERFA and JPL DE430
    assert abs(sun_ra - expected_sun_ra) < 0.001, f"Sun RA {sun_ra:.3f}° differs from expected {expected_sun_ra}°"
    
    assigned_ra = (sun_ra + 180.0) % 360.0
    expected_assigned_ra = 303.595  # Opposite the sun
    assert abs(assigned_ra - expected_assigned_ra) < 0.001, f"Assigned RA {assigned_ra:.3f}° differs from expected {expected_assigned_ra}°"
    
    # Get declination range at assigned RA
    dec_south, dec_north = rubin_boundary.get_dec_range(assigned_ra)
    print(f"\nTest data:")
    print(f"  Birth: lat={lat}°N, date={date}")
    print(f"  Sun RA: {sun_ra:.3f}° (expected {expected_sun_ra}°)")
    print(f"  Assigned RA: {assigned_ra:.3f}° (expected {expected_assigned_ra}°)")
    print(f"  Available dec range: {dec_south:.3f}° to {dec_north:.3f}°")
    
    # Map to declination
    # Note: Expected declination depends on test footprint configuration:
    # - At RA=303.1°, our test footprint has dec_north=23.7°
    # - This is near the lowest part of our test boundary (RA=270° has dec_north=20°)
    # - A different footprint (e.g. real Rubin data) would yield different declinations
    dec = map_latitude_to_declination(lat, assigned_ra, population_cdf, rubin_boundary)
    expected_dec = -7.891  # For our test footprint with linear population mapping
    assert abs(dec - expected_dec) < 0.1, f"Declination {dec:.3f}° differs from expected {expected_dec}°"
    print(f"  Assigned dec: {dec:.3f}° (expected {expected_dec}°)")
    
    # Verify declination is within valid range
    assert dec_south < dec < dec_north, f"Declination {dec}° outside valid range [{dec_south}°, {dec_north}°]"
    
    # Assign HEALPix and verify pixel center
    # Note: We use the nested ordering scheme (not ring) because it's better for:
    # - Hierarchical operations (quad-tree structure)
    # - Spatial queries (adjacent pixels stay adjacent at different resolutions)
    # - Parent-child relationships (simple bit operations)
    # The same location has different pixel numbers in different schemes:
    # - Nested: pixel 119822 (used here)
    # - Ring: pixel 147242 (same location, different numbering)
    pixel = assign_healpix_tile(assigned_ra, dec, nside)
    expected_pixel = 119822  # Verified with external HEALPix tools (nested scheme)
    assert pixel == expected_pixel, f"HEALPix pixel {pixel} differs from expected {expected_pixel}"
    print(f"  HEALPix pixel: {pixel} (expected {expected_pixel}, nested scheme)")
    
    # Verify pixel center coordinates
    hp = HEALPix(nside=nside, order="nested", frame="icrs")
    center = hp.healpix_to_skycoord(pixel)
    
    # Get actual and expected centers
    actual_ra = center.ra.deg
    actual_dec = center.dec.deg
    
    # These values are exact from astropy-healpix
    expected_center_ra = 303.3984375  # 303 + 51/128 degrees
    expected_center_dec = -7.78271438539095  # From astropy-healpix
    
    # Check coordinates with extreme precision
    # Note: HEALPix centers are exact geometric points, so we expect
    # perfect agreement with astropy-healpix's values
    tolerance = 1e-15  # Only for floating point roundoff
    assert abs(actual_ra - expected_center_ra) < tolerance, f"Pixel center RA {actual_ra:.12f}° differs from expected {expected_center_ra:.12f}°"
    assert abs(actual_dec - expected_center_dec) < tolerance, f"Pixel center Dec {actual_dec:.12f}° differs from expected {expected_center_dec:.12f}°"
    print(f"  Pixel center: RA {actual_ra:.12f}° (geometric {expected_center_ra:.12f}°)")
    print(f"               Dec {actual_dec:.12f}° (geometric {expected_center_dec:.12f}°)")
