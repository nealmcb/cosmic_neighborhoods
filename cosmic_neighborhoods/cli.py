"""Command-line interface for Cosmic Neighborhoods."""

from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
import json

from cosmic_neighborhoods.boundary import RubinBoundary

app = typer.Typer(help="Assign and explore your cosmic neighborhood in the Rubin sky.")
console = Console()

@app.command()
def boundary(
    ra: float = typer.Argument(
        ...,
        help="Right ascension in degrees (0 to 360)",
        min=0,
        max=360,
    ),
    cache_file: Path = typer.Option(
        "cosmic_neighborhoods/data/footprint/boundary_nside128.npz",
        help="Path to boundary cache file",
        exists=True,
        dir_okay=False,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output in JSON format",
    ),
) -> None:
    """Get Rubin footprint boundary at specific RA."""
    try:
        # Load boundary data
        boundary = RubinBoundary.from_cache(cache_file)
        
        # Get declination range
        dec_south, dec_north = boundary.get_dec_range(ra)
        
        result = {
            "ra_deg": ra,
            "dec_south_deg": dec_south,
            "dec_north_deg": dec_north,
            "width_deg": dec_north - dec_south,
        }
        
        if json_output:
            print(json.dumps(result))
        else:
            print(f"At RA {ra:.1f}°:")
            print(f"  Dec range: [{dec_south:.1f}°, {dec_north:.1f}°]")
            print(f"  Width: {dec_north - dec_south:.1f}°")
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def boundary_range(
    ra_start: float = typer.Argument(
        ...,
        help="Start right ascension in degrees",
        min=0,
        max=360,
    ),
    ra_end: float = typer.Argument(
        ...,
        help="End right ascension in degrees",
        min=0,
        max=360,
    ),
    step: float = typer.Option(
        1.0,
        help="RA step size in degrees",
        min=0.1,
        max=10.0,
    ),
    cache_file: Path = typer.Option(
        "cosmic_neighborhoods/data/footprint/boundary_nside128.npz",
        help="Path to boundary cache file",
        exists=True,
        dir_okay=False,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output in JSON format",
    ),
) -> None:
    """Get Rubin footprint boundary over a range of RAs."""
    try:
        # Load boundary data
        boundary = RubinBoundary.from_cache(cache_file)
        
        # Generate RA range
        if ra_end < ra_start:
            ra_end += 360  # Handle wrapping
        ra_values = []
        ra = ra_start
        while ra <= ra_end:
            ra_values.append(ra % 360)  # Normalize to [0, 360)
            ra += step
        
        # Get declination ranges
        results = []
        for ra in ra_values:
            dec_south, dec_north = boundary.get_dec_range(ra)
            results.append({
                "ra_deg": ra,
                "dec_south_deg": dec_south,
                "dec_north_deg": dec_north,
                "width_deg": dec_north - dec_south,
            })
        
        if json_output:
            print(json.dumps(results))
        else:
            # Find maximum width for formatting
            max_width = max(r["width_deg"] for r in results)
            
            print(f"Boundary from RA {ra_start:.1f}° to {ra_end % 360:.1f}° (step {step:.1f}°):")
            print("\nRA      Dec South   Dec North   Width")
            print("-" * 40)
            for r in results:
                print(f"{r['ra_deg']:6.1f}° {r['dec_south_deg']:9.1f}° {r['dec_north_deg']:9.1f}° {r['width_deg']:7.1f}°")
            
            # Show statistics
            print(f"\nMaximum width: {max_width:.1f}° at RA {results[max(range(len(results)), key=lambda i: results[i]['width_deg'])]['ra_deg']:.1f}°")
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()