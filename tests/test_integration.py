# this_file: tests/test_integration.py

import pytest
import subprocess
import tempfile
import json
import yaml
import plistlib
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import OrderedDict

from yaplon import __main__ as yaplon_main


class TestIntegration:
    """Integration tests for yaplon conversions."""

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing conversions."""
        return OrderedDict([
            ("name", "test"),
            ("version", "1.0.0"),
            ("active", True),
            ("count", 42),
            ("items", ["item1", "item2", "item3"]),
            ("nested", OrderedDict([("key", "value"), ("number", 123)]))
        ])

    @pytest.fixture
    def sample_json(self, sample_data):
        """Sample JSON string."""
        return json.dumps(sample_data, indent=2)

    @pytest.fixture
    def sample_yaml(self, sample_data):
        """Sample YAML string."""
        return yaml.dump(sample_data, default_flow_style=False)

    def test_json_to_yaml_conversion(self, sample_json, tmp_path):
        """Test JSON to YAML conversion."""
        json_file = tmp_path / "test.json"
        yaml_file = tmp_path / "test.yaml"
        
        json_file.write_text(sample_json)
        
        # Test using yaplon command
        result = subprocess.run([
            "python", "-m", "yaplon", "j2y",
            "-i", str(json_file),
            "-o", str(yaml_file)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert yaml_file.exists()
        
        # Verify the converted content
        converted_data = yaml.safe_load(yaml_file.read_text())
        assert converted_data["name"] == "test"
        assert converted_data["version"] == "1.0.0"

    def test_yaml_to_json_conversion(self, sample_yaml, tmp_path):
        """Test YAML to JSON conversion."""
        yaml_file = tmp_path / "test.yaml"
        json_file = tmp_path / "test.json"
        
        yaml_file.write_text(sample_yaml)
        
        # Test using yaplon command
        result = subprocess.run([
            "python", "-m", "yaplon", "y2j",
            "-i", str(yaml_file),
            "-o", str(json_file)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert json_file.exists()
        
        # Verify the converted content
        converted_data = json.loads(json_file.read_text())
        assert converted_data["name"] == "test"
        assert converted_data["version"] == "1.0.0"

    def test_json_to_plist_conversion(self, sample_json, tmp_path):
        """Test JSON to PLIST conversion."""
        json_file = tmp_path / "test.json"
        plist_file = tmp_path / "test.plist"
        
        json_file.write_text(sample_json)
        
        # Test using yaplon command
        result = subprocess.run([
            "python", "-m", "yaplon", "j2p",
            "-i", str(json_file),
            "-o", str(plist_file)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert plist_file.exists()
        
        # Verify the converted content
        with open(plist_file, 'rb') as f:
            converted_data = plistlib.load(f)
        assert converted_data["name"] == "test"
        assert converted_data["version"] == "1.0.0"

    def test_json_to_xml_conversion(self, sample_json, tmp_path):
        """Test JSON to XML conversion."""
        json_file = tmp_path / "test.json"
        xml_file = tmp_path / "test.xml"
        
        json_file.write_text(sample_json)
        
        # Test using yaplon command
        result = subprocess.run([
            "python", "-m", "yaplon", "j2x",
            "-i", str(json_file),
            "-o", str(xml_file)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert xml_file.exists()
        
        # Verify the converted content contains expected elements
        xml_content = xml_file.read_text()
        assert "<name>test</name>" in xml_content
        assert "<version>1.0.0</version>" in xml_content

    def test_pipe_conversion(self, sample_json):
        """Test conversion using pipes."""
        result = subprocess.run([
            "python", "-m", "yaplon", "j2y"
        ], input=sample_json, capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "name: test" in result.stdout
        assert "version: 1.0.0" in result.stdout

    def test_sort_option(self, tmp_path):
        """Test sort option."""
        json_data = '{"z": 1, "a": 2, "m": 3}'
        json_file = tmp_path / "test.json"
        yaml_file = tmp_path / "test.yaml"
        
        json_file.write_text(json_data)
        
        # Test with sort option
        result = subprocess.run([
            "python", "-m", "yaplon", "j2y", "--sort",
            "-i", str(json_file),
            "-o", str(yaml_file)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        yaml_content = yaml_file.read_text()
        
        # Should be sorted alphabetically
        lines = yaml_content.strip().split('\n')
        assert lines[0].startswith('a:')
        assert lines[1].startswith('m:')
        assert lines[2].startswith('z:')

    def test_mini_option(self, sample_json, tmp_path):
        """Test minify option."""
        json_file = tmp_path / "test.json"
        yaml_file = tmp_path / "test.yaml"
        
        json_file.write_text(sample_json)
        
        # Test with mini option
        result = subprocess.run([
            "python", "-m", "yaplon", "j2y", "--mini",
            "-i", str(json_file),
            "-o", str(yaml_file)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        yaml_content = yaml_file.read_text()
        
        # Minified YAML should be more compact
        assert yaml_content.count('\n') < sample_json.count('\n')

    def test_error_handling_invalid_json(self, tmp_path):
        """Test error handling for invalid JSON."""
        json_file = tmp_path / "invalid.json"
        yaml_file = tmp_path / "output.yaml"
        
        json_file.write_text('{"invalid": json}')  # Invalid JSON
        
        result = subprocess.run([
            "python", "-m", "yaplon", "j2y",
            "-i", str(json_file),
            "-o", str(yaml_file)
        ], capture_output=True, text=True)
        
        assert result.returncode != 0
        assert not yaml_file.exists()

    def test_shortcut_commands(self, sample_json, tmp_path):
        """Test shortcut commands like json22yaml."""
        json_file = tmp_path / "test.json"
        yaml_file = tmp_path / "test.yaml"
        
        json_file.write_text(sample_json)
        
        # Test json22yaml shortcut
        result = subprocess.run([
            "python", "-m", "yaplon.__main__", "j2y",  # Simulate json22yaml
            "-i", str(json_file),
            "-o", str(yaml_file)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert yaml_file.exists()


class TestCommandLineInterface:
    """Test command line interface behavior."""

    def test_help_command(self):
        """Test help command."""
        result = subprocess.run([
            "python", "-m", "yaplon", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "yaplon" in result.stdout
        assert "j2y" in result.stdout or "JSON to YAML" in result.stdout

    def test_version_access(self):
        """Test version access."""
        result = subprocess.run([
            "python", "-c", "import yaplon; print(yaplon.__version__)"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        version = result.stdout.strip()
        assert len(version) > 0
        assert version != "undefined"

    def test_command_without_args(self):
        """Test command behavior without arguments."""
        result = subprocess.run([
            "python", "-m", "yaplon"
        ], capture_output=True, text=True)
        
        # Should show help or usage information
        assert result.returncode != 0 or "usage" in result.stdout.lower() or "help" in result.stdout.lower()


@pytest.mark.slow
class TestPerformance:
    """Performance tests for yaplon."""

    def test_large_json_conversion(self, tmp_path):
        """Test conversion of large JSON files."""
        # Create a large JSON file
        large_data = {
            "items": [{"id": i, "name": f"item_{i}", "value": i * 2} for i in range(1000)]
        }
        
        json_file = tmp_path / "large.json"
        yaml_file = tmp_path / "large.yaml"
        
        with open(json_file, 'w') as f:
            json.dump(large_data, f, indent=2)
        
        # Test conversion
        result = subprocess.run([
            "python", "-m", "yaplon", "j2y",
            "-i", str(json_file),
            "-o", str(yaml_file)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert yaml_file.exists()
        
        # Verify some content
        yaml_content = yaml_file.read_text()
        assert "items:" in yaml_content
        assert "item_999" in yaml_content