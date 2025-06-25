# yaplon

Convert between JSON, YAML, PLIST (binary and XML), XML, and CSV (read-only for CSV input) on the command line.
Can be used in piping. Requires Python 3.9+.

- Copyright (c) 2021-2024 Adam Twardoch <adam+github@twardoch.com> & Jules (AI Agent)
- Copyright (c) 2012-2015 Isaac Muse <isaacmuse@gmail.com>
- [MIT license](./LICENSE)
- Based on [Serialized Data Converter for Sublime Text](https://github.com/facelessuser/SerializedDataConverter)

## Installation

- Install the [release version](https://pypi.org/project/yaplon/):

```
pip3 install --user --upgrade yaplon
```

- Install the [development version](https://github.com/twardoch/yaplon):

```
pip3 install --user --upgrade git+https://github.com/twardoch/yaplon
```

Or for development:
```bash
git clone https://github.com/twardoch/yaplon.git
cd yaplon
# Recommended: create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate # On macOS/Linux
# venv\Scripts\activate # On Windows
pip install -e .[dev]
```

## Usage

```
yaplon [c|j|p|x|y]2[j|p|x|y] -i input -o output [options]
```

Yaplon supports JSON input with C-style comments (`// ...` and `/* ... */`) and trailing commas in objects/arrays (similar to JSON5).

### Commands:

```
c2j  -i CSV -o JSON [-H] [-d DIALECT] [-k KEY] [-s] [-m]
c2p  -i CSV -o PLIST [-H] [-d DIALECT] [-k KEY] [-s] [-b]
c2x  -i CSV -o XML [-H] [-d DIALECT] [-k KEY] [-s] [-m] [-R ROOT] [-t TAG]
c2y  -i CSV -o YAML [-H] [-d DIALECT] [-k KEY] [-s] [-m]
j2p  -i JSON -o PLIST [-s] [-b]
j2x  -i JSON -o XML [-s] [-m] [-R ROOT] [-t TAG]
j2y  -i JSON -o YAML [-s] [-m]
p2j  -i PLIST -o JSON [-s] [-m] [-b] (binary in JSON)
p2x  -i PLIST -o XML [-s] [-m] [-R ROOT] [-t TAG]
p2y  -i PLIST -o YAML [-s] [-m]
x2j  -i XML -o JSON [-N] [-s] [-m]
x2p  -i XML -o PLIST [-N] [-s] [-b]
x2y  -i XML -o YAML [-N] [-s] [-m]
y2j  -i YAML -o JSON [-s] [-m] [-b] (binary in JSON)
y2p  -i YAML -o PLIST [-s] [-b]
y2x  -i YAML -o XML [-s] [-m] [-R ROOT] [-t TAG]
```
**General Options:**
- `-i <input_file>`: Input file (defaults to stdin if omitted or '-')
- `-o <output_file>`: Output file (defaults to stdout if omitted or '-')
- `-s, --sort`: Sort data before conversion (e.g., dictionary keys).
- `-m, --mini`: Minify output (specific to format, e.g., no indents in JSON/XML, flow style in YAML).

**Format-Specific Options:**
- `-b, --bin`:
    - For `*2p` (to Plist): Output binary Plist.
    - For `*2j` (to JSON from Plist/YAML/XML): Preserve binary data (e.g., from Plist `<data>` or YAML `!!binary`) as a base64 encoded string in JSON, instead of the default special dictionary representation `{"__bytes__": true, "base64": "..."}`.
- `-R <name>, --root <name>`: (for `*2x` - to XML) Specify root tag name if input data is a list or if overriding the default 'root' or single-key root. Used by `xmltodict` backend.
- `-t <name>, --tag <name>`: (for `*2x` - to XML) Wrap output in the specified tag. Uses `dict2xml` backend, which may produce simpler XML structure. If `-t` is used, `-R` is ignored.
- `-N, --namespaces`: (for `x2*` - from XML) Read XML namespaces.
- `-H, --header`: (for `c2*` - from CSV) Treat first row as header. Reads CSV as a list of dictionaries.
- `-d <dialect>, --dialect <dialect>`: (for `c2*` - from CSV) Specify CSV dialect (e.g., 'excel', 'excel-tab', 'unix').
- `-k <key_index>, --key <key_index>`: (for `c2*` - from CSV with header) Use column number (integer index) as the key for a top-level dictionary; values will be row dictionaries.

Also installs direct CLI tools that correspond to the commands:

- `csv22json`, `csv22plist`, `csv22xml`, `csv22yaml`,
- `json22plist`, `json22xml`, `json22yaml`,
- `plist22json`, `plist22xml`, `plist22yaml`,
- `xml22json`, `xml22plist`, `xml22yaml`,
- `yaml22json`, `yaml22plist`, `yaml22xml`

Note that they have `22` rather than `2` in the filenames, so they don’t conflict with other similar (often single-purpose) tools that you may have.

## Examples

### JSON to YAML

File to file via the dedicated CLI tool:

```
$ json22yaml -i input.json -o output.yaml
```

Using pipe redirects, via the yaplon tool with j2y command:

```
$ yaplon j2y < input.json > output.yaml
```

Read file, output minified to stdout, via the Python 3 module

```
$ python3 -m yaplon j2y -m -i input.json
```

### PLIST to JSON

Read PLIST file, output minified JSON file, via the dedicated CLI tool.

```
$ plist22json -m -i input.plist > output.json
```

Read plist file, output minified JSON to stdout, via the yaplon tool with p2j command.

```
$ yaplon p2j -m -i input.plist
```

## Changelog

- 1.5.7: switched to Unicode output in JSON, refactoring
- 1.5.3: added CSV reading and limited XML read/write
- 1.2.7: removed obsolete plistlib.Data reference
- 1.2.3: bugfix
- 1.2.1: added support for orderedattrdict.AttrDict
- 1.1.0: added -s for sorting data
- 1.0.8: initial public release

## Links

- Project homepage: [https://twardoch.github.io/yaplon/](https://twardoch.github.io/yaplon/)
- Python package on PyPi: [https://pypi.org/project/yaplon/](https://pypi.org/project/yaplon/)
- Source on Github: [https://github.com/twardoch/yaplon](https://github.com/twardoch/yaplon)
- Donate via [https://www.paypal.me/adamtwar](https://www.paypal.me/adamtwar)

## Development

To contribute to `yaplon` or set it up for development:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/twardoch/yaplon.git
    cd yaplon
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # Or: venv\Scripts\activate  # On Windows
    ```

3.  **Install in editable mode with development dependencies:**
    ```bash
    pip install -e .[dev]
    ```
    This installs the package in a way that your changes to the source code are immediately reflected. Development dependencies include tools for testing, linting, and packaging.

4.  **Running Tests:**
    Use the Makefile target:
    ```bash
    make test
    ```
    Or run pytest directly:
    ```bash
    python3 -m pytest
    ```
    To run with coverage:
    ```bash
    make test-cov
    # Or: pytest --cov=yaplon tests/
    ```

5.  **Linting and Formatting:**
    - To check code style with Flake8 and Black:
      ```bash
      make lint
      ```
    - To automatically format code with Black:
      ```bash
      make format
      ```

6.  **Building the Package:**
    To build the source distribution and wheel:
    ```bash
    make build
    ```

This project includes a comprehensive test suite and uses `flake8` for linting and `black` for code formatting to maintain code quality and consistency.
