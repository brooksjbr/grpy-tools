import shutil
from functools import wraps
from subprocess import PIPE, Popen
from typing import Annotated, Any, Callable, List, Set, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

CommandType = List[List[str]]
T = TypeVar("T")

# Define whitelist of allowed commands
PERMITTED_COMMANDS: Set[str] = {"git", "python", "pip", "gh"}


class BootstrapCommands(BaseModel):
    model_config = ConfigDict(strict=True)

    cmds: Annotated[CommandType, Field()]

    @model_validator(mode="after")
    def format_command_strings(self) -> "BootstrapCommands":
        processed_commands: CommandType = []
        for cmd in self.cmds:
            if len(cmd) == 1 and " " in cmd[0]:
                processed_commands.append(cmd[0].split())
            else:
                processed_commands.append(cmd)
        self.cmds = processed_commands
        return self

    def handle_exceptions(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                raise

        return wrapper

    @model_validator(mode="after")
    @handle_exceptions
    def validate_commands_exist(self) -> "BootstrapCommands":
        for cmd in self.cmds:
            if shutil.which(cmd[0]) is None:
                raise ValueError(f"Command '{cmd[0]}' not found in system PATH")
            if cmd[0] not in PERMITTED_COMMANDS:
                raise ValueError(f"Command '{cmd[0]}' is not in the permitted commands list")
        return self

    @handle_exceptions
    def run_commands(self) -> None:
        cmd = self.cmds[0]
        with Popen(cmd, stdin=PIPE, stderr=PIPE) as process:
            print(f"Executing command: {' '.join(cmd)}")
            cmd_result, err = process.communicate()
            return_code = process.returncode
            if return_code != 0:
                process.kill()
                raise RuntimeError(f"Command failed: {' '.join(cmd)}\nError: {err}")
            else:
                print(f"Command completed successfully: {' '.join(cmd)}")
                print(f"Output: {cmd_result}")

        print("All commands executed successfully")
        return None
