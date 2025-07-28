import pytest
import tempfile
import os
import plistlib
import io # Required for writer function tests

from yaplon import reader, writer
from tests.helpers import ( # Changed to absolute import path
    assert_plist_xml_strings_equal,
    assert_binary_plist_data_equal,
    run_yaplon_command,
    run_yaplon_pipe_command
)

# Sample JSON data
SAMPLE_JSON_STRING = '{"name": "Test", "value": 123, "items": [1, "two", 3.0]}'
SAMPLE_JSON_DICT = {"name": "Test", "value": 123, "items": [1, "two", 3.0]}

# Expected PLIST (XML format, with consistent space indentation)
# Note: plistlib.dumps sorts keys by default.
EXPECTED_PLIST_XML_SPACES = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>items</key>
	<array>
		<integer>1</integer>
		<string>two</string>
		<real>3.0</real>
	</array>
	<key>name</key>
	<string>Test</string>
	<key>value</key>
	<integer>123</integer>
</dict>
</plist>
"""

# Unsorted JSON for testing sorting
UNSORTED_JSON_STRING = '{"z_key": 1, "a_key": "value", "m_key": [3, 1, 2]}'
EXPECTED_SORTED_JSON_DICT_FOR_PLIST = {"a_key": "value", "m_key": [3, 1, 2], "z_key": 1}

# Expected Plist XML from sorted JSON
# Keys will be sorted: a_key, m_key, z_key
EXPECTED_SORTED_PLIST_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>a_key</key>
	<string>value</string>
	<key>m_key</key>
	<array>
		<integer>3</integer>
		<integer>1</integer>
		<integer>2</integer>
	</array>
	<key>z_key</key>
	<integer>1</integer>
</dict>
</plist>
"""

# --- Tests ---

def test_json_to_plist_xml_via_writer_functions():
    with io.StringIO(SAMPLE_JSON_STRING) as string_io_input: # Use io.StringIO for reader.json
        json_data = reader.json(string_io_input)
    assert json_data == SAMPLE_JSON_DICT, "JSON data not read correctly by reader.json"

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".plist") as tmp_plist_file:
        plist_filepath = tmp_plist_file.name
    try:
        writer.plist(json_data, plist_filepath, binary=False)
        with open(plist_filepath, "r", encoding="utf-8") as f:
            result_plist_xml = f.read()
    finally:
        os.remove(plist_filepath)
    assert_plist_xml_strings_equal(result_plist_xml, EXPECTED_PLIST_XML_SPACES)


def test_j2p_cli_xml_output():
    output_content, stderr = run_yaplon_command(
        ["j2p"],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".plist",
        is_binary_output=False # XML plist is text
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(output_content, EXPECTED_PLIST_XML_SPACES)

def test_j2p_cli_xml_output_sorted():
    output_content, stderr = run_yaplon_command(
        ["j2p", "-s"],
        input_content=UNSORTED_JSON_STRING,
        input_suffix=".json",
        output_suffix=".plist",
        is_binary_output=False
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(output_content, EXPECTED_SORTED_PLIST_XML)

def test_j2p_cli_binary_output_integrity():
    output_content_bytes, stderr = run_yaplon_command(
        ["j2p", "-b"],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".plist",
        is_binary_output=True
    )
    assert stderr == ""
    assert_binary_plist_data_equal(output_content_bytes, SAMPLE_JSON_DICT)

def test_j2p_cli_binary_output_sorted_integrity():
    output_content_bytes, stderr = run_yaplon_command(
        ["j2p", "-s", "-b"],
        input_content=UNSORTED_JSON_STRING,
        input_suffix=".json",
        output_suffix=".plist",
        is_binary_output=True
    )
    assert stderr == ""
    assert_binary_plist_data_equal(output_content_bytes, EXPECTED_SORTED_JSON_DICT_FOR_PLIST)

# Test direct CLI script json22plist
def test_json22plist_cli_xml_output():
    output_content, stderr = run_yaplon_command(
        [],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".plist",
        is_binary_output=False,
        cli_tool_name="json22plist"
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(output_content, EXPECTED_PLIST_XML_SPACES)

def test_json22plist_cli_xml_output_sorted():
    output_content, stderr = run_yaplon_command(
        ["-s"],
        input_content=UNSORTED_JSON_STRING,
        input_suffix=".json",
        output_suffix=".plist",
        is_binary_output=False,
        cli_tool_name="json22plist"
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(output_content, EXPECTED_SORTED_PLIST_XML)

def test_json22plist_cli_binary_output_integrity():
    output_content_bytes, stderr = run_yaplon_command(
        ["-b"],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".plist",
        is_binary_output=True,
        cli_tool_name="json22plist"
    )
    assert stderr == ""
    assert_binary_plist_data_equal(output_content_bytes, SAMPLE_JSON_DICT)

def test_json22plist_cli_binary_output_sorted_integrity():
    output_content_bytes, stderr = run_yaplon_command(
        ["-s", "-b"],
        input_content=UNSORTED_JSON_STRING,
        input_suffix=".json",
        output_suffix=".plist",
        is_binary_output=True,
        cli_tool_name="json22plist"
    )
    assert stderr == ""
    assert_binary_plist_data_equal(output_content_bytes, EXPECTED_SORTED_JSON_DICT_FOR_PLIST)

# --- Piping Tests (XML Plist output) ---
def test_j2p_cli_xml_pipe_basic():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["j2p"],
        input_data=SAMPLE_JSON_STRING,
        is_binary_output=False # XML Plist is text
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(stdout_content.strip(), EXPECTED_PLIST_XML_SPACES) # Strip for pipe output

def test_j2p_cli_xml_pipe_sorted():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["j2p", "-s"],
        input_data=UNSORTED_JSON_STRING,
        is_binary_output=False
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(stdout_content.strip(), EXPECTED_SORTED_PLIST_XML)

def test_json22plist_cli_xml_pipe_basic():
    stdout_content, stderr = run_yaplon_pipe_command(
        [],
        input_data=SAMPLE_JSON_STRING,
        cli_tool_name="json22plist",
        is_binary_output=False
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(stdout_content.strip(), EXPECTED_PLIST_XML_SPACES)

def test_json22plist_cli_xml_pipe_sorted():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["-s"],
        input_data=UNSORTED_JSON_STRING,
        cli_tool_name="json22plist",
        is_binary_output=False
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(stdout_content.strip(), EXPECTED_SORTED_PLIST_XML)

# Note: Binary plist output to stdout is trickier to assert directly with text-based helpers.
# The generic run_yaplon_pipe_command can return bytes if is_binary_output=True.
# A dedicated test for binary pipe could be:
@pytest.mark.skip(reason="Verifying binary plist output from stdout pipe needs specific handling.")
def test_j2p_cli_binary_pipe_integrity():
    stdout_bytes, stderr = run_yaplon_pipe_command(
        ["j2p", "-b"],
        input_data=SAMPLE_JSON_STRING,
        is_binary_output=True
    )
    assert stderr == ""
    assert_binary_plist_data_equal(stdout_bytes, SAMPLE_JSON_DICT)
