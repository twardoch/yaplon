#!/usr/bin/env python3
# this_file: scripts/release.py

"""
Release script for yaplon package.
Handles version tagging, building, and releasing.
"""

import argparse
import subprocess
import sys
import os
import re
from pathlib import Path
from typing import Optional

# Add parent directory to path so we can import yaplon
sys.path.insert(0, str(Path(__file__).parent.parent))

from yaplon._version import get_version, set_version_in_init


def run_command(cmd: list, cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def validate_version(version: str) -> bool:
    """Validate semver version format."""
    pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    return bool(re.match(pattern, version))


def get_next_version(current_version: str, bump_type: str) -> str:
    """Get next version based on bump type."""
    if not validate_version(current_version):
        raise ValueError(f"Invalid current version: {current_version}")
    
    # Parse current version
    parts = current_version.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def check_git_status(repo_root: Path) -> bool:
    """Check if git working directory is clean."""
    try:
        result = run_command(["git", "status", "--porcelain"], cwd=repo_root)
        return len(result.stdout.strip()) == 0
    except subprocess.CalledProcessError:
        return False


def create_git_tag(repo_root: Path, version: str, message: str) -> None:
    """Create git tag for version."""
    tag_name = f"v{version}"
    
    # Check if tag already exists
    try:
        run_command(["git", "tag", "-l", tag_name], cwd=repo_root)
        result = run_command(["git", "tag", "-l", tag_name], cwd=repo_root, check=False)
        if result.stdout.strip():
            print(f"⚠️  Tag {tag_name} already exists!")
            return
    except subprocess.CalledProcessError:
        pass
    
    # Create tag
    run_command(["git", "tag", "-a", tag_name, "-m", message], cwd=repo_root)
    print(f"✅ Created tag {tag_name}")


def push_to_remote(repo_root: Path, push_tags: bool = True) -> None:
    """Push changes to remote repository."""
    # Push commits
    run_command(["git", "push"], cwd=repo_root)
    
    # Push tags
    if push_tags:
        run_command(["git", "push", "--tags"], cwd=repo_root)
    
    print("✅ Pushed to remote repository")


def build_and_test(repo_root: Path) -> bool:
    """Build and test the package."""
    print("🔧 Building and testing...")
    
    # Import build script
    build_script = repo_root / "scripts" / "build.py"
    if not build_script.exists():
        print("❌ Build script not found!")
        return False
    
    # Run CI workflow
    try:
        result = run_command([sys.executable, str(build_script), "--ci"], cwd=repo_root)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Build/test failed!")
        print(e.stdout)
        print(e.stderr)
        return False


def build_release_artifacts(repo_root: Path) -> None:
    """Build release artifacts."""
    print("📦 Building release artifacts...")
    
    build_script = repo_root / "scripts" / "build.py"
    
    # Build package
    run_command([sys.executable, str(build_script), "--build"], cwd=repo_root)
    
    # Build binary
    try:
        run_command([sys.executable, str(build_script), "--build-binary"], cwd=repo_root)
    except subprocess.CalledProcessError as e:
        print("⚠️  Binary build failed, continuing...")
        print(e.stdout)
        print(e.stderr)


def release_to_pypi(repo_root: Path, test_pypi: bool = False) -> None:
    """Release to PyPI."""
    print("🚀 Releasing to PyPI...")
    
    dist_dir = repo_root / "dist"
    if not dist_dir.exists() or not any(dist_dir.iterdir()):
        print("❌ No distribution files found!")
        return
    
    # Choose repository
    repository = "testpypi" if test_pypi else "pypi"
    
    # Upload
    cmd = [sys.executable, "-m", "twine", "upload"]
    if test_pypi:
        cmd.extend(["--repository", "testpypi"])
    cmd.extend([str(f) for f in dist_dir.glob("*")])
    
    try:
        run_command(cmd, cwd=repo_root)
        print(f"✅ Released to {'Test PyPI' if test_pypi else 'PyPI'}!")
    except subprocess.CalledProcessError as e:
        print("❌ PyPI release failed!")
        print(e.stdout)
        print(e.stderr)


def create_github_release(repo_root: Path, version: str, message: str) -> None:
    """Create GitHub release."""
    print("🐙 Creating GitHub release...")
    
    tag_name = f"v{version}"
    
    # Check if gh CLI is available
    try:
        run_command(["gh", "--version"], check=False)
    except subprocess.CalledProcessError:
        print("⚠️  GitHub CLI not available, skipping GitHub release")
        return
    
    # Create release
    try:
        cmd = [
            "gh", "release", "create", tag_name,
            "--title", f"Release {version}",
            "--notes", message
        ]
        
        # Add binary if it exists
        binary_file = repo_root / "dist" / "yaplon"
        if binary_file.exists():
            cmd.append(str(binary_file))
        
        run_command(cmd, cwd=repo_root)
        print("✅ GitHub release created!")
    except subprocess.CalledProcessError as e:
        print("❌ GitHub release failed!")
        print(e.stdout)
        print(e.stderr)


def main():
    """Main release script."""
    parser = argparse.ArgumentParser(description="Release script for yaplon")
    parser.add_argument("--version", help="Specific version to release")
    parser.add_argument("--bump", choices=["major", "minor", "patch"], help="Bump version type")
    parser.add_argument("--message", help="Release message")
    parser.add_argument("--test-pypi", action="store_true", help="Release to Test PyPI")
    parser.add_argument("--no-pypi", action="store_true", help="Skip PyPI release")
    parser.add_argument("--no-github", action="store_true", help="Skip GitHub release")
    parser.add_argument("--no-push", action="store_true", help="Skip pushing to remote")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    
    # Check git status
    if not check_git_status(repo_root):
        print("❌ Git working directory is not clean!")
        print("Please commit or stash your changes first.")
        sys.exit(1)
    
    # Determine version
    current_version = get_version()
    
    if args.version:
        if not validate_version(args.version):
            print(f"❌ Invalid version format: {args.version}")
            sys.exit(1)
        new_version = args.version
    elif args.bump:
        new_version = get_next_version(current_version, args.bump)
    else:
        print("❌ Please specify either --version or --bump")
        sys.exit(1)
    
    # Determine message
    release_message = args.message or f"Release {new_version}"
    
    print(f"📋 Release Plan:")
    print(f"  Current version: {current_version}")
    print(f"  New version: {new_version}")
    print(f"  Message: {release_message}")
    print(f"  PyPI: {'Test PyPI' if args.test_pypi else 'PyPI' if not args.no_pypi else 'Skipped'}")
    print(f"  GitHub: {'Enabled' if not args.no_github else 'Skipped'}")
    print(f"  Push: {'Enabled' if not args.no_push else 'Skipped'}")
    
    if args.dry_run:
        print("🔍 Dry run mode - no changes will be made")
        return
    
    # Confirm
    if not args.dry_run:
        response = input("Continue with release? (y/N): ")
        if response.lower() != 'y':
            print("❌ Release cancelled")
            return
    
    try:
        # Update version in code
        set_version_in_init(new_version)
        print(f"✅ Updated version to {new_version}")
        
        # Build and test
        if not build_and_test(repo_root):
            print("❌ Build/test failed!")
            sys.exit(1)
        
        # Commit version change
        run_command(["git", "add", "--all"], cwd=repo_root)
        run_command(["git", "commit", "-m", f"Bump version to {new_version}"], cwd=repo_root)
        
        # Create tag
        create_git_tag(repo_root, new_version, release_message)
        
        # Push to remote
        if not args.no_push:
            push_to_remote(repo_root)
        
        # Build release artifacts
        build_release_artifacts(repo_root)
        
        # Release to PyPI
        if not args.no_pypi:
            release_to_pypi(repo_root, test_pypi=args.test_pypi)
        
        # Create GitHub release
        if not args.no_github:
            create_github_release(repo_root, new_version, release_message)
        
        print(f"🎉 Release {new_version} completed successfully!")
        
    except Exception as e:
        print(f"❌ Release failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()