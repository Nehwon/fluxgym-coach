# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Documentation**:
  - Comprehensive update of all documentation files
  - Improved README with better project structure and setup instructions
  - Added contribution guidelines and project status
  - Enhanced module documentation

### Changed
- **Code Quality**:
  - Improved error messages and logging
  - Better type hints throughout the codebase
  - Updated development dependencies

## [0.2.1] - 2024-06-24

### Fixed
- **Cache Handling**:
  - Fixed cache detection for batch processing
  - Improved cache key generation for better reliability
  - Added detailed logging for cache operations
- **Batch Processing**:
  - Fixed result aggregation in `upscale_batch` method
  - Improved error handling for mixed cached/uncached images
  - Fixed HTTP 422 error in batch API calls

### Added
- **Documentation**:
  - Added DECISIONS.md for tracking technical decisions
  - Updated project documentation structure
  - Improved inline code documentation

### Changed
- **Code Quality**:
  - Refactored cache management code
  - Improved error messages and logging
  - Enhanced code maintainability

## [0.2.0] - 2024-06-23

## [0.1.0] - 2025-06-23

### Added
- **Tests and Benchmarks**:
  - Benchmark script to measure cache performance
  - Test image generation with gradients and text
  - Execution time measurement with and without cache
  - Detailed statistics (average, min, max, standard deviation)
  - Support for multiple runs for reliable results

### Changed
- **Documentation**:
  - Merged `PROTOCOLE.md` and `PROTOCOLE_RACINE.md` into a single file
  - Updated `PROJET.md` with current development plan
  - Added contribution guidelines in `PROTOCOLE_RACINE.md`
  - Improved test documentation

### Fixed
- **Cache**:
  - Fixed modified file detection
  - Improved error handling during cache read/write operations
  - Automatic cleanup of invalid cache entries

### Technical Changes
- Migrated to Python 3.8+
- Added dependencies: `numpy`, `Pillow` for tests
- Updated development dependencies

## [0.0.1] - 2025-06-22

### Added
- **Cache System**:
  - New `ImageCache` class to manage processed image caching
  - Cache integration in `upscale_batch` method
  - File hash verification to detect modifications
  - Command-line options to control cache (`--no-cache`, `--force-reprocess`, `--cache-dir`)
  - Cache support to avoid reprocessing unchanged images
  - Processing parameters in cache key
  - `xxhash` for fast file hashing

- **Batch Processing**:
  - New `upscale_batch` method to process multiple images in one request
  - Support for glob patterns in file selection
  - Granular error handling (one failing image doesn't block others)
  - Detailed progress display
  - Option to disable automatic colorization
  - Configurable batch size

- **Automatic Colorization**:
  - Smart black and white image detection
  - Automatic colorization via Stable Diffusion API
  - Customizable colorization parameters
  - Fallback to B/W mode on colorization failure

- **Unit Tests**:
  - 100% coverage for `image_enhancement.py` module
  - Tests for `upscale_batch` method
  - Tests for error handling in batch processing
  - Fixtures for image tests
  - Mocks for API calls with `requests`
  - API error handling tests
  - Black and white detection tests
  - Alpha channel preprocessing tests
  - Unsupported format handling tests
  - Parameter validation tests

- **Configuration**:
  - mypy setup for type checking
  - pytest configuration for code coverage
  - Integration with code quality tools

### Improvements
- Better memory management in batch processing
- Forced PNG conversion for output images
- Improved black and white image detection
- Updated documentation with new features
- Enhanced command-line interface with more options

### Fixed
- **Bugs**:
  - Fixed memory leaks in batch processing
  - Fixed non-proportional resizing issue
  - Fixed output format not being respected
  - Improved error handling and logging

## [Unreleased] - 2025-06-21

### Added
- Stable Diffusion Forge integration for image enhancement
  - Upscaling with different scale factors
  - Automatic black and white image detection
  - Automatic image format conversion (WebP, JPG, PNG, etc.)
  - Smart resizing with aspect ratio preservation
- New `image_enhancement.py` module
- Complete API documentation for image enhancement
- Unit tests for new features

### Security
- Updated vulnerable dependencies
- Improved input validation
- Enhanced error handling

### Performance
- Optimized memory usage
- Reduced test execution time
- Improved interface responsiveness

## [0.2.0] - 2025-06-20

### Changed
- Refactored `metadata.py` to use content hashing for metadata filenames
- Improved metadata deduplication for identical images
- Updated tests to reflect behavior changes
- Created `feature/fluxgym-coach` branch for development

## [0.1.0] - 2025-06-20

### Added
- Initial project structure
- Image processing module with hash-based renaming
- EXIF and basic metadata extraction module
- Basic command-line interface (CLI)
- Configuration system
- Validation utilities
- Basic documentation

---
*© 2024 Nehwon - All Rights Reserved*
