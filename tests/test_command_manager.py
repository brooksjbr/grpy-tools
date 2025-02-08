from subprocess import PIPE, TimeoutExpired
from unittest.mock import Mock, patch

import pytest

from src.grpy.tools.command_manager import CommandManager


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
def timeout_error_msg(git_status_cmd, request):
    expected_timeout = request.node.callspec.params.get("expected_timeout", 2.0)
    return f"Command '{git_status_cmd}' timed out after {expected_timeout} seconds"


@pytest.fixture
def mock_timeout_process(timeout_error_msg):
    with patch("src.grpy.tools.command_manager.Popen") as mock_popen:
        process_mock = Mock()
        process_mock.communicate.side_effect = TimeoutError(timeout_error_msg)
        mock_popen.return_value.__enter__.return_value = process_mock
        yield mock_popen, process_mock


@pytest.fixture
def command_manager(mock_timeout_process, git_status_cmd, timeout=None):
    mock_popen, process_mock = mock_timeout_process
    if timeout is None:
        return CommandManager(cmds=[git_status_cmd]), process_mock
    else:
        return CommandManager(cmds=[git_status_cmd], timeout=timeout), process_mock


def test_command_manager_init(nested_commands):
    cm = CommandManager(cmds=[nested_commands[0]])
    assert isinstance(cm, CommandManager)
    assert isinstance(cm.cmds, list)
    for cmd in cm.cmds:
        assert isinstance(cmd, list)


def test_command_manager_validate_cmds_list():
    with pytest.raises(ValueError) as exc_info:
        CommandManager(cmds=[["invalid_command", "git status"]])
    assert "Command 'invalid_command' not found in system PATH" in str(exc_info.value)


def test_command_manager_empty():
    with pytest.raises(ValueError) as exc_info:
        CommandManager(cmds=[]).run_commands()
    assert "List should have at least 1 item after validation, not 0" in str(exc_info.value)


def test_command_manager_nested_commands(nested_commands, formatted_commands):
    cm = CommandManager(cmds=nested_commands)
    assert len(cm.cmds) == 4
    assert cm.cmds == formatted_commands


def test_command_manager_none_input():
    with pytest.raises(ValueError) as exc_info:
        CommandManager(cmds=None)
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
            CommandManager(cmds=[["nonexistent", "arg1"], ["git", "status"]])

        assert "Command 'nonexistent' not found in system PATH" in str(exc_info.value)


def test_non_whitelisted_command_raises_error():
    cmd = (["ls", "-la", "/"],)
    with pytest.raises(ValueError) as exc_info:
        cm = CommandManager(cmds=[cmd])

        assert f"Command '{cmd[0]}' is not in the permitted commands list" in str(exc_info.value)

        cm.cmd_whitelist.append("ls")

        cm.cmds.append(cmd)

        assert "ls" in cm.cmd_whitelist
        assert cm.cmds == [["ls", "-la", "/"]]


def test_command_manager_successful_run():
    with patch("src.grpy.tools.command_manager.Popen") as mock_popen:
        process_mock = Mock()
        process_mock.communicate.return_value = (b"mock output", b"")
        process_mock.returncode = 0
        mock_popen.return_value.__enter__.return_value = process_mock

        cm = CommandManager(cmds=[["git", "status"]])
        cm.run_commands()

        mock_popen.assert_called_once_with(
            ["git", "status"], stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True
        )
        process_mock.communicate.assert_called_once()


@pytest.mark.parametrize(
    "timeout,expected_timeout",
    [
        (None, 2.0),  # Default timeout case
        (60.0, 60.0),  # Custom timeout case
        (-1.0, None),  # Invalid negative timeout
        (0, None),  # Invalid zero timeout
        (0.0, None),  # Invalid zero float timeout
    ],
)
def test_command_manager_timeouts(
    command_manager, git_status_cmd, timeout_error_msg, timeout, expected_timeout
):
    if expected_timeout is None:
        with pytest.raises(ValueError) as exc_info:
            CommandManager(cmds=[git_status_cmd], timeout=timeout)
        assert "Input should be greater than 0" in str(exc_info.value)
        return

    cm, process_mock = command_manager
    if timeout:
        cm.timeout = timeout
    assert cm.timeout == expected_timeout

    with pytest.raises(TimeoutExpired) as exc_info:
        cm.run_commands()
    assert timeout_error_msg in str(exc_info.value)
    process_mock.communicate.assert_called_once_with(timeout=expected_timeout)
