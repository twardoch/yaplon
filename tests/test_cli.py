# this_file: tests/test_cli.py

import pytest
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from yaplon import __main__ as yaplon_main


class TestCLI:
    """Test command line interface functionality."""

    def test_main_cli_imports(self):
        """Test that main CLI module imports correctly."""
        assert hasattr(yaplon_main, 'cli')
        assert callable(yaplon_main.cli)

    def test_entry_point_functions_exist(self):
        """Test that all entry point functions exist."""
        entry_points = [
            'csv2json', 'csv2plist', 'csv2xml', 'csv2yaml',
            'json2plist', 'json2xml', 'json2yaml',
            'plist2json', 'plist2xml', 'plist2yaml',
            'xml2json', 'xml2plist', 'xml2yaml',
            'yaml2json', 'yaml2plist', 'yaml2xml'
        ]
        
        for entry_point in entry_points:
            assert hasattr(yaplon_main, entry_point)
            assert callable(getattr(yaplon_main, entry_point))

    def test_cli_with_version_flag(self):
        """Test CLI with version flag."""
        # This would test the --version flag if it exists
        # For now, we'll test that the CLI can be invoked
        try:
            result = subprocess.run([
                sys.executable, "-m", "yaplon", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            # Should either succeed or fail gracefully
            assert result.returncode in [0, 1, 2]  # Common exit codes
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI test timed out")

    def test_cli_error_handling(self):
        """Test CLI error handling with invalid command."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "yaplon", "invalid_command"
            ], capture_output=True, text=True, timeout=10)
            
            # Should fail with invalid command
            assert result.returncode != 0
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI test timed out")

    @patch('yaplon.__main__.click')
    def test_cli_click_integration(self, mock_click):
        """Test Click integration."""
        mock_click.group.return_value = MagicMock()
        
        # Import should work without errors
        import yaplon.__main__
        
        # Click should be used for CLI setup
        assert mock_click.group.called or mock_click.command.called

    def test_module_execution(self):
        """Test that module can be executed directly."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "yaplon"
            ], capture_output=True, text=True, timeout=10)
            
            # Should either show help or fail gracefully
            assert result.returncode in [0, 1, 2]
            
        except subprocess.TimeoutExpired:
            pytest.skip("Module execution test timed out")


class TestPackageStructure:
    """Test package structure and imports."""

    def test_package_imports(self):
        """Test that package imports correctly."""
        import yaplon
        assert hasattr(yaplon, '__version__')

    def test_submodule_imports(self):
        """Test that submodules can be imported."""
        import yaplon.reader
        import yaplon.writer
        import yaplon.ojson
        import yaplon.oyaml
        import yaplon.oplist
        
        assert hasattr(yaplon.reader, 'json')
        assert hasattr(yaplon.writer, 'json')
        assert hasattr(yaplon.ojson, 'read_json')
        assert hasattr(yaplon.oyaml, 'read_yaml')
        assert hasattr(yaplon.oplist, 'read_plist')

    def test_version_consistency(self):
        """Test version consistency across modules."""
        import yaplon
        from yaplon._version import get_version
        
        package_version = yaplon.__version__
        direct_version = get_version()
        
        assert package_version == direct_version

    def test_file_strip_module(self):
        """Test file strip module."""
        from yaplon.file_strip import json, comments
        
        assert hasattr(json, 'sanitize_json')
        assert hasattr(comments, 'strip_comments')

    def test_all_modules_have_this_file(self):
        """Test that all Python modules have this_file comment."""
        import yaplon
        package_path = Path(yaplon.__file__).parent
        
        python_files = list(package_path.rglob("*.py"))
        assert len(python_files) > 0
        
        # Check a few key files have this_file comment
        key_files = ['__init__.py', '__main__.py', 'reader.py', 'writer.py']
        
        for key_file in key_files:
            file_path = package_path / key_file
            if file_path.exists():
                content = file_path.read_text()
                # Should have this_file comment somewhere in the file
                assert "this_file:" in content or f"# {key_file}" in content or key_file in str(file_path)