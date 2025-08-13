# Cosmic Neighborhood

There's a patch of sky that arcs overhead at night each year on your birthday -
a place in the cosmos always unfolding while you go about your life.

We invite you to reconnect with that part of the universe - and to share it with others
whose circumstances of birth align them with nearby regions of sky.

Using just your birth date and the latitude of your birthplace, you are assigned
a small patch of the sky observed by the Vera C. Rubin Observatory.

We'll help connect you with tools to track what changes there -
flares, new asteroids, distant supernovae -
and over time, help you find yourself in conversation with the cosmos
and with others whose patches lie close by.

This is your cosmic neighborhood: a way to stay curious, stay connected,
and find meaning in the rhythms of the sky.


This repository provides a simple tool that can be used to assign people to patches of the sky.
The tool is initially configured to cover just the areas of the sky that the
Rubin Observatory is surveying (its expected "footprint"), but can be easily adapted to
a different footprint, like that of the Zwicky Transient Facility.

Every night Rubin identifes perhaps 10 million changes in the sky, which
are communicated as "alerts" via "brokers". You can customize the broker to only
notify you about certain types of events in your chosen or assigned area of the sky.

## Calculating assignments: mapping people to the survey footprint
The project assigns cosmic neighborhoods so as to achieve a relatively even coverage of the
survey footprint, by taking into account both the shape of the footprint, and the distribution
of people across the planet and across time.

Birthdays are assumed to be relatively evenly spread out around the year, and are used to choose
the Right Ascension of the assigned neighborhood, such that it culminates around midnight
on their birthday. Face south at midnight on your birthday, and your assigned patch
will be as high in the sky as it ever gets.

Spreading the neighborhoods out evenly north-to-south across the footprint
is a bit trickier.
The goal is to make them visible from the person's birthplace, by assigning
those born furthest to the north to the most northernly areas of the footprint,
and proceeding south by mapping each percentile of the global human birth-latitude
distribution to the same percentile in the Rubin footprint’s cumulative sky area by declination.

## Installation

Requires Python 3.10+

```bash
# Create and activate virtual environment (using uv)
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

### Population Data Setup

The project uses the GHSL (Global Human Settlement Layer) population dataset from the EU Joint Research Centre. To set up:

1. Download the 2020 population data (30 arc-second resolution):
   ```bash
   wget https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_GLOBE_R2023A/GHS_POP_E2020_GLOBE_R2023A_4326_30ss/V1-0/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.zip
   ```

2. Unzip into the data directory:
   ```bash
   unzip GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.zip -d cosmic_neighborhoods/data/population/
   ```

The data files are gitignored and will be processed into latitude bins on first use.

## Usage

The tool provides several commands:

### Assign Your Patch

Get your personal patch of the night sky:

```bash
# Basic usage (resolution=7 for ~0.21 deg² pixels)
cosmic 45.0 1990-06-15

# Higher resolution (resolution=8 for ~0.05 deg² pixels)
cosmic 45.0 1990-06-15 8

# Lower resolution (resolution=4 for ~3.4 deg² pixels)
cosmic 45.0 1990-06-15 4

# Show data status and cache paths
cosmic --info

# JSON output
cosmic 45.0 1990-06-15 --json
```

### Initialize Data (First Use)

Before first use, you need to initialize the footprint and population data:

```bash
# Initialize footprint from OpSim database
cosmic --init-footprint PATH_TO_OPSIM.db

# Initialize population from GHSL data
cosmic --init-population PATH_TO_GHSL.tif
```

## Understanding Your Patch

Your cosmic neighborhood is defined by a HEALPix (Hierarchical Equal Area isoLatitude Pixelization) tile. This system divides the sky into equal-area pixels in a way that's particularly useful for astronomy:

- Each pixel has the same area (important for fair distribution)
- Pixels are arranged in a hierarchical pattern (like a nested tree)
- Higher resolution means smaller pixels:
  - Resolution 0: 12 pixels total (~3438 deg² each)
  - Resolution 4: 3072 pixels (~13.4 deg² each)
  - Resolution 7: 196,608 pixels (~0.21 deg² each, default)
  - Resolution 8: 786,432 pixels (~0.05 deg² each)

The HEALPix index (e.g., "pixel 119819") uniquely identifies your patch. We use the "nested" ordering scheme because it preserves relationships between pixels at different resolutions - a lower-resolution pixel contains all the higher-resolution pixels that would subdivide it.

## Accuracy Notes

This is version 1, focused on getting people connected with their patch of sky. The calculations are intentionally simplified:

- Sun times are approximate (±5-10 minutes)
- Patch assignment uses simple formulas
- No correction for atmospheric effects
- No correction for elevation

Future versions will improve accuracy while maintaining the focus on accessibility and engagement.

## Development

### Setup

```bash
# Create and activate virtual environment
uv venv .venv
source .venv/bin/activate

# Install package in editable mode with dev dependencies
uv pip install -e ".[dev]"
```

### Code Quality

The project uses several tools to maintain code quality:

- **Black** (via ruff): Code formatting with 100-character line length
- **Ruff**: Fast Python linting
- **Mypy**: Static type checking in strict mode
- **Pytest**: Unit testing with coverage reporting

Run quality checks:

```bash
# Run all checks (format, lint, typecheck, test)
make check

# Individual checks
make format     # Format code with ruff
make lint       # Run ruff linter
make typecheck  # Run mypy type checker
make test       # Run pytest with coverage

# Clean temporary files
make clean
```

### Project Structure

- `cosmic_neighborhoods/`
  - `cli.py`: Command-line interface
  - `ephemeris.py`: Solar position calculations
  - `population.py`: Population distribution handling
  - `footprint.py`: Rubin footprint extraction
  - `mapping.py`: Core assignment algorithms
  - `boundary.py`: Footprint boundary representation
  - `data/`: Data files and caches
    - `footprint/`: Rubin survey data
    - `population/`: GHSL population data
- `tests/`: Unit tests
- `pyproject.toml`: Project metadata and dependencies
- `Makefile`: Development automation

### Design Principles

1. **Pure Computation**: Core logic is kept separate from I/O and CLI
2. **Type Safety**: All functions have type hints and are mypy-checked
3. **Documentation**: All functions have docstrings explaining behavior
4. **Testing**: Core functions have unit tests with good coverage
5. **Performance**: Data is cached and processed efficiently
6. **User Experience**: Clear error messages and helpful CLI output

### Git Workflow

1. Run `make check` before commits
2. Ensure all tests pass
3. Keep commits focused and well-documented
4. Follow conventional commit messages:
   - `feat:` New features
   - `fix:` Bug fixes
   - `refactor:` Code restructuring
   - `docs:` Documentation updates
   - `test:` Test updates
   - `chore:` Maintenance tasks

## Data Sources

- Population data: [GHSL GHS-POP R2023A](https://ghsl.jrc.ec.europa.eu/download.php?ds=pop) from the EU Joint Research Centre
- Solar ephemeris: [Astropy](https://www.astropy.org/) library
- Calendar conversions: [convertdate](https://github.com/fitnr/convertdate) library

## License

MIT
