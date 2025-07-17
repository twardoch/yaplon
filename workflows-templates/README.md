# GitHub Actions Workflows

This directory contains GitHub Actions workflow templates for the yaplon project.

## Quick Setup

```bash
# Copy workflows to your repository
mkdir -p .github/workflows
cp workflows-templates/*.yml .github/workflows/
```

## Required Secrets

Configure these secrets in your GitHub repository settings:

- **PYPI_TOKEN**: Your PyPI API token for publishing packages
- **CODECOV_TOKEN**: (Optional) For code coverage reporting

## Workflows

### `ci.yml` - Continuous Integration
- **Triggers**: Push to master/main/develop branches
- **Purpose**: Test code quality and compatibility
- **Features**: Multi-platform testing, linting, security scanning

### `release.yml` - Release Automation  
- **Triggers**: Git tags matching `v*` pattern
- **Purpose**: Automated releases with PyPI publishing
- **Features**: Package building, binary creation, GitHub releases

### `pr.yml` - Pull Request Validation
- **Triggers**: Pull requests to main branches
- **Purpose**: Fast feedback for contributors
- **Features**: Quick tests, build verification

## Usage

1. Copy workflows to `.github/workflows/`
2. Configure repository secrets
3. Push changes or create tags to trigger workflows

For detailed setup instructions, see [GITHUB_SETUP.md](../GITHUB_SETUP.md).