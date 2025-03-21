import logging
import shlex
import shutil
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Annotated, Callable, List, Optional, TypeVar, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .log_manager import LogManager

CommandType = List[str]
CommandListType = List[CommandType]


T = TypeVar("T")
# Defining a return type for instances of this class
# This implemention is required to support Python version 3.9 and 3.10
# Typing includes type Self beginning in version 3.11
SelfCM = TypeVar("TCommandManager", bound="CommandManager")


class CommandManager(BaseModel):
    model_config = ConfigDict(strict=True, arbitrary_types_allowed=True)
    cmds: Annotated[CommandListType, Field(min_length=1)]
    timeout: Optional[float] = Field(default=2.0, gt=0, description="Command timeout in seconds")
    logger: Union[LogManager, logging.Logger] = Field(default_factory=LogManager)

    # TODO: add pydantic field support, exclude=True
    cmd_whitelist: List[str] = ["git", "python", "pip", "gh"]

    def __init__(self, **data) -> None:
        super().__init__(**data)

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
    def validate_commands(self) -> SelfCM:
        processed_commands: CommandType = []
        for cmd in self.cmds:
            formatted_cmd = shlex.split(cmd[0]) if " " in cmd[0] else cmd

            if shutil.which(formatted_cmd[0]) is None:
                raise ValueError(f"Command '{formatted_cmd[0]}' not found in system PATH")
            if formatted_cmd[0] not in self.cmd_whitelist:
                raise ValueError(
                    f"Command '{formatted_cmd[0]}' is not in the permitted commands list"
                )

            processed_commands.append(formatted_cmd)

        self.cmds = processed_commands
        return self

    @handle_exception
    def run_command(self, cmd: CommandType) -> None:
        with Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True) as process:
            self.logger.info(f"Executing command: {' '.join(cmd)}")

            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
            except (TimeoutExpired, TimeoutError):
                process.kill()
                raise TimeoutExpired(cmd, self.timeout)

            if stdout:
                self.logger.info(f"Command output:\n{stdout.strip()}")

            if process.returncode == 0:
                self.logger.info(f"Command completed successfully: {' '.join(cmd)}")
            else:
                process.kill()
                error_msg = stderr.strip() if stderr else "No error message provided"
                raise RuntimeError(f"Command failed: {' '.join(cmd)}\nError: {error_msg}")

    @handle_exception
    def run_commands(self) -> None:
        for cmd in self.cmds:
            self.run_command(cmd)
        self.logger.info("All commands executed successfully")
