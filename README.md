# Yaplon: Yet Another Plist/JSON/YAML/XML/CSV Converter

Yaplon is a versatile command-line tool for converting between various common structured data formats: JSON, YAML, Property Lists (PLIST, both binary and XML), XML, and CSV (read-only for CSV input). It's designed for developers, data analysts, system administrators, or anyone who needs to quickly and easily transform data from one format to another.

## Why Yaplon?

In a world of diverse applications and services, data often needs to be exchanged and processed in different formats. Yaplon simplifies this by providing:

*   **Unified Interface:** A single tool to handle multiple conversion types, reducing the need to learn and install separate utilities for each pair of formats.
*   **Command-Line Power:** Easily integrate Yaplon into your scripts and workflows using standard input/output piping.
*   **Flexibility:** Options to sort data (e.g., dictionary keys) before conversion for consistent output, and to minify the output for space efficiency.
*   **Format-Specific Features:** Handles nuances like JSON with comments, binary data in Plists and YAML, different XML structuring approaches, and various CSV dialects.
*   **Python 3.9+:** Modern Python codebase.

## Installation

### From PyPI (Recommended)

Install the latest stable release from the Python Package Index (PyPI):

```bash
pip3 install --user --upgrade yaplon
```

### Binary Downloads

Download pre-built binaries for your platform from the [releases page](https://github.com/twardoch/yaplon/releases):

- **Linux**: `yaplon-{version}-linux-x64`
- **Windows**: `yaplon-{version}-windows-x64.exe`
- **macOS**: `yaplon-{version}-macos-x64`

Make the binary executable and add it to your PATH.

### From GitHub (Development Version)

To install the latest development version directly from GitHub:

```bash
pip3 install --user --upgrade git+https://github.com/twardoch/yaplon
```

### For Development

If you want to contribute to Yaplon or modify it:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/twardoch/yaplon.git
    cd yaplon
    ```
2.  **Install development dependencies:**
    ```bash
    make install-dev
    ```
    This installs the package in editable mode with all development dependencies.

For detailed build and development instructions, see [BUILD.md](./BUILD.md).
For GitHub Actions setup, see [GITHUB_SETUP.md](./GITHUB_SETUP.md).

## Usage

Yaplon can be invoked using the main `yaplon` command followed by a conversion subcommand (e.g., `j2y` for JSON to YAML), or by using dedicated shortcut scripts (e.g., `json22yaml`).

### Main Command Structure

```bash
yaplon <command> -i <input_file> -o <output_file> [options]
```

*   `<command>`: Specifies the conversion type (see "Conversion Commands" below).
*   `-i <input_file>`: Input file. If omitted or specified as `-`, Yaplon reads from standard input (stdin).
*   `-o <output_file>`: Output file. If omitted or specified as `-`, Yaplon writes to standard output (stdout). This allows for easy piping.

### Conversion Commands

The following commands define the input and output formats:

*   `c2j`: CSV to JSON
*   `c2p`: CSV to PLIST
*   `c2x`: CSV to XML
*   `c2y`: CSV to YAML
*   `j2p`: JSON to PLIST
*   `j2x`: JSON to XML
*   `j2y`: JSON to YAML
*   `p2j`: PLIST to JSON
*   `p2x`: PLIST to XML
*   `p2y`: PLIST to YAML
*   `x2j`: XML to JSON
*   `x2p`: XML to PLIST
*   `x2y`: XML to YAML
*   `y2j`: YAML to JSON
*   `y2p`: YAML to PLIST
*   `y2x`: YAML to XML

Yaplon supports JSON input with C-style comments (`// ...` and `/* ... */`) and trailing commas in objects/arrays (similar to JSON5).

### General Options

These options are available for most conversion commands:

*   `-i <input_file>, --in <input_file>`: Specify the input file. Defaults to stdin.
*   `-o <output_file>, --out <output_file>`: Specify the output file. Defaults to stdout.
*   `-s, --sort`: Sort data before conversion. For dictionaries/maps, keys are sorted alphabetically. This helps in producing consistent output, especially for version control.
*   `-m, --mini`: Minify output. The specific effect depends on the format (e.g., no indents or newlines in JSON/XML, flow style in YAML).

### Format-Specific Options

*   **For `*2p` (to Plist):**
    *   `-b, --bin`: Output a binary Plist file. By default, an XML Plist is generated.
*   **For `p2j`, `y2j` (from Plist/YAML to JSON):**
    *   `-b, --bin`: Preserve binary data (e.g., from Plist `<data>` or YAML `!!binary`) as a simple base64 encoded string in JSON. The default behavior is to represent binary data as a special dictionary: `{"__bytes__": true, "base64": "..."}`.
*   **For `*2x` (to XML):**
    *   `-R <name>, --root <name>`: Specify the root tag name for the XML document. This is particularly useful if the input data is a list or if you want to override the default root tag (which is often 'root' or derived from a single top-level key). This option uses the `xmltodict` backend for XML generation.
    *   `-t <name>, --tag <name>`: Wrap the entire output in the specified tag. This option uses the `dict2xml` backend, which may produce a simpler XML structure, especially for lists. If `-t` is used, the `-R` option is ignored.
*   **For `x2*` (from XML):**
    *   `-N, --namespaces`: Process XML namespaces. If enabled, tag names in the resulting data structure will include namespace prefixes.
*   **For `c2*` (from CSV):**
    *   `-H, --header`: Treat the first row of the CSV as a header row. The CSV data will be read as a list of dictionaries (where keys are header names) instead of a list of lists.
    *   `-d <dialect>, --dialect <dialect>`: Specify the CSV dialect (e.g., 'excel', 'excel-tab', 'unix'). If not specified, Yaplon attempts to sniff the dialect.
    *   `-k <key_index>, --key <key_index>`: (Requires `-H` or implies it) Use the values from the column specified by `key_index` (a 1-based integer) as keys for a top-level dictionary. The values of this dictionary will be the row dictionaries (with the key column itself removed from the row dictionary).

### Dedicated CLI Tools

For convenience, Yaplon also installs shortcut scripts that correspond directly to the conversion commands:

*   `csv22json`, `csv22plist`, `csv22xml`, `csv22yaml`
*   `json22plist`, `json22xml`, `json22yaml`
*   `plist22json`, `plist22xml`, `plist22yaml`
*   `xml22json`, `xml22plist`, `xml22yaml`
*   `yaml22json`, `yaml22plist`, `yaml22xml`

Note: These scripts use `22` (e.g., `json22yaml`) instead of `2` to avoid potential conflicts with other similarly named conversion tools you might have installed.

### Examples

**JSON to YAML (file to file using dedicated tool):**

```bash
json22yaml -i input.json -o output.yaml
```

**JSON to YAML (using pipes and main `yaplon` command):**

```bash
cat input.json | yaplon j2y > output.yaml
```

**PLIST to JSON (minified, preserving binary as base64 strings):**

```bash
yaplon p2j -m -b -i input.plist -o output.json
```

**CSV with header to XML (using a specific column as key and custom root tag):**

```bash
yaplon c2x -H -k 1 --root "Entries" -i data.csv > data.xml
```

## Technical Details

This section describes the internal workings of Yaplon.

### Core Architecture

Yaplon's conversion process generally follows these steps:

1.  **Input:** Data is read from an input file or stdin.
2.  **Parsing (`reader.py`):** The input data is parsed into a standardized Python data structure, primarily using `collections.OrderedDict`. This preserves key order from the source format where applicable.
    *   The `reader.sort_ordereddict` function can be invoked via the `-s`/`--sort` CLI option to recursively sort these `OrderedDict`s by key.
3.  **Serialization (`writer.py`):** The Python `OrderedDict` object is then serialized into the target output format.
4.  **Output:** The resulting data is written to an output file or stdout.

The Command Line Interface (CLI) is built using the [Click](https://click.palletsprojects.com/) library.

### Format-Specific Handling

*   **JSON:**
    *   **Reading:** Handled by `yaplon.ojson.read_json`. This module supports JSON5-like features such as C-style comments (`//`, `/* */`) and trailing commas. These are stripped by `yaplon.file_strip.json.sanitize_json` before parsing with Python's standard `json` module (using `object_pairs_hook=OrderedDict`).
    *   **Writing:** Handled by `yaplon.ojson.json_dump`. Can produce regular or minified JSON. Binary data is handled based on the `-b` flag (see "Binary Data Representation" below).
*   **PLIST (Property List):**
    *   **Reading:** Handled by `yaplon.oplist.read_plist`, which wraps Python's standard `plistlib`. It parses both XML and binary Plists. Plist `<data>` elements are converted to Python `bytes` objects, and `<date>` elements become `datetime.datetime` objects.
    *   **Writing:** Handled by `yaplon.oplist.plist_dumps` (for XML Plist) and `yaplon.oplist.plist_binary_dumps` (for binary Plist, via `-b` flag). These also use `plistlib`.
*   **YAML:**
    *   **Reading:** Handled by `yaplon.oyaml.read_yaml`, which uses the [PyYAML](https://pyyaml.org/) library. It employs custom constructors to load YAML `!!binary` tags into Python `bytes` objects and `!!timestamp` tags into `datetime.datetime` objects. Data is loaded into `OrderedDict` to preserve order.
    *   **Writing:** Handled by `yaplon.oyaml.yaml_dumps`. Uses a custom dumper for `OrderedDict` to maintain key order and for `bytes` to serialize them as `!!binary` tags. Supports minified (flow style) output with the `-m` flag.
*   **XML:**
    *   **Reading:** Handled by `yaplon.reader.xml`, which uses the [xmltodict](https://github.com/martinblech/xmltodict) library to parse XML into an `OrderedDict`. Namespace processing can be enabled with the `-N` flag.
    *   **Writing:** Handled by `yaplon.writer.xml`. This function is noted as potentially "primitive and buggy" for complex cases. It can use two different backends:
        *   **`xmltodict.unparse`:** Used by default or when the `-R`/`--root` option is specified. This backend is generally more feature-rich for representing complex data structures.
        *   **`dict2xml.Converter`:** Used when the `-t`/`--tag` option is specified. This backend might produce simpler XML, especially for lists, and wraps the entire structure in a single user-defined tag.
        *   Before writing, Python `bytes` are converted to base64 encoded strings, and `datetime.datetime` objects are converted to ISO 8601 strings.
*   **CSV:**
    *   **Reading:** Handled by `yaplon.reader.csv` using Python's standard `csv` module.
        *   Can read as a list of lists or, if `-H`/`--header` is used, a list of `OrderedDict`s.
        *   Supports dialect sniffing or explicit dialect specification (`-d`).
        *   The `-k`/`--key` option allows restructuring the data into a top-level `OrderedDict` keyed by values from a specified column.
    *   **Writing:** CSV writing is not currently supported. Yaplon is read-only for CSV input.

### Data Representation

*   **Internal Structure:** `collections.OrderedDict` is used as the primary internal data structure after parsing to ensure that key order from formats like YAML or sorted JSON is preserved and can be maintained in the output.
*   **Binary Data:**
    *   **In Python:** Represented as `bytes` objects.
    *   **PLIST:** Native `<data>` tags.
    *   **YAML:** `!!binary` tag.
    *   **JSON Output:**
        *   Default: `{"__bytes__": true, "base64": "..."}` (a dictionary indicating binary content).
        *   With `-b` flag (for `p2j`, `y2j`): A simple base64 encoded string.
    *   **XML Output:** Base64 encoded string content within tags.

### Extensibility (Conceptual)

While not a formalized plugin system, adding support for a new format would conceptually involve:

1.  Creating new reader and writer functions in `yaplon/reader.py` and `yaplon/writer.py` respectively.
2.  The reader should parse the new format into an `OrderedDict` (or list of `OrderedDict`s, etc.).
3.  The writer should take an `OrderedDict` and serialize it to the new format.
4.  Adding corresponding CLI commands and options in `yaplon/__main__.py`.
5.  Writing comprehensive tests for the new conversions.

## Contributing

Contributions to Yaplon are welcome! Whether it's bug reports, feature suggestions, documentation improvements, or code contributions, your help is appreciated.

### Development Setup

Please refer to the "Installation > For Development" section above for instructions on how to clone the repository and set up a development environment.

### Workflow

1.  **Fork the repository** on GitHub.
2.  **Create a new branch** for your feature or bug fix: `git checkout -b my-feature-branch`.
3.  **Set up development environment:**
    ```bash
    make install-dev
    ```
4.  **Make your changes.**
5.  **Write tests** for your changes in the `tests/` directory.
6.  **Run development workflow:**
    ```bash
    make dev  # format + lint + test-fast
    ```
7.  **Run full test suite:**
    ```bash
    make test
    ```
8.  **Commit your changes** with a clear and descriptive commit message.
9.  **Push your branch** to your fork: `git push origin my-feature-branch`.
10. **Open a Pull Request** against the `master` branch of the `twardoch/yaplon` repository.

### Build System

The project uses a modern build system with automated testing and releases:

- **Local Development**: `make dev` for quick development workflow
- **Testing**: `make test` for full test suite, `make test-fast` for quick tests
- **Building**: `make build` for packages, `make build-binary` for binaries
- **Releasing**: `python scripts/release.py --bump patch --message "msg"`

For detailed information, see [BUILD.md](./BUILD.md) and [USAGE.md](./USAGE.md).

### Issue Tracking

*   Please report bugs or suggest features by opening an issue on the [GitHub Issues page](https://github.com/twardoch/yaplon/issues).
*   Check the `TODO.md` file in the repository for a list of known tasks and planned enhancements.

### Changelog

For significant changes, please add an entry to the `CHANGELOG.md` file, describing the change and referencing the relevant issue or PR if applicable.

### Code Style

Yaplon uses [Black](https://github.com/psf/black) for code formatting and [Flake8](https://flake8.pycqa.org/en/latest/) for linting. Please ensure your contributions adhere to these standards by running `make format` and `make lint`.

### Testing

The project uses [pytest](https://docs.pytest.org/) for testing. New features should include corresponding tests, and bug fixes should ideally include a test that demonstrates the bug and verifies the fix.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for a history of changes to the project.

## License

Yaplon is distributed under the [MIT License](./LICENSE).

- Copyright (c) 2021-2024 Adam Twardoch <adam+github@twardoch.com> & Jules (AI Agent)
- Copyright (c) 2012-2015 Isaac Muse <isaacmuse@gmail.com>
- Based on [Serialized Data Converter for Sublime Text](https://github.com/facelessuser/SerializedDataConverter)

## Links

*   **Project Homepage:** [https://twardoch.github.io/yaplon/](https://twardoch.github.io/yaplon/)
*   **Python Package on PyPI:** [https://pypi.org/project/yaplon/](https://pypi.org/project/yaplon/)
*   **Source on GitHub:** [https://github.com/twardoch/yaplon](https://github.com/twardoch/yaplon)
*   **Donate:** Support the project via [PayPal](https://www.paypal.me/adamtwar) or [GitHub Sponsors](https://github.com/sponsors/twardoch). (Check `.github/FUNDING.yml`)
