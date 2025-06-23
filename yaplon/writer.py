#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Provides functions to write Python objects (typically OrderedDicts or lists)
to various data formats (JSON, Plist, XML, YAML) and output them to streams
or files. Handles options like minification and format-specific features
(e.g., binary Plist, XML root/wrapper tags).
"""

try:
    from collections import Mapping
except ImportError:
    from collections.abc import Mapping

from collections import OrderedDict

import sys # Moved import sys to the top
import click
import dict2xml
import xmltodict as oxml

import base64 # For bytes to base64 string
from yaplon import ojson
from yaplon import oplist
from yaplon import oyaml

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


def plist(obj, output, binary=False):
    """Writes a Python object to a Plist output stream or file path.

    Handles conversion to XML Plist (default) or binary Plist.
    Manages type conversions suitable for Plist (e.g., strings for numbers/bools
    are converted to native Plist types by plistlib).

    Args:
        obj: The Python object to serialize.
        output: A file path string (including '-') or a file-like object.
                If a path, the file is created/overwritten.
                If '-', stdout is used.
        binary: If True, outputs binary Plist; otherwise, XML Plist.
    """
    if binary:
        # click.File handles '-' for stdout in binary mode correctly
        output_stream = click.File("wb")(output)
        try:
            output_stream.write(oplist.plist_binary_dumps(obj))
        finally:
            if output_stream is not sys.stdout.buffer and output_stream is not sys.stdout and (hasattr(output_stream, 'name') and output_stream.name != '<stdout>'):
                output_stream.close()

    else:
        output_stream = click.File("w")(output)
        try:
            output_stream.write(oplist.plist_dumps(obj))
        finally:
            if output_stream is not sys.stdout:
                if hasattr(output_stream, 'name') and output_stream.name != '<stdout>':
                    output_stream.close()


def _simplexml(obj, output_target, mini=False, tag=""):
    """Internal helper to write Python object to XML using dict2xml.
    Handles file path string or stream output.
    """
    if mini:
        indent = ""
        newlines = False
    else:
        indent = "  "
        newlines = True

    xml_string = dict2xml.Converter(wrap=tag, indent=indent, newlines=newlines).build(obj)

    if hasattr(output_target, 'write'): # It's a file-like object
        output_target.write(xml_string)
    elif isinstance(output_target, str):
        if output_target == '-':
            sys.stdout.write(xml_string)
            if not xml_string.endswith('\n'): # Ensure newline for stdout consistency
                 sys.stdout.write('\n')
        else:
            with open(output_target, 'w', encoding='utf-8') as f:
                f.write(xml_string)
    else:
        raise TypeError(f"Unsupported output type for _simplexml: {type(output_target)}")


def xml(obj, output, mini=False, tag=None, root="root"):
    """Writes a Python object to an XML output stream or file.

    Uses dict2xml if 'tag' (for a wrapper element) is provided, resulting
    in simpler XML. Otherwise, uses xmltodict.unparse for more comprehensive
    XML generation (including type hints as attributes by default, though
    yaplon currently produces no type hints from this path).

    Bytes and datetime objects in 'obj' are pre-converted to base64 strings
    and ISO 8601 strings, respectively.

    Args:
        obj: The Python object to serialize.
        output: A file path string (including '-') or a file-like object.
        mini: If True, produces minified XML.
        tag: If provided, uses dict2xml to wrap the output with this tag.
             Ignores 'root' if 'tag' is set.
        root: Root element name if dict2xml is not used and 'obj' is not
              a dict with a single key (or to override that single key).
    """
    prepared_obj_for_xml = _prepare_obj_for_xml(obj)

    if tag:
        _simplexml(prepared_obj_for_xml, output, mini, tag)
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
        output_stream = None

        if isinstance(output, str) and output == '-':
            output_stream = sys.stdout
        elif isinstance(output, str) or hasattr(output, 'write'):
            output_stream = output
        else:
            raise TypeError(f"Unsupported output type for xmltodict: {type(output)}")

        xml_string = oxml.unparse(
            processed_obj_for_xmltodict,
            output=None,
            full_document=True,
            short_empty_elements=mini,
            pretty=pretty,
        )

        if output_stream == sys.stdout:
            sys.stdout.write(xml_string)
            if not xml_string.endswith('\n'):
                sys.stdout.write('\n')
        elif isinstance(output_stream, str):
            with open(output_stream, 'w', encoding='utf-8') as f:
                f.write(xml_string)
        else:
            output_stream.write(xml_string)


def yaml(obj, output, mini=False):
    """Writes a Python object to a YAML output stream.

    Args:
        obj: The Python object to serialize.
        output: A file-like object (text stream) to write YAML to.
        mini: If True, produces minified YAML (compact flow style).
    """
    output.write(oyaml.yaml_dumps(obj, compact=mini))
