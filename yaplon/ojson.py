"""
Serialized Data Converter.

Licensed under MIT
Copyright (c) 2012 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""

import base64
import collections
import json
import plistlib

__all__ = ("read_json", "json_dumps")


def json_dumps(obj, preserve_binary=False, compact=False):
    """Wrap json dumps."""
    if compact:
        indent = None
        separators = (',', ':')
    else:
        indent = 4
        separators = (',', ': ')

    return json.dumps(
        json_convert_to(obj, preserve_binary),
        ensure_ascii=False,
        sort_keys=False,
        indent=indent,
        separators=separators
    ).encode('utf-8').decode('raw_unicode_escape')


def read_json(stream):
    return json_convert_from(
        json.load(stream, object_pairs_hook=collections.OrderedDict
                  )
    )


def json_convert_to(obj, preserve_binary=False):
    """Strip tabs and trailing spaces to allow block format to successfully be triggered."""

    if isinstance(obj, (dict, collections.OrderedDict)):
        for k, v in obj.items():
            obj[k] = json_convert_to(v, preserve_binary)
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = json_convert_to(v, preserve_binary)
            count += 1
    # elif isinstance(obj, plistlib.Data):
    #    if preserve_binary:
    #        obj = collections.OrderedDict(
    #            [("!!python/object:plistlib.Data",
    #              base64.b64encode(obj.data).decode("ascii"))]
    #        )
    #    else:
    #        obj = base64.b64encode(obj.data).decode("ascii")

    return obj


def json_convert_from(obj):
    """Convert specific json items to a form usuable by others."""

    if isinstance(obj, (dict, collections.OrderedDict)):
        if len(obj) == 1 and "!!python/object:plistlib.Data" in obj:
            obj = obj["!!python/object:plistlib.Data"]
        else:
            for k, v in obj.items():
                obj[k] = json_convert_from(v)
    elif isinstance(obj, list):
        count = 0
        for v in obj:
            obj[count] = json_convert_from(v)
            count += 1

    return obj
