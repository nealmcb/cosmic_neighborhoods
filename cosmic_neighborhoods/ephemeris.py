"""Solar ephemeris calculations for cosmic neighborhood assignment."""

import re
from datetime import datetime
from typing import Dict, Optional, Tuple

import convertdate
from astropy.coordinates import get_sun
from astropy.time import Time
import astropy.units as u


def sun_ra_deg(date_gregorian: str) -> float:
    """Return Sun RA (degrees, ICRS) for ISO date 'YYYY-MM-DD' using Astropy get_sun().
    
    This calculates the Sun's right ascension at midnight UTC on the given date.
    For cosmic neighborhood assignment, we'll add 180° to this value to get the
    RA that culminates at local midnight.
    
    Args:
        date_gregorian: ISO format date string 'YYYY-MM-DD'
    
    Returns:
        float: Sun's right ascension in degrees (0-360)
    
    Raises:
        ValueError: If the date string is not in ISO format
    """
    # Strict ISO date format validation
    if not re.match(r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$", date_gregorian):
        raise ValueError(f"Invalid date format. Expected 'YYYY-MM-DD', got '{date_gregorian}'")
    
    try:
        # Parse date and create midnight UTC timestamp
        date = datetime.strptime(date_gregorian, "%Y-%m-%d")
        time = Time(date)
        
        # Get Sun position and extract RA in degrees
        sun = get_sun(time)
        ra = sun.ra.to_value(u.deg)
        
        # Normalize to 0-360 range
        return ra % 360.0
        
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}") from e


def _validate_date_components(year: int, month: int, day: int) -> None:
    """Validate that date components are within reasonable ranges.
    
    Args:
        year: Year number (any)
        month: Month number (should be 1-12)
        day: Day number (should be 1-31 depending on month)
    
    Raises:
        ValueError: If any component is out of range
    """
    if not 1 <= month <= 12:
        raise ValueError(f"Month must be between 1 and 12, got {month}")
    
    # Maximum days per month (ignoring leap years for simplicity)
    max_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not 1 <= day <= max_days[month - 1]:
        raise ValueError(f"Day {day} is not valid for month {month}")


def _parse_date(date_str: str) -> Tuple[int, int, int]:
    """Parse a date string in YYYY-MM-DD format into components.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
    
    Returns:
        Tuple of (year, month, day) as integers
    
    Raises:
        ValueError: If the format is invalid
    """
    if not re.match(r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$", date_str):
        raise ValueError("Date must be in YYYY-MM-DD format")
    
    try:
        y, m, d = map(int, date_str.split("-"))
        _validate_date_components(y, m, d)
        return y, m, d
    except ValueError as e:
        raise ValueError(f"Invalid date components: {e}")


def _get_julian_offset(year: int) -> int:
    """Get the number of days to add when converting Julian to Gregorian.
    
    The offset grows over time due to the Julian calendar's leap year rule.
    This implements the standard rules for the Gregorian reform.
    
    Args:
        year: The Julian calendar year
    
    Returns:
        int: Number of days to add for conversion
    """
    if year < 1582:
        return 0  # Before reform
    if year == 1582:
        return 10  # Reform year
    if year < 1700:
        return 10
    if year < 1800:
        return 11
    if year < 1900:
        return 12
    if year < 2100:
        return 13
    return 14  # Beyond 2100


def convert_to_gregorian(date_str: str, calendar: str) -> str:
    """Map date from named calendar to ISO Gregorian 'YYYY-MM-DD'.
    
    For 'gregorian' calendar, returns input unchanged after validation.
    For other calendars, uses convertdate to map to Gregorian.
    
    Supported calendars:
    - gregorian
    - julian
    - hebrew
    - islamic
    - persian
    - indian_civil
    - chinese
    
    Args:
        date_str: Date string in the format specific to the calendar
        calendar: Name of the calendar system
    
    Returns:
        str: ISO format Gregorian date 'YYYY-MM-DD'
    
    Raises:
        ValueError: If calendar is unknown or date format is invalid
    """
    # Define supported calendars and their date format examples
    SUPPORTED_CALENDARS: Dict[str, str] = {
        "gregorian": "YYYY-MM-DD",
        "julian": "YYYY-MM-DD",
        "hebrew": "YYYY-MM-DD",
        "islamic": "YYYY-MM-DD",
        "persian": "YYYY-MM-DD",
        "indian_civil": "YYYY-MM-DD",
        "chinese": "YYYY-MM-DD",
    }
    
    if calendar not in SUPPORTED_CALENDARS:
        cal_list = ", ".join(f"'{c}'" for c in SUPPORTED_CALENDARS)
        raise ValueError(
            f"Unknown calendar '{calendar}'. Supported calendars: {cal_list}. "
            "Each expects format: YYYY-MM-DD"
        )
    
    if calendar == "gregorian":
        # Validate format and return unchanged
        y, m, d = _parse_date(date_str)
        return date_str
    
    try:
        # Parse and validate input date
        y, m, d = _parse_date(date_str)
        
        if calendar == "julian":
            # Handle pre/post Gregorian reform dates
            if y > 1582 or (y == 1582 and (m > 10 or (m == 10 and d > 4))):
                # After reform: add appropriate offset
                jd = convertdate.julian.to_jd(y, m, d)
                offset = _get_julian_offset(y)
                g_y, g_m, g_d = convertdate.julian.from_jd(jd + offset)
            else:
                # Before reform: direct conversion
                g_y, g_m, g_d = convertdate.julian.to_gregorian(y, m, d)
        elif calendar == "hebrew":
            g_y, g_m, g_d = convertdate.hebrew.to_gregorian(y, m, d)
        elif calendar == "islamic":
            g_y, g_m, g_d = convertdate.islamic.to_gregorian(y, m, d)
        elif calendar == "persian":
            g_y, g_m, g_d = convertdate.persian.to_gregorian(y, m, d)
        elif calendar == "indian_civil":
            g_y, g_m, g_d = convertdate.indian_civil.to_gregorian(y, m, d)
        elif calendar == "chinese":
            g_y, g_m, g_d = convertdate.chinese.to_gregorian(y, m, d)
        else:
            raise ValueError(f"Calendar '{calendar}' is marked as supported but has no conversion")
            
        return f"{g_y:04d}-{g_m:02d}-{g_d:02d}"
        
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Invalid date format for {calendar} calendar. Expected format: YYYY-MM-DD"
        ) from e