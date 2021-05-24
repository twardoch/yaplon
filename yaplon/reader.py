#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
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
    obj = ojson.read_json(input)
    if sort:
        obj = sort_ordereddict(obj)
    return obj


def plist(input, sort=False):
    obj = oplist.read_plist(input)
    if sort:
        obj = sort_ordereddict(obj)
    return obj


def xml(input, namespaces=False, sort=False):
    obj = oxml.parse(input.read(), process_namespaces=namespaces)
    if sort:
        obj = sort_ordereddict(obj)
    return obj


def yaml(input, sort=False):
    obj = oyaml.read_yaml(input)
    if sort:
        obj = sort_ordereddict(obj)
    return obj
