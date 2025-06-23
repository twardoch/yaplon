"""
Provides helper functions for JSON serialization and deserialization,
including custom handling for `bytes` objects and ensuring `OrderedDict`
usage when reading JSON to preserve key order.

Based on code from SerializedDataConverter by Isaac Muse.
Licensed under MIT.
Copyright (c) 2012 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""

import collections
import json

__all__ = ("read_json", "json_dumps")


def json_dump(obj, stream, preserve_binary=False, compact=False):
    """Serialize Python object `obj` as a JSON formatted stream to `stream`.

    Handles `bytes` objects via `json_convert_to` based on `preserve_binary`.
    Supports compact (minified) output.

    Args:
        obj: The Python object to serialize.
        stream: A .write()-supporting file-like object.
        preserve_binary: If True, `bytes` are serialized as base64 strings.
                         Otherwise, as `{"__bytes__": true, "base64": "..."}`.
        compact: If True, output is minified (no indents/newlines).
    """
    if compact:
        indent = None
        separators = (",", ":")
    else:
        indent = 4
        separators = (",", ": ")

    return json.dump(
        json_convert_to(obj, preserve_binary),
        stream,
        ensure_ascii=False,
        sort_keys=False,
        indent=indent,
        separators=separators,
    )


def json_dumps(obj, preserve_binary=False, compact=False):
    """Serialize Python object `obj` to a JSON formatted string.

    Handles `bytes` objects via `json_convert_to` based on `preserve_binary`.
    Supports compact (minified) output.

    Args:
        obj: The Python object to serialize.
        preserve_binary: If True, `bytes` are serialized as base64 strings.
                         Otherwise, as `{"__bytes__": true, "base64": "..."}`.
        compact: If True, output is minified.

    Returns:
        A JSON formatted string.
    """
    if compact:
        indent = None
        separators = (",", ":")
    else:
        indent = 4
        separators = (",", ": ")

    return json.dumps(
        json_convert_to(obj, preserve_binary),
        ensure_ascii=False,
        sort_keys=False,
        indent=indent,
        separators=separators,
    )


def read_json(stream):
    """Deserialize JSON from `stream` to Python objects using OrderedDict.

    Uses `json_convert_from` to handle custom object representations
    (e.g., `{"__bytes__": true, "base64": "..."}` back to `bytes`).

    Args:
        stream: A .read()-supporting file-like object containing a JSON document.

    Returns:
        An OrderedDict representing the JSON data.
    """
    return json_convert_from(
        json.load(stream, object_pairs_hook=collections.OrderedDict)
    )

import base64

def json_convert_to(obj, preserve_binary=False):
    """Recursively convert Python objects to a JSON serializable format.

    Specifically handles `bytes` objects:
    - If `preserve_binary` is True, converts `bytes` to a base64 encoded string.
    - If `preserve_binary` is False, converts `bytes` to a dictionary
      `{"__bytes__": True, "base64": "encoded_string"}`.

    Recurses through dicts and lists. Other types are returned as is.

    Args:
        obj: The Python object to convert.
        preserve_binary: Flag to control `bytes` serialization format.

    Returns:
        A JSON serializable representation of the object.
    """
    if isinstance(obj, bytes):
        b64_data = base64.b64encode(obj).decode('ascii')
        if preserve_binary:
            return b64_data
        else:
            # Represent as a special dict to indicate it was originally bytes
            return {"__bytes__": True, "base64": b64_data}
    elif isinstance(obj, (dict, collections.OrderedDict)):
        # Return a new dict to avoid modifying original during iteration if it's complex
        return {k: json_convert_to(v, preserve_binary) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Return a new list
        return [json_convert_to(item, preserve_binary) for item in obj]

    # For other types, return as is, assuming json.dump can handle them
    # (e.g., str, int, float, bool, None)
    return obj


def json_convert_from(obj):
    """Recursively convert specific JSON structures back to Python types.

    Handles:
    - Dictionaries like `{"__bytes__": True, "base64": "..."}` back to `bytes`.
    - Legacy `{"!!python/object:plistlib.Data": "..."}` back to `bytes`.

    Recurses through dicts and lists.

    Args:
        obj: The JSON-decoded object (often a dict or list).

    Returns:
        The Python object with specific structures converted.
    """
    if isinstance(obj, (dict, collections.OrderedDict)):
        # Check for the new bytes representation first
        if obj.get("__bytes__") is True and "base64" in obj:
            try:
                return base64.b64decode(obj["base64"])
            except Exception: # pylint: disable=broad-except
                # If base64 decoding fails, return the dict as is, or handle error
                # For now, let's assume it was a legit dict not meant to be bytes
                pass # Fall through to general dict processing

        # Legacy handling for old plistlib.Data format, if it ever appears from other sources
        if len(obj) == 1 and "!!python/object:plistlib.Data" in obj:
            try:
                return base64.b64decode(obj["!!python/object:plistlib.Data"])
            except Exception: # pylint: disable=broad-except
                pass # Fall through

        # General dictionary processing
        return {k: json_convert_from(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = json_convert_from(v)
            count += 1

    return obj
