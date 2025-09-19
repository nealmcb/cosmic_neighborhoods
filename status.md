# Cosmic Neighborhoods Project Status

## Project Overview

**Cosmic Neighborhoods** is a Python tool that assigns personalized patches of the Vera C. Rubin Observatory's survey footprint to users based on their birth date and latitude. The project aims to create a meaningful connection between individuals and specific regions of the night sky, enabling them to track astronomical events and changes in their assigned "cosmic neighborhood."

### Core Concept
- Users provide their birth date and birthplace latitude
- The system assigns them a HEALPix pixel (sky patch) that:
  - Culminates around midnight on their birthday (using anti-solar point for RA)
  - Is positioned based on their latitude percentile within the Rubin footprint
  - Is visible from their birthplace location

## Current Status

### ✅ Completed Work

#### Core Functionality
- **Assignment Algorithm**: Complete implementation of cosmic neighborhood assignment
- **HEALPix Integration**: Full support for hierarchical sky pixelization (resolutions 0-8)
- **Solar Ephemeris**: Accurate sun position calculations using Astropy
- **Population Mapping**: Integration with GHSL population data for latitude distribution
- **CLI Interface**: Full command-line tool with Typer and Rich formatting
- **Data Caching**: Efficient caching system for footprint and population data

#### Data Infrastructure
- **OpSim Integration**: Rubin Observatory Operations Simulator database processing
- **Footprint Extraction**: Automated extraction of survey boundaries from OpSim
- **Population Processing**: GHSL dataset integration for global population distribution
- **Parquet Caching**: High-performance data storage using Parquet format

#### Analysis Tools
- **Visit Density Analysis**: Comprehensive analysis of Rubin survey coverage patterns
- **Timing Analysis**: Study of observation cadence and gaps between visits
- **Spatial Correlation**: Analysis of which pixels are visited on consecutive days
- **Visualization Tools**: Multiple plotting utilities for survey analysis

#### Code Quality
- **Type Safety**: Full mypy strict mode compliance
- **Testing**: Comprehensive test suite with pytest
- **Code Formatting**: Black/ruff formatting with 100-character line length
- **Documentation**: Extensive docstrings and README

### 🔄 Work in Progress

#### Visualization Issues
- **Marker Placement**: Ongoing debugging of 'X' marker placement on HEALPix Mollweide projections
- **Coordinate Transformation**: Challenges with accurate RA/Dec to plot coordinate conversion
- **Colorblind Accessibility**: Ensuring visualizations work for users with color vision deficiencies

#### Data Analysis
- **Deep Drilling Fields**: Identification and handling of high-visit-count special fields
- **Visit Distribution**: Analysis of the highly skewed distribution of visit counts per pixel
- **Timing Patterns**: Study of observation timing correlations across the survey

### ❌ Known Issues

#### Technical Debt
- **Memory Management**: Some analysis scripts require optimization for large datasets
- **Coordinate Systems**: Inconsistent handling of RA/Dec coordinate transformations
- **Data Format**: MJD storage format changes between string and array representations

#### Visualization Problems
- **Marker Accuracy**: 'X' markers not appearing in correct geographical locations on heatmaps
- **Projection Issues**: Mollweide projection coordinate conversion needs refinement
- **Color Schemes**: Need to ensure accessibility for colorblind users

## Recent Work (This Session)

### Major Accomplishments
1. **Full Dataset Processing**: Successfully built observation cache for complete Rubin survey
2. **Visit Distribution Analysis**: Discovered highly skewed distribution with most pixels having few visits
3. **Timing Analysis**: Implemented efficient analysis of observation gaps and cadence
4. **Spatial Correlation**: Created tools to analyze which pixels are visited the day after a given visit
5. **Performance Optimization**: Implemented single-pass algorithms for large dataset analysis

### Key Scripts Developed
- `scripts/analyze_pixel_timing.py`: Analysis of observation timing patterns
- `scripts/analyze_pixel_correlation.py`: Study of spatial correlations in visits
- `scripts/test_marker_placement.py`: Debugging tool for visualization issues
- `scripts/analyze_first_day.py`: First-day coverage analysis

### Data Generated
- `pixel_observations_full.parquet`: Complete observation cache (196,608 pixels)
- Multiple visualization PNG files showing survey patterns
- Visit distribution statistics and analysis

## Pending Work

### Code review
1. **Human Review of core requirement spec, tests, and code**
2. **Add more robust AI coding methodology rules**

### Immediate Priorities
3. **Code Cleanup**: Commit current work and clean up temporary files

### Usability Work
1. **Multiple Neighborhoods**: Support for users to adopt multiple complementary sky patches if they want to be active in all seasons and/or consecutive days
2. **Alert Observability**: Analysis of which alerts users can observe with different equipment
3. **Seasonal Variations**: Handle seasonal changes in survey patterns and alert distribution

### Visualization and multi-day tempo optimization
1. **Fix Marker Placement**: Resolve coordinate transformation issues for accurate 'X' marker placement
2. **Visualization Polish**: Ensure all heatmaps display correctly with proper markers

### Short-term Goals
1. **Deep Drilling Field Handling**: Proper identification and visualization of DDFs
2. **Visit Count Filtering**: Implement filtering to exclude low-visit pixels from footprint
3. **Performance Optimization**: Optimize memory usage for large dataset analysis

### Long-term Goals
1. **Community Features**: Gamification and social features for user engagement
2. **Educational Content**: Integration with citizen science projects
3. **Advanced Visualization**: Interactive tools and enhanced plotting capabilities

## Technical Architecture

### Core Components
- `cosmic_neighborhoods/cli.py`: Command-line interface
- `cosmic_neighborhoods/mapping.py`: Core assignment algorithms
- `cosmic_neighborhoods/footprint.py`: Rubin survey data processing
- `cosmic_neighborhoods/population.py`: Population distribution handling
- `cosmic_neighborhoods/ephemeris.py`: Solar position calculations

### Data Dependencies
- **OpSim Database**: Rubin Observatory Operations Simulator (SQLite)
- **GHSL Population Data**: Global Human Settlement Layer (GeoTIFF)
- **Astropy**: Astronomical calculations and coordinate systems
- **HEALPix**: Hierarchical sky pixelization

### Development Tools
- **Python 3.10+**: Core language requirement
- **Typer**: CLI framework
- **Rich**: Terminal output formatting
- **Pytest**: Testing framework
- **Mypy**: Type checking
- **Ruff**: Linting and formatting

## Files and Directories

### Key Files
- `README.md`: Project documentation and usage instructions
- `pyproject.toml`: Project configuration and dependencies
- `Makefile`: Development automation
- `TODO.md`: Detailed task tracking
- `project_notes.md`: Design decisions and technical notes

### Data Directory
- `cosmic_neighborhoods/data/footprint/`: Rubin survey data and caches
- `cosmic_neighborhoods/data/population/`: GHSL population data

### Scripts Directory
- `scripts/`: Analysis and visualization tools
- Various PNG files: Generated visualizations

### Test Directory
- `tests/`: Unit tests for core functionality
- `cosmic_neighborhoods/tests/`: Additional test modules

## Dependencies and Requirements

### Core Dependencies
- Python 3.10+
- Astropy (astronomical calculations)
- HEALPix (sky pixelization)
- NumPy, Pandas (data processing)
- Matplotlib (visualization)
- Typer, Rich (CLI interface)

### Development Dependencies
- Pytest (testing)
- Mypy (type checking)
- Ruff (linting/formatting)

### External Data
- Rubin OpSim database (SQLite)
- GHSL population dataset (GeoTIFF)

## Success Metrics

### Technical Metrics
- ✅ All tests passing
- ✅ Type checking compliance
- ✅ Code formatting standards
- ✅ Core functionality working
- 🔄 Visualization accuracy (in progress)
- ❌ Memory optimization (pending)

### User Experience Metrics
- ✅ CLI usability
- ✅ Clear error messages
- ✅ Comprehensive documentation
- 🔄 Visualization accessibility (in progress)
- ❌ Performance optimization (pending)

## Risk Assessment

### High Risk
- **Memory Issues**: Large dataset analysis may cause system crashes
- **Visualization Accuracy**: Incorrect marker placement could mislead users

### Medium Risk
- **Data Quality**: OpSim database changes could break processing
- **Performance**: Slow analysis could impact user experience

### Low Risk
- **Dependencies**: Well-maintained libraries with stable APIs
- **Core Algorithm**: Mathematically sound assignment logic

## Possible steps

### Immediate (Next Session)
1. **Debug Marker Placement**: Fix coordinate transformation in visualization scripts
2. **Test Visualization**: Verify all heatmaps display correctly with proper markers
3. **Commit Work**: Save current progress and clean up temporary files
4. **Document Issues**: Create clear documentation of remaining visualization problems

### Short-term (Next Week)
1. **Deep Drilling Fields**: Implement proper DDF identification and handling
2. **Visit Filtering**: Add filtering to exclude low-visit pixels from assignments
3. **Performance**: Optimize memory usage for large dataset analysis
4. **Testing**: Add comprehensive tests for new analysis scripts

### Medium-term (Next Month)
1. **Multiple Neighborhoods**: Design and implement support for multiple sky patches
2. **Alert Analysis**: Study alert observability with different equipment
3. **Seasonal Handling**: Implement seasonal variation analysis
4. **User Experience**: Improve CLI output and error handling

## Conclusion

The *Cursor AI thinks that* the Cosmic Neighborhoods project has made significant progress in its core functionality, with a working assignment system and comprehensive analysis tools. The main remaining challenges are in visualization accuracy and performance optimization. The project is well-positioned to move forward with advanced features like multiple neighborhoods and alert observability analysis once the current technical issues are resolved.

The *Cursor AI thinks that* the codebase is well-structured, thoroughly tested, and documented, providing a solid foundation for future development. The recent work on survey analysis has provided valuable insights into the Rubin Observatory's observation patterns and will inform future feature development.

The Cursor AI is overeager to add code without adequate human review. It is important to **Add more robust AI coding methodology rules**

First of all, Neal thinks significant **Human Review of goals, core requirement spec, tests, and code** is necessary.
