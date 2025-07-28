#!/usr/bin/env python
""" """

try:
    from collections.abc import Mapping
except ImportError:
    from collections.abc import Mapping

from collections import OrderedDict

import sys # Moved import sys to the top
import click
import dict2xml
import xmltodict as oxml

from yaplon import ojson, oplist, oyaml

import datetime # Ensure datetime is imported

# Helper function to prepare data for XML writers
def _prepare_obj_for_xml(item):
    """Recursively prepares an object for XML serialization.
    Converts bytes to base64 ASCII strings and datetime objects to ISO 8601 strings.
    """
    if isinstance(item, bytes):
        return base64.b64encode(item).decode('ascii')
    elif isinstance(item, datetime.datetime):
        if item.tzinfo is not None and item.tzinfo == datetime.timezone.utc:
            return item.isoformat(timespec='seconds').replace('+00:00', 'Z')
        # For naive datetime or non-UTC, produce ISO format.
        # Consider if local timezone conversion to UTC is desired here for naive before ISO.
        # For now, direct ISO format for naive or other TZs.
        return item.isoformat(timespec='seconds')
    elif isinstance(item, list):
        return [_prepare_obj_for_xml(i) for i in item]
    elif isinstance(item, Mapping): # Handles dict and OrderedDict
        return OrderedDict([(k, _prepare_obj_for_xml(v)) for k, v in item.items()])
    return item


def json(obj, output, mini=False, binary=False):
    """Writes a Python object to a JSON output stream.

    Args:
        obj: The Python object to serialize.
        output: A file-like object (text stream) to write JSON to.
        mini: If True, produces minified JSON (no indents/newlines).
        binary: If True, and obj contains bytes (e.g., from Plist/YAML binary),
                serializes bytes as base64 strings. Otherwise, uses a
                special dict `{"__bytes__":true, "base64":"..."}`.
    """
    ojson.json_dump(obj, output, preserve_binary=binary, compact=mini)


def plist(obj, output_stream, binary=False):
    """Writes a Python object to a Plist output stream.

    Handles conversion to XML Plist (default) or binary Plist.
    Manages type conversions suitable for Plist (e.g., strings for numbers/bools
    are converted to native Plist types by plistlib).

    Args:
        obj: The Python object to serialize.
        output_stream: A file-like object (binary for binary Plist, text for XML Plist)
                       to write Plist data to.
        binary: If True, outputs binary Plist; otherwise, XML Plist.
    """
    if binary:
        # Ensure output_stream is suitable for binary writing (caller's responsibility via __main__.py)
        output_stream.write(oplist.plist_binary_dumps(obj))
    else:
        # Ensure output_stream is suitable for text writing (caller's responsibility via __main__.py)
        output_stream.write(oplist.plist_dumps(obj))


def _simplexml(obj, output, mini=False, tag=""):
    if mini:
        indent = ""
        newlines = False
    else:
        indent = "  "
        newlines = True
    output.write(
        dict2xml.Converter(wrap=tag, indent=indent, newlines=newlines).build(obj)
    )


def xml(obj, output, mini=False, tag=None, root="root"):
    # This is extremely primitive and buggy
    if isinstance(obj, Mapping):
        obj = OrderedDict(obj)
        if len(obj.keys()) > 1:
            obj = OrderedDict([(root, obj)])
        else:
            root = list(obj.keys())[0]
    else:
        obj = OrderedDict([(root, obj)])
    if tag:
        _simplexml(prepared_obj_for_xml, output_stream, mini=mini, tag=tag)
    else:
        processed_obj_for_xmltodict = prepared_obj_for_xml
        if isinstance(processed_obj_for_xmltodict, Mapping):
            if len(processed_obj_for_xmltodict.keys()) != 1 or root != 'root':
                is_single_key_and_root = (len(processed_obj_for_xmltodict.keys()) == 1 and list(processed_obj_for_xmltodict.keys())[0] == root)
                if not is_single_key_and_root:
                    processed_obj_for_xmltodict = OrderedDict([(root, processed_obj_for_xmltodict)])
        else:
            processed_obj_for_xmltodict = OrderedDict([(root, processed_obj_for_xmltodict)])

        pretty = not mini
        try:
            oxml.unparse(
                obj,
                output,
                full_document=True,
                short_empty_elements=mini,
                pretty=pretty,
            )
        except:
            pass


def yaml(obj, output, mini=False):
    """Writes a Python object to a YAML output stream.

    Args:
        obj: The Python object to serialize.
        output: A file-like object (text stream) to write YAML to.
        mini: If True, produces minified YAML (compact flow style).
    """
    output.write(oyaml.yaml_dumps(obj, compact=mini))
