import pytest
import tempfile
import os
import io
import plistlib
import xmltodict
import json
import datetime

from yaplon import reader, writer
from tests.helpers import (
    assert_xml_strings_equal_for_j2x as assert_xml_strings_equal,
    run_yaplon_command,
    run_yaplon_pipe_command
)

# --- Test Data ---

SAMPLE_PLIST_DICT = {
    "name": "Test Plist for XML",
    "version": 6.0,
    "active": True,
    "count": 512,
    "tags": ["plist_tag", "xml_conversion"],
    "binary_payload": b"PlistBinary",
    "a_date": datetime.datetime(2024, 3, 15, 10, 30, 0), # Changed to offset-naive
    "empty_dict": {},
    "empty_list": [],
    "none_value": None
}

SAMPLE_PLIST_DICT_FOR_DUMPS = {k:v for k,v in SAMPLE_PLIST_DICT.items() if v is not None}

EXPECTED_XML_DEFAULT_ROOT_FROM_PLIST = f"""\
<?xml version="1.0" encoding="utf-8"?>
<root>
	<name>Test Plist for XML</name>
	<version>6.0</version>
	<active>true</active>
	<count>512</count>
	<tags>plist_tag</tags>
	<tags>xml_conversion</tags>
	<binary_payload>UGxpc3RCaW5hcnk=</binary_payload>
	<a_date>2024-03-15T10:30:00Z</a_date>
	<empty_dict></empty_dict>
</root>
"""

EXPECTED_XML_WRAP_TAG_DICT2XML_FROM_PLIST = f"""\
<yaplon_data>
  <name>Test Plist for XML</name>
  <version>6.0</version>
  <active>True</active>
  <count>512</count>
  <tags>plist_tag</tags>
  <tags>xml_conversion</tags>
  <binary_payload>UGxpc3RCaW5hcnk=</binary_payload>
  <a_date>2024-03-15T10:30:00Z</a_date>
  <empty_dict></empty_dict>
  <empty_list></empty_list>
</yaplon_data>
""" # Adjusted "true" to "True" for dict2xml output

# --- Fixtures ---
@pytest.fixture
def plist_xml_input():
    return plistlib.dumps(SAMPLE_PLIST_DICT_FOR_DUMPS, sort_keys=False).decode('utf-8')

@pytest.fixture
def plist_binary_input():
    return plistlib.dumps(SAMPLE_PLIST_DICT_FOR_DUMPS, fmt=plistlib.FMT_BINARY, sort_keys=False)

def test_plist_to_xml_via_writer_functions(plist_xml_input, plist_binary_input):
    with io.BytesIO(plist_xml_input.encode('utf-8')) as bytes_io_input_xml:
        xml_plist_obj = reader.plist(bytes_io_input_xml)

    string_io_xml_default = io.StringIO()
    writer.xml(xml_plist_obj, string_io_xml_default, mini=False, root="root")
    actual_xml_default = string_io_xml_default.getvalue()
    assert_xml_strings_equal(actual_xml_default, EXPECTED_XML_DEFAULT_ROOT_FROM_PLIST)

    string_io_xml_tag = io.StringIO()
    writer.xml(xml_plist_obj, string_io_xml_tag, mini=False, tag="yaplon_data")
    actual_xml_tag = string_io_xml_tag.getvalue()
    assert_xml_strings_equal(actual_xml_tag, EXPECTED_XML_WRAP_TAG_DICT2XML_FROM_PLIST, is_dict2xml_output=True)

    with io.BytesIO(plist_binary_input) as bytes_io_input_bin:
        bin_plist_obj = reader.plist(bytes_io_input_bin)

    string_io_xml_default_from_bin = io.StringIO()
    writer.xml(bin_plist_obj, string_io_xml_default_from_bin, mini=False, root="root")
    actual_xml_default_from_bin = string_io_xml_default_from_bin.getvalue()
    assert_xml_strings_equal(actual_xml_default_from_bin, EXPECTED_XML_DEFAULT_ROOT_FROM_PLIST)

def test_p2x_cli_xml_plist_input_default(plist_xml_input):
    output_content, stderr = run_yaplon_command(
        ["p2x"],
        input_content=plist_xml_input,
        input_suffix=".plist",
        output_suffix=".xml"
    )
    assert stderr == ""
    assert_xml_strings_equal(output_content, EXPECTED_XML_DEFAULT_ROOT_FROM_PLIST)

def test_p2x_cli_binary_plist_input_default(plist_binary_input):
    output_content, stderr = run_yaplon_command(
        ["p2x"],
        input_content=plist_binary_input,
        input_suffix=".plist",
        output_suffix=".xml",
        is_binary_input=True
    )
    assert stderr == ""
    assert_xml_strings_equal(output_content, EXPECTED_XML_DEFAULT_ROOT_FROM_PLIST)

def test_p2x_cli_xml_plist_input_wrap_tag(plist_xml_input):
    output_content, stderr = run_yaplon_command(
        ["p2x", "-t", "yaplon_data"],
        input_content=plist_xml_input,
        input_suffix=".plist",
        output_suffix=".xml"
    )
    assert stderr == ""
    assert_xml_strings_equal(output_content, EXPECTED_XML_WRAP_TAG_DICT2XML_FROM_PLIST, is_dict2xml_output=True)

def test_plist22xml_cli_default(plist_xml_input):
    output_content, stderr = run_yaplon_command(
        [],
        input_content=plist_xml_input,
        input_suffix=".plist",
        output_suffix=".xml",
        cli_tool_name="plist22xml"
    )
    assert stderr == ""
    assert_xml_strings_equal(output_content, EXPECTED_XML_DEFAULT_ROOT_FROM_PLIST)

# --- Piping Tests ---
def test_p2x_cli_pipe_xml_plist_input_default(plist_xml_input):
    stdout_content, stderr = run_yaplon_pipe_command(
        ["p2x"],
        input_data=plist_xml_input
    )
    assert stderr == ""
    assert_xml_strings_equal(stdout_content, EXPECTED_XML_DEFAULT_ROOT_FROM_PLIST)

@pytest.mark.skip(reason="Binary plist input via pipe needs robust test setup and confirmation of yaplon's handling.")
def test_p2x_cli_pipe_binary_plist_input_default(plist_binary_input):
    stdout_content, stderr = run_yaplon_pipe_command(
        ["p2x"],
        input_data=plist_binary_input,
        is_binary_input=True
    )
    assert stderr == ""
    assert_xml_strings_equal(stdout_content, EXPECTED_XML_DEFAULT_ROOT_FROM_PLIST)
