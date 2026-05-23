"""Tests for depwatch.dependency_reader module."""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from depwatch.dependency_reader import (
    parse_requirements_line,
    read_requirements,
    diff_dependencies,
)


# --- parse_requirements_line ---

def test_parse_requirements_line_pinned():
    result = parse_requirements_line("requests==2.28.0")
    assert result == ("requests", "==", "2.28.0")


def test_parse_requirements_line_gte():
    result = parse_requirements_line("flask>=2.0")
    assert result == ("flask", ">=", "2.0")


def test_parse_requirements_line_normalizes_name():
    result = parse_requirements_line("my-package==1.0.0")
    assert result is not None
    assert result[0] == "my_package"


def test_parse_requirements_line_comment_returns_none():
    assert parse_requirements_line("# this is a comment") is None


def test_parse_requirements_line_blank_returns_none():
    assert parse_requirements_line("") is None
    assert parse_requirements_line("   ") is None


def test_parse_requirements_line_no_version_returns_none():
    assert parse_requirements_line("requests") is None


# --- read_requirements ---

def test_read_requirements_parses_file(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("requests==2.28.0\nflask>=2.0\n# comment\n\nnumpy==1.24.0\n")

    deps = read_requirements(str(req_file))
    assert deps["requests"] == "2.28.0"
    assert deps["flask"] == "2.0"
    assert deps["numpy"] == "1.24.0"
    assert len(deps) == 3


def test_read_requirements_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_requirements("/nonexistent/requirements.txt")


# --- diff_dependencies ---

def test_diff_dependencies_detects_update():
    old = {"requests": "2.27.0"}
    new = {"requests": "2.28.0"}
    changes = diff_dependencies(old, new)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "updated"
    assert changes[0]["old_version"] == "2.27.0"
    assert changes[0]["new_version"] == "2.28.0"


def test_diff_dependencies_detects_added():
    old = {}
    new = {"flask": "2.0.0"}
    changes = diff_dependencies(old, new)
    assert changes[0]["change_type"] == "added"
    assert changes[0]["old_version"] == ""


def test_diff_dependencies_detects_removed():
    old = {"boto3": "1.26.0"}
    new = {}
    changes = diff_dependencies(old, new)
    assert changes[0]["change_type"] == "removed"
    assert changes[0]["new_version"] == ""


def test_diff_dependencies_no_changes():
    deps = {"requests": "2.28.0", "flask": "2.0.0"}
    assert diff_dependencies(deps, deps) == []
