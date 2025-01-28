import logging
import shlex
import shutil
from subprocess import PIPE, Popen
from typing import Annotated, Callable, List, Set, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

CommandType = List[str]
CommandListType = List[CommandType]

# Define whitelist of allowed commands
PERMITTED_COMMANDS: Set[str] = {"git", "python", "pip", "gh"}

T = TypeVar("T")


class BootstrapCommands(BaseModel):
    model_config = ConfigDict(strict=True, arbitrary_types_allowed=True)

    cmds: Annotated[CommandListType, Field(min_length=1)]
    logger: logging.Logger = Field(
        default_factory=lambda: logging.getLogger(__name__),
        exclude=True,
    )

    def handle_exception(validator_method: Callable[..., T]) -> Callable[..., T]:
        def wrapper(self, *args, **kwargs):
            try:
                return validator_method(self, *args, **kwargs)
            except ValidationError as exc:
                self.logger.error(f"Error: {str(exc)}")
            return self

        return wrapper

    @model_validator(mode="after")
    @handle_exception
    def format_command_strings(self) -> "BootstrapCommands":
        processed_commands: CommandType = []
        for cmd in self.cmds:
            if " " in cmd[0]:
                processed_commands.append(shlex.split(cmd[0]))
            else:
                processed_commands.append(cmd)
        self.cmds = processed_commands
        return self

    @model_validator(mode="after")
    @handle_exception
    def validate_commands_exist(self) -> "BootstrapCommands":
        for cmd in self.cmds:
            if shutil.which(cmd[0]) is None:
                raise ValueError(f"Command '{cmd[0]}' not found in system PATH")
            if cmd[0] not in PERMITTED_COMMANDS:
                raise ValueError(f"Command '{cmd[0]}' is not in the permitted commands list")
        return self

    @handle_exception
    def run_command(self, cmd: CommandType) -> None:
        with Popen(cmd, stdin=PIPE, stderr=PIPE) as process:
            self.logger.info(f"Executing command: {' '.join(cmd)}")
            cmd_result, err = process.communicate()
            return_code = process.returncode
            if return_code != 0:
                process.kill()
                raise RuntimeError(f"Command failed: {' '.join(cmd)}\nError: {err}")
            else:
                self.logger.info(f"Command completed successfully: {' '.join(cmd)}")
                self.logger.info(f"Output: {cmd_result}")

    @handle_exception
    def run_commands(self) -> None:
        for cmd in self.cmds:
            self.run_command(cmd)
        self.logger.info("All commands executed successfully")
