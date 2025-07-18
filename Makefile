# Makefile for yaplon development

.PHONY: all clean install install-dev lint format test test-fast test-slow test-coverage build build-binary release version-check

# Variables
PYTHON = python3
PIP = pip3
PACKAGE_NAME = yaplon

# Default target
all: install-dev lint test

# Clean up build artifacts and virtual environment
clean:
	rm -rf build dist *.egg-info .pytest_cache .tox venv __pycache__ yaplon/__pycache__ tests/__pycache__
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf htmlcov coverage.xml .coverage

# Install production dependencies
install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

# Install development dependencies
install-dev: install
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .[dev]

# Lint the code
lint:
	flake8 $(PACKAGE_NAME) tests
	black --check $(PACKAGE_NAME) tests setup.py

# Format the code
format:
	black $(PACKAGE_NAME) tests setup.py

# Run all tests
test: install-dev
	$(PYTHON) -m pytest

# Run fast tests only
test-fast: install-dev
	$(PYTHON) -m pytest -m "not slow"

# Run slow tests only
test-slow: install-dev
	$(PYTHON) -m pytest -m "slow"

# Run tests with coverage
test-coverage: install-dev
	$(PYTHON) -m pytest --cov=$(PACKAGE_NAME) --cov-report=html --cov-report=term

# Check version consistency
version-check:
	@echo "Package version: $$($(PYTHON) -c 'import $(PACKAGE_NAME); print($(PACKAGE_NAME).__version__)')"
	@echo "Git tag version: $$(git describe --tags --abbrev=0 2>/dev/null || echo 'No tags')"

# Build the package
build: clean version-check
	$(PYTHON) setup.py sdist bdist_wheel

# Build binary with PyInstaller
build-binary: install-dev
	pyinstaller --onefile --name=$(PACKAGE_NAME) $(PACKAGE_NAME)/__main__.py

# Release the package to PyPI
release: build test
	twine upload dist/*

# Development workflow
dev: install-dev format lint test-fast

# CI workflow
ci: install-dev lint test-coverage
