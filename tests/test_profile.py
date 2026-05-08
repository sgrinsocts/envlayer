"""Tests for envlayer.profile module."""

import pytest

from envlayer.profile import load_profile, merge_envs, list_profiles


# ---------------------------------------------------------------------------
# merge_envs
# ---------------------------------------------------------------------------

def test_merge_envs_override_true():
    base = {"A": "1", "B": "2"}
    overlay = {"B": "99", "C": "3"}
    result = merge_envs(base, overlay, override=True)
    assert result == {"A": "1", "B": "99", "C": "3"}


def test_merge_envs_override_false():
    base = {"A": "1", "B": "2"}
    overlay = {"B": "99", "C": "3"}
    result = merge_envs(base, overlay, override=False)
    # base wins for B, overlay fills C
    assert result == {"A": "1", "B": "2", "C": "3"}


def test_merge_envs_empty_base():
    result = merge_envs({}, {"X": "10"})
    assert result == {"X": "10"}


def test_merge_envs_empty_overlay():
    result = merge_envs({"X": "10"}, {})
    assert result == {"X": "10"}


def test_merge_envs_both_empty():
    assert merge_envs({}, {}) == {}


def test_merge_envs_does_not_mutate_inputs():
    base = {"A": "1"}
    overlay = {"A": "2"}
    merge_envs(base, overlay)
    assert base["A"] == "1"


# ---------------------------------------------------------------------------
# load_profile (file-based)
# ---------------------------------------------------------------------------

def test_load_profile_no_profile(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\nFOO=bar\n")
    result = load_profile(str(env_file))
    assert result == {"KEY": "value", "FOO": "bar"}


def test_load_profile_with_existing_profile(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=base\nFOO=bar\n")
    profile_file = tmp_path / ".env.staging"
    profile_file.write_text("KEY=staging\nEXTRA=yes\n")

    result = load_profile(str(env_file), profile="staging")
    assert result["KEY"] == "staging"
    assert result["FOO"] == "bar"
    assert result["EXTRA"] == "yes"


def test_load_profile_missing_profile_file_falls_back(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=base\n")
    # No .env.prod file exists
    result = load_profile(str(env_file), profile="prod")
    assert result == {"KEY": "base"}


def test_load_profile_override_false(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=base\n")
    profile_file = tmp_path / ".env.dev"
    profile_file.write_text("KEY=dev\nNEW=1\n")

    result = load_profile(str(env_file), profile="dev", override=False)
    assert result["KEY"] == "base"   # base wins
    assert result["NEW"] == "1"      # gap filled by profile


# ---------------------------------------------------------------------------
# list_profiles
# ---------------------------------------------------------------------------

def test_list_profiles(tmp_path):
    (tmp_path / ".env").write_text("A=1")
    (tmp_path / ".env.dev").write_text("A=2")
    (tmp_path / ".env.staging").write_text("A=3")
    (tmp_path / ".env.prod").write_text("A=4")

    profiles = list_profiles(str(tmp_path / ".env"))
    assert profiles == ["dev", "prod", "staging"]


def test_list_profiles_none_found(tmp_path):
    (tmp_path / ".env").write_text("A=1")
    assert list_profiles(str(tmp_path / ".env")) == []
