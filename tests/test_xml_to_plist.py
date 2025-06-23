import pytest
import tempfile
import os
import io
import plistlib
import xmltodict

from yaplon import reader, writer
from tests.helpers import (
    assert_plist_xml_strings_equal,
    assert_binary_plist_data_equal,
    run_yaplon_command,
    run_yaplon_pipe_command
)

# --- Test Data ---

SAMPLE_XML_STRING_NO_EMPTY_VAL = """\
<?xml version="1.0" encoding="utf-8"?>
<root>
    <name>Test XML for Plist</name>
    <version>5.0</version>
    <active>true</active>
    <count>256</count>
    <items>
        <item>apple</item>
        <item>banana</item>
    </items>
    <binary_data>QmFzZTY0RGF0YQ==</binary_data> <!-- "Base64Data" string -->
</root>
"""

EXPECTED_DICT_FROM_XML_NO_EMPTY_VAL = xmltodict.parse(SAMPLE_XML_STRING_NO_EMPTY_VAL)

EXPECTED_PLIST_XML_NO_EMPTY_VAL = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>root</key>
	<dict>
		<key>active</key>
		<true/>
		<key>binary_data</key>
		<string>QmFzZTY0RGF0YQ==</string>
		<key>count</key>
		<integer>256</integer>
		<key>items</key>
		<dict>
			<key>item</key>
			<array>
				<string>apple</string>
				<string>banana</string>
			</array>
		</dict>
		<key>name</key>
		<string>Test XML for Plist</string>
		<key>version</key>
		<real>5.0</real>
	</dict>
</dict>
</plist>
"""
EXPECTED_PLIST_DICT_NO_EMPTY_VAL = {
    "root": {
        "active": True,
        "binary_data": "QmFzZTY0RGF0YQ==",
        "count": 256,
        "items": {"item": ["apple", "banana"]},
        "name": "Test XML for Plist",
        "version": 5.0,
    }
}

# --- Tests ---

def test_xml_to_plist_via_writer_functions():
    with io.StringIO(SAMPLE_XML_STRING_NO_EMPTY_VAL) as string_io_input:
        xml_data_dict = reader.xml(string_io_input)

    assert xmltodict.parse(xmltodict.unparse(xml_data_dict)) == EXPECTED_DICT_FROM_XML_NO_EMPTY_VAL

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".plist", encoding='utf-8') as tmp_xml_plist_file:
        xml_plist_filepath = tmp_xml_plist_file.name
    try:
        writer.plist(xml_data_dict, xml_plist_filepath, binary=False)
        with open(xml_plist_filepath, "r", encoding='utf-8') as f:
            actual_xml_plist = f.read()
        assert_plist_xml_strings_equal(actual_xml_plist, EXPECTED_PLIST_XML_NO_EMPTY_VAL)
    finally:
        os.remove(xml_plist_filepath)

    with tempfile.NamedTemporaryFile(mode="wb+", delete=False, suffix=".plist") as tmp_bin_plist_file:
        bin_plist_filepath = tmp_bin_plist_file.name
    try:
        writer.plist(xml_data_dict, bin_plist_filepath, binary=True)
        with open(bin_plist_filepath, "rb") as f:
            actual_binary_plist_bytes = f.read()
        assert_binary_plist_data_equal(actual_binary_plist_bytes, EXPECTED_PLIST_DICT_NO_EMPTY_VAL)
    finally:
        os.remove(bin_plist_filepath)

def test_x2p_cli_xml_default():
    output_content, stderr = run_yaplon_command(
        ["x2p"],
        input_content=SAMPLE_XML_STRING_NO_EMPTY_VAL,
        input_suffix=".xml",
        output_suffix=".plist",
        is_binary_output=False
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(output_content, EXPECTED_PLIST_XML_NO_EMPTY_VAL)

def test_x2p_cli_binary_output():
    output_content_bytes, stderr = run_yaplon_command(
        ["x2p", "-b"],
        input_content=SAMPLE_XML_STRING_NO_EMPTY_VAL,
        input_suffix=".xml",
        output_suffix=".plist",
        is_binary_output=True
    )
    assert stderr == ""
    assert_binary_plist_data_equal(output_content_bytes, EXPECTED_PLIST_DICT_NO_EMPTY_VAL)

def test_xml22plist_cli_default():
    output_content, stderr = run_yaplon_command(
        [],
        input_content=SAMPLE_XML_STRING_NO_EMPTY_VAL,
        input_suffix=".xml",
        output_suffix=".plist",
        cli_tool_name="xml22plist",
        is_binary_output=False
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(output_content, EXPECTED_PLIST_XML_NO_EMPTY_VAL)

# --- Piping Tests ---
def test_x2p_cli_pipe_xml_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["x2p"],
        input_data=SAMPLE_XML_STRING_NO_EMPTY_VAL,
        is_binary_output=False
    )
    assert stderr == ""
    assert_plist_xml_strings_equal(stdout_content, EXPECTED_PLIST_XML_NO_EMPTY_VAL)

def test_x2p_cli_pipe_binary_output():
    stdout_content_bytes, stderr = run_yaplon_pipe_command(
        ["x2p", "-b"],
        input_data=SAMPLE_XML_STRING_NO_EMPTY_VAL,
        is_binary_output=True
    )
    assert stderr == ""
    assert_binary_plist_data_equal(stdout_content_bytes, EXPECTED_PLIST_DICT_NO_EMPTY_VAL)

# TODO: Add sorting, namespace, error handling, None value, and attribute tests.
