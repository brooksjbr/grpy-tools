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
def error_msg(invalid_path):
    return f"This path does not exist: {invalid_path}"


def test_bootstrap_path_instance_creation(generate_path):
    bootstrap_path = BootstrapPath(current=generate_path, target=generate_path)

    assert isinstance(bootstrap_path, BootstrapPath)
    assert bootstrap_path.current == generate_path
    assert bootstrap_path.target == generate_path


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


def test_bootstrap_path_missing_current(generate_path):
    with pytest.raises(ValidationError) as exc_info:
        BootstrapPath(target=generate_path)

    assert exc_info.value.errors()[0]["type"] == "missing"
    assert "Field required" in exc_info.value.errors()[0]["msg"]


def test_bootstrap_path_missing_target(generate_path):
    with pytest.raises(ValidationError) as exc_info:
        BootstrapPath(current=generate_path)

    assert exc_info.value.errors()[0]["type"] == "missing"
    assert "Field required" in exc_info.value.errors()[0]["msg"]
