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


@pytest.fixture
def git_status_cmd():
    return ["git", "status"]


@pytest.fixture
def timeout_error_msg():
    return "Command timed out"


@pytest.fixture
def mock_timeout_process(timeout_error_msg):
    with patch("src.grpy.tools.command_tool.Popen") as mock_popen:
        process_mock = Mock()
        process_mock.communicate.side_effect = TimeoutError(timeout_error_msg)
        mock_popen.return_value.__enter__.return_value = process_mock
        yield mock_popen, process_mock


def test_command_tool_init(nested_commands):
    ct = CommandTool(cmds=[nested_commands[0]])
    assert isinstance(ct, CommandTool)
    assert isinstance(ct.cmds, list)
    for cmd in ct.cmds:
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
    ct = CommandTool(cmds=nested_commands)
    assert len(ct.cmds) == 4
    assert ct.cmds == formatted_commands


def test_command_tool_none_input():
    with pytest.raises(ValueError) as exc_info:
        CommandTool(cmds=None)
    assert "Input should be a valid list" in str(exc_info.value)


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
    cmd = (["ls", "-la", "/"],)
    with pytest.raises(ValueError) as exc_info:
        ct = CommandTool(cmds=[cmd])

        assert f"Command '{cmd[0]}' is not in the permitted commands list" in str(exc_info.value)

        ct.cmd_whitelist.append("ls")

        ct.cmds.append(cmd)

        assert "ls" in ct.cmd_whitelist
        assert ct.cmds == [["ls", "-la", "/"]]


def test_command_tool_successful_run():
    with patch("src.grpy.tools.command_tool.Popen") as mock_popen:
        process_mock = Mock()
        process_mock.communicate.return_value = (b"mock output", b"")
        process_mock.returncode = 0
        mock_popen.return_value.__enter__.return_value = process_mock

        ct = CommandTool(cmds=[["git", "status"]])
        ct.run_commands()

        mock_popen.assert_called_once_with(["git", "status"], stdin=PIPE, stderr=PIPE)
        process_mock.communicate.assert_called_once()


def test_command_tool_default_timeout(mock_timeout_process, git_status_cmd):
    mock_popen, process_mock = mock_timeout_process
    ct = CommandTool(cmds=[git_status_cmd])
    with pytest.raises(TimeoutError):
        ct.run_commands()

    mock_popen.assert_called_once_with(git_status_cmd, stdin=PIPE, stderr=PIPE)
    process_mock.communicate.assert_called_once_with(timeout=2.0)


def test_command_tool_custom_timeout(mock_timeout_process, git_status_cmd, timeout_error_msg):
    mock_popen, process_mock = mock_timeout_process
    ct = CommandTool(cmds=[git_status_cmd], timeout=60.0)
    assert ct.timeout == 60.0

    with pytest.raises(TimeoutError) as exc_info:
        ct.run_commands()

    assert timeout_error_msg in str(exc_info.value)
    mock_popen.assert_called_once_with(git_status_cmd, stdin=PIPE, stderr=PIPE)
    process_mock.communicate.assert_called_once_with(timeout=60.0)


@pytest.mark.parametrize("timeout_value", [-1.0, 0, 0.0])
def test_invalid_timeouts(timeout_value):
    with pytest.raises(ValueError) as exc_info:
        CommandTool(cmds=[["git", "status"]], timeout=timeout_value)
    assert "Input should be greater than 0" in str(exc_info.value)
