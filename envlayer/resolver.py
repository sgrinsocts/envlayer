"""Resolve final env values by expanding variable references.

Supports ``$VAR`` and ``${VAR}`` syntax within values, with an optional
fallback from the OS environment.
"""

import os
import re
from typing import Dict, Optional

_VAR_RE = re.compile(r"\$\{(?P<braced>[^}]+)\}|\$(?P<plain>[A-Za-z_][A-Za-z0-9_]*)")


def resolve_value(
    value: str,
    env: Dict[str, str],
    *,
    fallback_os: bool = True,
) -> str:
    """Expand variable references inside *value*.

    Args:
        value: Raw string that may contain ``$VAR`` / ``${VAR}`` tokens.
        env: Dictionary used as the primary lookup source.
        fallback_os: When True and a variable is not in *env*, fall back to
                     ``os.environ``.  Unresolved variables expand to ``""``.

    Returns:
        String with all variable references replaced.
    """
    def _replace(match: re.Match) -> str:
        name = match.group("braced") or match.group("plain")
        if name in env:
            return env[name]
        if fallback_os:
            return os.environ.get(name, "")
        return ""

    return _VAR_RE.sub(_replace, value)


def resolve_env(
    env: Dict[str, str],
    *,
    fallback_os: bool = True,
) -> Dict[str, str]:
    """Expand variable references in all values of *env*.

    Each value is resolved against the *already-seen* keys in insertion order,
    which mirrors the behaviour of most shell env-file loaders.

    Args:
        env: Input environment dictionary.
        fallback_os: Passed through to :func:`resolve_value`.

    Returns:
        New dictionary with all values expanded.
    """
    resolved: Dict[str, str] = {}
    for key, raw_value in env.items():
        resolved[key] = resolve_value(raw_value, resolved, fallback_os=fallback_os)
    return resolved
