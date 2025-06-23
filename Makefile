# Makefile for yaplon development

.PHONY: all clean install lint format test build release

# Variables
PYTHON = python3
PIP = pip3
PACKAGE_NAME = yaplon

# Default target
all: install lint test

# Clean up build artifacts and virtual environment
clean:
	rm -rf build dist *.egg-info .pytest_cache .tox venv __pycache__ yaplon/__pycache__ tests/__pycache__

# Install dependencies
install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .[dev]

# Lint the code
lint:
	flake8 $(PACKAGE_NAME) tests
	black --check $(PACKAGE_NAME) tests setup.py

# Format the code
format:
	black $(PACKAGE_NAME) tests setup.py

# Run tests
test:
	$(PYTHON) -m pytest

# Build the package
build:
	$(PYTHON) setup.py sdist bdist_wheel

# Release the package to PyPI
release: build
	twine upload dist/*
