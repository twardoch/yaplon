# yaplon

Convert between JSON, YAML and PLIST (binary and XML) in the commandline.
Can be used in piping. Written in Python 3 (may be compatible with 2.7).

- Copyright (c) 2019 Adam Twardoch <adam+github@twardoch.com>
- Copyright (c) 2012-2015 Isaac Muse <isaacmuse@gmail.com>
- [MIT license](./LICENSE)
- Based on https://github.com/facelessuser/SerializedDataConverter

## Installation

```
pip3 install --user --upgrade git+https://github.com/twardoch/yaplon
```

## Usage

```
yaplon j2p|j2y|p2j|p2y|y2j|y2p -i input -o output [options]

Commands:
  j2p  -i JSON -o PLIST [-b] (make binary PLIST)
  j2y  -i JSON -o YAML [-m] (minify YAML)
  p2j  -i PLIST -o JSON [-b] (keep binary in JSON)
  p2y  -i PLIST -o YAML [-m] (minify YAML)
  y2j  -i YAML -o JSON [-b] (keep binary in JSON)
  y2p  -i YAML -o PLIST [-b] (make binary PLIST)
```

Also installs direct CLI tools: `json22plist`, `json22yaml`, `plist22json`, `plist22yaml`, `yaml22json`, `yaml22plist`.
