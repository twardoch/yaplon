import pytest
import tempfile
import os
import io
import json
import xmltodict

from yaplon import reader, writer
from tests.helpers import (
    assert_xml_strings_equal_for_j2x as assert_xml_strings_equal,
    run_yaplon_command,
    run_yaplon_pipe_command
)

# --- Test Data ---

SAMPLE_YAML_STRING = """\
name: Test YAML for XML
application:
  version: "1.2.3"
  release_date: 2024-03-10 # Loaded as datetime.date by PyYAML
  active: true
  threshold: 0.75
  ids:
    - 100
    - 200
    - 300
  config:
    path: /usr/local/etc
    retries: 3
binary_data: !!binary Um9ja3NBbmRSb2xs # "RocksAndRoll"
empty_list: []
empty_dict: {}
null_value: null
"""

# Expected Python dict from reader.yaml
# oyaml.timestamp_constructor converts datetime.date to "YYYY-MM-DD" string
EXPECTED_DICT_FROM_YAML = {
    "name": "Test YAML for XML",
    "application": {
        "version": "1.2.3",
        "release_date": "2024-03-10", # Corrected: PyYAML loads as date, oyaml.py str(date)
        "active": True,
        "threshold": 0.75,
        "ids": [100, 200, 300],
        "config": {
            "path": "/usr/local/etc",
            "retries": 3
        }
    },
    "binary_data": b"RocksAndRoll",
    "empty_list": [],
    "empty_dict": {},
    "null_value": None
}

# xmltodict.unparse behavior:
# - Bytes are base64 encoded by _prepare_obj_for_xml.
# - Numbers/booleans become text nodes (postprocessor in assert handles type check).
# - None results in an empty tag: <tag></tag> (or <tag/> if minified).
# - Empty dict results in an empty tag: <tag></tag> (or <tag/> if minified).
# - Empty list is OMITTED by xmltodict.unparse by default.
EXPECTED_XML_DEFAULT_ROOT = """\
<?xml version="1.0" encoding="utf-8"?>
<root>
	<name>Test YAML for XML</name>
	<application>
		<version>1.2.3</version>
		<release_date>2024-03-10</release_date>
		<active>true</active>
		<threshold>0.75</threshold>
		<ids>100</ids>
		<ids>200</ids>
		<ids>300</ids>
		<config>
			<path>/usr/local/etc</path>
			<retries>3</retries>
		</config>
	</application>
	<binary_data>Um9ja3NBbmRSb2xs</binary_data>
	<empty_dict></empty_dict>
	<null_value></null_value>
</root>
""" # empty_list is omitted

EXPECTED_XML_MINIFIED_DEFAULT_ROOT = '<?xml version="1.0" encoding="utf-8"?><root><name>Test YAML for XML</name><application><version>1.2.3</version><release_date>2024-03-10</release_date><active>true</active><threshold>0.75</threshold><ids>100</ids><ids>200</ids><ids>300</ids><config><path>/usr/local/etc</path><retries>3</retries></config></application><binary_data>Um9ja3NBbmRSb2xs</binary_data><empty_dict/><null_value/></root>' # empty_list omitted


# dict2xml behavior:
# - None values are OMITTED by default.
# - Empty lists/dicts result in empty tags: <tag></tag>.
EXPECTED_XML_WRAP_TAG_DICT2XML = """\
<yaplon_output>
  <name>Test YAML for XML</name>
  <application>
    <version>1.2.3</version>
    <release_date>2024-03-10</release_date>
    <active>true</active>
    <threshold>0.75</threshold>
    <ids>100</ids>
    <ids>200</ids>
    <ids>300</ids>
    <config>
      <path>/usr/local/etc</path>
      <retries>3</retries>
    </config>
  </application>
  <binary_data>Um9ja3NBbmRSb2xs</binary_data>
  <empty_list></empty_list>
  <empty_dict></empty_dict>
  <null_value>None</null_value> <!-- dict2xml converts None to "None" string -->
</yaplon_output>
"""

# --- Tests ---

def test_yaml_to_xml_via_writer_functions():
    with io.StringIO(SAMPLE_YAML_STRING) as string_io_input:
        yaml_data = reader.yaml(string_io_input)
    assert yaml_data == EXPECTED_DICT_FROM_YAML

    string_io_xml_default = io.StringIO()
    writer.xml(yaml_data, string_io_xml_default, mini=False, root="root")
    actual_xml_default = string_io_xml_default.getvalue()
    assert_xml_strings_equal(actual_xml_default, EXPECTED_XML_DEFAULT_ROOT)

    string_io_xml_tag = io.StringIO()
    writer.xml(yaml_data, string_io_xml_tag, mini=False, tag="yaplon_output")
    actual_xml_tag = string_io_xml_tag.getvalue()
    assert_xml_strings_equal(actual_xml_tag, EXPECTED_XML_WRAP_TAG_DICT2XML, is_dict2xml_output=True)

def test_y2x_cli_default_root():
    output_content, stderr = run_yaplon_command(
        ["y2x"],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".xml"
    )
    assert stderr == ""
    # print(f"Actual XML output for default root:\n{output_content}") # Kept for debugging if needed
    assert_xml_strings_equal(output_content, EXPECTED_XML_DEFAULT_ROOT)

def test_y2x_cli_minified_default_root():
    output_content, stderr = run_yaplon_command(
        ["y2x", "-m"],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".xml"
    )
    assert stderr == ""
    assert_xml_strings_equal(output_content, EXPECTED_XML_MINIFIED_DEFAULT_ROOT)

def test_y2x_cli_custom_root():
    output_content, stderr = run_yaplon_command(
        ["y2x", "-R", "customData"],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".xml"
    )
    assert stderr == ""
    expected_custom_root = EXPECTED_XML_DEFAULT_ROOT.replace("<root>", "<customData>").replace("</root>", "</customData>")
    assert_xml_strings_equal(output_content, expected_custom_root)

def test_y2x_cli_wrap_tag():
    output_content, stderr = run_yaplon_command(
        ["y2x", "-t", "yaplon_output"],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".xml"
    )
    assert stderr == ""
    assert_xml_strings_equal(output_content, EXPECTED_XML_WRAP_TAG_DICT2XML, is_dict2xml_output=True)

def test_yaml22xml_cli_default():
    output_content, stderr = run_yaplon_command(
        [],
        input_content=SAMPLE_YAML_STRING,
        input_suffix=".yaml",
        output_suffix=".xml",
        cli_tool_name="yaml22xml"
    )
    assert stderr == ""
    assert_xml_strings_equal(output_content, EXPECTED_XML_DEFAULT_ROOT)

# --- Piping Tests ---
def test_y2x_cli_pipe_default():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["y2x"],
        input_data=SAMPLE_YAML_STRING
    )
    assert stderr == ""
    assert_xml_strings_equal(stdout_content, EXPECTED_XML_DEFAULT_ROOT)

def test_y2x_cli_pipe_wrap_tag_minified():
    stdout_content, stderr = run_yaplon_pipe_command(
        ["y2x", "-t", "custom_tag", "-m"],
        input_data=SAMPLE_YAML_STRING
    )
    assert stderr == ""
    # Construct expected minified dict2xml output string manually for this specific case
    # Based on SAMPLE_YAML_STRING and tag "custom_tag", minified
    # dict2xml converts None to "None" string
    expected_minified_dict2xml = (
        "<custom_tag><name>Test YAML for XML</name>"
        "<application><version>1.2.3</version><release_date>2024-03-10</release_date>"
        "<active>true</active><threshold>0.75</threshold>"
        "<ids>100</ids><ids>200</ids><ids>300</ids>"
        "<config><path>/usr/local/etc</path><retries>3</retries></config></application>"
        "<binary_data>Um9ja3NBbmRSb2xs</binary_data>"
        "<empty_list></empty_list><empty_dict></empty_dict><null_value>None</null_value></custom_tag>"
    )
    assert_xml_strings_equal(stdout_content.strip(), expected_minified_dict2xml, is_dict2xml_output=True)
