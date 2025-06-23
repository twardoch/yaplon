import pytest
import tempfile
import os
import io
import yaml # For loading YAML to compare
import xmltodict # For parsing XML to dict for comparison
import json # Added import

from yaplon import reader, writer
from tests.helpers import (
    assert_yaml_strings_equal,
    run_yaplon_command,
    run_yaplon_pipe_command
)

# --- Test Data ---

SAMPLE_XML_STRING = """\
<?xml version="1.0" encoding="utf-8"?>
<root>
	<name>Test XML to YAML</name>
	<version>2.5</version>
	<active>true</active>
	<tags>
		<tag>xml_tag</tag>
		<tag>conversion</tag>
	</tags>
    <binary_content>VGhpcyBpcyBST0NLUw==</binary_content> <!-- "This is ROCKS" -->
    <empty_node></empty_node>
</root>
"""

# Expected Python dictionary that reader.xml (via xmltodict) would produce.
# Note: xmltodict will parse '2.5', 'true', 'xml_tag', etc., as strings.
# Empty nodes become None.
EXPECTED_DICT_FROM_XML_FOR_YAML = {
    "root": {
        "name": "Test XML to YAML",
        "version": "2.5",
        "active": "true",
        "tags": {
            "tag": ["xml_tag", "conversion"] # xmltodict makes list for repeated elements
        },
        "binary_content": "VGhpcyBpcyBST0NLUw==", # String from XML
        "empty_node": None
    }
}
# The `writer.yaml` will then process this dictionary.
# `oyaml.py`'s dumper will convert actual Python booleans/floats/ints correctly.
# Strings "true", "2.5" will remain strings in YAML.
# `bytes` objects (if any) would become `!!binary`.
# Since `reader.xml` produces strings here, they'll be YAML strings.

EXPECTED_YAML_PRETTY = """\
root:
  active: 'true'
  binary_content: VGhpcyBpcyBST0NLUw==
  empty_node: null
  name: Test XML to YAML
  tags:
    tag:
    - xml_tag
    - conversion
  version: '2.5'
""" # PyYAML sorts keys by default for block style. Quotes strings if they look like bools/numbers.

EXPECTED_YAML_MINIFIED = "{root: {active: 'true', binary_content: VGhpcyBpcyBST0NLUw==, empty_node: null, name: Test XML to YAML, tags: {tag: [xml_tag, conversion]}, version: '2.5'}}\n"
# Minified YAML (flow style) from OrderedDict (which reader.xml produces) should preserve order of keys from XML.
# Order in SAMPLE_XML_STRING: name, version, active, tags, binary_content, empty_node
EXPECTED_YAML_MINIFIED_ORDERED = "{root: {name: Test XML to YAML, version: '2.5', active: 'true', tags: {tag: [xml_tag, conversion]}, binary_content: VGhpcyBpcyBST0NLUw==, empty_node: null}}\n"


XML_FOR_SORTING_X2Y = """\
<data>
    <zebra>animal</zebra>
    <apple>fruit</apple>
    <banana>fruit</banana>
</data>
"""
# Expected YAML from sorted XML (keys sorted: apple, banana, zebra)
EXPECTED_YAML_SORTED_PRETTY_X2Y = """\
data:
  apple: fruit
  banana: fruit
  zebra: animal
"""
EXPECTED_YAML_SORTED_MINIFIED_X2Y = "{data: {apple: fruit, banana: fruit, zebra: animal}}\n"


# --- Tests ---

def test_xml_to_yaml_via_writer_functions():
    with io.StringIO(SAMPLE_XML_STRING) as string_io_input:
        # reader.xml uses xmltodict.parse(..., dict_constructor=OrderedDict)
        xml_data_dict = reader.xml(string_io_input)

    # Verify reader.xml output (optional, but good for sanity)
    # Using json.dumps for simple comparison of structure, acknowledging types will be strings
    assert json.dumps(xml_data_dict, sort_keys=True) == json.dumps(EXPECTED_DICT_FROM_XML_FOR_YAML, sort_keys=True)

    # Test writer.yaml (default pretty)
    string_io_pretty = io.StringIO()
    writer.yaml(xml_data_dict, string_io_pretty, mini=False)
    actual_yaml_pretty = string_io_pretty.getvalue()
    assert_yaml_strings_equal(actual_yaml_pretty, EXPECTED_YAML_PRETTY)

    # Test writer.yaml (minified)
    string_io_mini = io.StringIO()
    writer.yaml(xml_data_dict, string_io_mini, mini=True)
    actual_yaml_mini = string_io_mini.getvalue()
    # For minified, yaplon aims to preserve order from OrderedDict.
    assert_yaml_strings_equal(actual_yaml_mini.strip(), EXPECTED_YAML_MINIFIED_ORDERED.strip())


# CLI Tests
def test_x2y_cli_default():
    output_content, stderr = run_yaplon_command(
        ["x2y"],
        input_content=SAMPLE_XML_STRING,
        input_suffix=".xml",
        output_suffix=".yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content, EXPECTED_YAML_PRETTY)

def test_x2y_cli_minified():
    output_content, stderr = run_yaplon_command(
        ["x2y", "-m"],
        input_content=SAMPLE_XML_STRING,
        input_suffix=".xml",
        output_suffix=".yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content.strip(), EXPECTED_YAML_MINIFIED_ORDERED.strip())

def test_x2y_cli_sorted():
    output_content, stderr = run_yaplon_command(
        ["x2y", "-s"],
        input_content=XML_FOR_SORTING_X2Y,
        input_suffix=".xml",
        output_suffix=".yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content, EXPECTED_YAML_SORTED_PRETTY_X2Y)

def test_xml22yaml_cli_default():
    output_content, stderr = run_yaplon_command(
        [],
        input_content=SAMPLE_XML_STRING,
        input_suffix=".xml",
        output_suffix=".yaml",
        cli_tool_name="xml22yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content, EXPECTED_YAML_PRETTY)

def test_xml22yaml_cli_minified_sorted():
    output_content, stderr = run_yaplon_command(
        ["-m", "-s"],
        input_content=XML_FOR_SORTING_X2Y,
        input_suffix=".xml",
        output_suffix=".yaml",
        cli_tool_name="xml22yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content.strip(), EXPECTED_YAML_SORTED_MINIFIED_X2Y.strip())

# --- Piping Tests ---
def test_x2y_cli_pipe_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["x2y"],
        input_data=SAMPLE_XML_STRING
    )
    assert stderr == ""
    assert_yaml_strings_equal(stdout_content, EXPECTED_YAML_PRETTY)

def test_x2y_cli_pipe_minified_sorted():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["x2y", "-m", "-s"],
        input_data=XML_FOR_SORTING_X2Y
    )
    assert stderr == ""
    assert_yaml_strings_equal(stdout_content.strip(), EXPECTED_YAML_SORTED_MINIFIED_X2Y.strip())

# TODO:
# - Test -N (namespaces) option for X2Y.
# - Error handling for invalid XML input.
# - XML with attributes: how are they represented in YAML by default?
#   xmltodict parses `<tag attr="val">text</tag>` to `{'tag': {'@attr': 'val', '#text': 'text'}}`.
#   This structure would then be dumped to YAML. This is covered by SAMPLE_XML_STRING via JSON to XML tests implicitly.
#   For X2Y, if XML has attributes, they become dicts with '@' prefixes in YAML.
#   Example: <node id="1">value</node> -> YAML: node: {'@id': '1', '#text': 'value'} (or similar based on PyYAML)
#   This should be tested explicitly for X2Y.
#
# - Binary data: `reader.xml` produces a string for `<binary_field>SGVsbG8=</binary_field>`.
#   `writer.yaml` takes this string. PyYAML will dump it as a plain string, not `!!binary`.
#   If the goal is `XML <data> -> Python bytes -> YAML !!binary`, then `reader.xml` needs enhancement
#   to detect/convert base64 strings to `bytes` (perhaps with a flag or heuristic).
#   Current tests reflect that `<binary_content>VGhpcyBpcyBST0NLUw==</binary_content>` becomes a YAML string.
#   The `EXPECTED_YAML_PRETTY` shows `binary_content: VGhpcyBpcyBST0NLUw==` (a string). This is correct for current implementation.
#   The `EXPECTED_DICT_FROM_XML_FOR_YAML` also shows it as string. This is consistent.
#
# Key order for X2Y:
# - `reader.xml` uses `xmltodict.parse(..., dict_constructor=OrderedDict)`, so order from XML is preserved in the Python dict.
# - `writer.yaml` -> `oyaml.yaml_dumps`.
#   - If `mini=False` (pretty): PyYAML's default `sort_keys=True` applies. Output YAML keys are sorted.
#     `EXPECTED_YAML_PRETTY` reflects this.
#   - If `mini=True` (minified): `oyaml.yaml_dumps` uses `default_flow_style=True`. PyYAML's `dump` with
#     `OrderedDict` input and `default_flow_style=True` should preserve key order.
#     `EXPECTED_YAML_MINIFIED_ORDERED` reflects this.
# - `-s` flag for X2Y sorts the `OrderedDict` from `reader.xml` before passing to `writer.yaml`.
#   This sorted order is then reflected in both pretty (additionally sorted by PyYAML) and minified YAML.
#   `EXPECTED_YAML_SORTED_PRETTY_X2Y` and `EXPECTED_YAML_SORTED_MINIFIED_X2Y` reflect this.
# The current test data and expectations seem consistent with these behaviors.
