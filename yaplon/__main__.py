#!/usr/bin/env python3
"""
yaplon
------
Copyright (c) 2019 Adam Twardoch <adam+github@twardoch.com>
Copyright (c) 2012-2015 Isaac Muse <isaacmuse@gmail.com>
MIT license. Python 3.7.
Based on https://github.com/facelessuser/SerializedDataConverter

Convert between JSON, YAML and PLIST (binary and XML) in the commandline.
Usage: yaplon j2p|j2y|p2j|p2y|y2j|y2p -i input_file -o output_file [options]
Also installs direct CLI tools:
json22plist, json22yaml, plist22json, plist22yaml, yaml22json, yaml22plist
"""

import click

from yaplon import __version__, reader, writer

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

VERSION = __version__


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=VERSION)
def cli():
    """
    Convert between JSON, YAML, PLIST (binary/XML),
    XML and CSV (read-only) in the commandline.

    Usage: yaplon [c|j|p|x|y]2[j|p|x|y] -i input_file -o output_file [options]

    Omit -i to use stdin. Omit -o to use stdout.
    Type 'yaplon command --help' for more info on each conversion command.
    """


# json22plist


@cli.command(
    "j2p",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i JSON -o PLIST [-b] (make binary PLIST)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("r"),
    help="input JSON file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("wb"), # Changed from str to click.File("wb")
    help="output PLIST file, stdout if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="output binary PLIST")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def json2plist(input_file, output_file, binary, sort_keys):
    """
    -i JSON -o PLIST [-b] (make binary PLIST)
    """
    obj = reader.json_reader(input_stream=input_file, sort_data=sort_keys)
    writer.plist_writer(obj, output_stream=output_file, binary_format=binary)


# json22yaml


@cli.command(
    "j2y",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i JSON -o YAML [-m] (minify YAML)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("r"),
    help="input JSON file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("w"),
    help="output YAML file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified YAML")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def json2yaml(input_file, output_file, mini, sort_keys):
    """
    -i JSON -o YAML [-m] (minify YAML)
    """
    obj = reader.json_reader(input_stream=input_file, sort_data=sort_keys)
    writer.yaml_writer(obj, output_stream=output_file, mini=mini)


# plist22json


@cli.command(
    "p2j",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i PLIST -o JSON [-m] (minify) [-b] (keep binary)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("rb"),
    help="input PLIST file, stdin if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="preserve binary in JSON")
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("wb"), # Changed from "w" to "wb"
    help="output JSON file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified JSON")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def plist2json(input_file, output_file, mini, binary, sort_keys):
    """
    -i PLIST -o JSON [-m] (minify) [-b] (keep binary)
    """
    obj = reader.plist_reader(input_stream=input_file, sort_data=sort_keys)
    writer.json_writer(
        obj, output_stream=output_file, mini=mini, preserve_binary=binary
    )


# plist22yaml


@cli.command(
    "p2y",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i PLIST -o YAML [-m] (minify YAML)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("rb"),
    help="input PLIST file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("w"),
    help="output YAML file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified YAML")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def plist2yaml(input_file, output_file, mini, sort_keys):
    """
    -i PLIST -o YAML [-m] (minify YAML)
    """
    obj = reader.plist_reader(input_stream=input_file, sort_data=sort_keys)
    writer.yaml_writer(obj, output_stream=output_file, mini=mini)


# yaml22json


@cli.command(
    "y2j",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i YAML -o JSON [-m] (minify) [-b] (keep binary)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("r"),
    help="input YAML file, stdin if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="preserve binary in JSON")
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("wb"), # Changed from "w" to "wb"
    help="output JSON file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified JSON")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def yaml2json(input_file, output_file, mini, binary, sort_keys):
    """
    -i YAML -o JSON [-m] (minify) [-b] (keep binary)
    """
    obj = reader.yaml_reader(input_stream=input_file, sort_data=sort_keys)
    writer.json_writer(
        obj, output_stream=output_file, mini=mini, preserve_binary=binary
    )


# yaml22plist


@cli.command(
    "y2p",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i YAML -o PLIST [-b] (make binary PLIST)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("r"),
    help="input YAML file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("wb"), # Changed from str to click.File("wb")
    help="output PLIST file, stdout if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="output binary PLIST")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def yaml2plist(input_file, output_file, binary, sort_keys):
    """
    -i YAML -o PLIST [-b] (make binary PLIST)
    """
    obj = reader.yaml_reader(input_stream=input_file, sort_data=sort_keys)
    writer.plist_writer(obj, output_stream=output_file, binary_format=binary)


# csv22json


@cli.command(
    "c2j",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i CSV -o JSON [-d DIALECT] [-k KEY] [-m] (minify)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
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
    "output_file",
    default="-",
    type=click.File("wb"), # Changed from "w" to "wb"
    help="output JSON file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified JSON")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def csv2json(input_file, output_file, dialect, header, key, mini, sort_keys):
    """
    -i CSV -o JSON [-d DIALECT] [-k KEY] [-m] (minify)
    """
    obj = reader.csv_reader(
        input_stream=input_file,
        dialect_name=dialect,
        has_header=header,
        key_column_index=key,
        sort_data=sort_keys,
    )
    writer.json_writer(obj, output_stream=output_file, mini=mini)


# csv22yaml


@cli.command(
    "c2y",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i CSV -o YAML [-d DIALECT] [-k KEY] [-m] (minify)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
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
    "output_file",
    default="-",
    type=click.File("w"),
    help="output YAML file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified YAML")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def csv2yaml(input_file, output_file, dialect, header, key, mini, sort_keys):
    """
    -i CSV -o YAML [-d DIALECT] [-k KEY] [-m] (minify)
    """
    obj = reader.csv_reader(
        input_stream=input_file,
        dialect_name=dialect,
        has_header=header,
        key_column_index=key,
        sort_data=sort_keys,
    )
    writer.yaml_writer(obj, output_stream=output_file, mini=mini)


# csv22plist


@cli.command(
    "c2p",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i CSV -o PLIST [-d DIALECT] [-k KEY] [-m] (minify)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
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
    "output_file",
    default="-",
    type=click.File("w"),
    help="output PLIST file, stdout if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="output binary PLIST")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def csv2plist(input_file, output_file, dialect, header, key, binary, sort_keys):
    """
    -i CSV -o PLIST [-d DIALECT] [-k KEY] [-m] (minify) [-b] (binary PLIST)
    """
    obj = reader.csv_reader(
        input_stream=input_file,
        dialect_name=dialect,
        has_header=header,
        key_column_index=key,
        sort_data=sort_keys,
    )
    writer.plist_writer(obj, output_stream=output_file, binary_format=binary)


# json22xml


@cli.command(
    "j2x",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i JSON -o XML [-m] (minify) [-R roottag] [-t wraptag]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("r"),
    help="input JSON file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("wb"), # Changed from str to click.File("wb")
    help="output XML file, stdout if '-' or omitted",
)
@click.option(
    "-R", "--root", "root", default="root", type=str, help="root XML element if missing"
)
@click.option("-t", "--tag", "tag", type=str, help="wrap in tag")
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified XML")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def json2xml(input_file, output_file, mini, tag, root, sort_keys):
    """
    -i JSON -o XML [-m] (minify) [-R roottag] [-t wraptag]
    """
    obj = reader.json_reader(input_stream=input_file, sort_data=sort_keys)
    writer.xml_writer(
        obj,
        output_stream=output_file,
        mini=mini,
        item_tag_name=tag,
        root_tag_name=root,
    )


# plist22xml


@cli.command(
    "p2x",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i PLIST -o XML [-m] (minify) [-R roottag] [-t wraptag]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("rb"),
    help="input PLIST file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("wb"), # Changed from "w" to "wb"
    help="output XML file, stdout if '-' or omitted",
)
@click.option(
    "-R", "--root", "root", default="root", type=str, help="root XML element if missing"
)
@click.option("-t", "--tag", "tag", type=str, help="wrap in tag")
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified XML")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def plist2xml(input_file, output_file, mini, tag, root, sort_keys):
    """
    -i PLIST -o XML [-m] (minify) [-R roottag] [-t wraptag]
    """
    obj = reader.plist_reader(input_stream=input_file, sort_data=sort_keys)
    writer.xml_writer(
        obj,
        output_stream=output_file,
        mini=mini,
        item_tag_name=tag,
        root_tag_name=root,
    )


# yaml22xml


@cli.command(
    "y2x",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i YAML -o XML [-m] (minify) [-R roottag] [-t wraptag]",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("rb"),
    help="input PLIST file, stdin if '-' or omitted",
)
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("wb"), # Changed from "w" to "wb"
    help="output XML file, stdout if '-' or omitted",
)
@click.option(
    "-R", "--root", "root", default="root", type=str, help="root XML element if missing"
)
@click.option("-t", "--tag", "tag", type=str, help="wrap in tag")
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified XML")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def yaml2xml(input_file, output_file, mini, tag, root, sort_keys):
    """
    -i YAML -o XML [-m] (minify) [-R roottag] [-t wraptag]
    """
    obj = reader.yaml_reader(input_stream=input_file, sort_data=sort_keys)
    writer.xml_writer(
        obj,
        output_stream=output_file,
        mini=mini,
        item_tag_name=tag,
        root_tag_name=root,
    )


# csv22xml


@cli.command(
    "c2x",
    context_settings=CONTEXT_SETTINGS,
    short_help=(
        "-i CSV -o XML [-d DIALECT] [-k KEY] [-m] (minify) [-R roottag] [-t wraptag]"
    ),
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
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
    "output_file",
    default="-",
    type=click.File("w"),
    help="output XML file, stdout if '-' or omitted",
)
@click.option(
    "-R", "--root", "root", default="root", type=str, help="root XML element if missing"
)
@click.option("-t", "--tag", "tag", type=str, help="wrap in tag")
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified XML")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def csv2xml(input_file, output_file, dialect, header, key, mini, tag, root, sort_keys):
    """
    -i CSV -o XML [-d DIALECT] [-k KEY] [-m] (minify) [-R roottag] [-t wraptag]
    """
    obj = reader.csv_reader(
        input_stream=input_file,
        dialect_name=dialect,
        has_header=header,
        key_column_index=key,
        sort_data=sort_keys,
    )
    writer.xml_writer(
        obj,
        output_stream=output_file,
        mini=mini,
        item_tag_name=tag,
        root_tag_name=root,
    )


# xml22plist


@cli.command(
    "x2p",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i XML -o PLIST [-b] (make binary PLIST)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("r"),
    help="input JSON file, stdin if '-' or omitted",
)
@click.option(
    "-N", "--namespaces", "namespaces", is_flag=True, help="read XML namespaces"
)
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("wb"), # Changed from str to click.File("wb")
    help="output PLIST file, stdout if '-' or omitted",
)
@click.option("-b", "--bin", "binary", is_flag=True, help="output binary PLIST")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def xml2plist(input_file, output_file, namespaces, binary, sort_keys):
    """
    -i XML -o PLIST [-b] (make binary PLIST)
    """
    obj = reader.xml_reader(
        input_stream=input_file, process_namespaces=namespaces, sort_data=sort_keys
    )
    writer.plist_writer(obj, output_stream=output_file, binary_format=binary)


# xml22yaml


@cli.command(
    "x2y",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i XML -o YAML [-m] (minify YAML)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("r"),
    help="input JSON file, stdin if '-' or omitted",
)
@click.option(
    "-N", "--namespaces", "namespaces", is_flag=True, help="read XML namespaces"
)
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("w"),
    help="output YAML file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified YAML")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def xml2yaml(input_file, output_file, namespaces, mini, sort_keys):
    """
    -i XML -o YAML [-m] (minify YAML)
    """
    obj = reader.xml_reader(
        input_stream=input_file, process_namespaces=namespaces, sort_data=sort_keys
    )
    writer.yaml_writer(obj, output_stream=output_file, mini=mini)


# xml22json


@cli.command(
    "x2j",
    context_settings=CONTEXT_SETTINGS,
    short_help="-i XML -o JSON [-m] (minify) [-b] (keep binary)",
)
@click.version_option(version=VERSION)
@click.option(
    "-i",
    "--in",
    "input_file",
    default="-",
    type=click.File("rb"),
    help="input PLIST file, stdin if '-' or omitted",
)
@click.option(
    "-N", "--namespaces", "namespaces", is_flag=True, help="read XML namespaces"
)
@click.option(
    "-o",
    "--out",
    "output_file",
    default="-",
    type=click.File("wb"), # Changed from "w" to "wb"
    help="output JSON file, stdout if '-' or omitted",
)
@click.option("-m", "--mini", "mini", is_flag=True, help="output minified JSON")
@click.option("-s", "--sort", "sort_keys", is_flag=True, help="sort data")
def xml2json(input_file, output_file, namespaces, mini, sort_keys):
    """
    -i XML -o JSON [-m] (minify)
    """
    obj = reader.xml_reader(
        input_stream=input_file, process_namespaces=namespaces, sort_data=sort_keys
    )
    writer.json_writer(obj, output_stream=output_file, mini=mini)


if __name__ == "__main__":
    cli()
