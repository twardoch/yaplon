# Changelog

All notable changes to the "yaplon" project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project scaffolding:
    - Created `PLAN.md` for project planning.
    - Created `TODO.md` for task tracking.
    - Created `CHANGELOG.md` (this file) for documenting changes.
- **JSON Input Enhancement**: Yaplon now supports parsing JSON files that include C-style comments (both `// line` and `/* block */`) and trailing commas in objects and arrays, similar to JSON5. (Integrated `sanitize_json` from `yaplon.file_strip.json` into the `ojson.read_json` pipeline).
- Added tests for JSON sanitization features in `tests/test_json_sanitization.py`.

### Changed
- Refactored `yaplon.file_strip.comments.Comments` class to use static methods for comment stripping functions (`_cpp`, `_python`) and a dictionary-based style registry for improved clarity and to resolve a `TypeError` during comment stripping.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

---

*Older entries will be added below as development progresses.*
