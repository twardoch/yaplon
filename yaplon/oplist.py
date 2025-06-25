"""
Provides helper functions for Plist serialization and deserialization.

This module handles:
- Reading Plist files (XML or binary) into Python `OrderedDict` objects.
  During reading, Plist `<date>` tags are converted to `datetime.datetime` objects
  by `plistlib.load`, which are then further converted by this module into
  ISO 8601 formatted strings. Plist `<data>` tags become `bytes` objects.
- Dumping Python objects to XML or binary Plist strings. This involves:
  1. Preprocessing the input object with `_prepare_obj_for_plist` to convert
     string representations of numbers (e.g., "123", "1.0") and booleans
     (e.g., "true", "false") into their native Python types (int, float, bool).
     This is particularly useful when the data originates from formats like XML
     where such values might be initially parsed as strings.
  2. Further preprocessing with `plist_convert_to` to handle `None` values
     (according to `none_handler`) and optionally detect and convert ISO 8601
     date strings back into `datetime.datetime` objects if `detect_timestamp` is True.
  3. Finally, using `plistlib.dumps` for the actual serialization.

Based on code from SerializedDataConverter by Isaac Muse.
Licensed under MIT.
Copyright (c) 2012 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""

import collections
from collections import OrderedDict # Added import
import datetime
import plistlib
import re

__all__ = ("read_plist", "plist_dumps", "plist_binary_dumps")

def _prepare_obj_for_plist(item):
    """Recursively prepare an object for Plist serialization.

    Converts string values that look like numbers or booleans into their
    actual Python types (int, float, bool). This is useful if the input
    data (e.g., from XML) has these types represented as strings.

    Args:
        item: The Python object/item to prepare.

    Returns:
        The item with potential type conversions applied.
    """
    if isinstance(item, str):
        if item.lower() == 'true':
            return True
        if item.lower() == 'false':
            return False
        if item.isdigit(): # Check for int first
            return int(item)
        try: # Then check for float
            return float(item)
        except ValueError:
            return item # Keep as string if not convertible
    elif isinstance(item, list):
        return [_prepare_obj_for_plist(i) for i in item]
    elif isinstance(item, (dict, collections.OrderedDict)): # Handle dict and OrderedDict
        return OrderedDict([(k, _prepare_obj_for_plist(v)) for k, v in item.items()])
    return item


def strip_plist_comments(text):
    """Strip XML-style comments from binary Plist data.

    return re.sub(rb"^[\r\n\s]*<!--[\s\S]*?-->[\s\r\n]*|<!--[\s\S]*?-->", b"", text)


def plist_dumps(obj, detect_timestamp=False, none_handler="fail"):
    """Serialize Python object `obj` to an XML Plist formatted string.

    Before serialization by `plistlib.dumps`:
    1. `_prepare_obj_for_plist` converts string representations of numbers/booleans
       in `obj` to their native Python types.
    2. `plist_convert_to` handles `None` values based on `none_handler`
       and optionally converts string timestamps to `datetime` objects if
       `detect_timestamp` is True (though `plistlib.dumps` handles native datetimes).

    Args:
        obj: The Python object to serialize.
        detect_timestamp: If True, `plist_convert_to` attempts to convert
                          ISO 8601 date strings to `datetime.datetime` objects.
        none_handler: How `plist_convert_to` handles `None` values:
                      'fail' (default): Raise error if `None` encountered.
                      'strip': Remove keys with None values from dicts.
                      'false': Convert None values to Plist <false/>.
                      (Note: `plistlib.dumps` itself serializes Python `None`
                       in a list to `<string></string>` or omits if in dict with `skipkeys=True`,
                       but `plist_convert_to` intercepts `None` first based on this handler.)


    Returns:
        An XML Plist formatted string.
    """
    prepared_obj = _prepare_obj_for_plist(obj)
    return plistlib.dumps(
        plist_convert_to(obj, detect_timestamp, none_handler), sort_keys=False
    ).decode("utf-8")


def plist_binary_dumps(obj, detect_timestamp=False, none_handler="fail"):
    """Serialize Python object `obj` to a binary Plist formatted bytes object.

    Preprocessing of `obj` (type conversion for strings, None handling,
    optional timestamp detection) is the same as for `plist_dumps`.

    Args:
        obj: The Python object to serialize.
        detect_timestamp: If True, convert ISO date strings to `datetime` objects.
        none_handler: How to handle `None` values ('fail', 'strip', 'false').

    Returns:
        A bytes object containing the binary Plist data.
    """
    prepared_obj = _prepare_obj_for_plist(obj)
    return plistlib.dumps(
        plist_convert_to(prepared_obj, detect_timestamp, none_handler),
        fmt=plistlib.FMT_BINARY,
        sort_keys=False,
    )


import io

def read_plist(stream):
    return plist_convert_from(plistlib.load(stream, dict_type=collections.OrderedDict))


def convert_timestamp(obj):
    """Internal helper to convert a Plist date string (ISO 8601) to a datetime object.

    Uses `plistlib._date_from_string` for parsing.

    Args:
        obj: A string potentially representing an ISO 8601 timestamp.

    Returns:
        A datetime.datetime object if parsing is successful, otherwise None.
    """
    time_stamp = None
    if isinstance(obj, str) and plistlib._dateParser.match(obj): # Ensure obj is string
        time_stamp = plistlib._date_from_string(obj)
    return time_stamp


def plist_convert_from(obj):
    """Recursively process objects loaded by `plistlib.load`.

    Specifically, converts `datetime.datetime` objects (from Plist <date> tags)
    into ISO 8601 formatted strings. Other types like `bytes` (from <data>)
    are passed through. This function ensures that the data structure returned
    by `read_plist` has dates represented as strings.

    Args:
        obj: The object loaded by `plistlib.load` (e.g., dict, list, scalar).

    Returns:
        The processed object with dates converted to ISO strings.
    """
    if isinstance(obj, (collections.OrderedDict)): # Check for OrderedDict first
        # Create a new OrderedDict to avoid modifying during iteration if necessary
        return OrderedDict([(k, plist_convert_from(v)) for k, v in obj.items()])
    elif isinstance(obj, dict): # Fallback for regular dict, though plistlib.load uses OrderedDict
        return {k: plist_convert_from(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Return a new list with processed items
        return [plist_convert_from(v) for v in obj]
    elif isinstance(obj, datetime.datetime):
        # Convert datetime objects to ISO 8601 strings
        return plistlib._date_to_string(obj) # Uses plistlib's internal formatter

    return obj


def plist_convert_to(obj, detect_timestamp=False, none_handler="fail"):
    """Convert specific serialized items to a plist format."""

    if isinstance(obj, dict):
        for k, v in list(obj.items()) if none_handler == "strip" else obj.items():
            if none_handler == "strip" and v is None:
                del obj[k]
            elif none_handler == "false" and v is None:
                obj[k] = False
            else:
                new_dict[k] = plist_convert_to(v, detect_timestamp, none_handler)
        return new_dict
    elif isinstance(obj, list):
        count = 0
        offset = 0
        for v in obj[:] if none_handler == "strip" else obj:
            if none_handler == "strip" and v is None:
                del obj[count - offset]
                offset += 1
            elif none_handler == "false" and v is None:
                obj[count - offset] = False
            else:
                obj[count - offset] = plist_convert_to(
                    v, detect_timestamp, none_handler
                )
            count += 1
    elif isinstance(obj, str) and detect_timestamp:
        time_stamp = convert_timestamp(obj) # convert_timestamp now ensures obj is str
        if time_stamp is not None:
            return time_stamp # Return datetime object for plistlib

    return obj
