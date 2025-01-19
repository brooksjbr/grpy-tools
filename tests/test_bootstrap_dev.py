from pathlib import Path
from unittest.mock import patch

from src.grpy.dev_tools.bootstrap_dev import BootstrapDev


def test_project_name_default_value():
    with patch("src.grpy.dev_tools.bootstrap_dev.Path") as mock_path:
        mock_path.cwd.return_value = Path("my-project")
        bootstrap = BootstrapDev()
        assert bootstrap.project_name == "my-project"


def test_project_name_update_value():
    with patch("src.grpy.dev_tools.bootstrap_dev.Path") as mock_path:
        mock_path.cwd.return_value = Path("my-project")
        bootstrap = BootstrapDev()
        assert bootstrap.project_name == "my-project"
        bootstrap.project_name = "new-project"
        assert bootstrap.project_name == "new-project"


def test_project_path_default_value():
    with patch("src.grpy.dev_tools.bootstrap_dev.Path") as mock_path:
        mock_cwd = Path("/mock/workspace/project")
        mock_path.cwd.return_value = mock_cwd
        mock_path.return_value.resolve.return_value = mock_cwd
        mock_path.return_value.exists.return_value = True

        bootstrap = BootstrapDev()
        assert Path(bootstrap.project_path) == mock_cwd
