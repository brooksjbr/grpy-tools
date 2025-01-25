from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field, model_validator

CommandType = List[List[str]]


class BootstrapCommands(BaseModel):
    model_config = ConfigDict(strict=True)

    cmds: Annotated[CommandType, Field()]

    @model_validator(mode="after")
    def split_command_strings(self) -> "BootstrapCommands":
        processed_commands = []
        for cmd in self.cmds:
            if len(cmd) == 1 and " " in cmd[0]:
                processed_commands.append(cmd[0].split())
            else:
                processed_commands.append(cmd)
        self.cmds = processed_commands
        return self
