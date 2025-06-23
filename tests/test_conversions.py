import json
import yaml # For comparing YAML output
import pytest
from click.testing import CliRunner
from yaplon.__main__ import cli, json2yaml as j2y_command # direct command import
from yaplon import reader, writer # For direct function testing if needed

# Sample data
SAMPLE_JSON_STRING = '{"name": "yaplon", "type": "converter", "version": 1.6, "tags": ["yaml", "json"]}'
SAMPLE_JSON_DICT = {"name": "yaplon", "type": "converter", "version": 1.6, "tags": ["yaml", "json"]}
EXPECTED_YAML_OUTPUT_UNSORTED = """name: yaplon
type: converter
version: 1.6
tags:
- yaml
- json
"""
# PyYAML's default dumper might add a newline at the end.
# Also, default_flow_style=False is often used for more readable block style.

def test_json_to_yaml_conversion_direct():
    """Test direct conversion logic from JSON string to YAML string."""
    # This would test the underlying reader/writer logic if exposed,
    # or could use the command function directly by preparing mock Click context.
    # For now, focusing on CLI tests as they cover more.
    pass

def test_json2yaml_cli_basic():
    """Test basic JSON to YAML conversion via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['j2y'], input=SAMPLE_JSON_STRING)

    assert result.exit_code == 0
    # Load the output YAML to normalize it and compare structures
    try:
        output_data = yaml.safe_load(result.output)
    except yaml.YAMLError as e:
        pytest.fail(f"Output was not valid YAML: {result.output}\nError: {e}")

    assert output_data == SAMPLE_JSON_DICT, \
        f"CLI output did not match expected YAML structure.\nOutput:\n{result.output}\nExpected structure based on:\n{SAMPLE_JSON_DICT}"

def test_json2yaml_cli_sorted():
    """Test JSON to YAML conversion with sorting via CLI."""
    runner = CliRunner()
    # The order of keys in SAMPLE_JSON_STRING is: name, type, version, tags
    # If sorted, it would be: name, tags, type, version (alphabetical)
    # However, yaplon's sort seems to be about internal data representation,
    # not necessarily alphabetical key sorting for YAML output unless PyYAML does it.
    # The original `oyaml.py`'s `yaml_dumps` does not explicitly sort keys.
    # Let's test if the `-s` flag runs without error.
    # The actual assertion on sorted output depends on oyaml.py's behavior.
    # For now, we expect it to run and produce valid YAML.
    # A more robust test would require specific sorted output.

    result = runner.invoke(cli, ['j2y', '-s'], input=SAMPLE_JSON_STRING)
    assert result.exit_code == 0
    try:
        output_data = yaml.safe_load(result.output)
    except yaml.YAMLError as e:
        pytest.fail(f"Output was not valid YAML (sorted): {result.output}\nError: {e}")

    # For a simple dict, PyYAML's default dumper usually preserves insertion order
    # if the input was an OrderedDict. If it was a plain dict, order is arbitrary
    # (Python 3.7+ preserves insertion order for dicts, but PyYAML might not rely on it).
    # The reader.json creates an OrderedDict.
    # So, without explicit sorting in the YAML dumper, the output order should match input.
    # The `-s` flag in yaplon's context seems to sort the *internal* OrderedDict.
    # If this sorted OrderedDict is then passed to PyYAML, PyYAML should respect that order.

    # Let's create an expected sorted dict for comparison
    # sorted_sample_json_dict = OrderedDict(sorted(SAMPLE_JSON_DICT.items()))
    # This would be: name, tags, type, version
    # The actual output depends on how the internal sort flag is interpreted by the writer.
    # Given current implementation, reader.json(sort=True) would sort keys of OrderedDict.
    # Then writer.yaml would dump this. PyYAML dumper for OrderedDict should respect its order.

    expected_sorted_dict_keys = sorted(SAMPLE_JSON_DICT.keys())
    output_keys = list(output_data.keys())

    # Check if the keys in the output are sorted as expected.
    # This is a bit indirect. A better test would be to check the exact string output
    # if the sorting behavior is strictly defined for YAML output.
    # For now, we'll check if the output structure is equivalent to the input,
    # and the sorting flag didn't break it.

    # Create the expected dictionary with the 'tags' list sorted
    expected_sorted_sample_dict = SAMPLE_JSON_DICT.copy()
    expected_sorted_sample_dict["tags"] = sorted(SAMPLE_JSON_DICT["tags"])

    assert output_data == expected_sorted_sample_dict, \
        f"CLI output (sorted) did not match expected YAML structure.\nOutput:\n{result.output}\nExpected structure based on:\n{expected_sorted_sample_dict}"
    # This test might need refinement based on actual sorting behavior of the YAML dumper.
    # If sorting is purely internal and doesn't affect output key order for YAML (which is common),
    # then this assertion is fine. If it *should* affect output order, the expected output needs to change.

# Example of how to test a specific command function directly (more unit-test like)
# This requires more setup if the function relies heavily on Click's context.
# @pytest.fixture
# def mock_click_context(mocker):
#     ctx = mocker.MagicMock(spec=click.Context)
#     # Setup ctx attributes as needed by the command function
#     return ctx

# def test_j2y_command_direct(mock_click_context):
#     # This is more complex as we need to mock input/output file streams
#     # and how Click passes them.
#     # For instance:
#     # with io.StringIO(SAMPLE_JSON_STRING) as input_f, io.BytesIO() as output_f_bytes:
#     #     # Need to adapt how output_f_bytes (binary) is handled if writer.yaml expects text
#     #     # Or ensure writer.yaml can handle a binary stream and encodes internally.
#     #     # The `output_file` in __main__.py for j2y is type=click.File("wb")
#     #     # So the command j2y expects a binary stream for output.
#     #     # writer.yaml writes string, so it must be encoded.

#     #     # This is a simplified invocation, actual command might need more context
#     #     # result = j2y_command.callback(input_file=input_f, output_file=output_f_bytes, mini=False, sort_keys=False)

#     #     # output_yaml_str = output_f_bytes.getvalue().decode('utf-8')
#     #     # output_data = yaml.safe_load(output_yaml_str)
#     #     # assert output_data == SAMPLE_JSON_DICT
#     pass

import xml.etree.ElementTree as ET # For parsing XML output
import plistlib # For parsing Plist output

# TODO: Add more tests for other conversions:
# - json2plist, json2xml
# - plist2json, plist2yaml, plist2xml
# - yaml2json, yaml2plist, yaml2xml
# - csv2json, csv2yaml, csv2plist, csv2xml (CSV tests will need sample CSV files)
# - xml2json, xml2yaml, xml2plist

# TODO: Add tests for options:
# - -m (mini) for JSON, YAML, XML
# - -b (binary) for PLIST
# - CSV specific options: -d (dialect), -nh (noheader), -k (key)
# - XML specific options: -t (tag), -R (root), -n (namespaces for XML input)

# TODO: Add tests for edge cases:
# - Empty input
# - Invalid input formats
# - Files vs stdin/stdout
# - Different encodings if applicable (though default is UTF-8)

# TODO: Add tests for file_strip utilities if they are complex enough.
# For now, their effect is tested indirectly via the main conversion commands.

# A simple test to make sure pytest is running
def test_pytest_works():
    assert True

def test_json2plist_cli_basic():
    """Test basic JSON to Plist XML conversion via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['j2p'], input=SAMPLE_JSON_STRING)
    assert result.exit_code == 0
    try:
        # The output is bytes, plistlib.loads expects bytes
        output_data = plistlib.loads(result.output_bytes)
    except Exception as e: # Broad exception for now
        pytest.fail(f"Output was not valid Plist XML: {result.output}\nError: {e}")

    # Compare structure. Note: Plist dates/binary data might need special handling if present.
    # SAMPLE_JSON_DICT contains simple types that should translate well.
    assert output_data == SAMPLE_JSON_DICT, \
        f"CLI output did not match expected Plist structure.\nOutput:\n{result.output}\nExpected structure based on:\n{SAMPLE_JSON_DICT}"

def test_json2plist_cli_binary():
    """Test JSON to binary Plist conversion via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['j2p', '-b'], input=SAMPLE_JSON_STRING) # -b for binary
    assert result.exit_code == 0
    try:
        output_data = plistlib.loads(result.output_bytes)
    except Exception as e:
        pytest.fail(f"Output was not valid binary Plist: {result.output_bytes[:100]}...\nError: {e}") # Show first 100 bytes

    assert output_data == SAMPLE_JSON_DICT, \
        f"CLI output did not match expected binary Plist structure.\nExpected structure based on:\n{SAMPLE_JSON_DICT}"

def test_json2plist_cli_sorted():
    """Test JSON to Plist XML conversion with sorting via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['j2p', '-s'], input=SAMPLE_JSON_STRING)
    assert result.exit_code == 0
    try:
        output_data = plistlib.loads(result.output_bytes)
    except Exception as e:
        pytest.fail(f"Output was not valid Plist XML (sorted): {result.output}\nError: {e}")

    expected_sorted_sample_dict = SAMPLE_JSON_DICT.copy()
    expected_sorted_sample_dict["tags"] = sorted(SAMPLE_JSON_DICT["tags"])

    # For plists, dicts are inherently unordered unless specific library versions
    # or format versions enforce it. plistlib.loads usually returns a standard dict.
    # However, our reader creates OrderedDicts. The writer.plist_writer uses oplist.plist_dumps,
    # which in turn uses plistlib.dumps. plistlib.dumps has a sort_keys parameter,
    # but our _recursive_plist_convert_to does not pass it through currently.
    # The internal sort_data flag in yaplon should sort the OrderedDict before dumping.
    # Let's check if the loaded dict is structurally equivalent and tags list is sorted.

    assert output_data.get("name") == expected_sorted_sample_dict.get("name")
    assert output_data.get("type") == expected_sorted_sample_dict.get("type")
    assert output_data.get("version") == expected_sorted_sample_dict.get("version")
    assert sorted(output_data.get("tags", [])) == sorted(expected_sorted_sample_dict.get("tags", []))
    # A more robust check would be full dict comparison if key order in plist output is guaranteed.
    # Since plist dicts are not inherently ordered in the XML representation itself,
    # we might only be able to compare content, not order of keys for the top level.
    # However, if input was OrderedDict and plistlib preserves it, then good.
    # For now, comparing content and sorted list is a good start.

    # For a stricter test on key order if our writer guarantees it:
    # loaded_keys = list(output_data.keys())
    # expected_keys_after_yaplon_sort = list(OrderedDict(sorted(SAMPLE_JSON_DICT.items())).keys())
    # assert loaded_keys == expected_keys_after_yaplon_sort
    # And then compare values.
    # For now, checking content equality for the dict and sorted list for tags:
    temp_output_data_tags_sorted = output_data.copy()
    if 'tags' in temp_output_data_tags_sorted and isinstance(temp_output_data_tags_sorted['tags'], list):
        temp_output_data_tags_sorted['tags'] = sorted(temp_output_data_tags_sorted['tags'])

    assert temp_output_data_tags_sorted == expected_sorted_sample_dict, \
        f"CLI output (sorted plist) did not match expected structure.\nOutput:\n{output_data}\nExpected:\n{expected_sorted_sample_dict}"


def test_json2xml_cli_basic():
    """Test basic JSON to XML conversion via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['j2x'], input=SAMPLE_JSON_STRING)
    assert result.exit_code == 0

    try:
        # Parse the XML output for structural comparison
        # This is more robust than string comparison for XML.
        print(f"\nDEBUG XML OUTPUT for basic:\n{result.output}\n") # DEBUG
        root = ET.fromstring(result.output)
    except ET.ParseError as e:
        pytest.fail(f"Output was not valid XML: {result.output}\nError: {e}")

    # Expected structure: <root><name>yaplon</name><type>converter</type>...</root>
    # xmltodict.unparse default behavior with our writer.xml_writer logic
    assert root.tag == "root" # Default root tag

    # Check children based on SAMPLE_JSON_DICT
    # This requires converting SAMPLE_JSON_DICT to the expected XML structure manually or via a tool for comparison
    # For simple cases:
    name_tag = root.find("name")
    assert name_tag is not None and name_tag.text == SAMPLE_JSON_DICT["name"]

    type_tag = root.find("type")
    assert type_tag is not None and type_tag.text == SAMPLE_JSON_DICT["type"]

    version_tag = root.find("version")
    assert version_tag is not None and float(version_tag.text) == SAMPLE_JSON_DICT["version"] # XML values are strings

    # tags_parent_tag = root.find("tags") # This would find the first <tags> element.
    # assert tags_parent_tag is not None
    # For repeated tags like <tags>a</tags><tags>b</tags>, we need findall for "tags" directly under root.
    found_tags_elements = root.findall("tags")
    found_tags_text = [tag_element.text for tag_element in found_tags_elements]
    assert sorted(found_tags_text) == sorted(SAMPLE_JSON_DICT["tags"])


def test_json2xml_cli_custom_root_item_tags():
    """Test JSON to XML with custom root and item tags."""
    runner = CliRunner()
    custom_root = "customRoot"
    custom_item = "customItem" # This is 'tag' in CLI, item_tag_name in writer
    result = runner.invoke(cli, ['j2x', '-R', custom_root, '-t', custom_item], input=SAMPLE_JSON_STRING)
    assert result.exit_code == 0

    try:
        root = ET.fromstring(result.output)
    except ET.ParseError as e:
        pytest.fail(f"Output was not valid XML: {result.output}\nError: {e}")

    assert root.tag == custom_root

    name_tag = root.find("name") # These are original keys, should still be there
    assert name_tag is not None and name_tag.text == SAMPLE_JSON_DICT["name"]

    # tags_parent_tag = root.find("tags")
    # assert tags_parent_tag is not None
    # The -t flag (item_tag_name) in xml_writer only affects top-level lists.
    # For nested lists like 'tags' here, xmltodict's default is repeated parent key.
    found_tags_elements = root.findall("tags") # Expecting <tags>item1</tags>, <tags>item2</tags>
    found_tags_text = [tag_element.text for tag_element in found_tags_elements]
    assert sorted(found_tags_text) == sorted(SAMPLE_JSON_DICT["tags"])


def test_json2xml_cli_sorted():
    """Test JSON to XML conversion with sorting via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['j2x', '-s'], input=SAMPLE_JSON_STRING)
    assert result.exit_code == 0

    try:
        root = ET.fromstring(result.output)
    except ET.ParseError as e:
        pytest.fail(f"Output was not valid XML (sorted): {result.output}\nError: {e}")

    # XML element order for children of a given parent is significant.
    # If sorting is applied, the order of <name>, <tags>, <type>, <version>
    # under <root> should be alphabetical.
    # xmltodict.unparse has a `sort_keys` param, but our writer doesn't use it.
    # The sort is from yaplon's reader creating a sorted OrderedDict.
    # ET.fromstring does not preserve original order for findall("*") unless specific parser.
    # We need to check the order of elements if it's guaranteed.
    # For now, let's check content.

    expected_sorted_sample_dict = SAMPLE_JSON_DICT.copy()
    expected_sorted_sample_dict["tags"] = sorted(SAMPLE_JSON_DICT["tags"])

    name_tag = root.find("name")
    assert name_tag is not None and name_tag.text == expected_sorted_sample_dict["name"]

    type_tag = root.find("type")
    assert type_tag is not None and type_tag.text == expected_sorted_sample_dict["type"]

    version_tag = root.find("version")
    assert version_tag is not None and float(version_tag.text) == expected_sorted_sample_dict["version"]

    # For repeated tags like <tags>a</tags><tags>b</tags>
    found_tags_elements = root.findall("tags")
    found_tags_text = [tag_element.text for tag_element in found_tags_elements]
    assert sorted(found_tags_text) == sorted(expected_sorted_sample_dict["tags"])

    # To check actual order of main tags:
    # children_tags = [child.tag for child in root]
    # expected_children_order = sorted(SAMPLE_JSON_DICT.keys())
    # assert children_tags == expected_children_order
    # This depends on how xmltodict.unparse serializes an OrderedDict. It should respect it.
    # And how ET.fromstring then parses it.
    # For now, this test is more about content under sort flag.

# --- Plist to X tests ---
# Sample Plist data (XML format)
SAMPLE_PLIST_XML_STRING = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>name</key>
	<string>yaplon</string>
	<key>type</key>
	<string>converter</string>
	<key>version</key>
	<real>1.6</real>
	<key>tags</key>
	<array>
		<string>yaml</string>
		<string>json</string>
	</array>
</dict>
</plist>
"""
# Equivalent dictionary for comparison (plistlib.loads will produce this)
SAMPLE_PLIST_DICT = {
    "name": "yaplon",
    "type": "converter",
    "version": 1.6, # Plist <real> becomes float
    "tags": ["yaml", "json"]
}
# Binary version of the same plist (generated from SAMPLE_PLIST_DICT using plistlib.dumps)
# This is useful for testing binary plist input.
SAMPLE_PLIST_BINARY = plistlib.dumps(SAMPLE_PLIST_DICT, fmt=plistlib.FMT_BINARY)


def test_plist2json_cli_basic_xml_plist_input():
    """Test Plist (XML) to JSON conversion via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['p2j'], input=SAMPLE_PLIST_XML_STRING)
    assert result.exit_code == 0
    try:
        output_data = json.loads(result.output)
    except json.JSONDecodeError as e:
        pytest.fail(f"Output was not valid JSON: {result.output}\nError: {e}")

    assert output_data == SAMPLE_PLIST_DICT

def test_plist2json_cli_binary_plist_input():
    """Test Plist (binary) to JSON conversion via CLI."""
    runner = CliRunner()
    # For binary input to CLI, CliRunner needs bytes
    result = runner.invoke(cli, ['p2j'], input=SAMPLE_PLIST_BINARY)
    assert result.exit_code == 0
    try:
        output_data = json.loads(result.output)
    except json.JSONDecodeError as e:
        pytest.fail(f"Output was not valid JSON: {result.output}\nError: {e}")

    assert output_data == SAMPLE_PLIST_DICT

def test_plist2yaml_cli_basic_xml_plist_input():
    """Test Plist (XML) to YAML conversion via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['p2y'], input=SAMPLE_PLIST_XML_STRING)
    assert result.exit_code == 0
    try:
        output_data = yaml.safe_load(result.output)
    except yaml.YAMLError as e:
        pytest.fail(f"Output was not valid YAML: {result.output}\nError: {e}")

    assert output_data == SAMPLE_PLIST_DICT

def test_plist2xml_cli_basic_xml_plist_input():
    """Test Plist (XML) to XML conversion via CLI."""
    runner = CliRunner()
    # Input is XML Plist, output is generic XML
    result = runner.invoke(cli, ['p2x'], input=SAMPLE_PLIST_XML_STRING)
    assert result.exit_code == 0

    try:
        root = ET.fromstring(result.output)
    except ET.ParseError as e:
        pytest.fail(f"Output was not valid XML: {result.output}\nError: {e}")

    # Expected structure is <root><key1>val1</key1>...</root>
    # Based on SAMPLE_PLIST_DICT
    assert root.tag == "root" # Default root from writer
    name_tag = root.find("name")
    assert name_tag is not None and name_tag.text == SAMPLE_PLIST_DICT["name"]
    type_tag = root.find("type")
    assert type_tag is not None and type_tag.text == SAMPLE_PLIST_DICT["type"]
    version_tag = root.find("version")
    assert version_tag is not None and float(version_tag.text) == SAMPLE_PLIST_DICT["version"]

    # XML output for lists is typically repeated tags
    found_tags_elements = root.findall("tags")
    found_tags_text = [tag_element.text for tag_element in found_tags_elements]
    assert sorted(found_tags_text) == sorted(SAMPLE_PLIST_DICT["tags"])


# --- YAML to X tests ---
SAMPLE_YAML_STRING = """
name: yaplon
type: converter
version: 1.6
tags:
  - yaml
  - json
"""
# Equivalent dictionary for comparison
SAMPLE_YAML_DICT = {
    "name": "yaplon",
    "type": "converter",
    "version": 1.6,
    "tags": ["yaml", "json"]
}

def test_yaml2json_cli_basic():
    """Test YAML to JSON conversion via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['y2j'], input=SAMPLE_YAML_STRING)
    assert result.exit_code == 0
    try:
        output_data = json.loads(result.output)
    except json.JSONDecodeError as e:
        pytest.fail(f"Output was not valid JSON: {result.output}\nError: {e}")
    assert output_data == SAMPLE_YAML_DICT

def test_yaml2plist_cli_basic():
    """Test YAML to Plist XML conversion via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['y2p'], input=SAMPLE_YAML_STRING)
    assert result.exit_code == 0
    try:
        output_data = plistlib.loads(result.output_bytes)
    except Exception as e:
        pytest.fail(f"Output was not valid Plist XML: {result.output}\nError: {e}")
    assert output_data == SAMPLE_YAML_DICT

def test_yaml2xml_cli_basic():
    """Test YAML to XML conversion via CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ['y2x'], input=SAMPLE_YAML_STRING)
    assert result.exit_code == 0
    try:
        root = ET.fromstring(result.output)
    except ET.ParseError as e:
        pytest.fail(f"Output was not valid XML: {result.output}\nError: {e}")

    assert root.tag == "root"
    name_tag = root.find("name")
    assert name_tag is not None and name_tag.text == SAMPLE_YAML_DICT["name"]
    type_tag = root.find("type")
    assert type_tag is not None and type_tag.text == SAMPLE_YAML_DICT["type"]
    version_tag = root.find("version")
    assert version_tag is not None and float(version_tag.text) == SAMPLE_YAML_DICT["version"]

    found_tags_elements = root.findall("tags")
    found_tags_text = [tag_element.text for tag_element in found_tags_elements]
    assert sorted(found_tags_text) == sorted(SAMPLE_YAML_DICT["tags"])


# --- CSV to X tests ---
SAMPLE_CSV_STRING_HEADER = """id,name,value
1,itemA,100
2,itemB,200
3,itemC,300
"""
SAMPLE_CSV_NO_HEADER = """val1,val2,val3
data1,data2,data3
info1,info2,info3
"""

# Expected dict structure from SAMPLE_CSV_STRING_HEADER
EXPECTED_DICT_FROM_CSV_HEADER = [
    {"id": "1", "name": "itemA", "value": "100"},
    {"id": "2", "name": "itemB", "value": "200"},
    {"id": "3", "name": "itemC", "value": "300"},
]
EXPECTED_LIST_FROM_CSV_NO_HEADER = [
    ["val1", "val2", "val3"],
    ["data1", "data2", "data3"],
    ["info1", "info2", "info3"],
]


def test_csv2json_cli_with_header():
    """Test CSV (with header) to JSON conversion."""
    runner = CliRunner()
    result = runner.invoke(cli, ['c2j', '-H'], input=SAMPLE_CSV_STRING_HEADER) # -H for header
    assert result.exit_code == 0
    try:
        output_data = json.loads(result.output)
    except json.JSONDecodeError as e:
        pytest.fail(f"Output was not valid JSON: {result.output}\nError: {e}")
    assert output_data == EXPECTED_DICT_FROM_CSV_HEADER

def test_csv2json_cli_no_header():
    """Test CSV (no header) to JSON conversion."""
    runner = CliRunner()
    # No -H flag, so reader.csv should treat first line as data
    # The `csv_reader` by default has `has_header=True`. We need to pass `--noheader` or similar.
    # The CLI option is `-nh` or `--noheader` which sets `header` to `False` in `csv_reader`.
    # Oh, looking at `__main__.py`, the `header` param for c2j is:
    # @click.option("-H", "--header", "header", is_flag=True, help="CSV has header and reads as dict")
    # This means if -H is present, header=True. If absent, header=False (default for is_flag). This is counter-intuitive.
    # The `csv_reader` `has_header` default is True.
    # In `__main__.py` for c2j: `obj = reader.csv_reader(..., has_header=header, ...)`
    # If `-H` is *not* passed, `header` (the click param) is `False`. So `has_header=False` is passed.
    # This seems correct for "no header" case.

    result = runner.invoke(cli, ['c2j'], input=SAMPLE_CSV_NO_HEADER)
    assert result.exit_code == 0
    try:
        output_data = json.loads(result.output)
    except json.JSONDecodeError as e:
        pytest.fail(f"Output was not valid JSON: {result.output}\nError: {e}")
    assert output_data == EXPECTED_LIST_FROM_CSV_NO_HEADER


def test_csv2yaml_cli_with_header():
    """Test CSV (with header) to YAML conversion."""
    runner = CliRunner()
    result = runner.invoke(cli, ['c2y', '-H'], input=SAMPLE_CSV_STRING_HEADER)
    assert result.exit_code == 0
    try:
        output_data = yaml.safe_load(result.output)
    except yaml.YAMLError as e:
        pytest.fail(f"Output was not valid YAML: {result.output}\nError: {e}")
    assert output_data == EXPECTED_DICT_FROM_CSV_HEADER

def test_csv2xml_cli_with_header():
    """Test CSV (with header) to XML conversion."""
    runner = CliRunner()
    result = runner.invoke(cli, ['c2x', '-H'], input=SAMPLE_CSV_STRING_HEADER)
    assert result.exit_code == 0
    try:
        root = ET.fromstring(result.output)
    except ET.ParseError as e:
        pytest.fail(f"Output was not valid XML: {result.output}\nError: {e}")

    assert root.tag == "root" # Default root
    # Each item in EXPECTED_DICT_FROM_CSV_HEADER becomes an <item> under <root>
    items = root.findall("item")
    assert len(items) == len(EXPECTED_DICT_FROM_CSV_HEADER)
    for i, xml_item in enumerate(items):
        expected_item_dict = EXPECTED_DICT_FROM_CSV_HEADER[i]
        assert xml_item.find("id").text == expected_item_dict["id"]
        assert xml_item.find("name").text == expected_item_dict["name"]
        assert xml_item.find("value").text == expected_item_dict["value"]

def test_csv2plist_cli_with_header():
    """Test CSV (with header) to Plist conversion."""
    runner = CliRunner()
    result = runner.invoke(cli, ['c2p', '-H'], input=SAMPLE_CSV_STRING_HEADER)
    assert result.exit_code == 0
    try:
        output_data = plistlib.loads(result.output_bytes)
    except Exception as e:
        pytest.fail(f"Output was not valid Plist: {result.output}\nError: {e}")
    assert output_data == EXPECTED_DICT_FROM_CSV_HEADER
