"""
File Strip.

Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
"""

import re
from re import Match, Pattern # UP035
from typing import Callable, ClassVar # List removed

LINE_PRESERVE: Pattern[str] = re.compile(r"\r?\n", re.MULTILINE)
CPP_PATTERN: Pattern[str] = re.compile(
    r"""(?x)
        (?P<comments>
            /\*[^*]*\*+(?:[^/*][^*]*\*+)*/  # multi-line comments
          | \s*//(?:[^\r\n])*               # single line comments
        )
      | (?P<code>
            "(?:\\.|[^"\\])*"               # double quotes
          | '(?:\\.|[^'\\])*'               # single quotes
          | .[^/"']*                        # everything else
        )
    """,
    re.DOTALL,
)
PY_PATTERN: Pattern[str] = re.compile(
    r"""(?x)
        (?P<comments>
            \s*\#(?:[^\r\n])*               # single line comments
        )
      | (?P<code>
            "{3}(?:\\.|[^\\])*"{3}          # triple double quotes
          | '{3}(?:\\.|[^\\])*'{3}          # triple single quotes
          | "(?:\\.|[^"\\])*"               # double quotes
          | '(?:\\.|[^'])*'                 # single quotes
          | .[^\#"']*                       # everything else
        )
    """,
    re.DOTALL,
)


def _strip_regex(pattern: Pattern[str], text: str, preserve_lines: bool) -> str:
    """Generic function that strips out comments pased on the given pattern."""

    def remove_comments(group: str, preserve_lines_eval: bool = False) -> str:
        """Remove comments."""
        return "".join(LINE_PRESERVE.findall(group)) if preserve_lines_eval else ""

    def evaluate(m: Match[str], preserve_lines_eval: bool) -> str:
        """Search for comments."""
        g = m.groupdict()
        return (
            g["code"]
            if g["code"] is not None
            else remove_comments(g["comments"], preserve_lines_eval)
        )

    return "".join(evaluate(m, preserve_lines) for m in pattern.finditer(text))


def _cpp_stripper(text: str, preserve_lines: bool = False) -> str:
    """C/C++ style comment stripper."""
    return _strip_regex(CPP_PATTERN, text, preserve_lines)


def _python_stripper(text: str, preserve_lines: bool = False) -> str:
    """Python style comment stripper."""
    return _strip_regex(PY_PATTERN, text, preserve_lines)


class Comments:
    """Comment strip class."""

    styles: ClassVar[list[str]] = [] # UP006
    _style_callers: ClassVar[dict[str, Callable[[str, bool], str]]] = {}

    def __init__(self, style: str, preserve_lines: bool = False):
        """Initialize."""
        self.preserve_lines = preserve_lines
        if style not in self.styles:
            raise ValueError(f"Unknown style: {style}")
        self.call: Callable[[str, bool], str] = self._style_callers[style]

    @classmethod
    def add_style(cls, style: str, fn: Callable[[str, bool], str]) -> None:
        """Add comment style."""
        if style not in cls._style_callers:
            cls._style_callers[style] = fn
            cls.styles.append(style)

    def strip(self, text: str) -> str:
        """Strip comments."""
        return self.call(text, self.preserve_lines)


Comments.add_style("c", _cpp_stripper)
Comments.add_style("json", _cpp_stripper)
Comments.add_style("cpp", _cpp_stripper)
Comments.add_style("python", _python_stripper)
