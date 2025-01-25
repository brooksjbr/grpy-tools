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
    return f"Path does not exist: {invalid_path}"


def test_bootstrap_path_init(mock_cwd, generate_path):
    bp = BootstrapPath()

    assert isinstance(bp, BootstrapPath)
    assert bp.target == generate_path


def test_bootstrap_path_update_target_after_init(mock_cwd, tmp_path_factory):
    path2 = tmp_path_factory.mktemp("path2")

    bootstrap_path = BootstrapPath()
    bootstrap_path.target = path2

    assert bootstrap_path.target == path2


def test_bootstrap_path_path_unreadable(invalid_path):
    with pytest.raises(ValidationError) as exc_info:
        BootstrapPath(target=invalid_path)
    assert f"Path is not readable: {invalid_path}" in str(exc_info.value)


def test_bootstrap_path_empty_path():
    with pytest.raises(ValidationError):
        BootstrapPath(target="")


def test_bootstrap_path_invalid_type():
    with pytest.raises(ValidationError):
        BootstrapPath(target=123)


def test_bootstrap_path_multiple_updates(mock_cwd, tmp_path_factory):
    path1 = tmp_path_factory.mktemp("path1")
    path2 = tmp_path_factory.mktemp("path2")
    path3 = tmp_path_factory.mktemp("path3")

    bp = BootstrapPath(target=path1)
    assert bp.target == path1

    bp.target = path2
    assert bp.target == path2

    bp.target = path3
    assert bp.target == path3


def test_bootstrap_path_relative_path(mock_cwd):
    relative_path = Path("./test_dir")
    relative_path.mkdir(exist_ok=True)

    with pytest.raises(ValidationError):
        BootstrapPath(target=relative_path)

    relative_path.rmdir()
