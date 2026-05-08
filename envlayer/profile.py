"""Profile-based env layer merging.

Supports loading a base .env file and overriding values with a
profile-specific .env.<profile> file.
"""

from pathlib import Path
from typing import Dict, Optional

from envlayer.parser import parse_env_file


def load_profile(
    base_path: str,
    profile: Optional[str] = None,
    *,
    override: bool = True,
) -> Dict[str, str]:
    """Load env vars from a base file, optionally merged with a profile overlay.

    Args:
        base_path: Path to the base .env file.
        profile: Optional profile name.  When given, the file
                 ``<base_path>.<profile>`` is loaded and merged on top.
        override: If True (default), profile values overwrite base values.
                  If False, base values take precedence (profile fills gaps).

    Returns:
        Merged dictionary of environment variables.
    """
    base = parse_env_file(base_path)

    if profile is None:
        return base

    profile_path = f"{base_path}.{profile}"
    if not Path(profile_path).exists():
        return base

    overlay = parse_env_file(profile_path)
    return merge_envs(base, overlay, override=override)


def merge_envs(
    base: Dict[str, str],
    overlay: Dict[str, str],
    *,
    override: bool = True,
) -> Dict[str, str]:
    """Merge two env dictionaries.

    Args:
        base: Base environment dictionary.
        overlay: Overlay environment dictionary.
        override: When True overlay values win; when False base values win.

    Returns:
        New merged dictionary.
    """
    if override:
        return {**base, **overlay}
    # base values take precedence — overlay only fills missing keys
    return {**overlay, **base}


def list_profiles(base_path: str) -> list:
    """Return profile names available for *base_path*.

    Scans the parent directory for files named ``<basename>.<profile>``.

    Args:
        base_path: Path to the base .env file.

    Returns:
        Sorted list of profile name strings.
    """
    p = Path(base_path)
    prefix = p.name + "."
    profiles = [
        child.name[len(prefix):]
        for child in p.parent.iterdir()
        if child.name.startswith(prefix) and child.is_file()
    ]
    return sorted(profiles)
