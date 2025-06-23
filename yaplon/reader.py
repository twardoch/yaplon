#!/usr/bin/env python
"""Module for reading various data formats."""

import csv as ocsv # I001 handled by ruff format
from collections import OrderedDict # I001
from typing import Any, IO, Optional, Union # List, Dict, io removed (F401/UP035)

import xmltodict as oxml # I001

from yaplon import ojson, oplist, oyaml # I001


def _sort_complex_object(data: Any) -> Any:
    """
    Recursively sorts an object if it's an OrderedDict.
    If it's a list, attempts to sort its elements if they are sortable dicts/lists.
    """
    if isinstance(data, OrderedDict):
        res = OrderedDict()
        for k, v in sorted(data.items()):
            res[k] = _sort_complex_object(v)  # Recurse for nested dicts
        return res
    if isinstance(data, list):
        # Attempt to sort if items are dicts (by first key) or simple sortable types
        try:
            if data and all(isinstance(x, OrderedDict) for x in data):
                return sorted(
                    data, key=lambda item: next(iter(item.keys())) if item else "" # RUF015
                )
            if data and all(isinstance(x, (str, int, float, bool)) for x in data):
                return sorted(data)
            # For lists of lists, or mixed types, recursive sort is complex/undefined.
            # For now, just recurse into elements if they are dicts or lists
            return [_sort_complex_object(item) for item in data]
        except (TypeError, IndexError):  # Best effort
            return data  # Return as is if sorting fails
    return data


def csv_reader(
    input_stream: IO[str],
    dialect_name: Optional[str] = None,
    has_header: bool = True,
    # 0-indexed column to use for dict key if creating a dict of records
    key_column_index: Optional[int] = None,
    sort_data: bool = False,
) -> Union[list[Any], OrderedDict[str, Any]]: # UP035 List, F821 OrderedDictType -> OrderedDict
    """
    Reads a CSV stream and converts it into a list of OrderedDicts (if header)
    or a list of lists. If key_column_index is provided, it attempts to create
    an OrderedDict mapping keys from that column to record OrderedDicts.
    """
    data_obj: Union[list[Any], OrderedDict[str, Any]] # UP035, F821
    fields: Optional[list[str]] = None # UP035
    actual_dialect: Union[str, ocsv.Dialect]

    if dialect_name:
        try:
            actual_dialect = ocsv.get_dialect(dialect_name)
        except ocsv.Error:  # If dialect name is not registered
            # Try to use it as a Sniffer hint if it's a known format like 'excel-tab'
            # This part is tricky; csv.reader needs a dialect object or registered name
            # For simplicity, if get_dialect fails, fall back to sniffing.
            # Or, one could register custom dialects if 'dialect_name' means more.
            dialect_name = None  # Force sniffing

    if not dialect_name:  # Sniff if no dialect name or if get_dialect failed
        sniffer = ocsv.Sniffer()
        try:
            # Read a sample for sniffing, then reset stream position
            sample = "".join(
                [input_stream.readline() for _ in range(5)]
            )  # Read a few lines
            actual_dialect = sniffer.sniff(sample)
        except ocsv.Error:
            actual_dialect = "excel"  # Fallback
        input_stream.seek(0)  # Reset stream position

    if dialect_name and not isinstance(
        actual_dialect, ocsv.Dialect
    ):  # Should be caught by try-except above
        actual_dialect = (
            dialect_name  # Use string if not a dialect object (e.g. "excel")
        )

    reader = ocsv.reader(input_stream, dialect=actual_dialect)

    # If a key_column_index is specified, output will be a dict, and header is implied.
    if key_column_index is not None:
        has_header = True
        data_obj = OrderedDict()
    else:
        data_obj = []

    if has_header:
        try:
            fields = next(reader)
        except StopIteration:  # Empty CSV
            return data_obj

        if key_column_index is not None and not (0 <= key_column_index < len(fields)):
            # Invalid key_column_index, proceed without using it for dict wrapping
            key_column_index = None
            data_obj = []  # Switch back to list output if key_column_index was bad

    for row in reader:
        if fields:  # If header was present (or implied by key_column_index)
            # Pad row with None if it's shorter than fields list
            padded_row = row + [None] * (len(fields) - len(row))
            record = OrderedDict(
                zip(fields, padded_row[: len(fields)])
            )  # Ensure only map to available fields

            if (
                key_column_index is not None and fields
            ):  # Already checked this above, but for safety
                # Use the value from the specified column of the current row as the key
                key_field_name = fields[key_column_index]
                record_key_value = record.pop(
                    key_field_name, None
                )  # Remove key field from record
                if record_key_value is not None and isinstance(
                    data_obj, OrderedDict
                ):  # data_obj is dict
                    data_obj[str(record_key_value)] = record
                elif isinstance(
                    data_obj, list
                ):  # Fallback if something went wrong with key_col_idx
                    data_obj.append(record)
            elif isinstance(data_obj, list):
                data_obj.append(record)
        elif isinstance(data_obj, list):  # No header
            data_obj.append(row)

    if sort_data:
        return _sort_complex_object(data_obj)
    return data_obj


def json_reader(input_stream: IO[str], sort_data: bool = False) -> Any:
    """Reads a JSON stream."""
    # Assuming ojson.read_json is updated to accept a stream
    obj = ojson.read_json(input_stream)
    if sort_data:
        return _sort_complex_object(obj)
    return obj


def plist_reader(input_stream: IO[bytes], sort_data: bool = False) -> Any:
    """Reads a PList stream (bytes)."""
    # Assuming oplist.read_plist is updated to accept a stream
    obj = oplist.read_plist(input_stream)
    if sort_data:
        return _sort_complex_object(obj)
    return obj


def xml_reader(
    input_stream: IO[str], process_namespaces: bool = False, sort_data: bool = False
) -> Any:
    """Reads an XML stream."""
    # dict_constructor=OrderedDict ensures order is preserved from XML where meaningful
    obj = oxml.parse(
        input_stream.read(),
        process_namespaces=process_namespaces,
        dict_constructor=OrderedDict,
    )
    if sort_data:
        return _sort_complex_object(obj)
    return obj


def yaml_reader(input_stream: IO[str], sort_data: bool = False) -> Any:
    """Reads a YAML stream."""
    # Assuming oyaml.read_yaml is updated/intended to accept a stream
    obj = oyaml.read_yaml(input_stream)
    if sort_data:
        return _sort_complex_object(obj)
    return obj


# Renamed functions for clarity (e.g., csv -> csv_reader, sort_ordereddict -> _sort_complex_object)
# Renamed parameters for clarity (input -> input_stream, sort -> sort_data, etc.)
# Added more specific type hints.
# Improved CSV dialect sniffing and error handling.
# Clarified CSV key_column_index usage (0-indexed, used for dict wrapping).
# Standardized sorting logic with _sort_complex_object.
# Assumed underlying ojson, oplist, oyaml readers will be adapted for stream inputs.
