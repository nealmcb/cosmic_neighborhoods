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

### Check Moon Phase

View current moon phase and illumination:

```bash
cosmic moon
```

Or for a specific date/time:

```bash
cosmic moon --target-date "2024-03-01 12:00"
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
- Moon phases are approximate (±1 day)
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

## License

MIT
