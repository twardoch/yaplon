# Changelog

All notable changes to the "yaplon" project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Comprehensive Test Suite**: Added extensive test coverage for all conversion paths with over 20 new test files covering JSON, YAML, PLIST, XML, and CSV conversions.
- **JSON Input Enhancement**: Yaplon now supports parsing JSON files that include C-style comments (both `// line` and `/* block */`) and trailing commas in objects and arrays, similar to JSON5. (Integrated `sanitize_json` from `yaplon.file_strip.json` into the `ojson.read_json` pipeline).
- **Project Management**: Created `PLAN.md`, `TODO.md`, and `CHANGELOG.md` for better project organization and tracking.
- **Development Documentation**: Added development setup instructions and expanded README with detailed usage examples.

### Changed
- **Output Stream Handling**: Standardized output stream management across all writer functions for consistency and reliability.
- **CLI Refactoring**: Modernized command-line interface implementation with improved error handling and type consistency.
- **Comments Processing**: Refactored `yaplon.file_strip.comments.Comments` class to use static methods for comment stripping functions (`_cpp`, `_python`) and a dictionary-based style registry for improved clarity and to resolve a `TypeError` during comment stripping.
- **Binary Data Handling**: Enhanced binary data preservation and conversion across formats with consistent base64 encoding/decoding.

### Fixed
- **Python 3.10 Compatibility**: Fixed compatibility issues for Python 3.10+.
- **Unicode Output**: Switched to proper Unicode output in JSON format.
- **Type Handling**: Improved type conversion consistency across different format conversions.

## [1.6.0] - 2025-06-25

### Changed
- **Python 3.10 Compatibility**: Applied fixes for Python 3.10 compatibility issues.

## [1.5.7] - 2025-06-25  

### Changed
- **JSON Unicode Output**: Switched to Unicode output in JSON instead of ASCII escaping.
- **Code Refactoring**: General code cleanup and refactoring for better maintainability.

## [1.5.6]

### Changed
- Initial switch to Unicode output in JSON with refactoring improvements.
