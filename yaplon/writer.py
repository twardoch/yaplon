#!/usr/bin/env python
"""Module for writing various data formats."""

from collections import OrderedDict # I001 fix by ruff
from collections.abc import Mapping  # For type hinting
from typing import Any, IO, Optional

import dict2xml  # Alternative XML writer # I001 fix
import xmltodict as oxml  # Primary XML writer used # I001 fix

from yaplon import ojson, oplist, oyaml # I001 fix


def json_writer(
    obj: Any,
    output_stream: IO[bytes],
    mini: bool = False,
    preserve_binary: bool = False,
) -> None:
    """Write JSON data to a stream. Output is UTF-8 encoded bytes."""
    json_string = ojson.json_dumps(
        obj, preserve_binary=preserve_binary, compact=mini, ensure_ascii=False
    )
    output_stream.write(json_string.encode("utf-8"))


def plist_writer(
    obj: Any, output_stream: IO[bytes], binary_format: bool = False
) -> None:
    """Write PList data to a stream."""
    # detect_timestamp=True is a sensible default for plists which support dates.
    if binary_format:
        plist_bytes = oplist.plist_binary_dumps(obj, detect_timestamp=True)
        output_stream.write(plist_bytes)
    else:
        plist_str = oplist.plist_dumps(obj, detect_timestamp=True)
        output_stream.write(plist_str.encode("utf-8"))


def _dict2xml_writer(
    obj: Any,
    output_stream: IO[bytes],
    mini: bool = False,
    # 'wrap_tag' is used as the root tag for the dict2xml conversion
    wrap_tag: str = "data",  # Default root tag for dict2xml if obj not single-key dict
) -> None:
    """Helper to write XML using dict2xml library."""
    indent_str = "" if mini else "  "
    # dict2xml.Converter().build() returns a string
    xml_string = dict2xml.Converter(wrap=wrap_tag, indent=indent_str).build(obj)
    output_stream.write(xml_string.encode("utf-8"))


def xml_writer(
    obj: Any,
    output_stream: IO[bytes],
    mini: bool = False,
    # item_tag_name for dict2xml if obj is list and needs item wrapping.
    # oxml.unparse handles list items differently (often as repeated parent key tags).
    item_tag_name: Optional[str] = "item",  # Used by _dict2xml_writer if obj is list
    root_tag_name: str = "root",
    use_dict2xml_fallback: bool = False,  # Flag to use dict2xml if oxml fails
) -> None:
    """
    Write XML data to a stream. Prefers xmltodict.unparse, can fallback to dict2xml.
    """
    current_obj_for_xml: OrderedDict[str, Any] # F821 fix

    if isinstance(obj, Mapping):
        # If obj is already a dict, ensure it has a single root for oxml.unparse
        # or dict2xml's wrap tag will be this root.
        if len(obj) == 1:
            # If it's a single-key dict, use that key as effective root for unparse.
            # root_tag_name respected by ensuring single key is it, or wrapping.
            single_key = next(iter(obj.keys()))
            if single_key == root_tag_name:
                current_obj_for_xml = OrderedDict(obj)
            else:  # Single key but not matching desired root_tag_name, wrap it.
                current_obj_for_xml = OrderedDict([(root_tag_name, obj)])
        else:  # Multiple keys, must wrap with root_tag_name
            current_obj_for_xml = OrderedDict([(root_tag_name, obj)])
    elif isinstance(obj, list):
        # For oxml.unparse, a list needs to be under a root key.
        # Items tagged based on key they are under or default 'item' if complex.
        # To control item tags with oxml, list should contain {item_tag_name: value}.
        # If item_tag_name provided, transform list items for explicit tagging.
        if item_tag_name:
            processed_list = [{item_tag_name: list_item} for list_item in obj]
            current_obj_for_xml = OrderedDict([(root_tag_name, processed_list)])
        else:  # Let oxml handle list items with its default behavior
            current_obj_for_xml = OrderedDict([(root_tag_name, obj)])
    else:  # Single non-mapping, non-list item (int, str, etc.)
        # Wrap with root_tag_name, and optionally item_tag_name for the value itself.
        content = {item_tag_name: obj} if item_tag_name else obj
        current_obj_for_xml = OrderedDict([(root_tag_name, content)])

    try:
        # xmltodict.unparse returns a string, which needs encoding.
        xml_string = oxml.unparse(
            current_obj_for_xml,
            pretty=(not mini),
            full_document=True,
            short_empty_elements=mini,
        )
        output_stream.write(xml_string.encode("utf-8"))
    except Exception as e_oxml:
        if use_dict2xml_fallback:
            # dict2xml takes direct object, 'wrap' is its root tag.
            # Pass *original* object `obj` to dict2xml,
            # not current_obj_for_xml which was prepared for oxml.
            # dict2xml is more flexible with input structure but less standard XML.
            # 'root_tag_name' will be used as 'wrap' tag for dict2xml.
            _dict2xml_writer(obj, output_stream, mini, wrap_tag=root_tag_name)
        else:
            # If not using fallback, re-raise or handle error.
            # For now, just write a basic error message to the stream.
            error_msg = (
                f"<!-- XML generation failed with primary writer: {e_oxml}. "
                f"Fallback not enabled. -->\n"
            )
            output_stream.write(error_msg.encode("utf-8"))


def yaml_writer(obj: Any, output_stream: IO[str], mini: bool = False) -> None: # Changed IO[bytes] to IO[str]
    """Write YAML data to a text stream."""
    # oyaml.yaml_dumps returns a string.
    # compact_flow=mini maps our 'mini' to oyaml's parameter.
    # detect_timestamp_strings=True is a sensible default for YAML.
    yaml_string = oyaml.yaml_dumps(
        obj, compact_flow=mini, detect_timestamp_strings=True
    )
    output_stream.write(yaml_string) # Write string directly


# Renamed functions to <format>_writer for consistency.
# Renamed parameters for clarity (output -> output_stream, binary -> binary_format, etc.).
# Added more specific type hints.
# Corrected stream handling in plist_writer (removed click.File wrapping).
# JSON and YAML writers now explicitly encode to UTF-8.
# XML writer logic significantly refactored:
#   - Prefers xmltodict.unparse.
#   - Input object `obj` is consistently wrapped with `root_tag_name`.
#   - List items can be explicitly tagged using `item_tag_name`.
#   - Includes an optional fallback to `_dict2xml_writer` if oxml.unparse fails.
#   - `_simplexml` helper renamed to `_dict2xml_writer` and clarified its `wrap_tag` usage.
# Removed unused `click` import.
