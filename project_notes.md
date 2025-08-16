# Cosmic Neighborhoods Project Notes

## Project Goals
- Assign users personalized patches of Rubin Observatory sky based on birth date and latitude
- Make assignments deterministic and privacy-respecting
- Map population-latitude percentile to corresponding declination within Rubin footprint
- Use anti-solar point on birthday for RA (visible at local midnight)

## Technical Requirements
- Python 3.10+
- Use Typer for CLI, Rich for output formatting
- No external API calls in v1
- Use black (line length 100), ruff, mypy --strict
- All functions must have type hints and docstrings
- All core functions must have unit tests
- Use pytest, maintain test coverage

## Policies
- Preserve planned work and ideas in TODO.md

## Design Decisions
- HEALPix for sky tiling (nside=2^resolution, resolution 0-8)
- Store footprint boundaries in .npz format
- Use astropy for solar ephemeris
- Calculate sun's RA at noon UTC
- Use "nested" HEALPix ordering scheme
- Support both human-readable and JSON output

## Current Status
- Core assignment functionality working
- Basic CLI implemented
- Tests passing with high precision checks
- Footprint visualization needs improvement

## Pending Tasks
- Add birth time support (YYYY-MM-DDThh:mm format)
- Modify footprint to exclude areas with few visits
- Design system for seasonal alert distribution variations

## Key Constraints
- Must work without external APIs
- Must respect user's colorblindness
- Must maintain high precision in astronomical calculations
- Must be suitable for casual users

## Unresolved Questions
- Design approach for handling seasonal and daily alert distribution variations (sun proximity, moon phase, weather patterns) to help users optimize their alert subscriptions
- How to handle seasonal variations in alert distribution
- How to optimize alert subscriptions for sun/moon proximity
- How to handle weather interference patterns
- How to implement magnified region plots

## Data Sources
- Rubin OpSim baseline footprint (SQLite database)
- GHSL population dataset
- Astropy solar ephemeris
