"""
Provides helper functions for YAML serialization and deserialization using PyYAML.

It customizes PyYAML's loader to ensure that YAML mappings are loaded as
`collections.OrderedDict` to preserve key order. It also includes custom
constructors to handle specific YAML tags:
- `!!binary` tags are converted to Python `bytes` objects.
- `!!timestamp` tags (representing `datetime.date` or `datetime.datetime`)
  are converted to ISO 8601 formatted strings upon loading.
- `!!regex` tags are loaded as plain strings.

For YAML dumping, it provides a custom Dumper for more control over output
formatting, such as scalar styles (block, literal, quoted) and ensuring
that `OrderedDict` and `AttrDict` instances are serialized while preserving
key order. PyYAML's default handling for Python `bytes` (to `!!binary` tag)
and `datetime` objects (to YAML timestamp strings) applies during dumping.

The module also includes helpers for preprocessing Python objects before
dumping, for example, to detect strings that look like timestamps and
convert them to `datetime` objects so they are serialized correctly as
YAML timestamps.

Based on code from SerializedDataConverter by Isaac Muse.
Licensed under MIT.
Copyright (c) 2012 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""

import datetime
# import plistlib # Not directly used in this module anymore, was for plistlib.Data
import re
from collections import OrderedDict

import yaml
from orderedattrdict import AttrDict

__all__ = ("read_yaml", "yaml_dumps")

# http://yaml.org/type/timestamp.html
YAML_TIMESTAMP = re.compile(
    r"""
        (?P<year>[0-9][0-9][0-9][0-9])               # year
        -(?P<month>[0-9][0-9]?)                      # month
        -(?P<day>[0-9][0-9]?)                        # day
        (?:
            (?:(?:[Tt]|[ \t]+)(?P<hour>[0-9][0-9]?)) # hour
            :(?P<minute>[0-9][0-9])                  # minute
            :(?P<second>[0-9][0-9])                  # second
            (?:\.(?P<microsecond>[0-9]*))?           # microsecond
            (?:
                [ \t]*Z
                | (?:
                    (?P<tz_sign>[-+])                 # time zone sign
                    (?P<tz_hour>[0-9][0-9]?)          # time zone hour
                    (?::(?P<tz_minute>[0-9][0-9]))?   # time zone minute
                )
            )?
        )?
    """,
    re.VERBOSE,
)


def read_yaml(stream, loader=yaml.SafeLoader): # Changed default to SafeLoader
    """Deserialize YAML from `stream` to Python objects using a custom PyYAML Loader.

    The custom loader ensures that:
    - YAML mappings are loaded as `collections.OrderedDict` to preserve key order.
    - `!!binary` tags are converted to `bytes` objects.
    - `!!timestamp` tags (parsed by PyYAML into `datetime.date` or `datetime.datetime`)
      are converted by a custom constructor into ISO 8601 formatted strings
      (e.g., "YYYY-MM-DD" for dates, "YYYY-MM-DDTHH:MM:SS[.ffffff]Z" for datetimes, ensuring UTC 'Z').
    - `!!regex` tags are loaded as strings.

    Args:
        stream: A .read()-supporting file-like object containing a YAML document.
        loader: The PyYAML Loader class to base the custom loader on (default: `yaml.SafeLoader`).

    Returns:
        An OrderedDict (usually) or other Python object representing the YAML data.
    """

    def binary_constructor(loader_instance, node): # Added loader_instance arg
        """YAML constructor to convert !!binary tags to Python bytes."""
        return loader_instance.construct_yaml_binary(node)

    def timestamp_constructor(loader_instance, node): # Added loader_instance arg
        """YAML constructor for !!timestamp tags.
        Converts datetime.date to "YYYY-MM-DD" string.
        Converts datetime.datetime to "YYYY-MM-DDTHH:MM:SS[.ffffff]Z" ISO 8601 string (UTC).
        """
        timestamp_obj = loader_instance.construct_yaml_timestamp(node) # PyYAML parses into date/datetime

        if isinstance(timestamp_obj, datetime.datetime):
            # Ensure UTC if aware, then format
            if timestamp_obj.tzinfo is not None and timestamp_obj.tzinfo != datetime.timezone.utc:
                timestamp_obj = timestamp_obj.astimezone(datetime.timezone.utc)
            elif timestamp_obj.tzinfo is None: # If naive, assume UTC for ISO Z format
                 timestamp_obj = timestamp_obj.replace(tzinfo=datetime.timezone.utc)

            # Format with 'Z' for UTC
            iso_str = timestamp_obj.isoformat(timespec='microseconds')
            if iso_str.endswith('+00:00'):
                iso_str = iso_str[:-6] + 'Z'
            return iso_str
        elif isinstance(timestamp_obj, datetime.date):
            # For datetime.date objects, convert to simple YYYY-MM-DD string
            return timestamp_obj.isoformat() # datetime.date.isoformat() is YYYY-MM-DD
        return str(timestamp_obj) # Fallback for other timestamp-like objects

    def construct_mapping(loader_instance, node): # Added loader_instance arg
        """YAML constructor to ensure mappings become OrderedDict."""
        loader_instance.flatten_mapping(node)
        return OrderedDict(loader_instance.construct_pairs(node))

    class CustomLoader(loader):
        """Custom PyYAML Loader with specific constructors."""
        pass

    CustomLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )
    CustomLoader.add_constructor("tag:yaml.org,2002:binary", binary_constructor)
    CustomLoader.add_constructor("tag:yaml.org,2002:timestamp", timestamp_constructor)
    CustomLoader.add_constructor("tag:yaml.org,2002:regex", CustomLoader.construct_yaml_str) # Use method from loader

    return yaml.load(stream, Loader=CustomLoader)


def yaml_dump(
    data,
    stream=None,
    dumper=yaml.SafeDumper, # Changed default to SafeDumper
    width=180,
    quote_strings=False,
    block_strings=False,
    double_quote=False,
    **kwargs
):
    """Serialize a Python object to a YAML formatted stream or string using a custom Dumper.

    The custom Dumper allows for:
    - Control over scalar string styles (block, literal, single/double quoted)
      based on content and flags (`quote_strings`, `block_strings`, `double_quote`).
    - Representation of `OrderedDict` and `AttrDict` while preserving key order.
    - PyYAML's default handling for `bytes` (to `!!binary` tag) and `datetime` objects
      (to YAML timestamp strings) will apply if they are present in `data`.

    Args:
        data: The Python object to serialize.
        stream: Optional .write()-supporting file-like object. If None, returns a string.
        dumper: The PyYAML Dumper class to base the custom dumper on (default: `yaml.SafeDumper`).
        width: Preferred line width for output.
        quote_strings: If True, attempts to quote strings containing spaces if not block.
        block_strings: If True, attempts to use block style for multi-line strings.
        double_quote: If True, uses double quotes for quoted strings; else single.
        **kwargs: Additional keyword arguments passed to `yaml.dump` (e.g., `sort_keys`).

    Returns:
        A YAML formatted string if `stream` is None, otherwise None.
    """
    if not width:
        width = float("inf")

    def should_use_block(value):
        """Internal helper: True if string value benefits from block style."""
        for c in "\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
            if c in value:
                return True
        return False

    def should_use_quotes(value):
        """Internal helper: True if string value with spaces should be quoted."""
        if isinstance(value, str):
            if " " in value and not should_use_block(value):
                return True
        return False

    def must_use_quotes(value):
        """Internal helper: True if string value must be quoted due to YAML syntax conflicts."""
        if isinstance(value, str) and len(value) > 0:
            if ":" in value and not should_use_block(value):
                return True
            if value[0] in (" ", ".", "@", "'", '"', "!", "&", "*", "-", "?", "{", "}", "[", "]", ",", "|", ">", "%", "`", "#", "<"):
                return True
            if value[-1] in (" ", "."):
                return True
            val_lower = value.lower()
            if val_lower in ("true", "false", "null", "on", "off", "yes", "no", "~") :
                 return True
            try:
                float(value)
                return True
            except ValueError:
                pass
        return False

    def my_represent_scalar(self, tag, value, style=None):
        """Custom scalar representer to control quoting and block styles."""
        if style is None: # Only intervene if no style is explicitly set by PyYAML
            if block_strings and should_use_block(value):
                style = "|"
            elif should_use_block(value):
                style = "|"
            elif must_use_quotes(value):
                style = '"' if double_quote else "'"
            elif quote_strings and should_use_quotes(value):
                style = '"' if double_quote else "'"
            # else, let PyYAML decide the default_style (usually plain)

            if value == "":
                style = '"' if double_quote else "'"

        # Use self.default_style if no other style was determined by our logic but one is needed
        if style is None and self.default_style is not None and \
           (must_use_quotes(value) or (quote_strings and should_use_quotes(value))):
            style = self.default_style

        node = yaml.representer.ScalarNode(tag, value, style=style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        return node

    class CustomDumper(dumper):
        """Custom PyYAML Dumper with improved scalar representation and OrderedDict/AttrDict support."""
        pass

    CustomDumper.represent_scalar = my_represent_scalar
    CustomDumper.add_representer(
        OrderedDict,
        lambda dumper_instance, data: dumper_instance.represent_mapping( # Use dumper_instance
            "tag:yaml.org,2002:map", data.items()
        ),
    )
    CustomDumper.add_representer(
        AttrDict,
        lambda dumper_instance, data: dumper_instance.represent_mapping( # Use dumper_instance
            "tag:yaml.org,2002:map", data.items()
        ),
    )
    # PyYAML's SafeDumper already handles bytes to !!binary and datetime to !!timestamp
    # So, no explicit representers for those are needed here if using SafeDumper as base.

    # Ensure `sort_keys=False` is default if not specified, to respect OrderedDict.
    # PyYAML's default is sort_keys=True for Dumper/SafeDumper.
    if 'sort_keys' not in kwargs:
        kwargs['sort_keys'] = False

    return yaml.dump(data, stream, Dumper=CustomDumper, width=width, allow_unicode=True, **kwargs)


def convert_timestamp(obj_str): # Renamed obj to obj_str for clarity
    """Parses a string matching the YAML timestamp regular expression.

    Converts to a `datetime.date` or `datetime.datetime` object.
    Handles timezone information if present.

    Args:
        obj_str: A string potentially representing a YAML timestamp.

    Returns:
        A `datetime.date` or `datetime.datetime` object, or None if parsing fails.
    """
    delta = None
    time_stamp = None
    if not isinstance(obj_str, str): # Guard against non-string input
        return None
    m = YAML_TIMESTAMP.match(obj_str)
    if m is not None:
        g = m.groupdict()
        year = int(g["year"])
        month = int(g["month"])
        day = int(g["day"])
        if g["hour"] is None:
            time_stamp = datetime.date(year, month, day)
        else:
            hour = int(g["hour"])
            minute = int(g["minute"])
            second = int(g["second"])
            microsecond = 0
            if g["microsecond"] is not None:
                micro_string = g["microsecond"][:6]
                microsecond = int(micro_string + ("0" * (6 - len(micro_string))))

            tzinfo = None
            if g["tz_sign"] is not None:
                tz_hour = int(g["tz_hour"])
                tz_minute = int(g["tz_minute"]) if g["tz_minute"] is not None else 0
                offset_seconds = (tz_hour * 3600 + tz_minute * 60) * (-1 if g["tz_sign"] == "-" else 1)
                tzinfo = datetime.timezone(datetime.timedelta(seconds=offset_seconds))
            elif g["tz_sign"] is None and 'Z' in obj_str : # Check for 'Z' if no explicit offset
                tzinfo = datetime.timezone.utc

            time_stamp = datetime.datetime(
                year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo
            )
            # This part was for adjusting to local time, which is not needed if tzinfo is set.
            # if delta is not None and time_stamp is not None:
            #    time_stamp = time_stamp - delta
    return time_stamp


def yaml_convert_to(obj, strip_tabs=False, detect_timestamp=False):
    """Recursively prepare Python objects for YAML serialization by `yaml_dump`.

    Specifically:
    - If `detect_timestamp` is True, converts string values matching the YAML
      timestamp pattern into `datetime.date` or `datetime.datetime` objects
      (using the `convert_timestamp` helper). These are then serialized by PyYAML
      into YAML timestamp format (e.g., `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`).
    - If `strip_tabs` is True (and `detect_timestamp` is False for a given string,
      or timestamp conversion fails), replaces tabs with 4 spaces and strips
      trailing spaces from strings.

    Args:
        obj: The Python object to prepare.
        strip_tabs: If True, process tabs/spaces in strings.
        detect_timestamp: If True, attempt to convert date-like strings to datetime objects.

    Returns:
        The prepared object, possibly with new list/dict instances if modified.
    """
    if isinstance(obj, (dict, OrderedDict)):
        new_dict = OrderedDict() if isinstance(obj, OrderedDict) else {}
        for k, v in obj.items():
            new_dict[k] = yaml_convert_to(v, strip_tabs, detect_timestamp)
        return new_dict
    elif isinstance(obj, list):
        return [yaml_convert_to(item, strip_tabs, detect_timestamp) for item in obj]
    elif isinstance(obj, str):
        if detect_timestamp:
            time_stamp = convert_timestamp(obj)
            if time_stamp is not None:
                return time_stamp
        # Fallthrough if not a detected timestamp or detect_timestamp is False
        if strip_tabs:
            return obj.replace("\t", "    ").rstrip(" ")
        return obj

    return obj


def yaml_dumps(
    obj,
    compact=False,
    detect_timestamp=False,
    width=180,
    quote_strings=False,
    block_strings=False,
    indent=None, # Changed default to None, yaml_dump will handle default if not compact
    double_quote=False,
    **kwargs
):
    """Serialize a Python object `obj` to a YAML formatted string.

    This is a convenience wrapper around `yaml_dump`.
    It calls `yaml_convert_to` for preprocessing based on `detect_timestamp`.
    Handles `compact` (minified) output by setting `default_flow_style=True`.

    Args:
        obj: The Python object to serialize.
        compact: If True, output is minified (flow style).
        detect_timestamp: Passed to `yaml_convert_to` for date string detection.
        width: Passed to `yaml_dump`.
        quote_strings: Passed to `yaml_dump`.
        block_strings: Passed to `yaml_dump`.
        indent: Passed to `yaml_dump`. If `compact` is True, `indent` is effectively 0
                due to `default_flow_style=True`. If `compact` is False and `indent`
                is None, PyYAML's default indentation (usually 2) is used.
        double_quote: Passed to `yaml_dump`.
        **kwargs: Additional arguments passed to `yaml_dump` and then to `PyYAML.dump`.

    Returns:
        A YAML formatted string.
    """
    # Prepare kwargs for yaml_dump
    dump_kwargs = kwargs.copy() # Start with a copy of incoming kwargs

    if compact:
        dump_kwargs['default_flow_style'] = True
        # When flow style is true, indent is often less relevant or handled differently by PyYAML
        # PyYAML's default indent for block style is 2. For flow, it's more about spacing.
        # Explicitly setting indent for yaml_dump if compact, but usually it's 0 or small.
        # Let yaml_dump handle its default logic based on default_flow_style.
        dump_kwargs['indent'] = 0 if indent is None else indent
    elif indent is not None: # Not compact, but indent is specified
        dump_kwargs['indent'] = indent
    # If not compact and indent is None, yaml_dump will use PyYAML's default.

    strip_tabs = False # Not currently exposed as an option, could be added

    return yaml_dump(
        yaml_convert_to(obj, strip_tabs, detect_timestamp),
        width=width,
        quote_strings=quote_strings,
        block_strings=block_strings,
        double_quote=double_quote,
        **dump_kwargs
    )
