# this_file: tests/test_version.py

import pytest
import subprocess
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from yaplon._version import get_version, get_fallback_version, set_version_in_init


class TestVersionManagement:
    """Test version management system."""

    def test_get_fallback_version_with_init_file(self, tmp_path):
        """Test fallback version reading from __init__.py file."""
        # Create a temporary __init__.py file
        init_file = tmp_path / "__init__.py"
        init_file.write_text('__version__ = "1.2.3"\n')
        
        # Patch the path to point to our temporary file
        with patch('yaplon._version.Path') as mock_path:
            mock_path.return_value.parent = tmp_path
            version = get_fallback_version()
            assert version == "1.2.3"

    def test_get_fallback_version_without_init_file(self, tmp_path):
        """Test fallback version when __init__.py doesn't exist."""
        # Patch the path to point to empty directory
        with patch('yaplon._version.Path') as mock_path:
            mock_path.return_value.parent = tmp_path
            version = get_fallback_version()
            assert version == "0.0.0-dev"

    def test_get_fallback_version_malformed_init_file(self, tmp_path):
        """Test fallback version with malformed __init__.py file."""
        # Create a malformed __init__.py file
        init_file = tmp_path / "__init__.py"
        init_file.write_text('# No version here\n')
        
        with patch('yaplon._version.Path') as mock_path:
            mock_path.return_value.parent = tmp_path
            version = get_fallback_version()
            assert version == "0.0.0-dev"

    @patch('yaplon._version.subprocess.run')
    def test_get_version_from_git_tags(self, mock_run):
        """Test version retrieval from git tags."""
        # Mock git describe success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "v1.2.3\n"
        
        with patch('yaplon._version.Path') as mock_path:
            mock_path.return_value.parent.parent = Path("/fake/repo")
            (mock_path.return_value.parent.parent / ".git").exists.return_value = True
            
            version = get_version()
            assert version == "1.2.3"

    @patch('yaplon._version.subprocess.run')
    def test_get_version_from_git_tags_without_v_prefix(self, mock_run):
        """Test version retrieval from git tags without v prefix."""
        # Mock git describe success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "1.2.3\n"
        
        with patch('yaplon._version.Path') as mock_path:
            mock_path.return_value.parent.parent = Path("/fake/repo")
            (mock_path.return_value.parent.parent / ".git").exists.return_value = True
            
            version = get_version()
            assert version == "1.2.3"

    @patch('yaplon._version.subprocess.run')
    def test_get_version_git_failure_fallback(self, mock_run):
        """Test fallback when git command fails."""
        # Mock git describe failure
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        
        with patch('yaplon._version.get_fallback_version', return_value="2.0.0"):
            version = get_version()
            assert version == "2.0.0"

    @patch('yaplon._version.subprocess.run')
    def test_get_version_no_git_repo(self, mock_run):
        """Test fallback when not in git repo."""
        with patch('yaplon._version.Path') as mock_path:
            mock_path.return_value.parent.parent = Path("/fake/repo")
            (mock_path.return_value.parent.parent / ".git").exists.return_value = False
            
            with patch('yaplon._version.get_fallback_version', return_value="3.0.0"):
                version = get_version()
                assert version == "3.0.0"

    def test_set_version_in_init_existing_file(self, tmp_path):
        """Test setting version in existing __init__.py file."""
        # Create existing __init__.py
        init_file = tmp_path / "__init__.py"
        init_file.write_text('__version__ = "1.0.0"\nother_content = "test"\n')
        
        with patch('yaplon._version.Path') as mock_path:
            mock_path.return_value.parent = tmp_path
            set_version_in_init("2.0.0")
            
            content = init_file.read_text()
            assert '__version__ = "2.0.0"' in content
            assert 'other_content = "test"' in content

    def test_set_version_in_init_new_file(self, tmp_path):
        """Test setting version in new __init__.py file."""
        with patch('yaplon._version.Path') as mock_path:
            mock_path.return_value.parent = tmp_path
            set_version_in_init("1.5.0")
            
            init_file = tmp_path / "__init__.py"
            content = init_file.read_text()
            assert '__version__ = "1.5.0"' in content

    def test_version_validation_semver(self):
        """Test that only valid semver versions are accepted."""
        with patch('yaplon._version.subprocess.run') as mock_run:
            # Test valid semver
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "v1.2.3\n"
            
            with patch('yaplon._version.Path') as mock_path:
                mock_path.return_value.parent.parent = Path("/fake/repo")
                (mock_path.return_value.parent.parent / ".git").exists.return_value = True
                
                version = get_version()
                assert version == "1.2.3"

    def test_version_validation_invalid_semver(self):
        """Test that invalid semver falls back."""
        with patch('yaplon._version.subprocess.run') as mock_run:
            # Test invalid semver
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "v1.2\n"  # Invalid semver
            
            with patch('yaplon._version.Path') as mock_path:
                mock_path.return_value.parent.parent = Path("/fake/repo")
                (mock_path.return_value.parent.parent / ".git").exists.return_value = True
                
                with patch('yaplon._version.get_fallback_version', return_value="4.0.0"):
                    version = get_version()
                    assert version == "4.0.0"


class TestVersionIntegration:
    """Integration tests for version system."""

    def test_version_import_from_init(self):
        """Test that version can be imported from __init__.py."""
        from yaplon import __version__
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_command_line_access(self):
        """Test version access from command line."""
        result = subprocess.run(
            ["python", "-c", "from yaplon import __version__; print(__version__)"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0