# GitHub Setup Guide

This guide explains how to set up the GitHub Actions workflows for the yaplon project.

## Overview

Due to GitHub App permissions, the workflow files are provided as templates in the `workflows-templates/` directory. You need to manually copy them to `.github/workflows/` to activate them.

## Setup Steps

### 1. Create Workflows Directory

```bash
mkdir -p .github/workflows
```

### 2. Copy Workflow Templates

```bash
cp workflows-templates/ci.yml .github/workflows/
cp workflows-templates/release.yml .github/workflows/
cp workflows-templates/pr.yml .github/workflows/
```

### 3. Configure Repository Secrets

Go to your GitHub repository settings > Secrets and variables > Actions, and add:

#### Required Secrets:
- `PYPI_TOKEN`: Your PyPI API token for publishing packages
  - Get from: https://pypi.org/manage/account/token/
  - Scope: Entire account or specific project

#### Optional Secrets:
- `CODECOV_TOKEN`: For code coverage reporting
  - Get from: https://codecov.io/
  - Used for coverage reports in pull requests

### 4. Configure Repository Settings

#### Branch Protection (Recommended):
1. Go to Settings > Branches
2. Add rule for `master` branch:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select required status checks: `test`, `build-test`, `security`

#### Actions Permissions:
1. Go to Settings > Actions > General
2. Set "Actions permissions" to "Allow all actions and reusable workflows"
3. Set "Workflow permissions" to "Read and write permissions"

### 5. Test the Setup

#### Test CI Workflow:
```bash
# Make a small change and push to master
git add .
git commit -m "Test CI workflow"
git push origin master
```

#### Test Release Workflow:
```bash
# Create and push a tag
git tag v1.6.1
git push origin v1.6.1
```

#### Test PR Workflow:
```bash
# Create a feature branch and open a PR
git checkout -b test-pr
git push origin test-pr
# Then open PR on GitHub
```

## Workflow Overview

### CI Workflow (`.github/workflows/ci.yml`)
- **Triggers**: Push to master/main/develop branches
- **Actions**: 
  - Multi-platform testing (Ubuntu, Windows, macOS)
  - Python version matrix (3.9, 3.10, 3.11, 3.12)
  - Linting and formatting checks
  - Security scanning
  - Coverage reporting
  - Package building

### Release Workflow (`.github/workflows/release.yml`)
- **Triggers**: Git tags matching `v*` pattern
- **Actions**:
  - Full test suite across all platforms
  - Package building (wheel and sdist)
  - Binary building for all platforms
  - PyPI publishing
  - GitHub release creation with assets

### PR Workflow (`.github/workflows/pr.yml`)
- **Triggers**: Pull requests to master/main/develop
- **Actions**:
  - Fast test subset for quick feedback
  - Code quality checks
  - Build verification
  - PR information reporting

## Release Process

### Using the Release Script:
```bash
# Patch release (1.2.3 → 1.2.4)
python scripts/release.py --bump patch --message "Bug fixes"

# Minor release (1.2.3 → 1.3.0)
python scripts/release.py --bump minor --message "New features"

# Major release (1.2.3 → 2.0.0)
python scripts/release.py --bump major --message "Breaking changes"
```

### Manual Release:
```bash
# Update version and create tag
git tag v1.6.1
git push origin v1.6.1
```

## Troubleshooting

### Common Issues:

#### 1. Workflow Not Running
- Check if workflows are in `.github/workflows/` directory
- Verify repository Actions are enabled
- Check branch protection rules

#### 2. PyPI Publishing Fails
- Verify `PYPI_TOKEN` secret is set correctly
- Check token permissions
- Ensure package name doesn't conflict

#### 3. Binary Build Fails
- Check PyInstaller compatibility
- Verify all dependencies are included
- Check platform-specific requirements

#### 4. Tests Fail
- Run tests locally first: `make test`
- Check dependency versions
- Verify Python version compatibility

### Debugging Workflows:

1. **Check workflow status**: Go to Actions tab in GitHub
2. **View logs**: Click on failed workflow run
3. **Local testing**: Use `make ci` to simulate CI locally
4. **Test specific components**: Use individual make targets

## Manual Setup Alternative

If you prefer to set up workflows manually:

### 1. Create Basic CI:
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: make ci
```

### 2. Create Basic Release:
```yaml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: make build
    - run: python -m twine upload dist/*
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

## Security Considerations

### Token Security:
- Use repository secrets for sensitive data
- Limit token permissions to minimum required
- Rotate tokens regularly

### Workflow Security:
- Review workflow changes in PRs
- Use official actions when possible
- Pin action versions for security

### Release Security:
- Verify release artifacts before publishing
- Use signed commits for releases
- Monitor for unauthorized changes

## Support

For issues with the GitHub setup:
1. Check this documentation
2. Review workflow logs in GitHub Actions
3. Test locally with `make ci`
4. File an issue with workflow logs attached

## Next Steps

After setting up the workflows:
1. Test the CI by pushing a small change
2. Create a test release with a patch version
3. Monitor the Actions tab for workflow results
4. Update documentation based on your experience