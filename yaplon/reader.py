#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

__version__ = '0.0.1'

from . import ojson
from . import oplist
from . import oyaml
import xmltodict as oxml
import csv as ocsv

from collections import OrderedDict

def sortOD(od):
    res = OrderedDict()
    for k, v in sorted(od.items()):
        if isinstance(v, dict):
            res[k] = sortOD(v)
        else:
            res[k] = v
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
        if key:
            if key <= len(fields):
                obj = OrderedDict()
            else:
                key = None
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
        obj = sortOD(obj)
    return obj

def json(input, sort=False):
    obj = ojson.read_json(input)
    if sort:
        obj = sortOD(obj)
    return obj

def plist(input, sort=False):
    obj = oplist.read_plist(input)
    if sort:
        obj = sortOD(obj)
    return obj

def xml(input, namespaces=False, sort=False):
    obj = oxml.parse(input.read(), process_namespaces=namespaces)
    if sort:
        obj = sortOD(obj)
    return obj

def yaml(input, sort=False):
    obj = oyaml.read_yaml(input)
    if sort:
        obj = sortOD(obj)
    return obj
