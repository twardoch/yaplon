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

        timestamp = self.construct_yaml_timestamp(node)
        if not isinstance(timestamp, datetime.datetime):
            timestamp = str(timestamp)
        else:
            timestamp = (
                "%(year)04d-%(month)02d-%(day)02dT%(hour)02d:%(minute)02d:%(second)02d%(microsecond)sZ"
                % {
                    "year": timestamp.year,
                    "month": timestamp.month,
                    "day": timestamp.day,
                    "hour": timestamp.hour,
                    "minute": timestamp.minute,
                    "second": timestamp.second,
                    "microsecond": ".%06d" % timestamp.microsecond
                    if timestamp.microsecond != 0
                    else "",
                }
            )
        return timestamp

    def construct_mapping(loader, node):
        """Keep dict ordered."""

        loader.flatten_mapping(node)
        return OrderedDict(loader.construct_pairs(node))

    class Loader(loader):
        """Custom loader."""

    Loader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )

    Loader.add_constructor("tag:yaml.org,2002:binary", binary_constructor)

    Loader.add_constructor("tag:yaml.org,2002:timestamp", timestamp_constructor)

    # Add !!Regex support during translation
    Loader.add_constructor("tag:yaml.org,2002:regex", Loader.construct_yaml_str)

    return yaml.load(stream, Loader)


def yaml_dump(
    data,
    stream=None,
    dumper=yaml.Dumper,
    width=180,
    quote_strings=False,
    block_strings=False,
    double_quote=False,
    **kwargs,
):
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
            if " " in value:
                return True
        return False

    def must_use_quotes(value):
        """Internal helper: True if string value must be quoted due to YAML syntax conflicts."""
        if isinstance(value, str) and len(value) > 0:
            if ":" in value:
                return True
            elif value[0] in (" ", ".", "@"):
                return True
            elif value[-1] in (" ", "."):
                return True
            except ValueError:
                pass
        return False

    def my_represent_scalar(self, tag, value, style=None):
        """Scalar."""
        if style is None:
            if block_strings and should_use_quotes(value):
                style = "|"
            elif should_use_block(value):
                style = "|"
            else:
                if quote_strings and should_use_quotes(value):
                    style = "double-quoted" if double_quote else "single-quoted"
                elif must_use_quotes(value):
                    style = "double-quoted" if double_quote else self.default_style
                else:
                    style = self.default_style
            if value == "":
                style = "double-quoted" if double_quote else "single-quoted"

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
        lambda self, data: self.represent_mapping(
            "tag:yaml.org,2002:map", data.items()
        ),
    )
    CustomDumper.add_representer(
        AttrDict,
        lambda self, data: self.represent_mapping(
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

    return yaml.dump(data, stream, Dumper, width=width, allow_unicode=True, **kwargs)

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
            else:
                microsecond = 0

            tzinfo = None
            if g["tz_sign"] is not None:
                tz_hour = int(g["tz_hour"])
                tz_minute = int(g["tz_minute"]) if g.tz_minute is not None else 0
                delta = datetime.timedelta(hours=tz_hour, minutes=tz_minute) * (
                    -1 if g["tz_sign"] == "-" else 1
                )
            else:
                delta = None

            time_stamp = datetime.datetime(
                year, month, day, hour, minute, second, microsecond
            )

    return time_stamp if delta is None else time_stamp - delta


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
        return obj.replace("\t", "    ").rstrip(" ") if strip_tabs else obj
    return obj


def yaml_dumps(
    obj,
    compact=False,
    detect_timestamp=False,
    width=180,
    quote_strings=False,
    block_strings=False,
    indent=4,
    double_quote=False,
):
    """Wrapper for yaml dump."""
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
    )
