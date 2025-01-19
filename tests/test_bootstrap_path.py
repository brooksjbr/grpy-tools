from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.grpy.dev_tools.bootstrap_path import BootstrapPath


def test_bootstrap_path_attributes():
    mock_working_path = Path("/mock/user/projects/mock-project")
    with patch.object(Path, "exists", return_value=True):
        bootstrap = BootstrapPath(working_path=mock_working_path)
    assert isinstance(bootstrap, BootstrapPath)
    assert bootstrap.working_path == mock_working_path


def test_boostrap_path_validation():
    path = Path("/this/path/does/not/exist")
    with pytest.raises(ValidationError):
        bp = BootstrapPath(working_path=path)
        assert bp.working_path is None
