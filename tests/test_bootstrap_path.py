from pathlib import Path

import pytest
from pydantic import ValidationError

from src.grpy.dev_tools.bootstrap_path import BootstrapPath


@pytest.fixture
def invalid_path():
    return Path("/invalid/filesystem/path")


@pytest.fixture(scope="session")
def generate_path(tmp_path_factory):
    dir = tmp_path_factory.mktemp("data")
    return dir


@pytest.fixture
def mock_cwd(monkeypatch, generate_path):
    monkeypatch.chdir(generate_path)
    return generate_path


@pytest.fixture
def error_msg(invalid_path):
    return f"This path does not exist: {invalid_path}"


def test_bootstrap_path_init(mock_cwd, generate_path):
    bp = BootstrapPath()

    assert isinstance(bp, BootstrapPath)
    assert bp.current == generate_path
    assert bp.target == generate_path
    assert bp.subdirectory is None


def test_bootstrap_path_init_update_path_with_valid_paths(tmp_path_factory):
    path1 = tmp_path_factory.mktemp("path1")
    path2 = tmp_path_factory.mktemp("path2")

    bootstrap_path = BootstrapPath()

    bootstrap_path.current = path1
    bootstrap_path.target = path2

    assert bootstrap_path.current == path1
    assert bootstrap_path.target == path2
    assert bootstrap_path.current != bootstrap_path.target


def test_bootstrap_path_init_update_path_with_invalid_paths(mock_cwd, generate_path, invalid_path):
    bootstrap_path = BootstrapPath()

    with pytest.raises(ValidationError) as exc_info:
        bootstrap_path.current = invalid_path
        bootstrap_path.target = invalid_path

    err = invalid_path
    assert exc_info.value.errors()[0]["type"] == "value_error"
    assert str(err) in exc_info.value.errors()[0]["msg"]


def test_bootstrap_path_init_update_path_with_invalid_current(
    mock_cwd, generate_path, invalid_path
):
    bootstrap_path = BootstrapPath()

    with pytest.raises(ValidationError) as exc_info:
        bootstrap_path.current = invalid_path

    err = invalid_path
    assert exc_info.value.errors()[0]["type"] == "value_error"
    assert str(err) in exc_info.value.errors()[0]["msg"]


def test_bootstrap_path_init_update_path_with_invalid_target(mock_cwd, generate_path, invalid_path):
    bootstrap_path = BootstrapPath()

    with pytest.raises(ValidationError) as exc_info:
        bootstrap_path.target = invalid_path

    err = invalid_path
    assert exc_info.value.errors()[0]["type"] == "value_error"
    assert str(err) in exc_info.value.errors()[0]["msg"]


def test_bootstrap_path_invalid_target(generate_path, invalid_path, error_msg):
    with pytest.raises(ValidationError) as exc_info:
        BootstrapPath(current=generate_path, target=invalid_path)

    assert exc_info.value.errors()[0]["type"] == "value_error"
    assert error_msg in exc_info.value.errors()[0]["msg"]


def test_bootstrap_path_invalid_current(generate_path, invalid_path, error_msg):
    with pytest.raises(ValidationError) as exc_info:
        BootstrapPath(current=invalid_path, target=generate_path)

    assert exc_info.value.errors()[0]["type"] == "value_error"
    assert error_msg in exc_info.value.errors()[0]["msg"]


def test_bootstrap_path_with_subdirectory_field(mock_cwd, generate_path):
    bootstrap_path = BootstrapPath(subdirectory="new_project")

    assert isinstance(bootstrap_path, BootstrapPath)
    assert bootstrap_path.current == generate_path
    assert bootstrap_path.target == generate_path
    assert bootstrap_path.subdirectory == "new_project"
    assert isinstance(bootstrap_path.subdirectory, str)
