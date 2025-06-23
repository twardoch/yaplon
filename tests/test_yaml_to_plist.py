import pytest
import tempfile
import os
import io
import yaml
import plistlib
from xml.etree import ElementTree as ET

from yaplon import reader, writer
from tests.helpers import (
    assert_plist_xml_strings_equal, # Using the one from helpers
    assert_binary_plist_data_equal, # Using the one from helpers
    run_yaplon_command,
    run_yaplon_pipe_command
)

# --- Test Data ---

SAMPLE_YAML_STRING = """\
name: Test YAML for Plist
version: 4.0
active: true
tags:
  - yaml_tag
  - conversion_tag
binary_payload: !!binary Um9ja3Mh # "Rocks!" base64 encoded
"""

EXPECTED_DICT_FROM_YAML_FOR_PLIST = {
    "name": "Test YAML for Plist",
    "version": 4.0,
    "active": True,
    "tags": ["yaml_tag", "conversion_tag"],
    "binary_payload": b"Rocks!"
}

# Plist key order is typically sorted alphabetically by plistlib.dumps
EXPECTED_PLIST_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>active</key>
	<true/>
	<key>binary_payload</key>
	<data>Um9ja3Mh</data>
	<key>name</key>
	<string>Test YAML for Plist</string>
	<key>tags</key>
	<array>
		<string>yaml_tag</string>
		<string>conversion_tag</string>
	</array>
	<key>version</key>
	<real>4.0</real>
</dict>
</plist>
"""

UNSORTED_YAML_FOR_PLIST = """\
zulu_time: 2024-03-10T10:00:00Z
alpha_num: 1
bravo_str: "text"
"""

EXPECTED_SORTED_DICT_FOR_PLIST = { # After yaplon -s sorts the dict from YAML
    "alpha_num": 1,
    "bravo_str": "text",
    "zulu_time": "2024-03-10T10:00:00Z"
}
# Plistlib will then sort these keys alphabetically for XML output
EXPECTED_SORTED_PLIST_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>alpha_num</key>
	<integer>1</integer>
	<key>bravo_str</key>
	<string>text</string>
	<key>zulu_time</key>
	<string>2024-03-10T10:00:00Z</string>
</dict>
</plist>
"""

# --- Tests ---

def test_yaml_to_plist_via_writer_functions():
    with io.StringIO(SAMPLE_YAML_STRING) as string_io_input:
        yaml_data = reader.yaml(string_io_input)
    assert yaml_data == EXPECTED_DICT_FROM_YAML_FOR_PLIST

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".plist", encoding='utf-8') as tmp_xml_plist_file:
        xml_plist_filepath = tmp_xml_plist_file.name
    try:
        writer.plist(yaml_data, xml_plist_filepath, binary=False)
        with open(xml_plist_filepath, "r", encoding='utf-8') as f:
            actual_xml_plist = f.read()
        assert_plist_xml_strings_equal(actual_xml_plist, EXPECTED_PLIST_XML)
    finally:
        os.remove(xml_plist_filepath)

    with tempfile.NamedTemporaryFile(mode="wb+", delete=False, suffix=".plist") as tmp_bin_plist_file:
        bin_plist_filepath = tmp_bin_plist_file.name
    try:
        writer.plist(yaml_data, bin_plist_filepath, binary=True)
        with open(bin_plist_filepath, "rb") as f:
            actual_binary_plist_bytes = f.read()
        assert_binary_plist_data_equal(actual_binary_plist_bytes, EXPECTED_DICT_FROM_YAML_FOR_PLIST)
    finally:
        os.remove(bin_plist_filepath)

def test_y2p_cli_xml_default():
    output_content, stderr = run_yaplon_command(
        ["y2p"],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".plist",
        is_binary_output=False # XML Plist is text
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(output_content, EXPECTED_PLIST_XML)

def test_y2p_cli_binary():
    output_content_bytes, stderr = run_yaplon_command(
        ["y2p", "-b"],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".plist",
        is_binary_output=True
    )
    assert stderr == ""
    assert_binary_plist_data_equal(output_content_bytes, EXPECTED_DICT_FROM_YAML_FOR_PLIST)

def test_y2p_cli_xml_sorted():
    output_content, stderr = run_yaplon_command(
        ["y2p", "-s"],
        input_content=UNSORTED_YAML_FOR_PLIST,
        input_suffix=".yaml",
        output_suffix=".plist",
        is_binary_output=False
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(output_content, EXPECTED_SORTED_PLIST_XML)

def test_yaml22plist_cli_xml_default():
    output_content, stderr = run_yaplon_command(
        [],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".plist",
        cli_tool_name="yaml22plist",
        is_binary_output=False
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(output_content, EXPECTED_PLIST_XML)

def test_yaml22plist_cli_binary_sorted():
    output_content_bytes, stderr = run_yaplon_command(
        ["-b", "-s"],
        input_content=UNSORTED_YAML_FOR_PLIST,
        input_suffix=".yaml",
        output_suffix=".plist",
        cli_tool_name="yaml22plist",
        is_binary_output=True
    )
    assert stderr == ""
    assert_binary_plist_data_equal(output_content_bytes, EXPECTED_SORTED_DICT_FOR_PLIST)

# --- Piping Tests ---
def test_y2p_cli_pipe_xml_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["y2p"],
        input_data=SAMPLE_YAML_STRING,
        is_binary_output=False # Expect XML string on stdout
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(stdout_content, EXPECTED_PLIST_XML)

def test_y2p_cli_pipe_xml_sorted():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["y2p", "-s"],
        input_data=UNSORTED_YAML_FOR_PLIST,
        is_binary_output=False
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(stdout_content, EXPECTED_SORTED_PLIST_XML)

def test_y2p_cli_pipe_binary_default():
    stdout_content_bytes, stderr = run_yaplon_pipe_command(
        ["y2p", "-b"],
        input_data=SAMPLE_YAML_STRING,
        is_binary_output=True # Expect binary plist bytes on stdout
    )
    assert stderr == ""
    assert_binary_plist_data_equal(stdout_content_bytes, EXPECTED_DICT_FROM_YAML_FOR_PLIST)
