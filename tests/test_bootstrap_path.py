from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.grpy.dev_tools.bootstrap_path import BootstrapPath


@pytest.fixture
def mock_current():
    return Path("/mock/current")


@pytest.fixture
def mock_target():
    return Path("/mock/target")


def test_invalid_current_path(mock_current, mock_target):
    with patch.object(Path, "exists", spec=Path) as invalid_path:
        invalid_path.exists.return_value = False
        invalid_path.__str__.return_value = str(mock_current)

    with patch("pathlib.Path", spec=Path) as valid_path:
        valid_path.exists.return_value = True
        valid_path.__str__.return_value = str(mock_target)

    # Verify the mock behavior first
    assert not invalid_path.exists()
    assert valid_path.exists()

    with pytest.raises(ValidationError) as exc_info:
        bp = BootstrapPath(current=invalid_path, target=valid_path)
        assert bp.target == str(mock_target)

    assert f"This path does not exist: {mock_current}" in exc_info.value.errors()[0]["msg"]
    assert exc_info.value.errors()[0]["type"] == "value_error"


def test_invalid_target_path(mock_current, mock_target):
    with patch.object(Path, "exists", spec=Path) as valid_path:
        valid_path.exists.return_value = True
        valid_path.__str__.return_value = str(mock_current)

    with patch("pathlib.Path", spec=Path) as invalid_path:
        invalid_path.exists.return_value = False
        invalid_path.__str__.return_value = str(mock_target)

    # Verify the mock behavior first
    assert not invalid_path.exists()
    assert valid_path.exists()

    with pytest.raises(ValidationError) as exc_info:
        bp = BootstrapPath(current=valid_path, target=invalid_path)
        assert bp.current == str(mock_current)

    assert f"This path does not exist: {mock_target}" in exc_info.value.errors()[0]["msg"]
    assert exc_info.value.errors()[0]["type"] == "value_error"


def test_bootstrap_path_instance_creation(mock_current, mock_target):
    with patch.object(Path, "exists", return_value=True) as mock:
        mock.current = mock_current
        mock.target = mock_target
        bootstrap_path = BootstrapPath(current=mock_current, target=mock_target)

    assert isinstance(bootstrap_path, BootstrapPath)
    assert bootstrap_path.current == mock_current
    assert bootstrap_path.target == mock_target


def test_bootstrap_path_errors_bad_current(mock_current, mock_target):
    with patch.object(Path, "exists", return_value=False) as mock:
        mock.current = mock_current
        with pytest.raises(ValidationError) as exc_info:
            BootstrapPath(current=mock.current, target=mock_target)

        assert exc_info.value.errors()[0]["type"] == "value_error"
        assert f"This path does not exist: {mock_current}" in exc_info.value.errors()[0]["msg"]


def test_bootstrap_path_missing_current(mock_target):
    with pytest.raises(ValidationError) as exc_info:
        BootstrapPath(target=mock_target)

    assert exc_info.value.errors()[0]["type"] == "missing"
    assert "Field required" in exc_info.value.errors()[0]["msg"]


def test_bootstrap_path_missing_target():
    mock_current = Path("/mock/user/projects/mock_venv")

    with pytest.raises(ValidationError) as exc_info:
        BootstrapPath(target=mock_current)

    assert exc_info.value.errors()[0]["type"] == "missing"
    assert "Field required" in exc_info.value.errors()[0]["msg"]
