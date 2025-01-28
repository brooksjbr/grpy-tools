import logging
import shutil
from subprocess import PIPE, Popen
from typing import Annotated, List, Set

from pydantic import BaseModel, ConfigDict, Field, model_validator

CommandType = List[List[str]]

# Define whitelist of allowed commands
PERMITTED_COMMANDS: Set[str] = {"git", "python", "pip", "gh"}


class BootstrapCommands(BaseModel):
    model_config = ConfigDict(strict=True, arbitrary_types_allowed=True)  # Allow Logger type

    cmds: Annotated[CommandType, Field()]
    logger: logging.Logger = Field(
        default_factory=lambda: logging.getLogger(__name__),
        exclude=True,  # Exclude from serialization
    )

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

    @model_validator(mode="after")
    def validate_commands_exist(self) -> "BootstrapCommands":
        for cmd in self.cmds:
            if shutil.which(cmd[0]) is None:
                raise ValueError(f"Command '{cmd[0]}' not found in system PATH")
            if cmd[0] not in PERMITTED_COMMANDS:
                raise ValueError(f"Command '{cmd[0]}' is not in the permitted commands list")
        return self

    def run_commands(self) -> None:
        cmd = self.cmds[0]
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

        self.logger.info("All commands executed successfully")
        return None
