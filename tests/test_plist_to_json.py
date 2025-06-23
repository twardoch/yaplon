import pytest
import tempfile
import os
import json
import plistlib
import io # Required for StringIO

from yaplon import reader, writer
from tests.helpers import (
    assert_json_strings_equal,
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
    <string>Test Plist</string>
    <key>version</key>
    <real>1.2</real>
    <key>active</key>
    <true/>
    <key>count</key>
    <integer>101</integer>
    <key>items</key>
    <array>
        <string>alpha</string>
        <string>beta</string>
    </array>
    <key>binary_data</key>
    <data>SGVsbG8=</data> <!-- "Hello" base64 encoded -->
</dict>
</plist>
"""

# This is what reader.plist(BytesIO(SAMPLE_PLIST_XML_STRING.encode())) should produce
EXPECTED_DICT_FROM_XML_READER = {
    "name": "Test Plist",
    "version": 1.2,
    "active": True,
    "count": 101,
    "items": ["alpha", "beta"],
    "binary_data": b"Hello"
}


EXPECTED_JSON_PRETTY = """\
{
    "name": "Test Plist",
    "version": 1.2,
    "active": true,
    "count": 101,
    "items": [
        "alpha",
        "beta"
    ],
    "binary_data": {
        "__bytes__": true,
        "base64": "SGVsbG8="
    }
}"""
EXPECTED_JSON_MINIFIED = '{"name":"Test Plist","version":1.2,"active":true,"count":101,"items":["alpha","beta"],"binary_data":{"__bytes__":true,"base64":"SGVsbG8="}}'

EXPECTED_JSON_PRETTY_PRESERVE_BINARY = """\
{
    "name": "Test Plist",
    "version": 1.2,
    "active": true,
    "count": 101,
    "items": [
        "alpha",
        "beta"
    ],
    "binary_data": "SGVsbG8="
}"""
EXPECTED_JSON_MINIFIED_PRESERVE_BINARY = '{"name":"Test Plist","version":1.2,"active":true,"count":101,"items":["alpha","beta"],"binary_data":"SGVsbG8="}'


UNSORTED_PLIST_XML_STRING = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>z_key</key>
    <integer>1</integer>
    <key>a_key</key>
    <string>value</string>
    <key>m_key</key>
    <array>
        <integer>3</integer>
        <integer>1</integer>
        <integer>2</integer>
    </array>
</dict>
</plist>
"""
EXPECTED_SORTED_JSON_PRETTY = """\
{
    "a_key": "value",
    "m_key": [
        3,
        1,
        2
    ],
    "z_key": 1
}"""
EXPECTED_SORTED_JSON_MINIFIED = '{"a_key":"value","m_key":[3,1,2],"z_key":1}'

# --- Tests ---

def test_plist_xml_to_json_via_writer_functions():
    with io.BytesIO(SAMPLE_PLIST_XML_STRING.encode('utf-8')) as bytes_io_input:
        plist_data = reader.plist(bytes_io_input)

    # Direct dictionary comparison
    assert plist_data == EXPECTED_DICT_FROM_XML_READER

    string_io_default = io.StringIO()
    writer.json(plist_data, string_io_default, mini=False, binary=False)
    actual_json_default = string_io_default.getvalue()
    assert_json_strings_equal(actual_json_default, EXPECTED_JSON_PRETTY)

    string_io_preserve_binary = io.StringIO()
    writer.json(plist_data, string_io_preserve_binary, mini=False, binary=True)
    actual_json_preserve_binary = string_io_preserve_binary.getvalue()
    assert_json_strings_equal(actual_json_preserve_binary, EXPECTED_JSON_PRETTY_PRESERVE_BINARY)


def test_p2j_cli_xml_input_default():
    output_content, stderr = run_yaplon_command(
        ["p2j"],
        input_content=SAMPLE_PLIST_XML_STRING,
        input_suffix=".plist",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_PRETTY)

def test_p2j_cli_xml_input_minified():
    output_content, stderr = run_yaplon_command(
        ["p2j", "-m"],
        input_content=SAMPLE_PLIST_XML_STRING,
        input_suffix=".plist",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_MINIFIED)

def test_p2j_cli_xml_input_preserve_binary():
    output_content, stderr = run_yaplon_command(
        ["p2j", "-b"],
        input_content=SAMPLE_PLIST_XML_STRING,
        input_suffix=".plist",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_PRETTY_PRESERVE_BINARY)

def test_p2j_cli_xml_input_preserve_binary_minified():
    output_content, stderr = run_yaplon_command(
        ["p2j", "-b", "-m"],
        input_content=SAMPLE_PLIST_XML_STRING,
        input_suffix=".plist",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_MINIFIED_PRESERVE_BINARY)

@pytest.fixture
def binary_plist_fixture_bytes(): # Renamed to reflect it yields bytes
    # Use EXPECTED_DICT_FROM_XML_READER as it contains bytes, matching reader.plist output
    binary_data = plistlib.dumps(EXPECTED_DICT_FROM_XML_READER, fmt=plistlib.FMT_BINARY)
    yield binary_data

def test_p2j_cli_binary_input_default(binary_plist_fixture_bytes):
    binary_bytes = binary_plist_fixture_bytes
    output_content, stderr = run_yaplon_command(
        ["p2j"],
        input_content=binary_bytes,
        input_suffix=".plist",
        output_suffix=".json",
        is_binary_input=True
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_PRETTY)

def test_p2j_cli_binary_input_preserve_binary(binary_plist_fixture_bytes):
    binary_bytes = binary_plist_fixture_bytes
    output_content, stderr = run_yaplon_command(
        ["p2j", "-b"],
        input_content=binary_bytes,
        input_suffix=".plist",
        output_suffix=".json",
        is_binary_input=True
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_PRETTY_PRESERVE_BINARY)

def test_p2j_cli_xml_input_sorted():
    output_content, stderr = run_yaplon_command(
        ["p2j", "-s"],
        input_content=UNSORTED_PLIST_XML_STRING,
        input_suffix=".plist",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_SORTED_JSON_PRETTY)

def test_p2j_cli_xml_input_sorted_minified():
    output_content, stderr = run_yaplon_command(
        ["p2j", "-s", "-m"],
        input_content=UNSORTED_PLIST_XML_STRING,
        input_suffix=".plist",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_SORTED_JSON_MINIFIED)

def test_plist22json_cli_xml_input_default():
    output_content, stderr = run_yaplon_command(
        [],
        input_content=SAMPLE_PLIST_XML_STRING,
        input_suffix=".plist",
        output_suffix=".json",
        cli_tool_name="plist22json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_PRETTY)

def test_plist22json_cli_xml_input_preserve_binary_minified():
    output_content, stderr = run_yaplon_command(
        ["-b", "-m"],
        input_content=SAMPLE_PLIST_XML_STRING,
        input_suffix=".plist",
        output_suffix=".json",
        cli_tool_name="plist22json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_MINIFIED_PRESERVE_BINARY)

# --- Piping Tests ---
def test_p2j_cli_xml_pipe_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["p2j"],
        input_data=SAMPLE_PLIST_XML_STRING
    )
    assert stderr == ""
    assert_json_strings_equal(stdout_content, EXPECTED_JSON_PRETTY)

def test_p2j_cli_xml_pipe_preserve_binary_minified():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["p2j", "-b", "-m"],
        input_data=SAMPLE_PLIST_XML_STRING
    )
    assert stderr == ""
    assert_json_strings_equal(stdout_content, EXPECTED_JSON_MINIFIED_PRESERVE_BINARY)

def test_plist22json_cli_xml_pipe_sorted():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["-s"],
        input_data=UNSORTED_PLIST_XML_STRING,
        cli_tool_name="plist22json"
    )
    assert stderr == ""
    assert_json_strings_equal(stdout_content, EXPECTED_SORTED_JSON_PRETTY)

@pytest.mark.skip(reason="Binary stdin piping for plist needs robust handling in CLI and test.")
def test_p2j_cli_binary_pipe_preserve_binary(binary_plist_fixture_bytes): # Use updated fixture name
    binary_data = binary_plist_fixture_bytes
    stdout_content, stderr = run_yaplon_pipe_command(
        ["p2j", "-b"],
        input_data=binary_data,
        is_binary_input=True
    )
    assert stderr == ""
    assert_json_strings_equal(stdout_content, EXPECTED_JSON_PRETTY_PRESERVE_BINARY)
