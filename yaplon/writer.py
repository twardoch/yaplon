#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

__version__ = '0.0.1'

import click
from yaplon import ojson
from yaplon import oplist
from yaplon import oyaml
import xmltodict as oxml
import dict2xml
from collections import OrderedDict, Mapping


def json(obj, output, mini=False, binary=False):
    output.write(ojson.json_dumps(obj, preserve_binary=binary, compact=mini))

def plist(obj, output, binary=False):
    if binary:
        output = click.File("wb")(output)
        output.write(oplist.plist_binary_dumps(obj))
    else:
        output = click.File("w")(output)
        output.write(oplist.plist_dumps(obj))

def _simplexml(obj, output, mini=False, tag=''):
    if mini:
        indent = ''
        newlines = False
    else:
        indent = '  '
        newlines = True
    output.write(
        dict2xml.Converter(
            wrap=tag, indent=indent, newlines=newlines
        ).build(obj)
    )

def xml(obj, output, mini=False, tag=None, root='root'):
    # This is extremely primitive and buggy
    if isinstance(obj, Mapping):
        obj = OrderedDict(obj)
        if len(obj.keys()) > 1:
            obj = OrderedDict([(root, obj)])
        else:
            root=list(obj.keys())[0]
    else:
        obj = OrderedDict([(root, obj)])
    if tag:
        _simplexml(obj, output, mini, tag)
    else:
        pretty = not mini
        try:
            oxml.unparse(obj, output, full_document=True, short_empty_elements=mini, pretty=pretty)
        except:
            pass

def yaml(obj, output, mini=False):
    output.write(oyaml.yaml_dumps(obj, compact=mini))


