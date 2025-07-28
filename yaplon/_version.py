#!/usr/bin/env python3
# this_file: yaplon/_version.py

import subprocess
import re
import os
from pathlib import Path

def get_version():
    """
    Get version from git tags with fallback to file-based version.
    Uses semantic versioning format (MAJOR.MINOR.PATCH).
    """
    try:
        # Try to get version from git tags
        repo_root = Path(__file__).parent.parent
        
        # Check if we're in a git repository
        if not (repo_root / ".git").exists():
            return get_fallback_version()
        
        # Get the most recent tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--match=v*", "--abbrev=0"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            tag = result.stdout.strip()
            # Remove 'v' prefix if present
            version = tag.lstrip('v')
            
            # Validate semver format
            if re.match(r'^\d+\.\d+\.\d+$', version):
                return version
        
        # If no proper tag found, try to get any tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            tag = result.stdout.strip()
            # Remove 'v' prefix if present
            version = tag.lstrip('v')
            
            # Validate semver format
            if re.match(r'^\d+\.\d+\.\d+$', version):
                return version
                
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Fallback to file-based version
    return get_fallback_version()

def get_fallback_version():
    """Get version from __init__.py file as fallback."""
    try:
        init_file = Path(__file__).parent / "__init__.py"
        if init_file.exists():
            with open(init_file, 'r') as f:
                content = f.read()
                match = re.search(r'^__version__ = ["\']([^"\']+)["\']', content, re.MULTILINE)
                if match:
                    return match.group(1)
    except Exception:
        pass
    
    return "0.0.0-dev"

def set_version_in_init(version):
    """Set version in __init__.py file."""
    init_file = Path(__file__).parent / "__init__.py"
    
    if init_file.exists():
        with open(init_file, 'r') as f:
            content = f.read()
        
        # Update version
        new_content = re.sub(
            r'^__version__ = ["\'][^"\']+["\']',
            f'__version__ = "{version}"',
            content,
            flags=re.MULTILINE
        )
        
        with open(init_file, 'w') as f:
            f.write(new_content)
    else:
        # Create __init__.py with version
        with open(init_file, 'w') as f:
            f.write(f'__version__ = "{version}"\n')

# Main version for the module
__version__ = get_version()

if __name__ == "__main__":
    print(get_version())