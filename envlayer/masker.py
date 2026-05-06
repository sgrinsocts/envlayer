"""Secret masking utilities for envlayer."""

import re
from typing import Collection

# Default patterns that indicate a value should be treated as a secret
DEFAULT_SECRET_PATTERNS = (
    re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|private[_-]?key|auth)"),
)

MASK_PLACEHOLDER = "***"


def is_secret_key(key: str, patterns: Collection[re.Pattern] = DEFAULT_SECRET_PATTERNS) -> bool:
    """Return True if the key name matches any known secret pattern."""
    return any(pattern.search(key) for pattern in patterns)


def mask_value(value: str, visible_chars: int = 0) -> str:
    """Return a masked representation of *value*.

    Args:
        value: The original secret value.
        visible_chars: How many trailing characters to leave visible (0 = fully masked).

    Returns:
        Masked string, e.g. "***" or "***abc" when visible_chars=3.
    """
    if not value:
        return MASK_PLACEHOLDER
    if visible_chars > 0 and len(value) > visible_chars:
        return MASK_PLACEHOLDER + value[-visible_chars:]
    return MASK_PLACEHOLDER


def mask_env(
    env: dict[str, str],
    patterns: Collection[re.Pattern] = DEFAULT_SECRET_PATTERNS,
    visible_chars: int = 0,
) -> dict[str, str]:
    """Return a copy of *env* with secret values replaced by masked placeholders.

    Non-secret keys are left untouched.

    Args:
        env: Mapping of environment variable names to their values.
        patterns: Regex patterns used to identify secret keys.
        visible_chars: Trailing characters to keep visible in masked values.

    Returns:
        New dict with secrets masked.
    """
    return {
        key: mask_value(value, visible_chars) if is_secret_key(key, patterns) else value
        for key, value in env.items()
    }
