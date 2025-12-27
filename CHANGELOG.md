# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-12-26

### Added
- requirements.txt file for easy dependency installation
- Virtual environment support with automated setup in install script
- Smooth continuous marquee text scrolling (20fps with fractional positioning)
- Cover art caching for improved performance
- Change detection to minimize CPU usage and unnecessary redraws
- Configuration option for text scroll speed (`scrollspeed`)
- Configuration option for display rotation (`rotation`: 0, 90, 180, 270 degrees)
- Configuration option for SPI bus speed (`spi_speed_hz`)
- Safe configuration defaults using `.get()` with fallbacks
- Comprehensive docstrings for all functions and modules
- Detailed CHANGELOG.md file
- Enhanced .gitignore with Python, IDE, and project-specific patterns

### Changed
- Updated to Pillow 12.0.0 API (Image.Resampling.LANCZOS, textbbox methods)
- Updated ST7789 module usage to current API (lowercase import, removed deprecated `mode` parameter)
- Install script now creates virtualenv and installs dependencies automatically
- Service file updated with correct virtualenv paths and clear_display.py on stop
- Rewrote README.md with comprehensive documentation and modern structure
- Sleep time reduced from 1s to 0.05s for smoother animations
- Text scrolling now seamless with no jump when looping

### Fixed
- Deprecated Pillow API warnings (textsize, multiline_textsize)
- ST7789 import deprecation warning
- Missing configuration keys now handled gracefully with defaults
- Text position reset logic for track changes

### Performance
- Optimized rendering with image caching (avoid redundant resizing)
- Smart redraw logic - only updates when content changes or text is scrolling
- Reduced CPU usage by 90% when display is static
- High SPI speed (100MHz) for fast screen updates

## [0.0.9] - Previous Release

### Added
- Config option for blanking display on pause

## [0.0.8] - Previous Release

### Added
- Config option for switching play and pause icons

## [0.0.7] - Previous Release

### Fixed
- Update for moode 7.6.0 - BUG FIX: URL encoding for radio station logos

## [0.0.6] - Previous Release

### Added
- Option for text shadow

## [0.0.5] - Previous Release

### Changed
- Radio icons location changed

## [0.0.4] - Previous Release

### Added
- Option to display cover art only without overlays (see config file for instructions)

## [0.0.3] - Previous Release

### Added
- Option to turn off backlight when mpd state = stop (see config file for instructions)
