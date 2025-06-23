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
    """Generic internal function that strips out comments based on the given regex pattern."""

    def remove_comments(group_text, preserve_lines_flag=False): # Renamed preserve_lines for clarity
        """Remove comment text, optionally preserving line breaks within it."""
        if preserve_lines_flag:
            return "".join([x[0] for x in LINE_PRESERVE.findall(group_text)])
        return ""

    def evaluate(match_obj, preserve_lines_flag): # Renamed m, preserve_lines
        """Evaluate a regex match: return code or processed comment group."""
        g = match_obj.groupdict()
        if g["code"] is not None:
            return g["code"]
        else:
            return remove_comments(g["comments"], preserve_lines_flag)

    return "".join(map(lambda m: evaluate(m, preserve_lines), pattern.finditer(text)))


# These are intended as static methods for the Comments class or direct use if refactored.
# For now, they are module-level functions used by Comments.add_style.
def _cpp(text, preserve_lines=False):
    """Strips C/C++ style comments (/* ... */ and // ...)."""
    return _strip_regex(CPP_PATTERN, text, preserve_lines)


def _python(text, preserve_lines=False):
    """Strips Python style comments (# ...)."""
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


class Comments(object):
    """
    Manages and applies different comment stripping styles.

    Styles (e.g., 'c', 'python') are registered using `add_style` along with
    their corresponding stripping functions. The `strip` method then applies
    the configured style to a given text.
    """

    styles = [] # Class variable to store registered style names

    def __init__(self, style=None, preserve_lines=False):
        """Initialize with a specific comment style and line preservation flag.

        Args:
            style: The name of the comment style to use (must be registered).
            preserve_lines: If True, line breaks within comments are preserved,
                            otherwise comments are replaced with an empty string.
        """
        self.preserve_lines = preserve_lines
        self.call = self._get_style(style) # Changed to call _get_style

    @classmethod
    def add_style(cls, style, fn):
        """Class method to register a new comment stripping style.

        Args:
            style: The name of the style (e.g., "c", "python").
            fn: The function that implements stripping for this style.
                The function should accept (text, preserve_lines) arguments.
        """
        if not hasattr(cls, style): # Check if style method already exists
            setattr(cls, style, fn) # Make it a method of the class for direct call
            if style not in cls.styles: # Keep track of style names
                 cls.styles.append(style)

    def _get_style(self, style): # Changed to _get_style for internal use
        """Internal method to retrieve the function for a given style name."""
        if hasattr(self, style) and style in self.styles:
            return getattr(self, style) # Return the method itself
        else:
            raise CommentException(f"Comment style '{style}' not recognized or registered.")

    def strip(self, text):
        """Applies the configured comment stripping style to the given text.

        Args:
            text: The input string from which to strip comments.

        Returns:
            The text with comments stripped according to the configured style.
        """
        if not self.call: # Should not happen if constructor worked
            raise CommentException("No comment stripping style configured.")
        # The self.call is now the stripping function (e.g., _cpp or _python)
        # which needs to be called with text and preserve_lines.
        return self.call(text, self.preserve_lines)


Comments.add_style("c", _cpp)
Comments.add_style("json", _cpp)
Comments.add_style("cpp", _cpp)
Comments.add_style("python", _python)
