#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Provides functions to read various data formats (CSV, JSON, Plist, XML, YAML)
and parse them into Python objects, typically OrderedDicts to preserve structure.
Handles type conversions where appropriate (e.g., Plist data/dates, YAML tags).
"""

import csv as ocsv
from collections import OrderedDict

import xmltodict as oxml

from yaplon import ojson
from yaplon import oplist
from yaplon import oyaml


def sort_ordereddict(od):
    res = OrderedDict()
    for k, v in sorted(od.items()):
        res[k] = sort_ordereddict(v) if isinstance(v, dict) else v
    return res


def csv(input, dialect=None, header=True, key=None, sort=False):
    """Reads CSV from input stream into a list of lists or list of OrderedDicts.

    Args:
        input: A file-like object (text stream) for CSV input.
        dialect: CSV dialect name (e.g., 'excel', 'excel-tab') or a dialect object.
                 If None, dialect is sniffed from the input.
        header: If True, treats the first row as field names and returns a list
                of OrderedDicts. If False, returns a list of lists.
                Automatically True if 'key' is specified.
        key: If 'header' is True and 'key' (an integer column index) is provided,
             returns an OrderedDict where keys are taken from the specified
             column, and values are the row OrderedDicts (with the key field removed).
        sort: If True, and if the output is an OrderedDict (due to 'key' arg),
              sorts the OrderedDict by its keys.

    Returns:
        A list of lists, list of OrderedDicts, or an OrderedDict, depending on options.
    """
    obj = []
    fields = None
    if dialect:
        dialect = ocsv.get_dialect(dialect)
    else:
        sniffer = ocsv.Sniffer()
        dialect = sniffer.sniff(input.readline())()
        input.seek(0)
    reader = ocsv.reader(input, dialect=dialect)
    if key:
        header = True
    if header:
        fields = next(reader)
        if key and key <= len(fields):
            obj = OrderedDict()
        else:
            key = None
    for row in reader:
        if header:
            row = OrderedDict(zip(fields, row))
            if key:
                rowkey = row.pop(fields[key - 1])
                obj[rowkey] = row
            else:
                obj.append(row)
        else:
            obj.append(row)
    if sort:
        obj = sort_ordereddict(obj)
    return obj


def json(input, sort=False):
    """Reads JSON from input stream into an OrderedDict. Optionally sorts.

    Args:
        input: A file-like object (text stream) for JSON input.
        sort: If True, recursively sorts the resulting OrderedDict by keys.

    Returns:
        An OrderedDict representing the JSON data.
    """
    obj = ojson.read_json(input)
    if sort:
        obj = sort_ordereddict(obj)
    return obj


def plist(input, sort=False):
    """Reads Plist (XML or binary) from input stream into an OrderedDict.

    Converts Plist <data> to bytes and <date> to datetime.datetime objects.
    Optionally sorts the resulting OrderedDict.

    Args:
        input: A file-like object (binary stream) for Plist input.
        sort: If True, recursively sorts the resulting OrderedDict by keys.

    Returns:
        An OrderedDict representing the Plist data.
    """
    obj = oplist.read_plist(input)
    if sort:
        obj = sort_ordereddict(obj)
    return obj


def xml(input, namespaces=False, sort=False):
    """Reads XML from input stream into an OrderedDict using xmltodict.

    XML element text content is generally parsed as strings.
    Optionally processes namespaces and sorts the resulting OrderedDict.

    Args:
        input: A file-like object (text stream) for XML input.
        namespaces: If True, processes XML namespaces, prefixing keys.
        sort: If True, recursively sorts the resulting OrderedDict by keys.

    Returns:
        An OrderedDict representing the XML data.
    """
    # xmltodict.parse uses OrderedDict by default if dict_constructor is not specified
    # or if cchardet is available. yaplon.reader.xml explicitly uses OrderedDict.
    obj = oxml.parse(input.read(), process_namespaces=namespaces, dict_constructor=OrderedDict)
    if sort:
        obj = sort_ordereddict(obj)
    return obj


def yaml(input, sort=False):
    """Reads YAML from input stream into an OrderedDict.

    Handles custom YAML tags like !!binary (to bytes) and !!timestamp (to ISO string)
    via oyaml.py's custom constructors. Optionally sorts.

    Args:
        input: A file-like object (text stream) for YAML input.
        sort: If True, recursively sorts the resulting OrderedDict by keys.

    Returns:
        An OrderedDict representing the YAML data.
    """
    obj = oyaml.read_yaml(input)
    if sort:
        obj = sort_ordereddict(obj)
    return obj
