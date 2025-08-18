# TODO List

## Footprint Analysis
- [ ] Create visualization of footprint visit density, focusing on northern region sparseness (and ensure it handles log scale to capture both rare pixels and DDFs)
- [ ] Produce the footprint density visualization in a FITS format or similar, so it can be opened in Aladin.
- [ ] Modify footprint boundary to exclude areas with fewer than ~10 expected visits
- [ ] Update boundary cache format to include visit counts and regenerate cache file

## Birth Time Support
- [ ] Add support for birth time in CLI (e.g., YYYY-MM-DDThh:mm format)
- [ ] Update ephemeris calculations to use exact time instead of just date
- [ ] Update documentation and help text to explain time format options

## Multiple Neighborhoods Support
- [ ] Design support for users to adopt multiple complementary neighborhoods
- [ ] Extend sun_ra_deg() to support multiple time offsets
- [ ] Add CLI options for generating additional neighborhoods
- [ ] Create algorithm to space neighborhoods optimally (considering 3-day survey window)
- [ ] Integrate visit density data for optimal neighborhood placement
- [ ] Add metadata to track optimal viewing periods between neighborhoods
- [ ] Enhance visualization to show multiple neighborhoods and viewing windows

## Alert Observability Analysis
- [ ] Analyze expected magnitude distribution of Rubin alerts
- [ ] Document magnitude ranges for different alert types
- [ ] Create table of typical magnitude limits for different equipment
- [ ] Design system to match users with observable alerts
- [ ] Analyze alert broker filtering capabilities
- [ ] Set up AlertSim for local testing and analysis
- [ ] Create guidelines for observation strategy by equipment type
- [ ] Improve visibility of Deep Drilling Fields in visualization - avoid yellow/green that makes DDFs invisible to colorblind users
- [ ] Design system for handling seasonal and daily alert distribution variations (sun proximity, moon phase, weather patterns) to help users optimize their alert subscriptions

## Terminology and Documentation
- [ ] Review and document HEALPix terminology (order vs nside)
- [ ] Update CLI to show order k (for Aladin compatibility)
- [ ] Update documentation to explain both terms
- [ ] Add examples using both systems

## Development Setup (Completed)
- [x] Create Makefile with development targets (check, test, lint, etc.)
- [x] Configure ruff for linting and formatting (100 char line length)
- [x] Configure mypy with --strict mode for type checking
- [x] Configure pytest with coverage reporting and add basic assignment tests
- [x] Update README with development workflow and make targets
- [x] Add MIT license file and update pyproject.toml license field

## Community Engagement
- [ ] Design core gamification features
- [ ] Create achievement system for different alert types
- [ ] Design privacy-preserving sharing capabilities
- [ ] Create educational content about cosmic neighborhoods
- [ ] Plan citizen science project integration points
- [ ] Design system for forming observing groups
- [ ] Create accessible visualizations for all users