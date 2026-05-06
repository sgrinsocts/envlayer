"""Tests for envlayer.parser module."""

import pytest
from envlayer.parser import parse_env


def test_simple_key_value():
    assert parse_env("FOO=bar") == {"FOO": "bar"}


def test_multiple_entries():
    text = "FOO=bar\nBAZ=qux"
    assert parse_env(text) == {"FOO": "bar", "BAZ": "qux"}


def test_ignores_comments():
    text = "# this is a comment\nFOO=bar"
    assert parse_env(text) == {"FOO": "bar"}


def test_ignores_empty_lines():
    text = "\n\nFOO=bar\n\n"
    assert parse_env(text) == {"FOO": "bar"}


def test_export_prefix():
    assert parse_env("export FOO=bar") == {"FOO": "bar"}


def test_single_quoted_value():
    assert parse_env("FOO='hello world'") == {"FOO": "hello world"}


def test_double_quoted_value():
    assert parse_env('FOO="hello world"') == {"FOO": "hello world"}


def test_double_quoted_escape_newline():
    assert parse_env('FOO="line1\\nline2"') == {"FOO": "line1\nline2"}


def test_double_quoted_escape_tab():
    assert parse_env('FOO="col1\\tcol2"') == {"FOO": "col1\tcol2"}


def test_double_quoted_escaped_quote():
    assert parse_env('FOO="say \\"hi\\""') == {"FOO": 'say "hi"'}


def test_inline_comment_stripped_from_unquoted():
    result = parse_env("FOO=bar  # this is ignored")
    assert result == {"FOO": "bar"}


def test_inline_comment_preserved_in_single_quotes():
    result = parse_env("FOO='bar # not a comment'")
    assert result == {"FOO": "bar # not a comment"}


def test_spaces_around_equals():
    assert parse_env("FOO = bar") == {"FOO": "bar"}


def test_empty_value():
    assert parse_env("FOO=") == {"FOO": ""}


def test_empty_quoted_value():
    assert parse_env('FOO=""') == {"FOO": ""}


def test_invalid_line_raises():
    with pytest.raises(ValueError, match="Invalid syntax on line 1"):
        parse_env("123INVALID=value")


def test_underscore_in_key():
    assert parse_env("MY_VAR=hello") == {"MY_VAR": "hello"}


def test_numeric_suffix_in_key():
    assert parse_env("VAR2=two") == {"VAR2": "two"}
