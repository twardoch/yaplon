#!/usr/bin/env python3
# this_file: scripts/build.py

"""
Build script for yaplon package.
Handles version management, building, and testing.
"""

import argparse
import subprocess
import sys
import os
import shutil
from pathlib import Path
from typing import Optional

# Add parent directory to path so we can import yaplon
sys.path.insert(0, str(Path(__file__).parent.parent))

from yaplon._version import get_version, set_version_in_init


def run_command(cmd: list, cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def clean_build_artifacts(repo_root: Path) -> None:
    """Clean build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    artifacts = [
        "build", "dist", "*.egg-info", ".pytest_cache", ".tox", 
        "venv", "__pycache__", "yaplon/__pycache__", "tests/__pycache__",
        "htmlcov", "coverage.xml", ".coverage"
    ]
    
    for pattern in artifacts:
        for path in repo_root.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed directory: {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed file: {path}")
    
    # Clean pyc files
    for pyc_file in repo_root.rglob("*.pyc"):
        pyc_file.unlink()
    
    # Clean __pycache__ directories
    for pycache_dir in repo_root.rglob("__pycache__"):
        if pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)


def install_dependencies(repo_root: Path, dev: bool = False) -> None:
    """Install dependencies."""
    print("📦 Installing dependencies...")
    
    # Upgrade pip
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install production dependencies
    requirements_file = repo_root / "requirements.txt"
    if requirements_file.exists():
        run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
    
    # Install development dependencies
    if dev:
        dev_requirements = repo_root / "requirements-dev.txt"
        if dev_requirements.exists():
            run_command([sys.executable, "-m", "pip", "install", "-r", str(dev_requirements)])
    
    # Install package in editable mode
    setup_py = repo_root / "setup.py"
    if setup_py.exists():
        if dev:
            run_command([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], cwd=repo_root)
        else:
            run_command([sys.executable, "-m", "pip", "install", "-e", "."], cwd=repo_root)


def run_tests(repo_root: Path, fast: bool = False, coverage: bool = False) -> bool:
    """Run tests."""
    print("🧪 Running tests...")
    
    cmd = [sys.executable, "-m", "pytest"]
    
    if fast:
        cmd.extend(["-m", "not slow"])
    
    if coverage:
        cmd.extend([
            "--cov=yaplon", 
            "--cov-report=html", 
            "--cov-report=term",
            "--cov-report=xml"
        ])
    
    try:
        result = run_command(cmd, cwd=repo_root)
        print("✅ Tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Tests failed!")
        print(e.stdout)
        print(e.stderr)
        return False


def run_lint(repo_root: Path) -> bool:
    """Run linting."""
    print("🔍 Running linting...")
    
    try:
        # Run flake8
        run_command([sys.executable, "-m", "flake8", "yaplon", "tests"], cwd=repo_root)
        
        # Run black check
        run_command([sys.executable, "-m", "black", "--check", "yaplon", "tests", "setup.py"], cwd=repo_root)
        
        print("✅ Linting passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Linting failed!")
        print(e.stdout)
        print(e.stderr)
        return False


def format_code(repo_root: Path) -> None:
    """Format code with black."""
    print("🎨 Formatting code...")
    
    try:
        run_command([sys.executable, "-m", "black", "yaplon", "tests", "setup.py"], cwd=repo_root)
        print("✅ Code formatted!")
    except subprocess.CalledProcessError as e:
        print("❌ Formatting failed!")
        print(e.stdout)
        print(e.stderr)


def check_version(repo_root: Path) -> None:
    """Check version consistency."""
    print("🔢 Checking version consistency...")
    
    package_version = get_version()
    
    # Check git tags
    try:
        result = run_command(["git", "describe", "--tags", "--abbrev=0"], cwd=repo_root, check=False)
        if result.returncode == 0:
            git_version = result.stdout.strip().lstrip('v')
            print(f"Package version: {package_version}")
            print(f"Git tag version: {git_version}")
            
            if package_version != git_version:
                print("⚠️  Version mismatch detected!")
        else:
            print(f"Package version: {package_version}")
            print("Git tag version: No tags found")
    except subprocess.CalledProcessError:
        print(f"Package version: {package_version}")
        print("Git tag version: Unable to check")


def build_package(repo_root: Path) -> None:
    """Build the package."""
    print("📦 Building package...")
    
    # Clean first
    clean_build_artifacts(repo_root)
    
    # Check version
    check_version(repo_root)
    
    # Build
    run_command([sys.executable, "setup.py", "sdist", "bdist_wheel"], cwd=repo_root)
    
    print("✅ Package built successfully!")
    
    # Show built files
    dist_dir = repo_root / "dist"
    if dist_dir.exists():
        print("Built files:")
        for file in dist_dir.iterdir():
            print(f"  - {file.name}")


def build_binary(repo_root: Path) -> None:
    """Build binary with PyInstaller."""
    print("🔧 Building binary...")
    
    main_file = repo_root / "yaplon" / "__main__.py"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name=yaplon",
        str(main_file)
    ]
    
    try:
        run_command(cmd, cwd=repo_root)
        print("✅ Binary built successfully!")
        
        # Show built binary
        dist_dir = repo_root / "dist"
        binary_file = dist_dir / "yaplon"
        if binary_file.exists():
            print(f"Binary location: {binary_file}")
            print(f"Binary size: {binary_file.stat().st_size / 1024:.1f} KB")
    except subprocess.CalledProcessError as e:
        print("❌ Binary build failed!")
        print(e.stdout)
        print(e.stderr)


def main():
    """Main build script."""
    parser = argparse.ArgumentParser(description="Build script for yaplon")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--install-dev", action="store_true", help="Install development dependencies")
    parser.add_argument("--format", action="store_true", help="Format code")
    parser.add_argument("--lint", action="store_true", help="Run linting")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--test-fast", action="store_true", help="Run fast tests only")
    parser.add_argument("--test-coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--version-check", action="store_true", help="Check version consistency")
    parser.add_argument("--build", action="store_true", help="Build package")
    parser.add_argument("--build-binary", action="store_true", help="Build binary")
    parser.add_argument("--all", action="store_true", help="Run complete build process")
    parser.add_argument("--ci", action="store_true", help="Run CI workflow")
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    
    if args.clean:
        clean_build_artifacts(repo_root)
    
    if args.install:
        install_dependencies(repo_root, dev=False)
    
    if args.install_dev:
        install_dependencies(repo_root, dev=True)
    
    if args.format:
        format_code(repo_root)
    
    if args.lint:
        if not run_lint(repo_root):
            sys.exit(1)
    
    if args.test:
        if not run_tests(repo_root):
            sys.exit(1)
    
    if args.test_fast:
        if not run_tests(repo_root, fast=True):
            sys.exit(1)
    
    if args.test_coverage:
        if not run_tests(repo_root, coverage=True):
            sys.exit(1)
    
    if args.version_check:
        check_version(repo_root)
    
    if args.build:
        build_package(repo_root)
    
    if args.build_binary:
        build_binary(repo_root)
    
    if args.all:
        install_dependencies(repo_root, dev=True)
        format_code(repo_root)
        if not run_lint(repo_root):
            sys.exit(1)
        if not run_tests(repo_root):
            sys.exit(1)
        build_package(repo_root)
        print("🎉 Complete build process finished!")
    
    if args.ci:
        install_dependencies(repo_root, dev=True)
        if not run_lint(repo_root):
            sys.exit(1)
        if not run_tests(repo_root, coverage=True):
            sys.exit(1)
        print("🎉 CI workflow completed!")


if __name__ == "__main__":
    main()