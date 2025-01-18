import pytest
from pathlib import Path
from unittest.mock import patch

from src.grpy.dev_tools.bootstrap_dev import BootstrapDev


def test_bootstrap_dev_init_home():
    with patch("src.grpy.dev_tools.bootstrap_dev.Path") as mock_path:
        mock_path.home.return_value = Path("/mock/home")
        bootstrap = BootstrapDev()
        assert bootstrap.home == "/mock/home"


def test_bootstrap_dev_update_home():
    with patch("src.grpy.dev_tools.bootstrap_dev.Path") as mock_path:
        mock_path.home.return_value = Path("/mock/home")
        bootstrap = BootstrapDev()
        assert bootstrap.home == "/mock/home"
        bootstrap.home = "/mock/test"
        assert bootstrap.home == "/mock/test"

def test_invalid_home_path():
    bootstrap = BootstrapDev()
    nonexistent_path = Path("/definitely/not/a/real/path")

    with pytest.raises(ValueError, match="Path does not exist"):
        bootstrap.home = nonexistent_path
        path = bootstrap.validate_path(nonexistent_path)
        assert path == None
