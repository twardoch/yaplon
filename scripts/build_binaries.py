#!/usr/bin/env python3
# this_file: scripts/build_binaries.py

"""
Cross-platform binary build script for yaplon.
"""

import argparse
import subprocess
import sys
import os
import shutil
import platform
from pathlib import Path
from typing import Optional

# Add parent directory to path so we can import yaplon
sys.path.insert(0, str(Path(__file__).parent.parent))

from yaplon._version import get_version


def run_command(cmd: list, cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def get_platform_info():
    """Get platform information for binary naming."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Normalize system names
    if system == "darwin":
        system = "macos"
    elif system == "windows":
        system = "windows"
    elif system == "linux":
        system = "linux"
    
    # Normalize architecture names
    if machine in ["x86_64", "amd64"]:
        machine = "x64"
    elif machine in ["i386", "i686"]:
        machine = "x86"
    elif machine in ["aarch64", "arm64"]:
        machine = "arm64"
    
    return system, machine


def build_binary(repo_root: Path, output_dir: Path, spec_file: Optional[Path] = None) -> Path:
    """Build binary using PyInstaller."""
    system, machine = get_platform_info()
    version = get_version()
    
    # Determine binary name
    if system == "windows":
        binary_name = f"yaplon-{version}-{system}-{machine}.exe"
    else:
        binary_name = f"yaplon-{version}-{system}-{machine}"
    
    print(f"🔧 Building binary for {system}-{machine}...")
    print(f"📦 Version: {version}")
    print(f"📄 Binary name: {binary_name}")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build command
    if spec_file and spec_file.exists():
        # Use spec file
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--distpath", str(output_dir),
            "--workpath", str(output_dir / "build"),
            "--specpath", str(output_dir),
            str(spec_file)
        ]
    else:
        # Use command line options
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", binary_name.replace(".exe", ""),
            "--distpath", str(output_dir),
            "--workpath", str(output_dir / "build"),
            "--specpath", str(output_dir),
            "--console",
            "--clean",
            str(repo_root / "yaplon" / "__main__.py")
        ]
    
    # Add platform-specific options
    if system == "windows":
        cmd.extend([
            "--icon", str(repo_root / "yaplon.ico") if (repo_root / "yaplon.ico").exists() else "NONE"
        ])
    
    # Run PyInstaller
    try:
        result = run_command(cmd, cwd=repo_root)
        
        # Find the built binary
        if spec_file:
            built_binary = output_dir / "yaplon"
            if system == "windows":
                built_binary = built_binary.with_suffix(".exe")
        else:
            built_binary = output_dir / binary_name
        
        # Rename if needed
        if spec_file and built_binary.exists():
            final_binary = output_dir / binary_name
            if built_binary != final_binary:
                shutil.move(str(built_binary), str(final_binary))
                built_binary = final_binary
        
        if built_binary.exists():
            print(f"✅ Binary built successfully: {built_binary}")
            print(f"📏 Size: {built_binary.stat().st_size / 1024:.1f} KB")
            return built_binary
        else:
            print("❌ Binary not found after build")
            return None
            
    except subprocess.CalledProcessError as e:
        print("❌ Binary build failed!")
        print(e.stdout)
        print(e.stderr)
        return None


def test_binary(binary_path: Path) -> bool:
    """Test the built binary."""
    print(f"🧪 Testing binary: {binary_path}")
    
    tests = [
        # Test help
        ([str(binary_path), "--help"], "help"),
        # Test version
        ([str(binary_path), "--version"], "version"),
        # Test basic conversion (if possible)
    ]
    
    for cmd, test_name in tests:
        try:
            result = run_command(cmd, check=False)
            if result.returncode == 0:
                print(f"✅ {test_name} test passed")
            else:
                print(f"⚠️  {test_name} test returned {result.returncode}")
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            return False
    
    return True


def create_installer_script(binary_path: Path, output_dir: Path) -> Path:
    """Create a simple installer script."""
    system, machine = get_platform_info()
    
    if system == "windows":
        installer_script = output_dir / "install.bat"
        installer_content = f"""@echo off
echo Installing yaplon...
copy "{binary_path.name}" "%USERPROFILE%\\bin\\yaplon.exe"
if not exist "%USERPROFILE%\\bin" mkdir "%USERPROFILE%\\bin"
echo.
echo yaplon installed to %USERPROFILE%\\bin\\yaplon.exe
echo.
echo Make sure %USERPROFILE%\\bin is in your PATH
echo You can add it by running:
echo   setx PATH "%%PATH%%;%%USERPROFILE%%\\bin"
echo.
pause
"""
    else:
        installer_script = output_dir / "install.sh"
        installer_content = f"""#!/bin/bash
echo "Installing yaplon..."
sudo cp "{binary_path.name}" /usr/local/bin/yaplon
sudo chmod +x /usr/local/bin/yaplon
echo "yaplon installed to /usr/local/bin/yaplon"
echo "You can now run 'yaplon --help' from anywhere"
"""
    
    installer_script.write_text(installer_content)
    installer_script.chmod(0o755)
    
    print(f"✅ Installer script created: {installer_script}")
    return installer_script


def main():
    """Main binary build script."""
    parser = argparse.ArgumentParser(description="Build yaplon binaries")
    parser.add_argument("--output", "-o", type=Path, help="Output directory")
    parser.add_argument("--spec", type=Path, help="PyInstaller spec file")
    parser.add_argument("--test", action="store_true", help="Test the built binary")
    parser.add_argument("--installer", action="store_true", help="Create installer script")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts first")
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    output_dir = args.output or repo_root / "dist"
    
    # Clean if requested
    if args.clean and output_dir.exists():
        shutil.rmtree(output_dir)
        print(f"🧹 Cleaned output directory: {output_dir}")
    
    # Check if PyInstaller is available
    try:
        run_command([sys.executable, "-m", "PyInstaller", "--version"])
    except subprocess.CalledProcessError:
        print("❌ PyInstaller not found. Please install it:")
        print("  pip install pyinstaller")
        sys.exit(1)
    
    # Build binary
    binary_path = build_binary(repo_root, output_dir, args.spec)
    
    if not binary_path:
        print("❌ Binary build failed!")
        sys.exit(1)
    
    # Test binary
    if args.test:
        if not test_binary(binary_path):
            print("❌ Binary tests failed!")
            sys.exit(1)
    
    # Create installer
    if args.installer:
        create_installer_script(binary_path, output_dir)
    
    print(f"🎉 Binary build completed successfully!")
    print(f"📁 Binary location: {binary_path}")


if __name__ == "__main__":
    main()