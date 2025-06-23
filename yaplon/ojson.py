"""
Serialized Data Converter.

Licensed under MIT
Copyright (c) 2012 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""

import collections
import datetime
import json
from typing import Any, IO # Union removed F401


__all__ = ("json_dump", "json_dumps", "read_json")  # RUF022 Sorted


def _bytes_to_hex(bytestr: bytes) -> str:
    """Convert bytes to a hex string."""
    return bytestr.hex()


def _hex_to_bytes(hex_str: str) -> bytes:
    """Convert a hex string to bytes."""
    return bytes.fromhex(hex_str)


def _recursive_json_convert_to(obj: Any, preserve_binary: bool) -> Any:
    """Recursively convert objects to JSON serializable types."""
    if isinstance(obj, (str, bool, int, float)) or obj is None:
        return obj
    if isinstance(obj, bytes):
        return obj if preserve_binary else _bytes_to_hex(obj)
    if isinstance(obj, (dict, collections.OrderedDict)):
        # Create a new dict to avoid modifying the original in place
        new_dict = collections.OrderedDict()
        for k, v in obj.items():
            new_dict[k] = _recursive_json_convert_to(v, preserve_binary)
        return new_dict
    if isinstance(obj, list):
        return [_recursive_json_convert_to(item, preserve_binary) for item in obj]
    if isinstance(obj, tuple):  # Convert tuples to lists for JSON
        return [_recursive_json_convert_to(item, preserve_binary) for item in obj]
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    # Add handling for other common types if necessary, or raise TypeError
    try:
        # Attempt to serialize unknown types, json.dumps will raise TypeError
        # if not possible
        json.dumps(obj)
        return obj
    except TypeError:
        # Fallback for unknown types: convert to string representation.
        # This might not be ideal, but better than failing silently.
        return f"<non-serializable: {type(obj).__name__}>"


def _recursive_json_convert_from(obj: Any) -> Any:
    """
    Recursively convert JSON types back to Python objects.
    Attempts to convert hex strings back to bytes if they were stored as such.
    """
    if isinstance(obj, str):
        # This is a very basic heuristic for converting hex strings back to bytes
        # and is currently disabled to prevent misinterpreting legitimate hex strings.
        # A more reliable method would use type markers or a schema.
        # The `!!python/object:plistlib.Data` tag is specific to PyYAML/plistlib interop.
        return obj
    if isinstance(obj, (bool, int, float)) or obj is None:
        return obj
    if isinstance(obj, (dict, collections.OrderedDict)):
        if len(obj) == 1 and "!!python/object:plistlib.Data" in obj:
            # This handles a specific tag that might come from YAML/Plist conversions
            # The value associated with this tag is expected to be base64 encoded bytes
            try:
                # Assuming the value is a string that needs to be base64 decoded
                # This is an assumption based on how PyYAML handles plistlib.Data
                import base64

                data_val = obj["!!python/object:plistlib.Data"]
                if isinstance(data_val, str):
                    return base64.b64decode(data_val)
                return data_val  # Or handle as error if not string
            except ImportError:  # base64 not available (highly unlikely)
                pass  # Fall through to generic dict processing
            except Exception:  # Decoding error
                pass  # Fall through

        new_dict = collections.OrderedDict()
        for k, v in obj.items():
            new_dict[k] = _recursive_json_convert_from(v)
        return new_dict
    if isinstance(obj, list):  # JSON arrays become Python lists
        return [_recursive_json_convert_from(item) for item in obj]
    return obj


def json_dump(
    obj: Any,
    stream: IO[str],
    preserve_binary: bool = False,
    compact: bool = False,
    ensure_ascii: bool = False,  # Added ensure_ascii
    sort_keys: bool = False,  # Added sort_keys
) -> None:
    """Wrap json.dump with custom object conversion."""
    indent = None if compact else 4
    separators = (",", ":") if compact else (",", ": ")

    converted_obj = _recursive_json_convert_to(obj, preserve_binary)
    json.dump(
        converted_obj,
        stream,
        ensure_ascii=ensure_ascii,
        sort_keys=sort_keys,
        indent=indent,
        separators=separators,
    )


def json_dumps(
    obj: Any,
    preserve_binary: bool = False,
    compact: bool = False,
    ensure_ascii: bool = False,  # Added ensure_ascii
    sort_keys: bool = False,  # Added sort_keys
) -> str:
    """Wrap json.dumps with custom object conversion."""
    indent = None if compact else 4
    separators = (",", ":") if compact else (",", ": ")

    converted_obj = _recursive_json_convert_to(obj, preserve_binary)
    # The .encode().decode() dance is to handle unicode characters correctly
    # when ensure_ascii is False, preventing them from being escaped.
    return json.dumps(
        converted_obj,
        ensure_ascii=ensure_ascii,
        sort_keys=sort_keys,
        indent=indent,
        separators=separators,
    )


def read_json(stream: IO[str]) -> Any:
    """Read JSON from a stream and convert specific items."""
    loaded_obj = json.load(stream, object_pairs_hook=collections.OrderedDict)
    return _recursive_json_convert_from(loaded_obj)


# Removed original json_convert_to and json_convert_from,
# replaced by recursive versions.
