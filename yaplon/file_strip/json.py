"""
File Strip.

Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
"""

import re
from re import Match, Pattern # UP035

from .comments import Comments

JSON_PATTERN: Pattern[str] = re.compile(
    r"""(?x)
        (
            (?P<square_comma>
                ,                        # trailing comma
                (?P<square_ws>[\s\r\n]*) # white space
                (?P<square_bracket>\])   # bracket
            )
          | (?P<curly_comma>
                ,                        # trailing comma
                (?P<curly_ws>[\s\r\n]*)  # white space
                (?P<curly_bracket>\})    # bracket
            )
        )
      | (?P<code>
            "(?:\\.|[^"\\])*"            # double quoted string
          | '(?:\\.|[^'\\])*'            # single quoted string
          | .[^,"']*                     # everything else
        )
    """,
    re.DOTALL,
)


def strip_dangling_commas(text: str, preserve_lines: bool = False) -> str:
    """Strip dangling commas."""
    regex = JSON_PATTERN

    def remove_comma(g: dict[str, str | None], preserve_lines_eval: bool) -> str:
        """Remove comma."""
        if preserve_lines_eval:
            if g["square_comma"] is not None:
                return (g["square_ws"] or "") + (g["square_bracket"] or "")
            return (g["curly_ws"] or "") + (g["curly_bracket"] or "")
        return (
            g["square_bracket"] or "" if g["square_comma"] else g["curly_bracket"] or ""
        )

    def evaluate(m: Match[str], preserve_lines_eval: bool) -> str:
        """Search for dangling comma."""
        g = m.groupdict()
        return (
            remove_comma(g, preserve_lines_eval)
            if g["code"] is None
            else g["code"] or ""
        )

    return "".join(evaluate(m, preserve_lines) for m in regex.finditer(text))


def strip_json_comments(text: str, preserve_lines: bool = False) -> str:
    """Strip JavaScript like comments using the 'json' style from Comments class."""
    # Assuming 'json' style in Comments uses a C-like comment stripper
    return Comments(style="json", preserve_lines=preserve_lines).strip(text)


def sanitize_json(text: str, preserve_lines: bool = False) -> str:
    """Sanitize the JSON file by removing comments and dangling commas."""
    text_no_comments = strip_json_comments(text, preserve_lines)
    return strip_dangling_commas(text_no_comments, preserve_lines)
