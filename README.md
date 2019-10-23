# yaplon

Convert between JSON, YAML and PLIST (binary and XML) in the commandline.
Can be used in piping. Written in Python 3.7 (not 2.7 compatible).

- Copyright (c) 2019 Adam Twardoch <adam+github@twardoch.com>
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

## Usage

```
yaplon j2p|j2y|p2j|p2y|y2j|y2p -i input -o output [options]
```

### Commands:

```
j2p  -i JSON  -o PLIST [-b] (make binary PLIST)
j2y  -i JSON  -o YAML  [-m] (minify)
p2j  -i PLIST -o JSON  [-m] (minify) [-b] (keep binary)
p2y  -i PLIST -o YAML  [-m] (minify)
y2j  -i YAML  -o JSON  [-m] (minify) [-b] (keep binary)
y2p  -i YAML  -o PLIST [-b] (make binary PLIST)
```

Also installs direct CLI tools: `json22plist`, `json22yaml`, `plist22json`, `plist22yaml`, `yaml22json`, `yaml22plist` that correspond to the commands. Note that they have `22` rather than `2` in the filenames, so they don’t conflict with other similar (often single-purpose) tools that you may have.

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

- 1.1.0: added -s for sorting data
- 1.0.8: initial public release

## Links

- Project homepage: [https://twardoch.github.io/yaplon/](https://twardoch.github.io/yaplon/)
- Python package on PyPi: [https://pypi.org/project/yaplon/](https://pypi.org/project/yaplon/)
- Source on Github: [https://github.com/twardoch/yaplon](https://github.com/twardoch/yaplon)
- Donate via [https://www.paypal.me/adamtwar](https://www.paypal.me/adamtwar)
