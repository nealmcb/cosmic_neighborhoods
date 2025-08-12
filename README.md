# Cosmic Neighborhood

A CLI tool to help people form a relationship with their personal patch of the night sky. Each user gets assigned a unique patch of sky based on their birth date and latitude, helping them track discoveries, monitor alerts, and eventually connect with others who share similar cosmic neighborhoods.

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
cosmic assign --birth-date 1990-06-15 --latitude 45.0
```

### Check Sun Times

View sunrise, sunset, and twilight times for your location:

```bash
cosmic sun --latitude 45.0 --longitude -75.0
```

### Monitor Alerts (Coming Soon)

Check for events in your patch (stub in v1):

```bash
cosmic alerts --patch-id P0615N45
```

### JSON Output

All commands support JSON output with the `--json` flag:

```bash
cosmic assign --birth-date 1990-06-15 --latitude 45.0 --json
```

## Accuracy Notes

This is version 1, focused on getting people connected with their patch of sky. The calculations are intentionally simplified:

- Sun times are approximate (±5-10 minutes)
- Patch assignment uses simple formulas
- No correction for atmospheric effects
- No correction for elevation

Future versions will improve accuracy while maintaining the focus on accessibility and engagement.

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run quality checks
make check

# Run tests only
make test

# Run type checks only
make typecheck

# Run linting only
make lint
```

## Data Sources

- Population data: [GHSL GHS-POP R2023A](https://ghsl.jrc.ec.europa.eu/download.php?ds=pop) from the EU Joint Research Centre
- Solar ephemeris: [Astropy](https://www.astropy.org/) library
- Calendar conversions: [convertdate](https://github.com/fitnr/convertdate) library

## License

MIT