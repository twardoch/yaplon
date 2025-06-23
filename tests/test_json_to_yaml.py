import pytest
import tempfile
import os
import io
import json
import yaml # For loading YAML to compare Python objects

from yaplon import reader, writer
from tests.helpers import (
    assert_yaml_strings_equal,
    run_yaplon_command,
    run_yaplon_pipe_command
)

# --- Test Data ---

SAMPLE_JSON_STRING = '{"name": "Test JSON", "version": 1.0, "active": true, "items": ["one", 2, {"sub_item": "value"}], "none_value": null}'
SAMPLE_JSON_DICT = {"name": "Test JSON", "version": 1.0, "active": True, "items": ["one", 2, {"sub_item": "value"}], "none_value": None}

# Expected YAML output (standard, pretty-printed)
# PyYAML default `sort_keys=True` for block style, so keys are alphabetical.
EXPECTED_YAML_PRETTY = """\
active: true
items:
- one
- 2
- sub_item: value
name: Test JSON
none_value: null
version: 1.0
"""

# Expected YAML output (minified - flow style)
# yaplon.oyaml.yaml_dumps with compact=True passes default_flow_style=True to PyYAML's dump.
# PyYAML's dump with default_flow_style=True and OrderedDict input preserves order.
EXPECTED_YAML_MINIFIED = "{name: Test JSON, version: 1.0, active: true, items: [one, 2, {sub_item: value}], none_value: null}\n"


UNSORTED_JSON_STRING_FOR_YAML = '{"z_key": 1, "a_key": "value", "m_key": [3, 1, 2]}'
# Sorted output (pretty)
EXPECTED_YAML_SORTED_PRETTY = """\
a_key: value
m_key:
- 3
- 1
- 2
z_key: 1
"""
# Sorted output (minified - flow style, order from sorted OrderedDict)
EXPECTED_YAML_SORTED_MINIFIED = "{a_key: value, m_key: [3, 1, 2], z_key: 1}\n"


JSON_STRING_REPRESENTING_BYTES = '{"text": "abc", "data": {"__bytes__": true, "base64": "SGVsbG8="}}' # "Hello"
EXPECTED_YAML_WITH_BINARY_TAG = """\
data: !!binary SGVsbG8=
text: abc
"""
JSON_DICT_WITH_ACTUAL_BYTES = {"text": "abc", "data": b"Hello"}


# --- Tests ---

def test_json_to_yaml_via_writer_functions():
    # Use io.StringIO as reader.json expects a file-like object
    with io.StringIO(SAMPLE_JSON_STRING) as string_io_input:
        json_data = reader.json(string_io_input) # reader.json loads into OrderedDict

    # Test default pretty print
    string_io_pretty = io.StringIO()
    writer.yaml(json_data, string_io_pretty, mini=False)
    actual_yaml_pretty = string_io_pretty.getvalue()
    assert_yaml_strings_equal(actual_yaml_pretty, EXPECTED_YAML_PRETTY)

    string_io_mini = io.StringIO()
    writer.yaml(json_data, string_io_mini, mini=True)
    actual_yaml_mini = string_io_mini.getvalue()
    assert_yaml_strings_equal(actual_yaml_mini.strip(), EXPECTED_YAML_MINIFIED.strip())


def test_j2y_cli_default():
    output_content, stderr = run_yaplon_command(
        ["j2y"],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content, EXPECTED_YAML_PRETTY)

def test_j2y_cli_minified():
    output_content, stderr = run_yaplon_command(
        ["j2y", "-m"],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content.strip(), EXPECTED_YAML_MINIFIED.strip())

def test_j2y_cli_sorted():
    output_content, stderr = run_yaplon_command(
        ["j2y", "-s"],
        input_content=UNSORTED_JSON_STRING_FOR_YAML,
        input_suffix=".json",
        output_suffix=".yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content, EXPECTED_YAML_SORTED_PRETTY)

def test_json22yaml_cli_default():
    output_content, stderr = run_yaplon_command(
        [],
        input_content=SAMPLE_JSON_STRING,
        input_suffix=".json",
        output_suffix=".yaml",
        cli_tool_name="json22yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content, EXPECTED_YAML_PRETTY)

def test_json22yaml_cli_minified_sorted():
    output_content, stderr = run_yaplon_command(
        ["-m", "-s"],
        input_content=UNSORTED_JSON_STRING_FOR_YAML,
        input_suffix=".json",
        output_suffix=".yaml",
        cli_tool_name="json22yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content.strip(), EXPECTED_YAML_SORTED_MINIFIED.strip())

# --- Piping Tests ---
def test_j2y_cli_pipe_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["j2y"],
        input_data=SAMPLE_JSON_STRING
    )
    assert stderr == ""
    # For piped output, YAML might have an extra newline or not, depending on PyYAML.
    # assert_yaml_strings_equal loads them, so it's robust to this.
    # However, EXPECTED_YAML_PRETTY includes a trailing newline usually.
    assert_yaml_strings_equal(stdout_content, EXPECTED_YAML_PRETTY)

def test_j2y_cli_pipe_minified_sorted():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["j2y", "-m", "-s"],
        input_data=UNSORTED_JSON_STRING_FOR_YAML
    )
    assert stderr == ""
    assert_yaml_strings_equal(stdout_content.strip(), EXPECTED_YAML_SORTED_MINIFIED.strip())

def test_json22yaml_cli_pipe_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        [],
        input_data=SAMPLE_JSON_STRING,
        cli_tool_name="json22yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(stdout_content, EXPECTED_YAML_PRETTY)

# --- Tests for binary data handling ---
def test_json_dict_with_bytes_to_yaml_via_writer():
    string_io = io.StringIO()
    writer.yaml(JSON_DICT_WITH_ACTUAL_BYTES, string_io, mini=False)
    actual_yaml = string_io.getvalue()
    assert_yaml_strings_equal(actual_yaml, EXPECTED_YAML_WITH_BINARY_TAG)

def test_j2y_cli_with_json_representing_bytes():
    output_content, stderr = run_yaplon_command(
        ["j2y"],
        input_content=JSON_STRING_REPRESENTING_BYTES,
        input_suffix=".json",
        output_suffix=".yaml"
    )
    assert stderr == ""
    assert_yaml_strings_equal(output_content, EXPECTED_YAML_WITH_BINARY_TAG)
