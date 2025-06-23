"""
Serialized Data Converter.

Licensed under MIT
Copyright (c) 2012 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""

import datetime
import plistlib  # Used by a custom constructor
import re
from collections import OrderedDict
from re import Pattern  # UP035
from typing import ( # List, Tuple, OrderedDictType removed F401/UP035
    Any,
    IO,
    Literal,
    Type, # Will be changed to type by UP006
    Union,
)

import yaml
from orderedattrdict import AttrDict  # Used by a custom representer

# Attempt to use CSafeLoader/Dumper for performance, fallback to Python versions
try:
    from yaml import CSafeLoader as DefaultSafeLoader # I001 fix by ruff
    from yaml import CSafeDumper as DefaultSafeDumper
except ImportError:  # pragma: no cover
    from yaml import SafeLoader as DefaultSafeLoader  # type: ignore[misc] # I001 fix
    from yaml import SafeDumper as DefaultSafeDumper  # type: ignore[misc]


__all__ = ("read_yaml", "yaml_dumps")

# http://yaml.org/type/timestamp.html
# Adjusted to be more robust for parsing, especially microseconds and timezone.
YAML_TIMESTAMP_REGEX: Pattern[str] = re.compile(
    r"""
        (?P<year>[0-9]{4})               # year
        -(?P<month>[0-9]{1,2})           # month
        -(?P<day>[0-9]{1,2})             # day
        (?:
            (?:[Tt]|[ \t]+)              # Separator T or space
            (?P<hour>[0-9]{1,2})         # hour
            :(?P<minute>[0-9]{1,2})      # minute
            :(?P<second>[0-9]{1,2})      # second
            (?:\.(?P<microsecond>[0-9]{1,6}))? # microsecond (1 to 6 digits)
            (?:                          # Optional timezone
                [ \t]*Z                   # UTC (Z)
                |
                (?:
                    (?P<tz_sign>[-+])     # Timezone sign
                    (?P<tz_hour>[0-9]{1,2}) # Timezone hour
                    (?::(?P<tz_minute>[0-9]{1,2}))? # Optional timezone minute
                )
            )?
        )?
    """,
    re.VERBOSE,
)

YamlScalarActualStyle = Union[None, Literal["'", '"', "|", ">"]]


def _parse_yaml_timestamp_string(
    text: str,
) -> Union[datetime.datetime, datetime.date, None]:
    """Convert YAML timestamp string to datetime.datetime or datetime.date object."""
    match = YAML_TIMESTAMP_REGEX.match(text)
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
    if parts["microsecond"]:
        # Ensure microsecond is exactly 6 digits by padding with zeros if shorter
        microsecond_str = parts["microsecond"][:6].ljust(6, "0")
        microsecond = int(microsecond_str)

    tzinfo: Union[datetime.timezone, None] = None
    if parts["tz_sign"]:  # Explicit timezone offset
        tz_hour, tz_minute = int(parts["tz_hour"]), int(parts.get("tz_minute") or 0)
        delta_seconds = (tz_hour * 3600 + tz_minute * 60) * (
            -1 if parts["tz_sign"] == "-" else 1
        )
        tzinfo = datetime.timezone(datetime.timedelta(seconds=delta_seconds))
    elif text.endswith("Z"):  # UTC
        tzinfo = datetime.timezone.utc

    return datetime.datetime(
        year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo
    )


def _custom_yaml_load(
    stream: Union[IO[str], str], base_loader: type[yaml.Loader] = DefaultSafeLoader # UP006
) -> Any:
    """
    Load YAML with custom constructors for OrderedDict, binary data, and timestamps.
    """

    def binary_constructor(
        loader_self: yaml.Loader, node: yaml.nodes.ScalarNode
    ) -> bytes: # Changed from plistlib.Data to bytes
        """Constructor to handle binary data, returning Python bytes."""
        return loader_self.construct_yaml_binary(node) # This already returns bytes

    def timestamp_constructor(
        loader_self: yaml.Loader, node: yaml.nodes.ScalarNode
    ) -> Union[datetime.datetime, datetime.date, str]:
        """
        Constructor for YAML timestamp. Returns datetime object or original string
        if parsing fails. Original code converted valid datetimes back to a specific
        string format; this version prefers returning actual datetime objects.
        """
        # PyYAML's construct_yaml_timestamp already returns datetime.datetime or date.
        # The issue is that it might be too strict or not handle all desired formats.
        # We'll use our custom parser for strings PyYAML might not pick up as timestamps,
        # or if we want to ensure our specific ISO 8601 subset is handled.

        # Try PyYAML's default timestamp construction first
        try:
            # This may raise ConstructorError if node not a recognized timestamp
            dt_obj = loader_self.construct_yaml_timestamp(node)
            if isinstance(dt_obj, (datetime.datetime, datetime.date)):
                return dt_obj
        except yaml.constructor.ConstructorError:
            pass  # Fall through to custom string parsing

        # Fallback: if it's a scalar string, try our custom parser
        if isinstance(node, yaml.nodes.ScalarNode):
            scalar_str = loader_self.construct_scalar(node)
            if isinstance(scalar_str, str):
                parsed_dt = _parse_yaml_timestamp_string(scalar_str)
                if parsed_dt:
                    return parsed_dt
                return scalar_str  # Return as string if not a parsable timestamp

        # If all else fails, use the generic scalar constructor
        return loader_self.construct_scalar(node)

    def construct_ordered_mapping(
        loader_self: yaml.Loader, node: yaml.nodes.MappingNode
    ) -> OrderedDict[Any, Any]: # UP035 (collections.OrderedDict -> OrderedDict)
        """Construct an OrderedDict, preserving key order from YAML."""
        loader_self.flatten_mapping(node)  # Necessary before construct_pairs
        return OrderedDict(loader_self.construct_pairs(node))

    class CustomLoader(base_loader):  # type: ignore
        """Custom YAML Loader with specific type constructors."""

        pass

    CustomLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_ordered_mapping
    )
    CustomLoader.add_constructor("tag:yaml.org,2002:binary", binary_constructor)
    CustomLoader.add_constructor("tag:yaml.org,2002:timestamp", timestamp_constructor)
    CustomLoader.add_constructor(
        "tag:yaml.org,2002:regex", CustomLoader.construct_yaml_str
    )  # Regex as string

    return yaml.load(stream, Loader=CustomLoader)


def _custom_yaml_dump(
    data: Any,
    stream: Union[IO[str], None] = None,
    base_dumper: type[yaml.Dumper] = DefaultSafeDumper, # UP006
    width: float = 180,  # Original default
    quote_all_strings: bool = False,  # Simplified from quote_strings
    prefer_block_strings: bool = False,  # Simplified from block_strings
    force_double_quotes: bool = False,  # Simplified from double_quote
    default_flow_style: bool = False,  # Added for consistency
    indent: int = 4,  # Added
    **kwargs: Any,
) -> Union[str, None]:
    """
    Dump YAML with a custom Dumper for fine-grained control over string
    representation and types.
    """

    def _should_use_block_style(value: str) -> bool:
        """Control when to use block style (literal | or folded >)."""
        return any(
            c in value for c in "\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029"
        )

    def _string_needs_quotes(value: str) -> bool:
        """Determine if a string value must be quoted in YAML."""
        if not value:
            return True  # Empty string must be quoted
        # Check for leading/trailing whitespace, special characters, indicators, etc.
        # This is a simplified check; PyYAML's emitter has more comprehensive logic.
        if (
            value[0] in " &*?{}[],!%@`\"'|>-"
            or value[-1] in " :?"
            or ": " in value
            or " #" in value  # common sequence requiring quotes
            or value.lower() in ("true", "false", "null", "yes", "no", "on", "off")
            or (value.startswith("0") and value.isdigit())  # octal like
            or YAML_TIMESTAMP_REGEX.match(value)  # Looks like a timestamp
        ):
            return True
        try:
            float(value)  # Looks like a number
            return True
        except ValueError:
            pass
        return False

    def custom_represent_scalar(
        dumper_self: yaml.Dumper,
        tag: str,
        value: Any,
        style: YamlScalarActualStyle = None,
    ) -> yaml.nodes.ScalarNode:
        """Custom scalar representer for strings, allowing style hints."""
        if isinstance(value, str):
            if style is None:  # Determine best style if not explicitly provided
                if prefer_block_strings and _should_use_block_style(value):
                    style = "|"  # Literal block style for multiline
                elif quote_all_strings or _string_needs_quotes(value):
                    style = '"' if force_double_quotes else "'"

            if value == "":  # Empty string always quoted
                style = '"' if force_double_quotes else "'"

        # PyYAML's Dumper.represent_scalar expects style to be one of a few chars or None
        actual_style_char: Union[str, None] = None
        if style in ("'", '"', "|", ">"):
            actual_style_char = style

        node = DefaultSafeDumper.represent_scalar(
            dumper_self, tag, value, style=actual_style_char
        )
        return node  # type: ignore

    class CustomDumper(base_dumper):  # type: ignore
        """Custom Dumper with specific type representers."""

        pass

    # Override scalar representation for strings
    CustomDumper.add_representer(
        str, lambda d, s: custom_represent_scalar(d, "tag:yaml.org,2002:str", s)
    )

    CustomDumper.add_representer(
        OrderedDict,
        lambda d, data: d.represent_mapping("tag:yaml.org,2002:map", data.items()),
    )
    CustomDumper.add_representer(
        AttrDict,
        lambda d, data: d.represent_mapping("tag:yaml.org,2002:map", data.items()),
    )
    # PyYAML handles datetime.datetime and datetime.date to !!timestamp correctly by default.
    # plistlib.Data is no longer used; standard bytes are handled by PyYAML's default binary representer (!!binary tag).
    # If plistlib.Data objects could still somehow appear (e.g. from other parts of the code not yet updated),
    # a representer might be needed, but the goal is to phase out plistlib.Data.
    # CustomDumper.add_representer(
    #     plistlib.Data, lambda d, data: d.represent_binary(data.data)
    # )

    # `width` and `indent` are direct arguments to yaml.dump
    # `default_flow_style` is also a direct argument. Other kwargs are passed through.
    return yaml.dump(
        data,
        stream,
        Dumper=CustomDumper,
        width=width,
        allow_unicode=True,
        default_flow_style=default_flow_style,
        indent=indent,
        **kwargs,
    )


def _recursive_yaml_convert_to_serializable(
    obj: Any, strip_tabs_from_strings: bool, detect_timestamp_strings: bool
) -> Any:
    """Pre-process Python objects for YAML serialization if needed."""
    if isinstance(obj, dict):  # Handles dict, OrderedDict, AttrDict via representers
        return OrderedDict( # UP035
            (
                k,
                _recursive_yaml_convert_to_serializable(
                    v, strip_tabs_from_strings, detect_timestamp_strings
                ),
            )
            for k, v in obj.items()
        )
    if isinstance(obj, list):
        return [
            _recursive_yaml_convert_to_serializable(
                item, strip_tabs_from_strings, detect_timestamp_strings
            )
            for item in obj
        ]
    if isinstance(obj, tuple):  # Tuples become YAML sequences (like lists)
        return [
            _recursive_yaml_convert_to_serializable(
                item, strip_tabs_from_strings, detect_timestamp_strings
            )
            for item in obj
        ]
    if isinstance(obj, str):
        val_to_return: Any = obj
        if detect_timestamp_strings:
            dt_obj = _parse_yaml_timestamp_string(obj)
            if dt_obj:  # If successfully parsed, use the datetime object
                val_to_return = dt_obj
        if strip_tabs_from_strings and isinstance(
            val_to_return, str
        ):  # If still a string
            val_to_return = val_to_return.replace("\t", "    ").rstrip(
                " "
            )  # Original had rstrip
        return val_to_return
    # datetime, date, int, float, bool, None, plistlib.Data, bytes are handled by Dumper or PyYAML defaults
    return obj


def read_yaml(
    stream_or_path: Union[IO[str], str],
    loader_class: type[yaml.Loader] = DefaultSafeLoader, # UP006
) -> Any:
    """Read YAML from a stream or file path."""
    if isinstance(stream_or_path, str):  # It's a path
        with open(stream_or_path, encoding="utf-8") as f: # UP015 removed "r"
            return _custom_yaml_load(f, base_loader=loader_class)
    # It's a stream
    return _custom_yaml_load(stream_or_path, base_loader=loader_class)


def yaml_dumps(
    obj: Any,
    compact_flow: bool = False,  # Simplified from 'compact'
    detect_timestamp_strings: bool = False,
    line_width: float = 180,  # Changed from width to line_width
    quote_all_strings: bool = False,
    prefer_block_strings: bool = False,
    force_double_quotes: bool = False,  # Changed from double_quote
    indent_spaces: int = 4,  # Explicit indent parameter
    explicit_start: bool = False,  # Added for full control
    explicit_end: bool = False,  # Added for full control
    dumper_class: type[yaml.Dumper] = DefaultSafeDumper, # UP006
    **kwargs: Any,  # For other yaml.dump options like version, tags, etc.
) -> str:
    """Dump Python object to YAML string with extended formatting options."""

    processed_obj = _recursive_yaml_convert_to_serializable(
        obj, False, detect_timestamp_strings
    )  # strip_tabs is false here, handled by Dumper if needed

    # Determine default_flow_style based on compact_flow
    # If compact_flow is True, prefer flow style for collections. Else, block.
    actual_default_flow_style = bool(compact_flow) # SIM210
    actual_indent = 0 if compact_flow else indent_spaces

    # strip_tabs logic was in yaml_convert_to, now in dumper's string representation
    # (if dumper supports it). Current custom dumper does not explicitly handle it beyond
    # string replacement in _recursive_yaml_convert_to_serializable if flag passed.
    # The flag is `False` in the call to _recursive_yaml_convert_to_serializable above.

    dumped_str = _custom_yaml_dump(
        processed_obj,
        stream=None,  # Get string output
        base_dumper=dumper_class,
        width=line_width,
        quote_all_strings=quote_all_strings,
        prefer_block_strings=prefer_block_strings,
        force_double_quotes=force_double_quotes,
        default_flow_style=actual_default_flow_style,
        indent=actual_indent,
        explicit_start=explicit_start,
        explicit_end=explicit_end,
        **kwargs,
    )
    if dumped_str is None:  # Should not happen if stream is None
        return ""
    return dumped_str


# Removed: yaml_convert_to (logic merged into _recursive_yaml_convert_to_serializable)
# Removed: convert_timestamp (logic merged into _parse_yaml_timestamp_string)
# Removed: yaml_dump (internalized as _custom_yaml_dump)
