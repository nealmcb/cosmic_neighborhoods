# Cosmic Neighborhoods TODOs

## In Progress
None currently

## Pending

### Footprint Analysis
- [ ] Create visualization of footprint visit density, focusing on northern region sparseness
- [ ] Analyze distribution of expected visit counts across footprint
- [ ] Modify footprint boundary to exclude areas with fewer than ~10 expected visits
- [ ] Update boundary cache format to include visit counts and regenerate cache file

### Birth Time Support
- [ ] Add support for birth time in CLI (e.g., YYYY-MM-DDThh:mm format)
- [ ] Update ephemeris calculations to use exact time instead of just date
- [ ] Update documentation and help text to explain time format options

### Development Setup
- [ ] Create Makefile with development targets (check, test, lint, etc.)
- [ ] Configure ruff for linting and formatting (100 char line length)
- [ ] Configure mypy with --strict mode for type checking
- [ ] Configure pytest with coverage reporting
- [ ] Update README with development workflow and make targets

## Completed
- [x] Add MIT license file and update pyproject.toml license field
