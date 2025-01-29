from subprocess import PIPE
from unittest.mock import Mock, patch

import pytest

from src.grpy.tools.command_tool import CommandTool


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
        ["pip", "install", "-e", ".[dev]"],
        ["gh", "--help"],
        ["python", "--help"],
        ["git", "status"],
    ]


def test_command_tool_init(nested_commands):
    cb = CommandTool(cmds=[nested_commands[0]])
    assert isinstance(cb, CommandTool)
    assert isinstance(cb.cmds, list)
    for cmd in cb.cmds:
        assert isinstance(cmd, list)


def test_command_tool_validate_cmds_list():
    with pytest.raises(ValueError) as exc_info:
        CommandTool(cmds=[["invalid_command", "git status"]])
    assert "Command 'invalid_command' not found in system PATH" in str(exc_info.value)


def test_command_tool_empty():
    with pytest.raises(ValueError) as exc_info:
        CommandTool(cmds=[]).run_commands()
    assert "List should have at least 1 item after validation, not 0" in str(exc_info.value)


def test_command_tool_nested_commands(nested_commands, formatted_commands):
    cb = CommandTool(cmds=nested_commands)
    assert len(cb.cmds) == 4
    assert cb.cmds == formatted_commands


def test_command_tool_inner_cmd_formatted(nested_commands, formatted_commands):
    cb = CommandTool(cmds=nested_commands)
    assert cb.cmds[0] == formatted_commands[0]
    assert cb.cmds[1] == formatted_commands[1]


def test_command_tool_none_input():
    with pytest.raises(ValueError):
        CommandTool(cmds=None)


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
            CommandTool(cmds=[["nonexistent", "arg1"], ["git", "status"]])

        assert "Command 'nonexistent' not found in system PATH" in str(exc_info.value)


def test_non_whitelisted_command_raises_error():
    with pytest.raises(ValueError, match="Command 'rm' is not in the permitted commands list"):
        CommandTool(
            cmds=[
                ["rm", "-rf", "/"],
            ]
        )


def test_command_tool_successful_run():
    with patch("src.grpy.tools.command_tool.Popen") as mock_popen:
        process_mock = Mock()
        process_mock.communicate.return_value = (b"mock output", b"")
        process_mock.returncode = 0
        mock_popen.return_value.__enter__.return_value = process_mock

        cb = CommandTool(cmds=[["git", "status"]])
        cb.run_commands()

        mock_popen.assert_called_once_with(["git", "status"], stdin=PIPE, stderr=PIPE)
        process_mock.communicate.assert_called_once()
