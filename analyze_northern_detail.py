#!/usr/bin/env python3
"""Detailed analysis of Rubin footprint's northern region."""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from astropy.coordinates import SkyCoord, GeocentricTrueEcliptic
import astropy.units as u

from cosmic_neighborhoods.boundary import RubinBoundary

def get_ecliptic_curve():
    """Get ecliptic plane in RA/Dec coordinates."""
    ecl_lon = np.linspace(0, 360, 360)  # 1° steps
    ecl_lat = np.zeros_like(ecl_lon)
    coords = SkyCoord(
        lon=ecl_lon * u.deg,
        lat=ecl_lat * u.deg,
        frame=GeocentricTrueEcliptic
    )
    return coords.icrs.ra.deg, coords.icrs.dec.deg

def calc_airmass(dec_deg, site_lat=-30.2444):
    """Calculate approximate minimum airmass for a given declination.
    
    Uses simple approximation valid for zenith angles < 80°.
    For larger angles, should use more complex formula.
    """
    min_zenith = np.abs(dec_deg - site_lat)  # degrees
    if min_zenith > 80:
        return float('inf')  # Beyond simple approximation
    min_zenith_rad = np.radians(min_zenith)
    return 1 / np.cos(min_zenith_rad)

def main():
    """Create detailed visualization of northern region."""
    print("\nAnalyzing northern region in detail...")
    
    # Load boundary data
    boundary = RubinBoundary.from_cache("cosmic_neighborhoods/data/footprint/boundary_nside128.npz")
    
    # Create very detailed RA range (0.01° steps)
    ra_range = np.arange(70, 110, 0.01)
    dec_north = np.array([boundary.get_dec_range(ra)[1] for ra in ra_range])
    dec_south = np.array([boundary.get_dec_range(ra)[0] for ra in ra_range])
    
    # Get ecliptic curve
    ecl_ra, ecl_dec = get_ecliptic_curve()
    
    # Find maximum and local maxima
    max_idx = np.argmax(dec_north)
    max_ra = ra_range[max_idx]
    max_dec = dec_north[max_idx]
    max_airmass = calc_airmass(max_dec)
    
    # Calculate airmass statistics
    airmass = np.array([calc_airmass(dec) for dec in dec_north])
    valid_airmass = airmass[airmass < float('inf')]
    
    # Create figure
    plt.figure(figsize=(15, 10))
    
    # Plot northern boundary detail
    plt.plot(ecl_ra[(ecl_ra >= 70) & (ecl_ra <= 110)],
            ecl_dec[(ecl_ra >= 70) & (ecl_ra <= 110)],
            'r--', alpha=0.5, label='Ecliptic plane')
    
    plt.plot(ra_range, dec_north, 'b-', linewidth=1, label='Northern boundary')
    plt.plot(ra_range, dec_south, 'b-', linewidth=1, alpha=0.3)
    plt.fill_between(ra_range, dec_south, dec_north, color='blue', alpha=0.1)
    
    # Add grid
    plt.grid(True, alpha=0.2)
    for dec in range(-90, 41, 5):
        plt.axhline(dec, color='gray', alpha=0.1, linestyle='-')
    for ra in range(70, 111, 5):
        plt.axvline(ra, color='gray', alpha=0.1, linestyle='-')
    
    # Mark the absolute maximum
    plt.plot(max_ra, max_dec, 'r*', markersize=15,
            label=f'Maximum: {max_dec:.2f}° (X{max_airmass:.1f} airmass)')
    
    # Customize plot
    plt.xlim(70, 110)
    plt.ylim(-90, 40)
    plt.xlabel('Right Ascension (degrees)')
    plt.ylabel('Declination (degrees)')
    plt.title('Rubin Footprint Detail (0.01° RA resolution)')
    plt.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig('northern_detail.png', dpi=300)
    print("\nDetailed plot saved as northern_detail.png")
    
    # Print statistics
    print("\nKey statistics:")
    print(f"Maximum declination: {max_dec:.2f}° at RA {max_ra:.2f}°")
    print(f"Airmass at maximum: {max_airmass:.1f}X")
    
    print("\nAirmass statistics for northern boundary:")
    print(f"  Minimum: {valid_airmass.min():.1f}X")
    print(f"  Maximum: {valid_airmass.max():.1f}X")
    print(f"  Median: {np.median(valid_airmass):.1f}X")
    print(f"  Mean: {valid_airmass.mean():.1f}X")
    
    # Look at specific RA points
    key_ras = [80, 85, 90, 95, 100]
    print("\nConditions at key RAs:")
    for ra in key_ras:
        idx = np.abs(ra_range - ra).argmin()
        dec = dec_north[idx]
        am = calc_airmass(dec)
        print(f"  RA {ra:3d}°: Dec {dec:6.2f}°, Airmass {am:.1f}X")

if __name__ == "__main__":
    main()