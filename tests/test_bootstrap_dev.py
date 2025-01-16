import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.grpy.dev_tools.bootstrap_dev import BootstrapDev

@patch('pathlib.Path')
def test_bootstrap_dev_init(mock_path):
    mock_path.home.return_value = Path('/mock/home')
    home = str(mock_path.home())

    bootstrap = BootstrapDev(
        home=home,  # Convert Path object to string
        venv_path="projects/.venvs",
        project="grpy-dev-tools"
    )

    assert isinstance(bootstrap, BootstrapDev)
    assert bootstrap.home == '/mock/home'
    assert bootstrap.venv_path == "projects/.venvs"
    assert bootstrap.project == "grpy-dev-tools"

    mock_path.home.assert_called_once()
