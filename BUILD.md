# Build and Release Guide

This document describes how to build, test, and release yaplon using the modern build system.

## Quick Start

```bash
# Development setup
make install-dev

# Run tests
make test

# Build package
make build

# Build binaries
make build-binary

# Complete development workflow
make dev
```

## Build System Overview

The yaplon project uses a modern build system with the following components:

- **Version Management**: Git tag-based semantic versioning
- **Build Scripts**: Python-based build and release automation
- **Testing**: Comprehensive pytest-based test suite
- **CI/CD**: GitHub Actions workflows for automated testing and releases
- **Binary Distribution**: PyInstaller-based cross-platform binaries

## Version Management

### Semantic Versioning

The project follows [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backwards compatible manner
- **PATCH**: Backwards compatible bug fixes

### Version Sources

Version information is automatically derived from:

1. **Git Tags**: Primary source (e.g., `v1.2.3`)
2. **Fallback**: Version in `yaplon/__init__.py`

### Version Commands

```bash
# Check current version
python -c "import yaplon; print(yaplon.__version__)"

# Check version consistency
make version-check

# Manual version management
python yaplon/_version.py
```

## Build Scripts

### Build Script (`scripts/build.py`)

Comprehensive build automation:

```bash
# Install dependencies
python scripts/build.py --install-dev

# Format code
python scripts/build.py --format

# Run linting
python scripts/build.py --lint

# Run tests
python scripts/build.py --test
python scripts/build.py --test-fast
python scripts/build.py --test-coverage

# Build package
python scripts/build.py --build

# Build binary
python scripts/build.py --build-binary

# Complete build process
python scripts/build.py --all

# CI workflow
python scripts/build.py --ci
```

### Release Script (`scripts/release.py`)

Automated release management:

```bash
# Patch release (1.2.3 -> 1.2.4)
python scripts/release.py --bump patch --message "Bug fixes"

# Minor release (1.2.3 -> 1.3.0)
python scripts/release.py --bump minor --message "New features"

# Major release (1.2.3 -> 2.0.0)
python scripts/release.py --bump major --message "Breaking changes"

# Specific version
python scripts/release.py --version 1.5.0 --message "Special release"

# Test PyPI release
python scripts/release.py --bump patch --test-pypi --message "Test release"

# Dry run
python scripts/release.py --bump patch --message "Test" --dry-run
```

### Binary Build Script (`scripts/build_binaries.py`)

Cross-platform binary building:

```bash
# Build binary for current platform
python scripts/build_binaries.py

# Build with testing
python scripts/build_binaries.py --test

# Build with installer
python scripts/build_binaries.py --installer

# Custom output directory
python scripts/build_binaries.py --output ./binaries

# Use custom spec file
python scripts/build_binaries.py --spec yaplon.spec
```

## Testing

### Test Structure

```
tests/
├── __init__.py
├── helpers.py
├── test_version.py          # Version management tests
├── test_integration.py      # Integration tests
├── test_cli.py             # CLI tests
├── test_json_sanitization.py # JSON sanitization tests
└── test_*.py               # Format conversion tests
```

### Test Commands

```bash
# Run all tests
pytest

# Run fast tests only
pytest -m "not slow"

# Run slow tests only
pytest -m "slow"

# Run with coverage
pytest --cov=yaplon --cov-report=html

# Run specific test file
pytest tests/test_version.py

# Run specific test
pytest tests/test_version.py::TestVersionManagement::test_get_version_from_git_tags
```

### Test Configuration

- **pytest.ini**: Test configuration
- **Coverage**: 80% minimum coverage requirement
- **Markers**: `slow` and `integration` test markers
- **Parallel**: Support for parallel test execution

## Binary Distribution

### PyInstaller Configuration

- **Spec File**: `yaplon.spec` for advanced build configuration
- **Cross-Platform**: Support for Windows, macOS, and Linux
- **Optimization**: UPX compression and size optimization
- **Dependencies**: Automatic dependency detection

### Binary Naming

Binaries are named using the pattern:
```
yaplon-{version}-{platform}-{arch}[.exe]
```

Examples:
- `yaplon-1.6.0-linux-x64`
- `yaplon-1.6.0-windows-x64.exe`
- `yaplon-1.6.0-macos-x64`

### Binary Testing

Built binaries are automatically tested for:
- Basic functionality
- Help command
- Version reporting
- Core conversion features

## CI/CD Workflows

### GitHub Actions Setup

**Important**: Due to GitHub App permissions, workflow files are provided as templates in `workflows-templates/`. See [GITHUB_SETUP.md](./GITHUB_SETUP.md) for detailed setup instructions.

### Quick Setup:
```bash
# Copy workflows to activate them
mkdir -p .github/workflows
cp workflows-templates/*.yml .github/workflows/

# Configure secrets in GitHub repository settings
# - PYPI_TOKEN: For PyPI publishing
# - CODECOV_TOKEN: For coverage reporting (optional)
```

### GitHub Actions Workflows

1. **CI Workflow** (`workflows-templates/ci.yml`)
   - Triggered on pushes to main branches
   - Multi-platform testing (Ubuntu, Windows, macOS)
   - Python version matrix (3.9, 3.10, 3.11, 3.12)
   - Linting, formatting, and security checks
   - Coverage reporting

2. **Release Workflow** (`workflows-templates/release.yml`)
   - Triggered on git tags (`v*`)
   - Full test suite across all platforms
   - Package building
   - Binary building for all platforms
   - PyPI publishing
   - GitHub release creation

3. **Pull Request Workflow** (`workflows-templates/pr.yml`)
   - Triggered on pull requests
   - Fast test subset
   - Code quality checks
   - Build verification

### CI Configuration

- **Matrix Strategy**: Optimized for speed vs. coverage
- **Caching**: Pip dependencies cached for faster builds
- **Artifacts**: Build artifacts uploaded and shared between jobs
- **Security**: Automated security scanning with safety and bandit

For complete setup instructions, see [GITHUB_SETUP.md](./GITHUB_SETUP.md).

## Development Workflow

### Local Development

```bash
# Initial setup
git clone https://github.com/twardoch/yaplon.git
cd yaplon
make install-dev

# Development cycle
make dev  # format + lint + test-fast

# Before committing
make ci   # full CI workflow locally
```

### Release Process

1. **Prepare Release**
   ```bash
   # Update CHANGELOG.md
   # Commit changes
   git add .
   git commit -m "Prepare release"
   ```

2. **Create Release**
   ```bash
   # Patch release
   python scripts/release.py --bump patch --message "Bug fixes and improvements"
   
   # Or minor/major release
   python scripts/release.py --bump minor --message "New features"
   ```

3. **Automated Process**
   - Version is bumped in code
   - Git tag is created
   - Code is pushed to GitHub
   - GitHub Actions builds and releases
   - PyPI package is published
   - GitHub release is created with binaries

### Troubleshooting

#### Version Issues

```bash
# Check version consistency
make version-check

# Reset version from git tag
python -c "from yaplon._version import set_version_in_init, get_version; set_version_in_init(get_version())"
```

#### Build Issues

```bash
# Clean build artifacts
make clean

# Reinstall dependencies
make install-dev

# Check system requirements
python --version  # Should be 3.9+
pip --version
```

#### Test Issues

```bash
# Run tests with verbose output
pytest -v

# Run specific failing test
pytest tests/test_specific.py::test_function -v -s

# Update test dependencies
pip install -U pytest pytest-cov
```

## Makefile Reference

The Makefile provides convenient shortcuts:

```bash
make clean           # Clean build artifacts
make install         # Install production dependencies
make install-dev     # Install development dependencies  
make lint            # Run linting
make format          # Format code
make test            # Run all tests
make test-fast       # Run fast tests only
make test-slow       # Run slow tests only
make test-coverage   # Run tests with coverage
make build           # Build package
make build-binary    # Build binary
make release         # Release to PyPI
make version-check   # Check version consistency
make dev             # Development workflow
make ci              # CI workflow
```

## Migration from Legacy System

The old `dist.sh` script is deprecated. To migrate:

### Old Way
```bash
./dist.sh "Release message"
```

### New Way
```bash
python scripts/release.py --bump patch --message "Release message"
```

The new system provides:
- Better error handling
- Automated testing
- Version validation
- Multi-platform support
- GitHub integration
- Binary distribution

## Requirements

### System Requirements
- Python 3.9+
- Git
- Make (optional, for convenience)

### Python Dependencies
- Production: See `requirements.txt`
- Development: See `requirements-dev.txt`

### Optional Tools
- GitHub CLI (`gh`) for GitHub integration
- PyInstaller for binary building
- Twine for PyPI publishing

## Support

For issues with the build system:
1. Check this documentation
2. Check GitHub Actions logs
3. File an issue on GitHub
4. Check the existing test suite for examples