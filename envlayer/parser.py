"""Parser for .env files with support for comments, quoted values, and multiline strings."""

import re
from typing import Dict, Optional


ENV_LINE_RE = re.compile(
    r'^\s*(?:export\s+)?'
    r'(?P<key>[A-Za-z_][A-Za-z0-9_]*)'
    r'\s*=\s*'
    r'(?P<value>.*)$'
)


def _strip_inline_comment(value: str) -> str:
    """Remove inline comments from an unquoted value."""
    match = re.search(r'(?<!\\)\s+#.*$', value)
    if match:
        return value[:match.start()]
    return value


def _unquote(value: str) -> str:
    """Strip surrounding quotes and unescape escape sequences."""
    if len(value) >= 2:
        if (value[0] == '"' and value[-1] == '"'):
            inner = value[1:-1]
            inner = inner.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
            return inner
        if (value[0] == "'" and value[-1] == "'"):
            return value[1:-1]
    return _strip_inline_comment(value).strip()


def parse_env(text: str) -> Dict[str, str]:
    """
    Parse the contents of an .env file into a dictionary.

    Rules:
    - Lines starting with '#' (after optional whitespace) are ignored.
    - Empty lines are ignored.
    - Values may be single-quoted, double-quoted, or unquoted.
    - Double-quoted values support \\n, \\t, \\" escape sequences.
    - Unquoted values may have trailing inline comments (# preceded by whitespace).

    Args:
        text: Raw string content of an .env file.

    Returns:
        Ordered dict of key-value pairs.
    """
    result: Dict[str, str] = {}

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()

        if not line or line.startswith('#'):
            continue

        match = ENV_LINE_RE.match(line)
        if not match:
            raise ValueError(
                f"Invalid syntax on line {lineno}: {raw_line!r}"
            )

        key = match.group('key')
        raw_value = match.group('value').strip()
        result[key] = _unquote(raw_value)

    return result


def parse_env_file(path: str) -> Dict[str, str]:
    """
    Read and parse an .env file from disk.

    Args:
        path: Filesystem path to the .env file.

    Returns:
        Parsed key-value pairs.
    """
    with open(path, 'r', encoding='utf-8') as fh:
        return parse_env(fh.read())
