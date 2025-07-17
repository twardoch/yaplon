# Usage Guide

Quick reference for common yaplon development and release tasks.

## Development Setup

```bash
# Clone and setup
git clone https://github.com/twardoch/yaplon.git
cd yaplon
make install-dev

# Verify installation
python -c "import yaplon; print(yaplon.__version__)"
```

## Daily Development

```bash
# Format code
make format

# Run linting  
make lint

# Run fast tests
make test-fast

# Complete dev workflow
make dev
```

## Building

```bash
# Build Python package
make build

# Build binary for current platform
make build-binary

# Build with custom script
python scripts/build.py --all
```

## Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run specific test
pytest tests/test_version.py
```

## Releasing

### Patch Release (1.2.3 → 1.2.4)
```bash
python scripts/release.py --bump patch --message "Bug fixes"
```

### Minor Release (1.2.3 → 1.3.0)
```bash
python scripts/release.py --bump minor --message "New features"
```

### Major Release (1.2.3 → 2.0.0)
```bash
python scripts/release.py --bump major --message "Breaking changes"
```

### Custom Version
```bash
python scripts/release.py --version 1.5.0 --message "Special release"
```

### Test Release
```bash
python scripts/release.py --bump patch --test-pypi --message "Test"
```

## Binary Distribution

```bash
# Build binary for current platform
python scripts/build_binaries.py

# Build with testing
python scripts/build_binaries.py --test

# Build with installer script
python scripts/build_binaries.py --installer
```

## CI/CD

### GitHub Actions Setup
```bash
# Quick setup
./activate-workflows.sh

# Manual setup
mkdir -p .github/workflows
cp workflows-templates/*.yml .github/workflows/
```

### Local CI Simulation
```bash
make ci
```

### GitHub Actions
- Push to master → Full CI
- Create tag v1.2.3 → Release workflow
- Open PR → PR workflow

See [GITHUB_SETUP.md](./GITHUB_SETUP.md) for detailed setup instructions.

## Troubleshooting

### Version Issues
```bash
make version-check
```

### Build Issues
```bash
make clean
make install-dev
```

### Test Issues
```bash
pytest -v --tb=short
```

## Quick Commands

| Task | Command |
|------|---------|
| Setup | `make install-dev` |
| Format | `make format` |
| Lint | `make lint` |
| Test | `make test` |
| Build | `make build` |
| Binary | `make build-binary` |
| Release | `python scripts/release.py --bump patch --message "msg"` |
| Clean | `make clean` |
| Dev workflow | `make dev` |
| CI workflow | `make ci` |
| Activate workflows | `./activate-workflows.sh` |