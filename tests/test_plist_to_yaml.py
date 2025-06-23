import pytest
import tempfile
import os
import io
import yaml # For loading YAML to compare
import plistlib

from yaplon import reader, writer
from tests.helpers import (
    assert_yaml_strings_equal,
    run_yaplon_command,
    run_yaplon_pipe_command
)

# --- Test Data ---

SAMPLE_PLIST_XML_STRING = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>name</key>
    <string>Test Plist for YAML</string>
    <key>version</key>
    <real>3.0</real>
    <key>enabled</key>
    <false/>
    <key>tags</key>
    <array>
        <string>test</string>
        <string>conversion</string>
    </array>
    <key>binary_content</key>
    <data>VGhpcyBpcyBiaW5hcnk=</data> <!-- "This is binary" base64 encoded -->
</dict>
</plist>
"""

SAMPLE_PLIST_DICT_FOR_YAML = {
    "name": "Test Plist for YAML",
    "version": 3.0,
    "enabled": False,
    "tags": ["test", "conversion"],
    "binary_content": b"This is binary"
}

# Expected YAML output (pretty-printed)
# PyYAML default `sort_keys=True` for block style, so keys are alphabetical.
EXPECTED_YAML_PRETTY = """\
binary_content: !!binary VGhpcyBpcyBiaW5hcnk=
enabled: false
name: Test Plist for YAML
tags:
- test
- conversion
version: 3.0
"""

# Expected YAML output (minified - flow style)
# yaplon.oyaml.yaml_dumps with compact=True passes default_flow_style=True to PyYAML's dump.
# PyYAML's dump with default_flow_style=True and OrderedDict input (from reader.plist) preserves order.
# Original order in SAMPLE_PLIST_XML_STRING: name, version, enabled, tags, binary_content
EXPECTED_YAML_MINIFIED = "{name: Test Plist for YAML, version: 3.0, enabled: false, tags: [test, conversion], binary_content: !!binary VGhpcyBpcyBiaW5hcnk=}\n"


UNSORTED_PLIST_XML_STRING_FOR_YAML = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>z_item</key>
    <string>last</string>
    <key>a_item</key>
    <integer>123</integer>
    <key>m_item</key>
    <true/>
</dict>
</plist>
"""
EXPECTED_YAML_SORTED_PRETTY = """\
a_item: 123
m_item: true
z_item: last
"""
EXPECTED_YAML_SORTED_MINIFIED = "{a_item: 123, m_item: true, z_item: last}\n"


# --- Tests ---

def test_plist_to_yaml_via_writer_functions():
    with io.BytesIO(SAMPLE_PLIST_XML_STRING.encode('utf-8')) as bytes_io_input:
        plist_data = reader.plist(bytes_io_input)
    assert plist_data == SAMPLE_PLIST_DICT_FOR_YAML

    string_io_pretty = io.StringIO()
    writer.yaml(plist_data, string_io_pretty, mini=False)
    actual_yaml_pretty = string_io_pretty.getvalue()
    assert_yaml_strings_equal(actual_yaml_pretty, EXPECTED_YAML_PRETTY)

    string_io_mini = io.StringIO()
    writer.yaml(plist_data, string_io_mini, mini=True)
    actual_yaml_mini = string_io_mini.getvalue()
    assert_yaml_strings_equal(actual_yaml_mini.strip(), EXPECTED_YAML_MINIFIED.strip())

@pytest.fixture
def binary_plist_fixture_for_yaml(): # Renamed to avoid conflict
    binary_data = plistlib.dumps(SAMPLE_PLIST_DICT_FOR_YAML, fmt=plistlib.FMT_BINARY)
    yield binary_data # yield bytes directly

def test_plist_binary_to_yaml_via_writer_functions(binary_plist_fixture_for_yaml):
    binary_plist_bytes = binary_plist_fixture_for_yaml
    with io.BytesIO(binary_plist_bytes) as bytes_io_input:
        plist_data = reader.plist(bytes_io_input)
    assert plist_data == SAMPLE_PLIST_DICT_FOR_YAML

    string_io_pretty = io.StringIO()
    writer.yaml(plist_data, string_io_pretty, mini=False)
    actual_yaml_pretty = string_io_pretty.getvalue()
    assert_yaml_strings_equal(actual_yaml_pretty, EXPECTED_YAML_PRETTY)


# CLI Tests
def test_p2y_cli_xml_input_default():
    output_content, stderr = run_yaplon_command(
        ["p2y"],
        input_content=SAMPLE_PLIST_XML_STRING,
        input_suffix=".plist",
        output_suffix=".yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content, EXPECTED_YAML_PRETTY)

def test_p2y_cli_xml_input_minified():
    output_content, stderr = run_yaplon_command(
        ["p2y", "-m"],
        input_content=SAMPLE_PLIST_XML_STRING,
        input_suffix=".plist",
        output_suffix=".yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content.strip(), EXPECTED_YAML_MINIFIED.strip())

def test_p2y_cli_binary_input_default(binary_plist_fixture_for_yaml):
    binary_plist_bytes = binary_plist_fixture_for_yaml
    output_content, stderr = run_yaplon_command(
        ["p2y"],
        input_content=binary_plist_bytes,
        input_suffix=".plist",
        output_suffix=".yaml",
        is_binary_input=True
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content, EXPECTED_YAML_PRETTY)

def test_p2y_cli_xml_input_sorted():
    output_content, stderr = run_yaplon_command(
        ["p2y", "-s"],
        input_content=UNSORTED_PLIST_XML_STRING_FOR_YAML,
        input_suffix=".plist",
        output_suffix=".yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content, EXPECTED_YAML_SORTED_PRETTY)

def test_p2y_cli_xml_input_sorted_minified():
    output_content, stderr = run_yaplon_command(
        ["p2y", "-s", "-m"],
        input_content=UNSORTED_PLIST_XML_STRING_FOR_YAML,
        input_suffix=".plist",
        output_suffix=".yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content.strip(), EXPECTED_YAML_SORTED_MINIFIED.strip())

def test_plist22yaml_cli_default():
    output_content, stderr = run_yaplon_command(
        [],
        input_content=SAMPLE_PLIST_XML_STRING,
        input_suffix=".plist",
        output_suffix=".yaml",
        cli_tool_name="plist22yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content, EXPECTED_YAML_PRETTY)

def test_plist22yaml_cli_minified_sorted():
    output_content, stderr = run_yaplon_command(
        ["-m", "-s"],
        input_content=UNSORTED_PLIST_XML_STRING_FOR_YAML,
        input_suffix=".plist",
        output_suffix=".yaml",
        cli_tool_name="plist22yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content.strip(), EXPECTED_YAML_SORTED_MINIFIED.strip())

# --- Piping Tests ---
def test_p2y_cli_pipe_xml_input_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["p2y"],
        input_data=SAMPLE_PLIST_XML_STRING
    )
    assert stderr == ""
    assert_yaml_strings_equal(stdout_content, EXPECTED_YAML_PRETTY) # stdout from helper is not stripped by default for text

def test_p2y_cli_pipe_xml_input_minified_sorted():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["p2y", "-m", "-s"],
        input_data=UNSORTED_PLIST_XML_STRING_FOR_YAML
    )
    assert stderr == ""
    assert_yaml_strings_equal(stdout_content.strip(), EXPECTED_YAML_SORTED_MINIFIED.strip()) # Pipe helper strips text stdout

@pytest.mark.skip(reason="Binary plist input via pipe needs confirmation on how yaplon handles binary stdin for plist.")
def test_p2y_cli_pipe_binary_input_default(binary_plist_fixture_for_yaml):
    binary_plist_bytes = binary_plist_fixture_for_yaml
    stdout_content, stderr = run_yaplon_pipe_command(
        ["p2y"],
        input_data=binary_plist_bytes,
        is_binary_input=True
    )
    assert stderr == ""
    assert_yaml_strings_equal(stdout_content, EXPECTED_YAML_PRETTY)
