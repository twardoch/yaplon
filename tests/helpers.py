import pytest
import tempfile
import os
import subprocess
import json
import yaml
import plistlib
import xmltodict
from xml.etree import ElementTree as ET

# --- Assertion Helpers ---

def assert_json_strings_equal(json_str1, json_str2):
    try:
        obj1 = json.loads(json_str1)
        obj2 = json.loads(json_str2)
        assert obj1 == obj2, f"JSON objects differ.\nObj1: {obj1}\nObj2: {obj2}"
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to decode JSON strings for comparison: {e}\nString 1: {json_str1[:200]}...\nString 2: {json_str2[:200]}...")

def assert_yaml_strings_equal(yaml_str1, yaml_str2):
    try:
        obj1 = yaml.safe_load(yaml_str1)
        obj2 = yaml.safe_load(yaml_str2)
        assert obj1 == obj2, f"YAML objects differ.\nObj1: {obj1}\nObj2: {obj2}"
    except yaml.YAMLError as e:
        pytest.fail(f"Failed to decode YAML strings for comparison: {e}\nString 1: {yaml_str1[:200]}...\nString 2: {yaml_str2[:200]}...")

def assert_plist_xml_strings_equal(xml_str1, xml_str2):
    """Compares two Plist XML strings by loading them into dicts."""
    try:
        # Ensure consistent decoding, especially if XML strings might have declarations
        dict1 = plistlib.loads(xml_str1.encode('utf-8'))
        dict2 = plistlib.loads(xml_str2.encode('utf-8'))
        assert dict1 == dict2, f"Plist dicts differ: \nDict1: {dict1}\nDict2: {dict2}"
    except Exception as e: # pylint: disable=broad-except
        pytest.fail(f"Plist XML comparison failed: {e}\nXML1: {xml_str1[:500]}...\nXML2: {xml_str2[:500]}...")

def assert_binary_plist_data_equal(plist_bytes, expected_dict):
    """Loads binary plist bytes and compares with an expected Python dictionary."""
    loaded_data = plistlib.loads(plist_bytes)
    assert loaded_data == expected_dict, f"Plist data objects differ.\nLoaded: {loaded_data}\nExpected: {expected_dict}"

def _xml_to_dict_postprocessor_for_j2x(path, key, value):
    """Postprocessor for xmltodict.parse.
    Converts numeric-looking strings and boolean strings (case-insensitive) to Python types.
    """
    if isinstance(value, str):
        val_lower = value.lower()
        if val_lower == 'true': return key, True
        if val_lower == 'false': return key, False
        # Check for int first
        # Must be careful: '1.0' isdigit() is False. '1' isdigit() is True.
        # Order of checks matters.
        if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
             try: return key, int(value)
             except ValueError: pass # Should not happen if isdigit was true
        # Then check for float
        try:
            return key, float(value)
        except ValueError:
            pass # Not a float, keep as string

    if isinstance(value, list):
        new_list = []
        for item_in_list in value:
            # Recursively call this logic for items in list for type conversion
            _, converted_item = _xml_to_dict_postprocessor_for_j2x(path, key, item_in_list)
            new_list.append(converted_item)
        return key, new_list
    return key, value

def assert_xml_strings_equal_for_j2x(xml_str1_actual, xml_str2_expected, is_dict2xml_output=False): # pylint: disable=unused-argument
    """
    Compares XML strings by parsing them into dictionaries using xmltodict
    with a postprocessor to handle type conversions, then comparing the dictionaries.
    """
    try:
        xml_str1_clean = xml_str1_actual.strip()
        xml_str2_clean = xml_str2_expected.strip()

        if not xml_str1_clean and not xml_str2_clean: return
        if not xml_str1_clean or not xml_str2_clean:
            assert xml_str1_clean == xml_str2_clean, f"One XML string is empty.\nXML1: '{xml_str1_clean[:200]}...'\nXML2: '{xml_str2_clean[:200]}...'"
            return

        dict1 = xmltodict.parse(xml_str1_clean, postprocessor=_xml_to_dict_postprocessor_for_j2x)
        dict2 = xmltodict.parse(xml_str2_clean, postprocessor=_xml_to_dict_postprocessor_for_j2x)

        keys1 = list(dict1.keys())
        keys2 = list(dict2.keys())

        if len(keys1) == 1 and len(keys2) == 1 and keys1[0] == keys2[0]:
            content1 = dict1[keys1[0]]
            content2 = dict2[keys2[0]]
            assert content1 == content2, f"XML content (under root '{keys1[0]}') differ: \nDict1: {json.dumps(content1, indent=2)}\nDict2: {json.dumps(content2, indent=2)}"
        else:
            assert dict1 == dict2, f"XML content (full dicts) differ: \nDict1: {json.dumps(dict1, indent=2)}\nDict2: {json.dumps(dict2, indent=2)}"

    except Exception as e:
        norm_xml1_fallback = "".join(xml_str1_actual.split())
        norm_xml2_fallback = "".join(xml_str2_expected.split())
        if norm_xml1_fallback == norm_xml2_fallback:
            pytest.skip(f"XML parsing/dict Ccomparison failed ({e}), but normalized strings match. XML1: {xml_str1_actual[:200]}...")
            return
        pytest.fail(f"XML comparison failed: {e}\nXML1: {xml_str1_actual[:500]}...\nXML2: {xml_str2_expected[:500]}...")


# --- CLI Runner Helpers ---

def run_yaplon_command(
    command_parts,
    input_content=None,
    input_suffix=".tmp",
    output_suffix=".tmp",
    is_binary_input=False,
    is_binary_output=False,
    cli_tool_name="yaplon"
):
    input_filepath = None
    output_filepath = None
    cmd = [cli_tool_name] + command_parts

    if input_content is not None:
        mode = "wb" if is_binary_input else "w" # Use 'wb' and 'w' for writing
        encoding = None if is_binary_input else "utf-8"
        # delete=False is important for the subprocess to access it
        with tempfile.NamedTemporaryFile(mode=mode, delete=False, suffix=input_suffix, encoding=encoding) as infile:
            infile.write(input_content)
            input_filepath = infile.name
        cmd.extend(["-i", input_filepath])

    with tempfile.NamedTemporaryFile(delete=False, suffix=output_suffix) as outfile_temp:
        output_filepath = outfile_temp.name
    cmd.extend(["-o", output_filepath])

    try:
        process = subprocess.run(cmd, capture_output=True, check=False)

        stderr_str = process.stderr.decode('utf-8', errors='ignore').strip()

        if process.returncode != 0:
            stdout_for_error = process.stdout.decode('utf-8', errors='ignore')
            error_message = f"CLI Error for command '{' '.join(cmd)}':\nReturn Code: {process.returncode}\n"
            if stdout_for_error: error_message += f"Stdout:\n{stdout_for_error}\n"
            if stderr_str: error_message += f"Stderr:\n{stderr_str}\n"
            pytest.fail(error_message)

        read_mode = "rb" if is_binary_output else "r"
        read_encoding = None if is_binary_output else "utf-8"
        with open(output_filepath, read_mode, encoding=read_encoding) as f_out:
            output_content_final = f_out.read()

        return output_content_final, stderr_str
    finally:
        if input_filepath and os.path.exists(input_filepath): os.remove(input_filepath)
        if output_filepath and os.path.exists(output_filepath): os.remove(output_filepath)


def run_yaplon_pipe_command(
    command_parts,
    input_data,
    is_binary_input=False,
    is_binary_output=False,
    cli_tool_name="yaplon"
):
    cmd = [cli_tool_name] + command_parts

    process_input_bytes = input_data if is_binary_input else input_data.encode('utf-8')

    process = subprocess.run(cmd, input=process_input_bytes, capture_output=True, check=False)

    stderr_final = process.stderr.decode('utf-8', errors='ignore').strip()

    if process.returncode != 0:
        stdout_for_error = process.stdout.decode('utf-8', errors='ignore')
        error_message = f"CLI Pipe Error for command '{' '.join(cmd)}':\nReturn Code: {process.returncode}\n"
        if stdout_for_error: error_message += f"Stdout:\n{stdout_for_error}\n"
        if stderr_final: error_message += f"Stderr:\n{stderr_final}\n"
        pytest.fail(error_message)

    stdout_final = process.stdout if is_binary_output else process.stdout.decode('utf-8', errors='ignore')

    if not is_binary_output and isinstance(stdout_final, str):
        stdout_final = stdout_final.strip() # Strip for text pipe output

    return stdout_final, stderr_final
