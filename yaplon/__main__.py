#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yaplon
------
Copyright (c) 2019-2024 Adam Twardoch <adam+github@twardoch.com> & Jules (AI Agent)
Copyright (c) 2012-2015 Isaac Muse <isaacmuse@gmail.com>
MIT license. Requires Python 3.9+.
Based on https://github.com/facelessuser/SerializedDataConverter

Convert between JSON, YAML, PLIST (binary/XML), XML, and CSV (read-only for CSV input)
in the commandline. Can be used in piping.

Usage: yaplon <command> [options]
Example: yaplon j2y -i input.json -o output.yaml

Also installs direct CLI tools for each conversion, e.g., json22yaml, plist22json.
(Full list in README.md or by running 'yaplon --help').
"""

import click
import sys # Added for sys.stdout

from yaplon import __version__
from yaplon import reader
from yaplon import writer

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

VERSION = __version__


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=VERSION)
def cli():
    """
    Convert between JSON, YAML, PLIST (binary/XML),
    XML and CSV (read-only) in the commandline.

    Usage: yaplon [c|j|p|x|y]2[j|p|x|y] -i input -o output [options]

    Omit -i to use stdin. Omit -o to use stdout.
    Type 'yaplon command --help' for more info on each conversion command.
    """


# json22plist


@cli.command(
    "j2p",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert JSON to Plist. Options: [-s] [-b]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"),
    help="input JSON file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output_path", # Renamed to output_path
    default="-",
    type=click.Path(allow_dash=True), # Changed to Path
    help="output PLIST file, stdout if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="output binary PLIST")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def json2plist(input, output_path, binary, sort): # output renamed to output_path
    """Converts JSON input to Plist output.

    Input is read from a JSON file (or stdin).
    Output is written to a Plist file (or stdout).

    Options:
      -b, --bin: Output binary Plist format. Default is XML Plist.
      -s, --sort: Sort input JSON dictionary keys before conversion.
    """
    data = reader.json(input, sort=sort)
    if output_path == "-":
        output_stream = sys.stdout.buffer if binary else sys.stdout
        writer.plist(data, output_stream, binary=binary)
    else:
        mode = "wb" if binary else "w"
        encoding = None if binary else "utf-8"
        with open(output_path, mode, encoding=encoding) as f:
            writer.plist(data, f, binary=binary)


# json22yaml


@cli.command(
    "j2y",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert JSON to YAML. Options: [-s] [-m]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"),
    help="input JSON file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output",
    default="-",
    type=click.File("w"),
    help="output YAML file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified YAML")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def json2yaml(input, output, mini, sort):
    """Converts JSON input to YAML output.

    Input is read from a JSON file (or stdin).
    Output is written to a YAML file (or stdout).

    Options:
      -m, --mini: Output minified YAML (flow style, less indentation).
      -s, --sort: Sort input JSON dictionary keys before conversion.
    """
    writer.yaml(reader.json(input, sort=sort), output, mini=mini)


# plist22json


@cli.command(
    "p2j",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert Plist to JSON. Options: [-s] [-m] [-b]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("rb"),
    help="input PLIST file, stdin if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="preserve binary in JSON")
@click.option(
    "-o",
    "--out",
    "output",
    default="-",
    type=click.File("w"),
    help="output JSON file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified JSON")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def plist2json(input, output, mini, binary, sort):
    """Converts Plist input to JSON output.

    Input is read from a Plist file (XML or binary, or stdin).
    Output is written to a JSON file (or stdout).

    Options:
      -m, --mini: Output minified JSON (no indentation or newlines).
      -b, --bin: Preserve binary data from Plist <data> tags as base64
                 encoded strings in JSON, instead of the default special
                 dictionary representation `{"__bytes__": true, "base64": "..."}`.
      -s, --sort: Sort input Plist dictionary keys before conversion.
    """
    writer.json(reader.plist(input, sort=sort), output, mini=mini, binary=binary)


# plist22yaml


@cli.command(
    "p2y",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert Plist to YAML. Options: [-s] [-m]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("rb"),
    help="input PLIST file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output",
    default="-",
    type=click.File("w"),
    help="output YAML file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified YAML")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def plist2yaml(input, output, mini, sort):
    """Converts Plist input to YAML output.

    Input is read from a Plist file (XML or binary, or stdin).
    Output is written to a YAML file (or stdout).
    Binary data in Plist (<data> tags) becomes YAML `!!binary` tags.

    Options:
      -m, --mini: Output minified YAML (flow style, less indentation).
      -s, --sort: Sort input Plist dictionary keys before conversion.
    """
    writer.yaml(reader.plist(input, sort=sort), output, mini=mini)


# yaml22json


@cli.command(
    "y2j",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert YAML to JSON. Options: [-s] [-m] [-b]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"),
    help="input YAML file, stdin if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="preserve binary in JSON")
@click.option(
    "-o",
    "--out",
    "output",
    default="-",
    type=click.File("w"),
    help="output JSON file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified JSON")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def yaml2json(input, output, mini, binary, sort):
    """Converts YAML input to JSON output.

    Input is read from a YAML file (or stdin).
    Output is written to a JSON file (or stdout).
    YAML `!!binary` tags are converted to Python bytes and then to JSON
    based on the -b flag.

    Options:
      -m, --mini: Output minified JSON.
      -b, --bin: Preserve binary data from YAML `!!binary` tags as base64
                 encoded strings in JSON, instead of the default special
                 dictionary representation `{"__bytes__": true, "base64": "..."}`.
      -s, --sort: Sort input YAML dictionary keys before conversion.
    """
    writer.json(reader.yaml(input, sort=sort), output, mini=mini, binary=binary)


# yaml22plist


@cli.command(
    "y2p",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert YAML to Plist. Options: [-s] [-b]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"),
    help="input YAML file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output_path", # Renamed to output_path
    default="-",
    type=click.Path(allow_dash=True), # Changed to Path
    help="output PLIST file, stdout if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="output binary PLIST")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def yaml2plist(input, output_path, binary, sort): # output renamed to output_path
    """Converts YAML input to Plist output.

    Input is read from a YAML file (or stdin).
    Output is written to a Plist file (or stdout).
    YAML `!!binary` tags are converted to Python bytes, which then become
    Plist <data> elements.

    Options:
      -b, --bin: Output binary Plist format. Default is XML Plist.
      -s, --sort: Sort input YAML dictionary keys before conversion.
    """
    data = reader.yaml(input, sort=sort)
    if output_path == "-":
        output_stream = sys.stdout.buffer if binary else sys.stdout
        writer.plist(data, output_stream, binary=binary)
    else:
        mode = "wb" if binary else "w"
        encoding = None if binary else "utf-8"
        with open(output_path, mode, encoding=encoding) as f:
            writer.plist(data, f, binary=binary)


# csv22json


@cli.command(
    "c2j",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert CSV to JSON. Options: [-H] [-d DIALECT] [-k KEY] [-s] [-m]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"),
    help="input CSV file, stdin if '-' or omitted",
)
@click.option(
    "-H", "--header", "header", is_flag=True, help="CSV has header and reads as dict"
)
@click.option(
    "-d",
    "--dialect",
    "dialect",
    default=None,
    type=str,
    help="CSV dialect like 'excel' or 'excel-tab'",
)
@click.option(
    "-k",
    "--key",
    "key",
    default=0,
    type=int,
    help="if CSV has header, use column number as main key",
)
@click.option(
    "-o",
    "--out",
    "output",
    default="-",
    type=click.File("w"),
    help="output JSON file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified JSON")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def csv2json(input, output, dialect, header, key, mini, sort):
    """Converts CSV input to JSON output. (CSV input is read-only).

    Input is read from a CSV file (or stdin).
    Output is written to a JSON file (or stdout).

    Options:
      -H, --header: Treat first row as header. Reads CSV as a list of dictionaries.
      -d, --dialect: Specify CSV dialect (e.g., 'excel', 'excel-tab', 'unix').
      -k, --key: If CSV has header, use column number (int) as key for a top-level dict.
      -m, --mini: Output minified JSON.
      -s, --sort: Sort data (e.g. keys of dicts if -H used, or main dict keys if -k used).
    """
    writer.json(
        reader.csv(input, dialect=dialect, header=header, key=key, sort=sort),
        output,
        mini=mini,
    )


# csv22yaml


@cli.command(
    "c2y",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert CSV to YAML. Options: [-H] [-d DIALECT] [-k KEY] [-s] [-m]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"),
    help="input CSV file, stdin if '-' or omitted",
)
@click.option(
    "-H", "--header", "header", is_flag=True, help="CSV has header and reads as dict"
)
@click.option(
    "-d",
    "--dialect",
    "dialect",
    default=None,
    type=str,
    help="CSV dialect like 'excel' or 'excel-tab'",
)
@click.option(
    "-k",
    "--key",
    "key",
    default=0,
    type=int,
    help="if CSV has header, use column number as main key",
)
@click.option(
    "-o",
    "--out",
    "output",
    default="-",
    type=click.File("w"),
    help="output YAML file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified YAML")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def csv2yaml(input, output, dialect, header, key, mini, sort):
    """Converts CSV input to YAML output. (CSV input is read-only).

    Input is read from a CSV file (or stdin).
    Output is written to a YAML file (or stdout).

    Options:
      -H, --header: Treat first row as header. Reads CSV as a list of dictionaries.
      -d, --dialect: Specify CSV dialect (e.g., 'excel', 'excel-tab', 'unix').
      -k, --key: If CSV has header, use column number (int) as key for a top-level dict.
      -m, --mini: Output minified YAML.
      -s, --sort: Sort data.
    """
    writer.yaml(
        reader.csv(input, dialect=dialect, header=header, key=key, sort=sort),
        output,
        mini=mini,
    )


# csv22plist


@cli.command(
    "c2p",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert CSV to Plist. Options: [-H] [-d DIALECT] [-k KEY] [-s] [-b]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"),
    help="input CSV file, stdin if '-' or omitted",
)
@click.option(
    "-H", "--header", "header", is_flag=True, help="CSV has header and reads as dict"
)
@click.option(
    "-d",
    "--dialect",
    "dialect",
    default=None,
    type=str,
    help="CSV dialect like 'excel' or 'excel-tab'",
)
@click.option(
    "-k",
    "--key",
    "key",
    default=0,
    type=int,
    help="if CSV has header, use column number as main key",
)
@click.option(
    "-o",
    "--out",
    "output_path",  # Renamed
    default="-",
    type=click.Path(allow_dash=True), # Changed
    help="output PLIST file, stdout if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="output binary PLIST")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def csv2plist(input, output_path, dialect, header, key, binary, sort): # Renamed output
    """Converts CSV input to Plist output. (CSV input is read-only).

    Input is read from a CSV file (or stdin).
    Output is written to a Plist file (or stdout).

    Options:
      -H, --header: Treat first row as header.
      -d, --dialect: Specify CSV dialect.
      -k, --key: If CSV has header, use column number (int) as key for a top-level dict.
      -b, --bin: Output binary Plist.
      -s, --sort: Sort data.
    """
    data = reader.csv(input, dialect=dialect, header=header, key=key, sort=sort)
    if output_path == "-":
        output_stream = sys.stdout.buffer if binary else sys.stdout
        writer.plist(data, output_stream, binary=binary)
    else:
        mode = "wb" if binary else "w"
        encoding = None if binary else "utf-8"
        with open(output_path, mode, encoding=encoding) as f:
            writer.plist(data, f, binary=binary)


# json22xml


@cli.command(
    "j2x",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert JSON to XML. Options: [-s] [-m] [-R ROOT] [-t TAG]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"),
    help="input JSON file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output_stream", # Renamed
    default="-",
    type=click.File('w', encoding='utf-8'), # Changed
    help="output XML file, stdout if '-' or omitted",
)
@click.option(
    "-R", "--root", "root", default="root", type=str, help="root XML element if missing"
)
@click.option("-t", "--tag", "tag", type=str, help="wrap in tag")
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified XML")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def json2xml(input, output_stream, mini, tag, root, sort): # Renamed output
    """Converts JSON input to XML output.

    Input is read from a JSON file (or stdin).
    Output is written to an XML file (or stdout).

    Options:
      -m, --mini: Output minified XML.
      -R, --root <name>: Specify root tag name. (Used by xmltodict backend).
      -t, --tag <name>: Wrap output in this tag. (Uses dict2xml backend, simpler XML).
                       If -t is used, -R is ignored.
      -s, --sort: Sort input JSON dictionary keys.
    """
    writer.xml(reader.json(input, sort=sort), output_stream, mini=mini, tag=tag, root=root)


# plist22xml


@cli.command(
    "p2x",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert Plist to XML. Options: [-s] [-m] [-R ROOT] [-t TAG]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("rb"),
    help="input PLIST file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output",
    default="-",
    type=click.File("w"),
    help="output XML file, stdout if '-' or omitted",
)
@click.option(
    "-R", "--root", "root", default="root", type=str, help="root XML element if missing"
)
@click.option("-t", "--tag", "tag", type=str, help="wrap in tag")
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified XML")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def plist2xml(input, output, mini, tag, root, sort):
    """Converts Plist input to XML output.

    Input is read from a Plist file (XML or binary, or stdin).
    Output is written to an XML file (or stdout).
    Plist <data> and <date> are converted to strings/ISO strings before XML generation.

    Options:
      -m, --mini: Output minified XML.
      -R, --root <name>: Specify root tag name (xmltodict backend).
      -t, --tag <name>: Wrap output in this tag (dict2xml backend).
      -s, --sort: Sort input Plist dictionary keys.
    """
    writer.xml(reader.plist(input, sort=sort), output, mini=mini, tag=tag, root=root)


# yaml22xml


@cli.command(
    "y2x",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert YAML to XML. Options: [-s] [-m] [-R ROOT] [-t TAG]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"), # Corrected: YAML input is text
    help="input YAML file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output",
    default="-",
    type=click.File("w"),
    help="output XML file, stdout if '-' or omitted",
)
@click.option(
    "-R", "--root", "root", default="root", type=str, help="root XML element if missing"
)
@click.option("-t", "--tag", "tag", type=str, help="wrap in tag")
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified XML")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def yaml2xml(input, output, mini, tag, root, sort):
    """Converts YAML input to XML output.

    Input is read from a YAML file (or stdin).
    Output is written to an XML file (or stdout).
    YAML `!!binary` tags become base64 strings, `!!timestamp` become ISO strings in XML.

    Options:
      -m, --mini: Output minified XML.
      -R, --root <name>: Specify root tag name (xmltodict backend).
      -t, --tag <name>: Wrap output in this tag (dict2xml backend).
      -s, --sort: Sort input YAML dictionary keys.
    """
    writer.xml(reader.yaml(input, sort=sort), output, mini=mini, tag=tag, root=root)


# csv22xml


@cli.command(
    "c2x",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert CSV to XML. Options: [-H] [-d DIALECT] [-k KEY] [-s] [-m] [-R ROOT] [-t TAG]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"),
    help="input CSV file, stdin if '-' or omitted",
)
@click.option(
    "-H", "--header", "header", is_flag=True, help="CSV has header and reads as dict"
)
@click.option(
    "-d",
    "--dialect",
    "dialect",
    default=None,
    type=str,
    help="CSV dialect like 'excel' or 'excel-tab'",
)
@click.option(
    "-k",
    "--key",
    "key",
    default=0,
    type=int,
    help="if CSV has header, use column number as main key",
)
@click.option(
    "-o",
    "--out",
    "output",
    default="-",
    type=click.File("w"),
    help="output XML file, stdout if '-' or omitted",
)
@click.option(
    "-R", "--root", "root", default="root", type=str, help="root XML element if missing"
)
@click.option("-t", "--tag", "tag", type=str, help="wrap in tag")
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified XML")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def csv2xml(input, output, dialect, header, key, mini, tag, root, sort):
    """Converts CSV input to XML output. (CSV input is read-only).

    Input is read from a CSV file (or stdin).
    Output is written to an XML file (or stdout).

    Options:
      -H, --header: Treat first row as header.
      -d, --dialect: Specify CSV dialect.
      -k, --key: If CSV has header, use column number (int) as key for a top-level dict.
      -m, --mini: Output minified XML.
      -R, --root <name>: Specify root tag name (xmltodict backend).
      -t, --tag <name>: Wrap output in this tag (dict2xml backend).
      -s, --sort: Sort data.
    """
    writer.xml(
        reader.csv(input, dialect=dialect, header=header, key=key, sort=sort),
        output,
        mini=mini,
        tag=tag,
        root=root,
    )


# xml22plist


@cli.command(
    "x2p",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert XML to Plist. Options: [-N] [-s] [-b]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"), # XML input is text
    help="input XML file, stdin if '-' or omitted",
)
@click.option(
    "-N", "--namespaces", "namespaces", is_flag=True, help="read XML namespaces"
)
@click.option(
    "-o",
    "--out",
    "output_path", # Renamed
    default="-",
    type=click.Path(allow_dash=True), # Changed
    help="output PLIST file, stdout if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="output binary PLIST")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def xml2plist(input, output_path, namespaces, binary, sort): # Renamed output
    """Converts XML input to Plist output.

    Input is read from an XML file (or stdin).
    Output is written to a Plist file (or stdout).
    XML content is parsed to a Python dictionary; numeric/boolean strings
    are converted to Python types before Plist serialization.

    Options:
      -N, --namespaces: Read XML namespaces (affects dict keys).
      -b, --bin: Output binary Plist format.
      -s, --sort: Sort dictionary keys from XML before Plist conversion.
    """
    data = reader.xml(input, namespaces=namespaces, sort=sort)
    if output_path == "-":
        output_stream = sys.stdout.buffer if binary else sys.stdout
        writer.plist(data, output_stream, binary=binary)
    else:
        mode = "wb" if binary else "w"
        encoding = None if binary else "utf-8"
        with open(output_path, mode, encoding=encoding) as f:
            writer.plist(data, f, binary=binary)


# xml22yaml


@cli.command(
    "x2y",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert XML to YAML. Options: [-N] [-s] [-m]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"), # XML input is text
    help="input XML file, stdin if '-' or omitted",
)
@click.option(
    "-N", "--namespaces", "namespaces", is_flag=True, help="read XML namespaces"
)
@click.option(
    "-o",
    "--out",
    "output",
    default="-",
    type=click.File("w"),
    help="output YAML file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified YAML")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def xml2yaml(input, output, namespaces, mini, sort):
    """Converts XML input to YAML output.

    Input is read from an XML file (or stdin).
    Output is written to a YAML file (or stdout).
    XML content is parsed to a Python dictionary; this dictionary is then
    serialized to YAML. Base64 strings in XML become plain YAML strings.

    Options:
      -N, --namespaces: Read XML namespaces.
      -m, --mini: Output minified YAML.
      -s, --sort: Sort dictionary keys from XML.
    """
    writer.yaml(reader.xml(input, namespaces=namespaces, sort=sort), output, mini=mini)


# xml22json


@cli.command(
    "x2j",
    context_settings=CONTEXT_SETTINGS,
    short_help="Convert XML to JSON. Options: [-N] [-s] [-m]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input",
    default="-",
    type=click.File("r"), # Corrected: XML input is text
    help="input XML file, stdin if '-' or omitted",
)
@click.option(
    "-N", "--namespaces", "namespaces", is_flag=True, help="read XML namespaces"
)
@click.option(
    "-o",
    "--out",
    "output",
    default="-",
    type=click.File("w"),
    help="output JSON file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified JSON")
@click.option("-s", "--sort", "sort", is_flag=True, help="sort data")
def xml2json(input, output, namespaces, mini, sort):
    """Converts XML input to JSON output.

    Input is read from an XML file (or stdin).
    Output is written to a JSON file (or stdout).
    XML content is parsed to a Python dictionary which is then serialized to JSON.
    The -b (binary preservation) flag is NOT available for this command.

    Options:
      -N, --namespaces: Read XML namespaces.
      -m, --mini: Output minified JSON.
      -s, --sort: Sort dictionary keys from XML.
    """
    writer.json(reader.xml(input, namespaces=namespaces, sort=sort), output, mini=mini)


if __name__ == "__main__":
    cli()
