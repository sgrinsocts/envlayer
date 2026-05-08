"""Tests for envlayer.resolver module."""

import os
import pytest

from envlayer.resolver import resolve_value, resolve_env


# ---------------------------------------------------------------------------
# resolve_value
# ---------------------------------------------------------------------------

def test_resolve_value_no_references():
    assert resolve_value("hello", {}) == "hello"


def test_resolve_value_dollar_var():
    assert resolve_value("$HOME_DIR/app", {"HOME_DIR": "/usr/local"}) == "/usr/local/app"


def test_resolve_value_braced_var():
    assert resolve_value("${HOST}:${PORT}", {"HOST": "localhost", "PORT": "5432"}) == "localhost:5432"


def test_resolve_value_missing_falls_back_to_os(monkeypatch):
    monkeypatch.setenv("MY_SECRET_VAR", "from_os")
    result = resolve_value("${MY_SECRET_VAR}", {}, fallback_os=True)
    assert result == "from_os"


def test_resolve_value_missing_no_fallback():
    result = resolve_value("${UNDEFINED}", {}, fallback_os=False)
    assert result == ""


def test_resolve_value_mixed_defined_and_missing():
    env = {"DEFINED": "yes"}
    result = resolve_value("${DEFINED}-${MISSING}", env, fallback_os=False)
    assert result == "yes-"


def test_resolve_value_env_takes_priority_over_os(monkeypatch):
    monkeypatch.setenv("PRIORITY", "os_value")
    result = resolve_value("$PRIORITY", {"PRIORITY": "env_value"}, fallback_os=True)
    assert result == "env_value"


# ---------------------------------------------------------------------------
# resolve_env
# ---------------------------------------------------------------------------

def test_resolve_env_simple():
    env = {"BASE": "/app", "LOG_DIR": "${BASE}/logs"}
    result = resolve_env(env)
    assert result["LOG_DIR"] == "/app/logs"


def test_resolve_env_chain():
    env = {"A": "1", "B": "${A}2", "C": "${B}3"}
    result = resolve_env(env)
    assert result == {"A": "1", "B": "12", "C": "123"}


def test_resolve_env_no_mutation():
    env = {"URL": "http://$HOST", "HOST": "example.com"}
    original = dict(env)
    resolve_env(env)
    assert env == original


def test_resolve_env_empty():
    assert resolve_env({}) == {}


def test_resolve_env_no_references():
    env = {"KEY": "plain", "OTHER": "value"}
    assert resolve_env(env) == env


def test_resolve_env_forward_reference_not_resolved():
    # B is defined after C; C cannot see B yet
    env = {"C": "${B}_suffix", "B": "base"}
    result = resolve_env(env, fallback_os=False)
    # C is processed first — B not yet in resolved dict
    assert result["C"] == "_suffix"
    assert result["B"] == "base"
