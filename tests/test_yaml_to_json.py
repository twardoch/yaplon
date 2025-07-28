import pytest
import tempfile
import os
import json
import io
import yaml # For loading expected YAML if needed, though not primary for y2j

from yaplon import reader, writer
from tests.helpers import (
    assert_json_strings_equal,
    run_yaplon_command,
    run_yaplon_pipe_command
)

# --- Test Data ---

SAMPLE_YAML_STRING = """\
name: Test YAML
version: 2.0
active: false
items:
  - "gamma"
  - 42
  - sub_item: "another value"
none_value: null # Or ~
binary_data: !!binary TXlEYXRh # "MyData" base64 encoded
"""

EXPECTED_DICT_FROM_YAML = {
    "name": "Test YAML",
    "version": 2.0,
    "active": False,
    "items": ["gamma", 42, {"sub_item": "another value"}],
    "none_value": None,
    "binary_data": b"MyData"
}

EXPECTED_JSON_PRETTY_DEFAULT_BINARY = """\
{
    "name": "Test YAML",
    "version": 2.0,
    "active": false,
    "items": [
        "gamma",
        42,
        {
            "sub_item": "another value"
        }
    ],
    "none_value": null,
    "binary_data": {
        "__bytes__": true,
        "base64": "TXlEYXRh"
    }
}"""
EXPECTED_JSON_MINIFIED_DEFAULT_BINARY = '{"name":"Test YAML","version":2.0,"active":false,"items":["gamma",42,{"sub_item":"another value"}],"none_value":null,"binary_data":{"__bytes__":true,"base64":"TXlEYXRh"}}'

EXPECTED_JSON_PRETTY_PRESERVE_BINARY = """\
{
    "name": "Test YAML",
    "version": 2.0,
    "active": false,
    "items": [
        "gamma",
        42,
        {
            "sub_item": "another value"
        }
    ],
    "none_value": null,
    "binary_data": "TXlEYXRh"
}"""
EXPECTED_JSON_MINIFIED_PRESERVE_BINARY = '{"name":"Test YAML","version":2.0,"active":false,"items":["gamma",42,{"sub_item":"another value"}],"none_value":null,"binary_data":"TXlEYXRh"}'


UNSORTED_YAML_STRING = """\
z_key: 1
a_key: "value"
m_key:
  - 3
  - 1
  - 2
"""
EXPECTED_JSON_FROM_UNSORTED_YAML_PRETTY = """\
{
    "z_key": 1,
    "a_key": "value",
    "m_key": [
        3,
        1,
        2
    ]
}""" # reader.yaml loads into OrderedDict, writer.json preserves this order by default

EXPECTED_JSON_FROM_UNSORTED_YAML_SORTED_PRETTY = """\
{
    "a_key": "value",
    "m_key": [
        3,
        1,
        2
    ],
    "z_key": 1
}"""
EXPECTED_JSON_FROM_UNSORTED_YAML_SORTED_MINIFIED = '{"a_key":"value","m_key":[3,1,2],"z_key":1}'


# --- Tests ---

def test_yaml_to_json_via_writer_functions():
    with io.StringIO(SAMPLE_YAML_STRING) as string_io_input:
        yaml_data = reader.yaml(string_io_input)
    assert yaml_data == EXPECTED_DICT_FROM_YAML

    string_io_default = io.StringIO()
    writer.json(yaml_data, string_io_default, mini=False, binary=False)
    actual_json_default = string_io_default.getvalue()
    assert_json_strings_equal(actual_json_default, EXPECTED_JSON_PRETTY_DEFAULT_BINARY)

    string_io_preserve_binary = io.StringIO()
    writer.json(yaml_data, string_io_preserve_binary, mini=False, binary=True)
    actual_json_preserve_binary = string_io_preserve_binary.getvalue()
    assert_json_strings_equal(actual_json_preserve_binary, EXPECTED_JSON_PRETTY_PRESERVE_BINARY)

def test_y2j_cli_default():
    output_content, stderr = run_yaplon_command(
        ["y2j"],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_PRETTY_DEFAULT_BINARY)

def test_y2j_cli_minified():
    output_content, stderr = run_yaplon_command(
        ["y2j", "-m"],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_MINIFIED_DEFAULT_BINARY)

def test_y2j_cli_preserve_binary():
    output_content, stderr = run_yaplon_command(
        ["y2j", "-b"],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_PRETTY_PRESERVE_BINARY)

def test_y2j_cli_preserve_binary_minified():
    output_content, stderr = run_yaplon_command(
        ["y2j", "-b", "-m"],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_MINIFIED_PRESERVE_BINARY)

def test_y2j_cli_sorted():
    output_content, stderr = run_yaplon_command(
        ["y2j", "-s"],
        input_content=UNSORTED_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_FROM_UNSORTED_YAML_SORTED_PRETTY)

def test_y2j_cli_sorted_minified():
    output_content, stderr = run_yaplon_command(
        ["y2j", "-s", "-m"],
        input_content=UNSORTED_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_FROM_UNSORTED_YAML_SORTED_MINIFIED)

def test_yaml22json_cli_default():
    output_content, stderr = run_yaplon_command(
        [],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".json",
        cli_tool_name="yaml22json"
    )
    assert stderr == ""
    assert_json_strings_equal(output_content, EXPECTED_JSON_PRETTY_DEFAULT_BINARY)

def test_yaml22json_cli_preserve_binary_minified_sorted():
    output_content, stderr = run_yaplon_command(
        ["-b", "-m", "-s"],
        input_content=UNSORTED_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".json",
        cli_tool_name="yaml22json"
    )
    assert stderr == ""
    expected_json = EXPECTED_JSON_FROM_UNSORTED_YAML_SORTED_MINIFIED # -b no effect on this data
    assert_json_strings_equal(output_content, expected_json)

# --- Piping Tests ---
def test_y2j_cli_pipe_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["y2j"],
        input_data=SAMPLE_YAML_STRING
    )
    assert stderr == ""
    assert_json_strings_equal(stdout_content, EXPECTED_JSON_PRETTY_DEFAULT_BINARY)

def test_y2j_cli_pipe_preserve_binary_minified_sorted():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["y2j", "-b", "-m", "-s"],
        input_data=UNSORTED_YAML_STRING
    )
    assert stderr == ""
    expected_json = EXPECTED_JSON_FROM_UNSORTED_YAML_SORTED_MINIFIED # -b no effect here
    assert_json_strings_equal(stdout_content, expected_json)

def test_yaml22json_cli_pipe_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        [],
        input_data=SAMPLE_YAML_STRING,
        cli_tool_name="yaml22json"
    )
    assert stderr == ""
    assert_json_strings_equal(stdout_content, EXPECTED_JSON_PRETTY_DEFAULT_BINARY)
