from typing import final

from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Literal,
    Name,
    Number,
    Operator,
    Other,
    Punctuation,
    String,
    Text,
    Whitespace,
)


@final
class ModusOperandiStyle(Style):
    """Modus Operandi (light) style for Pygments.

    Based on Protesilaos Stavrou's Modus themes for Emacs.
    """

    name = "modus-operandi"

    # Modus Operandi colors
    background_color = "#f3f3fd"  # light lavender
    default_style = "#000000"  # fg-main

    styles = {  # noqa: RUF012
        # Base tokens
        Text: "#000000",  # fg-main
        Whitespace: "#000000",  # fg-main
        Error: "#ffffff bg:#a60000",  # white on red
        Other: "#000000",  # fg-main
        # Comments
        Comment: "italic #595959",  # fg-dim
        Comment.Hashbang: "italic #595959",  # fg-dim
        Comment.Multiline: "italic #595959",  # fg-dim
        Comment.Preproc: "italic #193668",  # fg-alt
        Comment.PreprocFile: "italic #193668",  # fg-alt
        Comment.Single: "italic #595959",  # fg-dim
        Comment.Special: "italic bold #721045",  # magenta
        # Keywords
        Keyword: "bold #721045",  # magenta
        Keyword.Constant: "bold #721045",  # magenta
        Keyword.Declaration: "bold #0031a9",  # blue
        Keyword.Namespace: "bold #0031a9",  # blue
        Keyword.Pseudo: "bold #721045",  # magenta
        Keyword.Reserved: "bold #721045",  # magenta
        Keyword.Type: "bold #6f5500",  # yellow
        # Literals
        Literal: "#005e8b",  # cyan
        Literal.Date: "#005e8b",  # cyan
        # Strings
        String: "#006800",  # green
        String.Affix: "#006800",  # green
        String.Backtick: "#006800",  # green
        String.Char: "#006800",  # green
        String.Delimiter: "#006800",  # green
        String.Doc: "italic #006800",  # green
        String.Double: "#006800",  # green
        String.Escape: "bold #a60000",  # red
        String.Heredoc: "#006800",  # green
        String.Interpol: "#005e8b",  # cyan
        String.Other: "#006800",  # green
        String.Regex: "#721045",  # magenta
        String.Single: "#006800",  # green
        String.Symbol: "#005e8b",  # cyan
        # Numbers
        Number: "#005e8b",  # cyan
        Number.Bin: "#005e8b",  # cyan
        Number.Float: "#005e8b",  # cyan
        Number.Hex: "#005e8b",  # cyan
        Number.Integer: "#005e8b",  # cyan
        Number.Integer.Long: "#005e8b",  # cyan
        Number.Oct: "#005e8b",  # cyan
        # Operators
        Operator: "#000000",  # fg-main
        Operator.Word: "bold #721045",  # magenta
        # Punctuation
        Punctuation: "#000000",  # fg-main
        # Names
        Name: "#000000",  # fg-main
        Name.Attribute: "#0031a9",  # blue
        Name.Builtin: "#721045",  # magenta
        Name.Builtin.Pseudo: "#721045",  # magenta
        Name.Class: "bold #6f5500",  # yellow
        Name.Constant: "#005e8b",  # cyan
        Name.Decorator: "#a60000",  # red
        Name.Entity: "#0031a9",  # blue
        Name.Exception: "bold #a60000",  # red
        Name.Function: "bold #0031a9",  # blue
        Name.Function.Magic: "#721045",  # magenta
        Name.Label: "#6f5500",  # yellow
        Name.Namespace: "bold #6f5500",  # yellow
        Name.Other: "#000000",  # fg-main
        Name.Property: "#0031a9",  # blue
        Name.Tag: "bold #721045",  # magenta
        Name.Variable: "#000000",  # fg-main
        Name.Variable.Class: "#000000",  # fg-main
        Name.Variable.Global: "#000000",  # fg-main
        Name.Variable.Instance: "#000000",  # fg-main
        Name.Variable.Magic: "#721045",  # magenta
        # Generics (diffs, etc.)
        Generic: "#000000",  # fg-main
        Generic.Deleted: "#8f1313 bg:#ffd8d5",  # fg-removed bg-removed
        Generic.Emph: "italic #000000",  # fg-main
        Generic.Error: "#a60000",  # red
        Generic.Heading: "bold #000000",  # fg-main
        Generic.Inserted: "#005000 bg:#c1f2d1",  # fg-added bg-added
        Generic.Output: "#000000",  # fg-main
        Generic.Prompt: "bold #0031a9",  # blue
        Generic.Strong: "bold #000000",  # fg-main
        Generic.Subheading: "bold #721045",  # magenta
        Generic.Traceback: "#a60000",  # red
    }


@final
class ModusVivendiStyle(Style):
    """Modus Vivendi (dark) style for Pygments.

    Based on Protesilaos Stavrou's Modus themes for Emacs.
    """

    name = "modus-vivendi"

    # Modus Vivendi colors
    background_color = "#2e2e3f"  # dark lavender
    default_style = "#ffffff"  # fg-main

    styles = {  # noqa: RUF012
        # Base tokens
        Text: "#ffffff",  # fg-main
        Whitespace: "#ffffff",  # fg-main
        Error: "#000000 bg:#ff5f59",  # black on red
        Other: "#ffffff",  # fg-main
        # Comments
        Comment: "italic #989898",  # fg-dim
        Comment.Hashbang: "italic #989898",  # fg-dim
        Comment.Multiline: "italic #989898",  # fg-dim
        Comment.Preproc: "italic #c6daff",  # fg-alt
        Comment.PreprocFile: "italic #c6daff",  # fg-alt
        Comment.Single: "italic #989898",  # fg-dim
        Comment.Special: "italic bold #feacd0",  # magenta
        # Keywords
        Keyword: "bold #feacd0",  # magenta
        Keyword.Constant: "bold #feacd0",  # magenta
        Keyword.Declaration: "bold #2fafff",  # blue
        Keyword.Namespace: "bold #2fafff",  # blue
        Keyword.Pseudo: "bold #feacd0",  # magenta
        Keyword.Reserved: "bold #feacd0",  # magenta
        Keyword.Type: "bold #d0bc00",  # yellow
        # Literals
        Literal: "#00d3d0",  # cyan
        Literal.Date: "#00d3d0",  # cyan
        # Strings
        String: "#44bc44",  # green
        String.Affix: "#44bc44",  # green
        String.Backtick: "#44bc44",  # green
        String.Char: "#44bc44",  # green
        String.Delimiter: "#44bc44",  # green
        String.Doc: "italic #44bc44",  # green
        String.Double: "#44bc44",  # green
        String.Escape: "bold #ff5f59",  # red
        String.Heredoc: "#44bc44",  # green
        String.Interpol: "#00d3d0",  # cyan
        String.Other: "#44bc44",  # green
        String.Regex: "#feacd0",  # magenta
        String.Single: "#44bc44",  # green
        String.Symbol: "#00d3d0",  # cyan
        # Numbers
        Number: "#00d3d0",  # cyan
        Number.Bin: "#00d3d0",  # cyan
        Number.Float: "#00d3d0",  # cyan
        Number.Hex: "#00d3d0",  # cyan
        Number.Integer: "#00d3d0",  # cyan
        Number.Integer.Long: "#00d3d0",  # cyan
        Number.Oct: "#00d3d0",  # cyan
        # Operators
        Operator: "#ffffff",  # fg-main
        Operator.Word: "bold #feacd0",  # magenta
        # Punctuation
        Punctuation: "#ffffff",  # fg-main
        # Names
        Name: "#ffffff",  # fg-main
        Name.Attribute: "#2fafff",  # blue
        Name.Builtin: "#feacd0",  # magenta
        Name.Builtin.Pseudo: "#feacd0",  # magenta
        Name.Class: "bold #d0bc00",  # yellow
        Name.Constant: "#00d3d0",  # cyan
        Name.Decorator: "#ff5f59",  # red
        Name.Entity: "#2fafff",  # blue
        Name.Exception: "bold #ff5f59",  # red
        Name.Function: "bold #2fafff",  # blue
        Name.Function.Magic: "#feacd0",  # magenta
        Name.Label: "#d0bc00",  # yellow
        Name.Namespace: "bold #d0bc00",  # yellow
        Name.Other: "#ffffff",  # fg-main
        Name.Property: "#2fafff",  # blue
        Name.Tag: "bold #feacd0",  # magenta
        Name.Variable: "#ffffff",  # fg-main
        Name.Variable.Class: "#ffffff",  # fg-main
        Name.Variable.Global: "#ffffff",  # fg-main
        Name.Variable.Instance: "#ffffff",  # fg-main
        Name.Variable.Magic: "#feacd0",  # magenta
        # Generics (diffs, etc.)
        Generic: "#ffffff",  # fg-main
        Generic.Deleted: "#ffbfbf bg:#4f1119",  # fg-removed bg-removed
        Generic.Emph: "italic #ffffff",  # fg-main
        Generic.Error: "#ff5f59",  # red
        Generic.Heading: "bold #ffffff",  # fg-main
        Generic.Inserted: "#a0e0a0 bg:#00381f",  # fg-added bg-added
        Generic.Output: "#ffffff",  # fg-main
        Generic.Prompt: "bold #2fafff",  # blue
        Generic.Strong: "bold #ffffff",  # fg-main
        Generic.Subheading: "bold #feacd0",  # magenta
        Generic.Traceback: "#ff5f59",  # red
    }
