from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from src.grpy.dev_tools.bootstrap_path import BootstrapPath


def test_bootstrap_path():
    mock_path = Mock(spec=Path)
    with patch.object(Path, "exists", return_value=True):
        bootstrap = BootstrapPath(working_path=mock_path)
    assert isinstance(bootstrap, BootstrapPath)
    assert bootstrap.working_path == mock_path


def test_boostrap_path_validation():
    path = Path("/this/path/does/not/exist")
    with pytest.raises(ValidationError):
        bp = BootstrapPath(working_path=path)
        assert bp.working_path == path
