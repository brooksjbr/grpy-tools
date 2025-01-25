import pytest

from src.grpy.dev_tools.bootstrap_commands import BootstrapCommands


def test_bootstrap_commands_with_string():
    cb = BootstrapCommands(cmds="npm install")
    assert isinstance(cb.cmds, str)
    assert cb.cmds == "npm install"


def test_bootstrap_commands_with_list():
    cb = BootstrapCommands(cmds=["npm install", "npm build"])
    assert isinstance(cb.cmds, list)
    assert len(cb.cmds) == 2
    assert all(isinstance(cmd, str) for cmd in cb.cmds)


def test_bootstrap_commands_strict_validation():
    with pytest.raises(ValueError):
        BootstrapCommands(cmds=123)
