import pytest
import tempfile
import os
import io
import json
import xmltodict # For robust XML comparison

from yaplon import reader, writer
from tests.helpers import (
    assert_xml_strings_equal_for_j2x, # Renamed in helpers
    run_yaplon_command,
    run_yaplon_pipe_command
)

# --- Test Data ---

SAMPLE_JSON_STRING = '{"name": "Test JSON for XML", "version": 1.0, "items": [1, "two"], "details": {"status": "active", "count": 42}}'
SAMPLE_JSON_DICT_TYPED = {"name": "Test JSON for XML", "version": 1.0, "items": [1, "two"], "details": {"status": True, "count": 42}}


EXPECTED_XML_PRETTY_DEFAULT_ROOT = """\
<?xml version="1.0" encoding="utf-8"?>
<root>
	<name>Test JSON for XML</name>
	<version>1.0</version>
	<items>1</items>
	<items>two</items>
	<details>
		<status>active</status>
		<count>42</count>
	</details>
</root>
"""
EXPECTED_XML_MINIFIED_DEFAULT_ROOT = '<?xml version="1.0" encoding="utf-8"?><root><name>Test JSON for XML</name><version>1.0</version><items>1</items><items>two</items><details><status>active</status><count>42</count></details></root>'

EXPECTED_XML_PRETTY_CUSTOM_ROOT = """\
<?xml version="1.0" encoding="utf-8"?>
<customRoot>
	<name>Test JSON for XML</name>
	<version>1.0</version>
	<items>1</items>
	<items>two</items>
	<details>
		<status>active</status>
		<count>42</count>
	</details>
</customRoot>
"""

EXPECTED_XML_PRETTY_WRAP_TAG_DICT2XML = """\
<data>
  <name>Test JSON for XML</name>
  <version>1.0</version>
  <items>1</items>
  <items>two</items>
  <details>
    <status>active</status>
    <count>42</count>
  </details>
</data>
"""

JSON_SINGLE_KEY_STRING = '{"mydata": {"item": "value", "number": 10}}'
EXPECTED_XML_SINGLE_KEY_ROOT = """\
<?xml version="1.0" encoding="utf-8"?>
<mydata>
	<item>value</item>
	<number>10</number>
</mydata>
"""

JSON_WITH_INTERNAL_BYTES_REPR = '{"field": "text", "binary": {"__bytes__": true, "base64": "SGVsbG8="}}'
EXPECTED_XML_WITH_BYTES_AS_B64_STRING = """\
<?xml version="1.0" encoding="utf-8"?>
<root>
	<field>text</field>
	<binary>SGVsbG8=</binary>
</root>
"""

# --- Tests ---

def test_json_to_xml_via_writer_functions():
    with io.StringIO(SAMPLE_JSON_STRING) as string_io_input:
        json_data = reader.json(string_io_input)

    string_io_xml_default = io.StringIO()
    writer.xml(json_data, string_io_xml_default, mini=False, root="root")
    actual_xml_default = string_io_xml_default.getvalue()
    assert_xml_strings_equal_for_j2x(actual_xml_default, EXPECTED_XML_PRETTY_DEFAULT_ROOT)

    string_io_xml_mini = io.StringIO()
    writer.xml(json_data, string_io_xml_mini, mini=True, root="root")
    actual_xml_mini = string_io_xml_mini.getvalue()
    assert_xml_strings_equal_for_j2x(actual_xml_mini, EXPECTED_XML_MINIFIED_DEFAULT_ROOT)

    string_io_xml_tag = io.StringIO()
    writer.xml(json_data, string_io_xml_tag, mini=False, tag="data")
    actual_xml_tag = string_io_xml_tag.getvalue()
    assert_xml_strings_equal_for_j2x(actual_xml_tag, EXPECTED_XML_PRETTY_WRAP_TAG_DICT2XML, is_dict2xml_output=True)

def test_j2x_cli_default():
    output_content, stderr = run_yaplon_command(
        ["j2x"],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".xml"
    )
    assert stderr == ""
    assert_xml_strings_equal_for_j2x(output_content, EXPECTED_XML_PRETTY_DEFAULT_ROOT)

def test_j2x_cli_minified():
    output_content, stderr = run_yaplon_command(
        ["j2x", "-m"],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".xml"
    )
    assert stderr == ""
    assert_xml_strings_equal_for_j2x(output_content, EXPECTED_XML_MINIFIED_DEFAULT_ROOT)

def test_j2x_cli_custom_root():
    output_content, stderr = run_yaplon_command(
        ["j2x", "-R", "customRoot"],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".xml"
    )
    assert stderr == ""
    assert_xml_strings_equal_for_j2x(output_content, EXPECTED_XML_PRETTY_CUSTOM_ROOT)

def test_j2x_cli_single_key_json_as_root():
    output_content, stderr = run_yaplon_command(
        ["j2x"],
        input_content=JSON_SINGLE_KEY_STRING,
        input_suffix=".json",
        output_suffix=".xml"
    )
    assert stderr == ""
    assert_xml_strings_equal_for_j2x(output_content, EXPECTED_XML_SINGLE_KEY_ROOT)

def test_j2x_cli_wrap_tag():
    output_content, stderr = run_yaplon_command(
        ["j2x", "-t", "data"],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".xml"
    )
    assert stderr == ""
    assert_xml_strings_equal_for_j2x(output_content, EXPECTED_XML_PRETTY_WRAP_TAG_DICT2XML, is_dict2xml_output=True)

def test_json22xml_cli_default():
    output_content, stderr = run_yaplon_command(
        [],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".xml",
        cli_tool_name="json22xml"
    )
    assert stderr == ""
    assert_xml_strings_equal_for_j2x(output_content, EXPECTED_XML_PRETTY_DEFAULT_ROOT)

def test_json22xml_cli_minified_custom_root():
    output_content, stderr = run_yaplon_command(
        ["-m", "-R", "customRoot"],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".xml",
        cli_tool_name="json22xml"
    )
    assert stderr == ""
    expected_minified_custom_root = '<?xml version="1.0" encoding="utf-8"?><customRoot><name>Test JSON for XML</name><version>1.0</version><items>1</items><items>two</items><details><status>active</status><count>42</count></details></customRoot>'
    assert_xml_strings_equal_for_j2x(output_content, expected_minified_custom_root)

# --- Piping Tests ---
def test_j2x_cli_pipe_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["j2x"],
        input_data=SAMPLE_JSON_STRING
    )
    assert stderr == ""
    assert_xml_strings_equal_for_j2x(stdout_content, EXPECTED_XML_PRETTY_DEFAULT_ROOT)

def test_j2x_cli_pipe_wrap_tag_minified():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["j2x", "-t", "data", "-m"],
        input_data=SAMPLE_JSON_STRING
    )
    assert stderr == ""
    expected_minified_dict2xml = '<data><name>Test JSON for XML</name><version>1.0</version><items>1</items><items>two</items><details><status>active</status><count>42</count></details></data>'
    assert_xml_strings_equal_for_j2x(stdout_content, expected_minified_dict2xml, is_dict2xml_output=True)

def test_j2x_cli_with_internal_bytes():
    output_content, stderr = run_yaplon_command(
        ["j2x"],
        input_content=JSON_WITH_INTERNAL_BYTES_REPR,
        input_suffix=".json",
        output_suffix=".xml"
    )
    assert stderr == ""
    assert_xml_strings_equal_for_j2x(output_content, EXPECTED_XML_WITH_BYTES_AS_B64_STRING)
