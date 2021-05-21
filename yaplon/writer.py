#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

__version__ = '0.0.1'

import click
from . import ojson
from . import oplist
from . import oyaml
import xmltodict as oxml
import dict2xml
from collections import OrderedDict

def json(obj, output, mini=False, binary=False):
    output.write(ojson.json_dumps(obj, preserve_binary=binary, compact=mini))

def plist(obj, output, binary=False):
    if binary:
        output = click.File("wb")(output)
        output.write(oplist.plist_binary_dumps(obj))
    else:
        output = click.File("w")(output)
        output.write(oplist.plist_dumps(obj))

def _simplexml(obj, output, mini=False):
    if mini:
        indent = ''
        newlines = False
    else:
        indent = '  '
        newlines = True
    output.write(
        dict2xml.Converter(
            wrap="", indent=indent, newlines=newlines
        ).build(obj)
    )

def xml(obj, output, mini=False, simple=False, header=True, root='root'):
    if type(obj) == type(list()):
        obj = OrderedDict([(root, obj)])
    elif type(obj) == type(dict()):
        obj = OrderedDict(obj)
    if len(obj.keys()) > 1:
        obj = OrderedDict([(root, obj)])
    pretty = not mini
    if simple:
        _simplexml(obj, output, mini)
    else:
        try:
            oxml.unparse(obj, output, full_document=header, short_empty_elements=mini, pretty=pretty)
        except AttributeError:
            _simplexml(obj, output, mini)

def yaml(obj, output, mini=False):
    output.write(oyaml.yaml_dumps(obj, compact=mini))


