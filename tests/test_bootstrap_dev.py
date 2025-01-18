from pathlib import Path
from unittest.mock import patch

import pytest

from src.grpy.dev_tools.bootstrap_dev import BootstrapDev


def test_home_default_value():
    with patch("src.grpy.dev_tools.bootstrap_dev.Path") as mock_path:
        mock_path.home.return_value = Path("/mock/home")
        bootstrap = BootstrapDev()
        assert bootstrap.home_dir == "/mock/home"


def test_home_update_value():
    with patch("src.grpy.dev_tools.bootstrap_dev.Path") as mock_path:
        mock_path.home.return_value = Path("/mock/home")
        bootstrap = BootstrapDev()
        assert bootstrap.home_dir == "/mock/home"
        bootstrap.home_dir = "/mock/test"
        assert bootstrap.home_dir == "/mock/test"


def test_invalid_home_path():
    bootstrap = BootstrapDev()
    nonexistent_path = Path("/definitely/not/a/real/path")

    with pytest.raises(ValueError, match="Path does not exist"):
        bootstrap.home_dir = nonexistent_path
        path = bootstrap.validate_path(nonexistent_path)
        assert path is None


def test_project_dir_default_value():
    with patch("src.grpy.dev_tools.bootstrap_dev.Path") as mock_path:
        mock_path.cwd.return_value = Path("my-project")
        bootstrap = BootstrapDev()
        assert bootstrap.project_dir == "my-project"


def test_project_dir_update_value():
    with patch("src.grpy.dev_tools.bootstrap_dev.Path") as mock_path:
        mock_path.cwd.return_value = Path("my-project")
        bootstrap = BootstrapDev()
        assert bootstrap.project_dir == "my-project"
        bootstrap.project_dir = "new-project"
        assert bootstrap.project_dir == "new-project"
