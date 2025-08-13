"""Tests for solar ephemeris calculations."""

import pytest

from cosmic_neighborhoods.ephemeris import convert_to_gregorian, sun_ra_deg


def test_sun_ra_solstices_equinoxes() -> None:
    """Test sun RA calculation on solstices and equinoxes."""
    # 2024 equinoxes and solstices (approximate dates)
    cases = [
        ("2024-03-20", 0.0, 5.0),  # Spring equinox: RA ≈ 0°
        ("2024-06-20", 90.0, 5.0),  # Summer solstice: RA ≈ 90°
        ("2024-09-22", 180.0, 5.0),  # Fall equinox: RA ≈ 180°
        ("2024-12-21", 270.0, 5.0),  # Winter solstice: RA ≈ 270°
    ]

    for date, expected_ra, tolerance in cases:
        ra = sun_ra_deg(date)
        # Allow for some difference due to precise timing
        assert abs((ra - expected_ra + 180) % 360 - 180) < tolerance


def test_sun_ra_invalid_date() -> None:
    """Test sun RA calculation with invalid date format."""
    with pytest.raises(ValueError):
        sun_ra_deg("2024/03/20")  # Wrong separator

    with pytest.raises(ValueError):
        sun_ra_deg("2024-3-20")  # Missing leading zero

    with pytest.raises(ValueError):
        sun_ra_deg("not-a-date")


def test_calendar_conversion_gregorian() -> None:
    """Test Gregorian calendar handling."""
    # Gregorian should pass through unchanged
    assert convert_to_gregorian("2024-03-20", "gregorian") == "2024-03-20"

    # Invalid formats should raise
    with pytest.raises(ValueError):
        convert_to_gregorian("2024/03/20", "gregorian")

    with pytest.raises(ValueError):
        convert_to_gregorian("not-a-date", "gregorian")


def test_calendar_conversion_julian() -> None:
    """Test Julian to Gregorian conversion."""
    # Known Julian to Gregorian conversions
    cases = [
        ("2024-03-20", "2024-04-02"),  # Modern date (13 day difference)
        ("1582-10-04", "1582-10-14"),  # Just before Gregorian reform (10 day difference)
        ("1000-01-01", "1000-01-06"),  # Medieval date (7 day difference)
    ]

    for julian_date, expected_gregorian in cases:
        assert convert_to_gregorian(julian_date, "julian") == expected_gregorian


def test_calendar_conversion_errors() -> None:
    """Test error handling in calendar conversion."""
    # Unknown calendar
    with pytest.raises(ValueError) as exc_info:
        convert_to_gregorian("2024-03-20", "unknown_calendar")
    assert "Unknown calendar" in str(exc_info.value)

    # Invalid date format for supported calendar
    with pytest.raises(ValueError):
        convert_to_gregorian("not-a-date", "julian")

    # Invalid date values
    with pytest.raises(ValueError):
        convert_to_gregorian("2024-13-01", "julian")  # Invalid month
