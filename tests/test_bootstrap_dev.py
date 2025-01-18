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
