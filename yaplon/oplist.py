"""
Serialized Data Converter.

Licensed under MIT
Copyright (c) 2012 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
import collections # For OrderedDict directly
import datetime
import plistlib
import re
from re import Pattern # UP035
from typing import Any, IO, Literal, Union # OrderedDict as OrderedDictType removed - F401

__all__ = ("plist_binary_dumps", "plist_dumps", "read_plist")  # Sorted

# Regex to match ISO 8601 date/datetime strings
# This is a simplified version. For full ISO 8601 parsing, a library might be better.
RE_ISO_TIMESTAMP: Pattern[str] = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"(?:[T ](?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"(?P<microsecond_group>(?:\.\d{1,6}))?"
    r"(?P<tz_utc>Z|(?P<tz_offset>[+-]\d{2}:\d{2}))?)?$"
)

NoneLiteralHandler = Literal["fail", "strip", "false"]


def strip_plist_comments(text: bytes) -> bytes:
    """Strip comments from plist (bytes input)."""
    # Comments in XML plists are standard XML comments <!-- ... -->
    return re.sub(rb"<!--[\s\S]*?-->", b"", text)


def _convert_iso_string_to_datetime(
    text: str,
) -> Union[datetime.datetime, datetime.date, None]:
    """
    Convert an ISO 8601 timestamp string to a datetime.datetime or datetime.date object.
    Returns None if the string is not a valid ISO timestamp.
    """
    match = RE_ISO_TIMESTAMP.match(text)
    if not match:
        return None

    parts = match.groupdict()
    year, month, day = int(parts["year"]), int(parts["month"]), int(parts["day"])

    if parts["hour"] is None:  # Date only
        return datetime.date(year, month, day)

    hour, minute, second = (
        int(parts["hour"]),
        int(parts["minute"]),
        int(parts["second"]),
    )

    microsecond = 0
    if parts["microsecond_group"]:
        # remove dot and ensure fixed length for int conversion
        microsecond_str = parts["microsecond_group"][1:]
        microsecond = int(microsecond_str.ljust(6, "0")[:6])

    tzinfo: Union[datetime.timezone, None] = None
    if parts["tz_utc"] == "Z":
        tzinfo = datetime.timezone.utc
    elif parts["tz_offset"]:
        offset_str = parts["tz_offset"]
        sign = -1 if offset_str.startswith("-") else 1
        h_offset, m_offset = map(int, offset_str[1:].split(":"))
        tzinfo = datetime.timezone(
            datetime.timedelta(hours=sign * h_offset, minutes=sign * m_offset)
        )

    return datetime.datetime(
        year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo
    )


def _recursive_plist_convert_from(obj: Any) -> Any:
    """
    Recursively convert plistlib loaded objects to more standard Python types.
    plistlib.load already converts <data> tags to bytes and <date> to datetime.
    This function primarily ensures OrderedDicts and lists are traversed.
    The original also converted datetimes to strings, which is reversed here
    to keep datetime objects.
    """
    # plistlib.Data is not available in Py3.9+. plistlib.load returns bytes directly.
    # So, no special handling for plistlib.Data needed here.
    if isinstance(obj, (dict, collections.OrderedDict)):
        new_dict = collections.OrderedDict()
        for k, v in obj.items():
            new_dict[k] = _recursive_plist_convert_from(v)
        return new_dict
    if isinstance(obj, list):
        return [_recursive_plist_convert_from(item) for item in obj]
    # datetime.datetime objects are already converted by plistlib.load.
    # No need to convert them to strings as the original did, unless specific.
    return obj


def _recursive_plist_convert_to(
    obj: Any, detect_timestamp: bool, none_handler: NoneLiteralHandler
) -> Any:
    """
    Recursively convert Python objects to types suitable for plistlib.dumps.
    Handles None based on none_handler and optionally converts ISO strings to datetimes.
    """
    if isinstance(obj, dict):
        new_dict = collections.OrderedDict()
        items_to_iterate = list(obj.items()) if none_handler == "strip" else obj.items()
        for k, v in items_to_iterate:
            if v is None:
                if none_handler == "strip":
                    continue
                if none_handler == "false":
                    new_dict[k] = False
                    continue
                # if none_handler == "fail", plistlib will raise error or skip key
                # depending on its own skipkeys argument (not used here for None).
                # Passing None through if not stripping or converting to False.
                new_dict[k] = None  # Or raise error if 'fail' implies immediate failure
            else:
                new_dict[k] = _recursive_plist_convert_to(
                    v, detect_timestamp, none_handler
                )
        return new_dict
    if isinstance(obj, list):
        new_list = []
        for v in obj:
            if v is None:
                if none_handler == "strip":
                    continue
                if none_handler == "false":
                    new_list.append(False)
                    continue
                new_list.append(None)
            else:
                new_list.append(
                    _recursive_plist_convert_to(v, detect_timestamp, none_handler)
                )
        return new_list
    if isinstance(obj, tuple):  # Convert tuples to lists
        return _recursive_plist_convert_to(list(obj), detect_timestamp, none_handler)
    if isinstance(obj, str) and detect_timestamp:
        dt_obj = _convert_iso_string_to_datetime(obj)
        if dt_obj is not None:
            return dt_obj  # plistlib handles datetime objects
    # bytes, int, float, bool, datetime.datetime are handled directly by plistlib.dumps
    return obj


def plist_dumps(
    obj: Any,
    detect_timestamp: bool = False,
    none_handler: NoneLiteralHandler = "fail",
    sort_keys: bool = False,  # Added sort_keys from plistlib.dumps
    skipkeys: bool = False,  # Added skipkeys from plistlib.dumps
) -> str:
    """Wrapper for PLIST XML dump, returns str."""
    converted_obj = _recursive_plist_convert_to(obj, detect_timestamp, none_handler)
    plist_bytes = plistlib.dumps(
        converted_obj, fmt=plistlib.FMT_XML, sort_keys=sort_keys, skipkeys=skipkeys
    )
    return plist_bytes.decode("utf-8")


def plist_binary_dumps(
    obj: Any,
    detect_timestamp: bool = False,
    none_handler: NoneLiteralHandler = "fail",
    sort_keys: bool = False,  # Added sort_keys from plistlib.dumps
    skipkeys: bool = False,  # Added skipkeys from plistlib.dumps
) -> bytes:
    """Wrapper for PLIST binary dump, returns bytes."""
    converted_obj = _recursive_plist_convert_to(obj, detect_timestamp, none_handler)
    return plistlib.dumps(
        converted_obj, fmt=plistlib.FMT_BINARY, sort_keys=sort_keys, skipkeys=skipkeys
    )


def read_plist(
    stream: IO[bytes],
) -> Any:  # stream should be IO[bytes] for plistlib.load
    """Read PList from a byte stream and convert to standard Python types."""
    # Assuming stream is opened in 'rb' mode.
    # plistlib.load handles XML comments, so strip_plist_comments is not used here.
    # If pre-stripping is needed for non-standard plists:
    #   content = stream.read()
    #   content_stripped = strip_plist_comments(content)
    #   loaded_obj = plistlib.loads(content_stripped, dict_type=collections.OrderedDict)
    loaded_obj = plistlib.load(stream, dict_type=collections.OrderedDict)
    return _recursive_plist_convert_from(loaded_obj)


# Removed convert_timestamp (logic in _convert_iso_string_to_datetime)
# and plist_convert_from/to (now _recursive_plist_convert_from/to).
