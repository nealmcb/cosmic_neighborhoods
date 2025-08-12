"""Command-line interface for Cosmic Neighborhoods.

Assigns personalized patches of the Rubin Observatory sky based on birth date and latitude.
Each person's cosmic neighborhood is a HEALPix tile that:
1. Culminates at local mean solar midnight on their birthday
2. Has a declination matching their birth latitude's population percentile
"""

from pathlib import Path
from typing import Optional, Tuple
import json
import warnings
import importlib.resources

# Suppress ERFA warnings about historical dates
warnings.filterwarnings('ignore', category=Warning)

import typer
from astropy_healpix import HEALPix
from astropy.coordinates import SkyCoord
import astropy.units as u

from cosmic_neighborhoods.boundary import RubinBoundary
from cosmic_neighborhoods.population import build_population_cdf
from cosmic_neighborhoods.mapping import map_latitude_to_declination, assign_healpix_tile
from cosmic_neighborhoods.ephemeris import sun_ra_deg, convert_to_gregorian

app = typer.Typer(
    help="""Assign your cosmic neighborhood in the Rubin sky.

Examples:
    # Vera Rubin's cosmic neighborhood (born in Philadelphia):
    cosmic 39.95 1928-07-23

    # Same location with lower resolution (larger patch):
    cosmic 39.95 1928-07-23 4

    # Winter solstice example with medium resolution:
    cosmic 39.95 1957-12-21 6

    # Show data status:
    cosmic --info

    # Initialize footprint data:
    cosmic --init-footprint PATH_TO_OPSIM.db""",
    no_args_is_help=True,
)

def get_package_root() -> Path:
    """Get the root directory of the cosmic_neighborhoods package."""
    try:
        # Python 3.9+: use files()
        root = Path(importlib.resources.files("cosmic_neighborhoods"))
    except AttributeError:
        # Fallback for older Python: use __file__
        root = Path(__file__).parent
    return root

def check_data_files() -> Tuple[bool, bool, str]:
    """Check if required data files exist and return status and message."""
    root = get_package_root()
    footprint_cache = root / "data/footprint/boundary_nside128.npz"
    pop_source = root / "data/population/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif"
    
    footprint_ok = footprint_cache.exists()
    population_ok = pop_source.exists()
    
    msg = ""
    if not footprint_ok or not population_ok:
        msg = "\nMissing required data:"
        if not footprint_ok:
            msg += "\n1. Footprint data:"
            msg += "\n   - Download OpSim baseline v3.2 database"
            msg += "\n   - Run: cosmic --init-footprint PATH_TO_OPSIM.db"
        if not population_ok:
            msg += "\n2. Population data:"
            msg += "\n   - Download GHSL GHS-POP R2023A data"
            msg += "\n   - Run: cosmic --init-population PATH_TO_GHSL.tif"
        msg += "\n\nRun 'cosmic --info' for more details"
    
    return footprint_ok, population_ok, msg

def resolution_to_nside(resolution: int) -> int:
    """Convert resolution (log2 nside) to nside."""
    return 2 ** resolution

def get_pixel_area(nside: int) -> float:
    """Get area of one HEALPix pixel in square degrees."""
    return 41252.96 / (12 * nside * nside)

def show_info() -> None:
    """Show data versions and cache status."""
    # Get absolute paths for cache files
    root = get_package_root()
    footprint_cache = root / "data/footprint/boundary_nside128.npz"
    pop_source = root / "data/population/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif"
    
    print("Cosmic Neighborhoods Status:")
    print()
    
    # Software status first
    print("Software:")
    print("  Version: 0.1.0")
    print()
    
    # Footprint status
    print("Footprint data:")
    if footprint_cache.exists():
        print("  Status: Ready")
        print("  Version: opsim-baseline-v3.2")
        print(f"  Path: {footprint_cache}")
    else:
        print("  Status: Not initialized")
        print(f"  Expected path: {footprint_cache}")
        print("  Action: Run cosmic --init-footprint PATH_TO_OPSIM.db")
    print()
    
    # Population status
    print("Population data:")
    if pop_source.exists():
        print("  Status: Ready")
        print("  Version: ghsl-2020")
        print(f"  Path: {pop_source}")
    else:
        print("  Status: Missing")
        print(f"  Expected path: {pop_source}")
        print("  Action: Download GHSL data and run cosmic --init-population PATH_TO_GHSL.tif")
    print()
    
    if not footprint_cache.exists() or not pop_source.exists():
        print("Setup required:")
        if not footprint_cache.exists():
            print("1. Download OpSim baseline v3.2 database")
            print("2. Run: cosmic --init-footprint PATH_TO_OPSIM.db")
        if not pop_source.exists():
            print("3. Download GHSL population data")
            print("4. Run: cosmic --init-population PATH_TO_GHSL.tif")

def initialize_footprint(opsim_db: Path) -> None:
    """Initialize footprint data from OpSim database."""
    try:
        # Extract boundary
        boundary = RubinBoundary.from_opsim(opsim_db)
        
        # Save to cache
        root = get_package_root()
        cache_file = root / "data/footprint/boundary_nside128.npz"
        cache_dir = cache_file.parent
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        boundary.save(cache_file)
        print(f"Footprint data cached to {cache_file}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise typer.Exit(1)

def initialize_population(pop_source: Path) -> None:
    """Initialize population data from GHSL GeoTIFF."""
    try:
        pop_cdf = build_population_cdf(pop_source)
        print(f"Population CDF built from {pop_source}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise typer.Exit(1)

def assign_neighborhood(
    lat: float,
    date: str,
    resolution: int = 7,
    calendar: str = "gregorian",
    json_output: bool = False,
) -> None:
    """Core assignment logic."""
    # Convert date to Gregorian
    if calendar != "gregorian":
        date = convert_to_gregorian(date, calendar)
    
    # Get Sun's RA and add 180° for nighttime
    sun_ra = sun_ra_deg(date)
    assigned_ra = (sun_ra + 180.0) % 360.0  # This puts us OPPOSITE the Sun, visible at midnight
    
    # Load population CDF
    root = get_package_root()
    pop_source = root / "data/population/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif"
    pop_cdf = build_population_cdf(pop_source)
    
    # Load footprint boundary
    try:
        cache_file = root / "data/footprint/boundary_nside128.npz"
        boundary = RubinBoundary.from_cache(cache_file)
    except FileNotFoundError:
        print("Error: Footprint data not initialized. Run 'cosmic --info' first.")
        raise typer.Exit(1)
    
    # Map latitude to declination
    dec = map_latitude_to_declination(lat, assigned_ra, pop_cdf, boundary)
    
    # Assign HEALPix tile
    nside = resolution_to_nside(resolution)
    pixel = assign_healpix_tile(assigned_ra, dec, nside)
    
    # Get pixel center and constellation
    hp = HEALPix(nside=nside, order='nested', frame='icrs')
    center = hp.healpix_to_skycoord(pixel)
    center_ra = center.ra.deg
    center_dec = center.dec.deg
    constellation = center.get_constellation()
    
    # Calculate pixel area
    area = get_pixel_area(nside)
    
    result = {
        "input": {
            "latitude_deg": lat,
            "date": date,
            "calendar": calendar,
        },
        "computed": {
            "sun_ra_deg": sun_ra,
            "assigned_ra_deg": assigned_ra,
            "assigned_dec_deg": dec,
        },
        "healpix": {
            "nside": nside,
            "scheme": "nested",
            "pixel": int(pixel),
            "area_deg2": area,
            "center_ra_deg": center_ra,
            "center_dec_deg": center_dec,
            "constellation": constellation,
        },
        "versions": {
            "footprint": "opsim-baseline-v3.2",
            "pop": "ghsl-2020",
            "code": "0.1.0",
        },
    }
    
    if json_output:
        print(json.dumps(result))
    else:
        print(f"Cosmic neighborhood for {lat:.6f}°N, {date}:")
        print(f"  Assigned point: RA {assigned_ra:.6f}°, Dec {dec:.6f}°")
        print(f"  Pixel center: RA {center_ra:.6f}°, Dec {center_dec:.6f}° (in {constellation})")
        print(f"  HEALPix {pixel} (nside={nside}, {area:.2f} deg²)")

@app.command()
def main(
    lat: Optional[float] = typer.Argument(
        None,
        help="Birth latitude in degrees (-90 to +90)",
        min=-90,
        max=90,
        show_default=False,
    ),
    date: Optional[str] = typer.Argument(
        None,
        help="Birth date (YYYY-MM-DD)",
        show_default=False,
    ),
    resolution: int = typer.Argument(
        7,
        help="HEALPix resolution (log2 of nside, 0-8; higher = smaller pixels)",
        min=0,
        max=8,
    ),
    info: bool = typer.Option(
        False,
        "--info",
        help="Show data versions and cache status",
        is_eager=True,
    ),
    init_footprint: Optional[Path] = typer.Option(
        None,
        "--init-footprint",
        help="Initialize footprint data from OpSim database",
        exists=True,
        dir_okay=False,
        is_eager=True,
    ),
    init_population: Optional[Path] = typer.Option(
        None,
        "--init-population",
        help="Initialize population data from GHSL GeoTIFF",
        exists=True,
        dir_okay=False,
        is_eager=True,
    ),
    calendar: str = typer.Option(
        "gregorian",
        "--calendar",
        help="Calendar system for date",
    ),
    json: bool = typer.Option(
        False,
        "--json",
        help="Output in JSON format",
    ),
) -> None:
    """Assign a cosmic neighborhood based on birth date and latitude."""
    try:
        if info:
            show_info()
            return
        elif init_footprint:
            initialize_footprint(init_footprint)
            return
        elif init_population:
            initialize_population(init_population)
            return
        
        # Default behavior: assignment
        if lat is None or date is None:
            if not any([info, init_footprint, init_population]):
                            print("Error: Latitude and date are required")
            print("Run 'cosmic --help' for usage examples")
            raise typer.Exit(1)
            return
        
        # Check data availability before attempting assignment
        footprint_ok, population_ok, msg = check_data_files()
        if not (footprint_ok and population_ok):
            print(msg)
            raise typer.Exit(1)
        
        assign_neighborhood(lat, date, resolution, calendar, json)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()