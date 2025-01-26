from unittest.mock import patch

import pytest

from src.grpy.dev_tools.bootstrap_commands import BootstrapCommands


@pytest.fixture
def nested_commands():
    return [
        ["pip install -e '.[dev]'"],
        ["gh --help"],
        ["python --help"],
        ["git status"],
    ]


@pytest.fixture
def formatted_commands():
    return [
        ["pip", "install", "-e", "'.[dev]'"],
        ["gh", "--help"],
        ["python", "--help"],
        ["git", "status"],
    ]


def test_bootstrap_commands_init(nested_commands):
    cb = BootstrapCommands(cmds=[nested_commands[0]])
    assert isinstance(cb, BootstrapCommands)
    assert isinstance(cb.cmds, list)
    for cmd in cb.cmds:
        assert isinstance(cmd, list)


def test_bootstrap_commands_validate_cmds_list():
    with pytest.raises(ValueError):
        BootstrapCommands(cmds=123)


def test_bootstrap_commands_invalid_cmds_inner_mixed_type_list():
    with pytest.raises(ValueError):
        BootstrapCommands(cmds=[123, "test"])


def test_bootstrap_commands_empty():
    cb = BootstrapCommands(cmds=[])
    assert isinstance(cb, BootstrapCommands)
    assert len(cb.cmds) == 0


def test_bootstrap_commands_nested_commands(nested_commands, formatted_commands):
    cb = BootstrapCommands(cmds=nested_commands)
    assert len(cb.cmds) == 4
    assert cb.cmds == formatted_commands


def test_bootstrap_commands_inner_cmd_formatted(nested_commands, formatted_commands):
    cb = BootstrapCommands(cmds=nested_commands)
    assert cb.cmds[0] == formatted_commands[0]
    assert cb.cmds[1] == formatted_commands[1]


def test_bootstrap_commands_none_input():
    with pytest.raises(ValueError):
        BootstrapCommands(cmds=None)


def test_command_is_missing_from_filesystem():
    with patch("shutil.which") as mock_which:

        def mock_response(cmd):
            valid_commands = {
                "git": "/mock/path/git",
                "python": "/mock/path/python",
                "nonexistent": None,
            }
            return valid_commands.get(cmd)

        mock_which.side_effect = mock_response

        with pytest.raises(ValueError) as exc_info:
            BootstrapCommands(cmds=[["nonexistent", "arg1"], ["git", "status"]])

        assert "Command 'nonexistent' not found in system PATH" in str(exc_info.value)


def test_non_whitelisted_command_raises_error():
    with pytest.raises(ValueError, match="Command 'rm' is not in the permitted commands list"):
        BootstrapCommands(
            cmds=[
                ["rm", "-rf", "/"],
            ]
        )
