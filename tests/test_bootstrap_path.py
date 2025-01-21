from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.grpy.dev_tools.bootstrap_path import BootstrapPath


@pytest.fixture
def mock_working_path():
    return Path("/mock/user/working")


@pytest.fixture
def mock_target_path():
    return Path("/mock/user/target")


def test_bootstrap_path_instance_creation(mock_working_path, mock_target_path):
    with patch.object(Path, "exists", return_value=True) as mock:
        mock.working_path = mock_working_path
        mock.target_path = mock_target_path
        bootstrap_path = BootstrapPath(working_path=mock_working_path, target_path=mock_target_path)

    assert isinstance(bootstrap_path, BootstrapPath)
    assert bootstrap_path.working_path == mock_working_path
    assert bootstrap_path.target_path == mock_target_path


def test_bootstrap_path_errors_bad_working_path(mock_working_path, mock_target_path):
    with patch.object(Path, "exists", return_value=False) as mock:
        mock.working_path = mock_working_path
        with pytest.raises(ValidationError) as exc_info:
            BootstrapPath(working_path=mock.working_path, target_path=mock_target_path)

        assert exc_info.value.errors()[0]["type"] == "value_error"
        assert f"This path does not exist: {mock_working_path}" in exc_info.value.errors()[0]["msg"]


def test_bootstrap_path_missing_working_path(mock_target_path):
    with pytest.raises(ValidationError) as exc_info:
        BootstrapPath(target_path=mock_target_path)

    assert exc_info.value.errors()[0]["type"] == "missing"
    assert "Field required" in exc_info.value.errors()[0]["msg"]


def test_bootstrap_path_missing_target_path():
    mock_working_path = Path("/mock/user/projects/mock_venv")

    with pytest.raises(ValidationError) as exc_info:
        BootstrapPath(target_path=mock_working_path)

    assert exc_info.value.errors()[0]["type"] == "missing"
    assert "Field required" in exc_info.value.errors()[0]["msg"]
