"""Tests for envlayer.masker."""

import re

import pytest

from envlayer.masker import (
    MASK_PLACEHOLDER,
    is_secret_key,
    mask_env,
    mask_value,
)


# ---------------------------------------------------------------------------
# is_secret_key
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", [
    "PASSWORD",
    "DB_PASSWORD",
    "secret",
    "API_TOKEN",
    "AUTH_KEY",
    "PRIVATE_KEY",
    "api_key",
    "MY_SECRET_VALUE",
])
def test_is_secret_key_matches(key):
    assert is_secret_key(key) is True


@pytest.mark.parametrize("key", [
    "USERNAME",
    "HOST",
    "PORT",
    "DATABASE_URL",
    "DEBUG",
])
def test_is_secret_key_no_match(key):
    assert is_secret_key(key) is False


def test_is_secret_key_custom_pattern():
    custom = [re.compile(r"(?i)internal")]
    assert is_secret_key("INTERNAL_FLAG", patterns=custom) is True
    assert is_secret_key("PASSWORD", patterns=custom) is False


# ---------------------------------------------------------------------------
# mask_value
# ---------------------------------------------------------------------------

def test_mask_value_fully_masked():
    assert mask_value("supersecret") == MASK_PLACEHOLDER


def test_mask_value_empty_string():
    assert mask_value("") == MASK_PLACEHOLDER


def test_mask_value_visible_chars():
    result = mask_value("supersecret", visible_chars=3)
    assert result == f"{MASK_PLACEHOLDER}ret"


def test_mask_value_visible_chars_exceeds_length():
    # When visible_chars >= len(value), fully mask
    result = mask_value("abc", visible_chars=5)
    assert result == MASK_PLACEHOLDER


# ---------------------------------------------------------------------------
# mask_env
# ---------------------------------------------------------------------------

def test_mask_env_masks_secrets():
    env = {"DB_PASSWORD": "s3cr3t", "HOST": "localhost"}
    masked = mask_env(env)
    assert masked["DB_PASSWORD"] == MASK_PLACEHOLDER
    assert masked["HOST"] == "localhost"


def test_mask_env_does_not_mutate_original():
    env = {"API_TOKEN": "tok_abc123", "PORT": "5432"}
    masked = mask_env(env)
    assert env["API_TOKEN"] == "tok_abc123"  # original unchanged
    assert masked["API_TOKEN"] == MASK_PLACEHOLDER


def test_mask_env_with_visible_chars():
    env = {"SECRET_KEY": "abcdef"}
    masked = mask_env(env, visible_chars=2)
    assert masked["SECRET_KEY"] == f"{MASK_PLACEHOLDER}ef"


def test_mask_env_empty_dict():
    assert mask_env({}) == {}
