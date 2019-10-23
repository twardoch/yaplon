#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    yaplon
    ------
    Copyright (c) 2019 Adam Twardoch <adam+github@twardoch.com>
    Copyright (c) 2012-2015 Isaac Muse <isaacmuse@gmail.com>
    MIT license. Python 3.7.
    Based on https://github.com/facelessuser/SerializedDataConverter

    Convert between JSON, YAML and PLIST (binary and XML) in the commandline.
    Usage: yaplon j2p|j2y|p2j|p2y|y2j|y2p -i input -o output [options]
    Also installs direct CLI tools:
    json22plist, json22yaml, plist22json, plist22yaml, yaml22json, yaml22plist
"""

import click
from . import __version__
from . import ojson
from . import oplist
from . import oyaml

from collections import OrderedDict

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

VERSION = __version__

def sortOD(od):
    res = OrderedDict()
    for k, v in sorted(od.items()):
        if isinstance(v, dict):
            res[k] = sortOD(v)
        else:
            res[k] = v
    return res

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=VERSION)
def cli():
    """
    Convert between JSON, YAML and PLIST (binary and XML) in the commandline.

    Usage: yaplon j2p|j2y|p2j|p2y|y2j|y2p -i input -o output [options]

    Omit -i to use stdin. Omit -o to use stdout.
    Type 'yaplon command --help' for more info on each conversion command.
    """

# json22plist


@cli.command(
    'j2p', context_settings=CONTEXT_SETTINGS,
    short_help='-i JSON -o PLIST [-b] (make binary PLIST)'
    )
@click.version_option(version=VERSION)
@click.option(
    '-i', '--in', 'input', default='-',
    type=click.File('r'),
    help="input JSON file, stdin if '-' or omitted"
    )
@click.option('-o', '--out', 'output', default='-',
              type=str,
              help="output PLIST file, stdout if '-' or omitted"
              )
@click.option('-b', '--bin', 'binary',
              is_flag=True,
              help="output binary PLIST"
              )
@click.option('-s', '--sort', 'sort',
              is_flag=True,
              help="sort data"
              )
def json2plist(input, output, binary, sort):
    """
    -i JSON -o PLIST [-b] (make binary PLIST)
    """
    obj = ojson.read_json(input)
    if sort:
        obj = sortOD(obj)
    if binary:
        output = click.File("wb")(output)
        output.write(oplist.plist_binary_dumps(obj))
    else:
        output = click.File("w")(output)
        output.write(oplist.plist_dumps(obj))


# json22yaml


@cli.command(
    'j2y', context_settings=CONTEXT_SETTINGS,
    short_help='-i JSON -o YAML [-m] (minify YAML)'
    )
@click.version_option(version=VERSION)
@click.option(
    '-i', '--in', 'input', default='-',
    type=click.File('r'),
    help="input JSON file, stdin if '-' or omitted"
    )
@click.option('-o', '--out', 'output', default='-',
              type=click.File('w'),
              help="output YAML file, stdout if '-' or omitted"
              )
@click.option('-m', '--mini', 'mini',
              is_flag=True,
              help="output minified YAML"
              )
@click.option('-s', '--sort', 'sort',
              is_flag=True,
              help="sort data"
              )
def json2yaml(input, output, mini, sort):
    """
    -i JSON -o YAML [-m] (minify YAML)
    """
    obj = ojson.read_json(input)
    if sort:
        obj = sortOD(obj)
    output.write(oyaml.yaml_dumps(obj, compact=mini))


# plist22json


@cli.command(
    'p2j', context_settings=CONTEXT_SETTINGS,
    short_help='-i PLIST -o JSON [-m] (minify) [-b] (keep binary)'
    )
@click.version_option(version=VERSION)
@click.option(
    '-i', '--in', 'input', default='-',
    type=click.File('rb'),
    help="input PLIST file, stdin if '-' or omitted"
    )
@click.option('-o', '--out', 'output', default='-',
              type=click.File('w'),
              help="output JSON file, stdout if '-' or omitted"
              )
@click.option('-b', '--bin', 'binary',
              is_flag=True,
              help="preserve binary in JSON"
              )
@click.option('-m', '--mini', 'mini',
              is_flag=True,
              help="output minified JSON"
              )
@click.option('-s', '--sort', 'sort',
              is_flag=True,
              help="sort data"
              )
def plist2json(input, output, mini, binary, sort):
    """
    -i PLIST -o JSON [-m] (minify) [-b] (keep binary)
    """
    obj = oplist.read_plist(input)
    if sort:
        obj = sortOD(obj)
    output.write(ojson.json_dumps(obj, preserve_binary=binary, compact=mini))


# plist22yaml


@cli.command(
    'p2y', context_settings=CONTEXT_SETTINGS,
    short_help='-i PLIST -o YAML [-m] (minify YAML)'
    )
@click.version_option(version=VERSION)
@click.option(
    '-i', '--in', 'input', default='-',
    type=click.File('rb'),
    help="input PLIST file, stdin if '-' or omitted"
    )
@click.option('-o', '--out', 'output', default='-',
              type=click.File('w'),
              help="output YAML file, stdout if '-' or omitted"
              )
@click.option('-m', '--mini', 'mini',
              is_flag=True,
              help="output minified YAML"
              )
@click.option('-s', '--sort', 'sort',
              is_flag=True,
              help="sort data"
              )
def plist2yaml(input, output, mini, sort):
    """
    -i PLIST -o YAML [-m] (minify YAML)
    """
    obj = oplist.read_plist(input)
    if sort:
        obj = sortOD(obj)
    output.write(oyaml.yaml_dumps(obj, compact=mini))


# yaml22json


@cli.command(
    'y2j', context_settings=CONTEXT_SETTINGS,
    short_help='-i YAML -o JSON [-m] (minify) [-b] (keep binary)'
    )
@click.version_option(version=VERSION)
@click.option(
    '-i', '--in', 'input', default='-',
    type=click.File('r'),
    help="input YAML file, stdin if '-' or omitted"
    )
@click.option('-o', '--out', 'output', default='-',
              type=click.File('w'),
              help="output JSON file, stdout if '-' or omitted"
              )
@click.option('-b', '--bin', 'binary',
              is_flag=True,
              help="preserve binary in JSON"
              )
@click.option('-m', '--mini', 'mini',
              is_flag=True,
              help="output minified JSON"
              )
@click.option('-s', '--sort', 'sort',
              is_flag=True,
              help="sort data"
              )
def yaml2json(input, output, mini, binary, sort):
    """
    -i YAML -o JSON [-m] (minify) [-b] (keep binary)
    """
    obj = oyaml.read_yaml(input)
    if sort:
        obj = sortOD(obj)
    output.write(ojson.json_dumps(obj, preserve_binary=binary, compact=mini))


# yaml22plist


@cli.command(
    'y2p', context_settings=CONTEXT_SETTINGS,
    short_help='-i YAML -o PLIST [-b] (make binary PLIST)'
    )
@click.version_option(version=VERSION)
@click.option(
    '-i', '--in', 'input', default='-',
    type=click.File('r'),
    help="input YAML file, stdin if '-' or omitted"
    )
@click.option('-o', '--out', 'output', default='-',
              type=str,
              help="output PLIST file, stdout if '-' or omitted"
              )
@click.option('-b', '--bin', 'binary',
              is_flag=True,
              help="output binary PLIST"
              )
@click.option('-s', '--sort', 'sort',
              is_flag=True,
              help="sort data"
              )
def yaml2plist(input, output, binary, sort):
    """
    -i YAML -o PLIST [-b] (make binary PLIST)
    """
    obj = oyaml.read_yaml(input)
    if sort:
        obj = sortOD(obj)
    if binary:
        output = click.File("wb")(output)
        output.write(oplist.plist_binary_dumps(obj))
    else:
        output = click.File("w")(output)
        output.write(oplist.plist_dumps(obj))


if __name__ == '__main__':
    cli()
