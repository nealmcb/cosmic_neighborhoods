#!/usr/bin/env python3
"""Simple tests to try out cosmic neighborhood functionality."""

from datetime import date
from cosmic_neighborhoods.ephemeris import sun_ra_deg, convert_to_gregorian

def main() -> None:
    """Run simple tests."""
    # Test Sun RA calculation
    today = date.today().strftime("%Y-%m-%d")
    print(f"\nSun's position today ({today}):")
    print(f"RA = {sun_ra_deg(today):.2f}°")
    print(f"Patch center will be at RA = {(sun_ra_deg(today) + 180) % 360:.2f}°")
    
    # Test calendar conversion
    test_date = "2024-03-19"
    print(f"\nCalendar conversion test:")
    print(f"Gregorian {test_date} is:")
    print(f"  Julian:   {convert_to_gregorian(test_date, 'julian')}")
    
    # You can uncomment these to test other calendar systems
    # print(f"  Hebrew:   {convert_to_gregorian(test_date, 'hebrew')}")
    # print(f"  Islamic:  {convert_to_gregorian(test_date, 'islamic')}")
    # print(f"  Persian:  {convert_to_gregorian(test_date, 'persian')}")

if __name__ == "__main__":
    main()
