"""
Provides a class and methods for stripping comments from text based on
language-specific patterns (currently C-style/JSON and Python-style).
Used as a utility for cleaning data before parsing.

Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
"""

import re

LINE_PRESERVE = re.compile(r"\r?\n", re.MULTILINE)
CPP_PATTERN = re.compile(
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
PY_PATTERN = re.compile(
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


def _strip_regex(pattern, text, preserve_lines):
    """Generic function that strips out comments pased on the given pattern."""

    def remove_comments(group, preserve_lines=False):
        """Remove comments."""

        return (
            "".join([x[0] for x in LINE_PRESERVE.findall(group)])
            if preserve_lines
            else ""
        )

    def evaluate(m, preserve_lines):
        """Search for comments."""

        g = m.groupdict()
        return (
            g["code"]
            if g["code"] is not None
            else remove_comments(g["comments"], preserve_lines)
        )

    return "".join(map(lambda m: evaluate(m, preserve_lines), pattern.finditer(text)))


@staticmethod
def _cpp(text, preserve_lines=False):
    """C/C++ style comment stripper."""

    return _strip_regex(CPP_PATTERN, text, preserve_lines)

    return "".join(map(lambda m: evaluate(m, preserve_lines), pattern.finditer(text)))


    return _strip_regex(PY_PATTERN, text, preserve_lines)


class CommentException(Exception):
    """Custom exception for comment stripping errors."""

    def __init__(self, value):
        """Initialize with the error value."""
        super().__init__(value)
        self.value = value

    def __str__(self):
        """Return the string representation of the error value."""
        return repr(self.value)


class Comments:
    """Comment strip class."""

    _styles_registry = {} # Renamed to avoid conflict if a style is named 'styles'

    def __init__(self, style=None, preserve_lines=False):
        """Initialize with a specific comment style and line preservation flag.

        Args:
            style: The name of the comment style to use (must be registered).
            preserve_lines: If True, line breaks within comments are preserved,
                            otherwise comments are replaced with an empty string.
        """
        self.preserve_lines = preserve_lines
        self.selected_style_fn = self._get_style_fn(style)

    @staticmethod
    def _cpp(text, preserve_lines=False):
        """Strips C/C++ style comments (/* ... */ and // ...)."""
        return _strip_regex(CPP_PATTERN, text, preserve_lines)

    @staticmethod
    def _python(text, preserve_lines=False):
        """Strips Python style comments (# ...)."""
        return _strip_regex(PY_PATTERN, text, preserve_lines)

    @classmethod
    def add_style(cls, style_name, style_function):
        """Class method to register a new comment stripping style.

        Args:
            style_name: The name of the style (e.g., "c", "python").
            style_function: The function that implements stripping for this style.
                            It should be a static method or a function that accepts
                            (text, preserve_lines) arguments.
        """
        if not callable(style_function):
            raise TypeError("Style function must be callable.")
        cls._styles_registry[style_name] = style_function

    def _get_style_fn(self, style_name):
        """Internal method to retrieve the function for a given style name."""
        style_fn = self._styles_registry.get(style_name)
        if style_fn is None:
            raise CommentException(f"Comment style '{style_name}' not recognized or registered.")
        return style_fn

    def strip(self, text):
        """Applies the configured comment stripping style to the given text.

        Args:
            text: The input string from which to strip comments.

        Returns:
            The text with comments stripped according to the configured style.
        """
        if not self.selected_style_fn: # Should not happen if constructor worked
            raise CommentException("No comment stripping style configured.")
        return self.selected_style_fn(text, self.preserve_lines)



Comments.add_style("c", _cpp)
Comments.add_style("json", _cpp)
Comments.add_style("cpp", _cpp)
Comments.add_style("python", _python)
