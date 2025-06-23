import pytest
import tempfile
import os
import io
import json
import xmltodict

from yaplon import reader, writer
from tests.helpers import (
    assert_json_strings_equal,
    run_yaplon_command,
    run_yaplon_pipe_command
)

# --- Test Data ---

SAMPLE_XML_STRING = """\
<?xml version="1.0" encoding="utf-8"?>
<root>
	<name>Test XML to JSON</name>
	<version>1.0</version>
	<items>1</items>
	<items>two</items>
	<details>
		<status>active</status>
		<count>42</count>
	</details>
    <empty_tag></empty_tag>
    <tag_with_attributes attr_key="attr_value">content</tag_with_attributes>
</root>
"""

# reader.xml uses xmltodict.parse(..., dict_constructor=OrderedDict)
# This is what we expect reader.xml to produce from SAMPLE_XML_STRING
EXPECTED_DICT_FROM_XML = xmltodict.parse(SAMPLE_XML_STRING)


EXPECTED_JSON_PRETTY_FROM_XML = """\
{
    "root": {
        "name": "Test XML to JSON",
        "version": "1.0",
        "items": [
            "1",
            "two"
        ],
        "details": {
            "status": "active",
            "count": "42"
        },
        "empty_tag": null,
        "tag_with_attributes": {
            "@attr_key": "attr_value",
            "#text": "content"
        }
    }
}"""

EXPECTED_JSON_MINIFIED_FROM_XML = '{"root":{"name":"Test XML to JSON","version":"1.0","items":["1","two"],"details":{"status":"active","count":"42"},"empty_tag":null,"tag_with_attributes":{"@attr_key":"attr_value","#text":"content"}}}'

XML_WITH_POTENTIAL_BINARY = """\
<?xml version="1.0" encoding="utf-8"?>
<data>
    <description>Some data</description>
    <binary_field>SGVsbG8=</binary_field> <!-- "Hello" -->
</data>
"""
EXPECTED_JSON_FROM_XML_WITH_BINARY_STRING = """\
{
    "data": {
        "description": "Some data",
        "binary_field": "SGVsbG8="
    }
}"""


XML_FOR_SORTING_TEST = """\
<config>
    <zulu>last</zulu>
    <alpha>first</alpha>
    <beta>middle</beta>
</config>
"""
EXPECTED_JSON_FROM_XML_SORTED = """\
{
    "config": {
        "alpha": "first",
        "beta": "middle",
        "zulu": "last"
    }
}"""

# --- Tests ---

def test_xml_to_json_via_writer_functions():
    with io.StringIO(SAMPLE_XML_STRING) as string_io_input:
        xml_data_dict = reader.xml(string_io_input)

    # Compare using json.dumps to handle OrderedDict vs dict for assertion
    assert json.dumps(xml_data_dict, sort_keys=True) == json.dumps(EXPECTED_DICT_FROM_XML, sort_keys=True)

    string_io_json = io.StringIO()
    writer.json(xml_data_dict, string_io_json, mini=False, binary=False)
    actual_json = string_io_json.getvalue()
    assert_json_strings_equal(actual_json, EXPECTED_JSON_PRETTY_FROM_XML)

def test_x2j_cli_default():
    output_content, stderr = run_yaplon_command(
        ["x2j"],
        input_content=SAMPLE_XML_STRING,
        input_suffix=".xml",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_PRETTY_FROM_XML)

def test_x2j_cli_minified():
    output_content, stderr = run_yaplon_command(
        ["x2j", "-m"],
        input_content=SAMPLE_XML_STRING,
        input_suffix=".xml",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_MINIFIED_FROM_XML)

def test_x2j_cli_invalid_binary_option():
    with pytest.raises(pytest.fail.Exception) as excinfo:
        run_yaplon_command(
            ["x2j", "-b"],
            input_content=XML_WITH_POTENTIAL_BINARY,
            input_suffix=".xml",
            output_suffix=".json"
        )
    assert "Error: No such option: -b" in str(excinfo.value)

def test_x2j_cli_sorted():
    output_content, stderr = run_yaplon_command(
        ["x2j", "-s"],
        input_content=XML_FOR_SORTING_TEST,
        input_suffix=".xml",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_FROM_XML_SORTED)

def test_xml22json_cli_default():
    output_content, stderr = run_yaplon_command(
        [],
        input_content=SAMPLE_XML_STRING,
        input_suffix=".xml",
        output_suffix=".json",
        cli_tool_name="xml22json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_PRETTY_FROM_XML)

def test_xml22json_cli_minified_sorted():
    output_content, stderr = run_yaplon_command(
        ["-m", "-s"],
        input_content=XML_FOR_SORTING_TEST,
        input_suffix=".xml",
        output_suffix=".json",
        cli_tool_name="xml22json"
    )
    assert stderr == ""
    expected_minified_sorted = '{"config":{"alpha":"first","beta":"middle","zulu":"last"}}'
    assert_json_strings_equal(output_content, expected_minified_sorted)

# --- Piping Tests ---
def test_x2j_cli_pipe_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["x2j"],
        input_data=SAMPLE_XML_STRING
    )
    assert stderr == ""
    assert_json_strings_equal(stdout_content, EXPECTED_JSON_PRETTY_FROM_XML)

def test_x2j_cli_pipe_minified_sorted():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["x2j", "-m", "-s"],
        input_data=XML_FOR_SORTING_TEST
    )
    assert stderr == ""
    expected_minified_sorted = '{"config":{"alpha":"first","beta":"middle","zulu":"last"}}'
    assert_json_strings_equal(stdout_content, expected_minified_sorted)
