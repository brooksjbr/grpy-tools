from typing import Annotated, List, Union

from pydantic import BaseModel, ConfigDict, Field

CommandType = Union[str, List[str]]


class BootstrapCommands(BaseModel):
    model_config = ConfigDict(strict=True)

    cmds: Annotated[CommandType, Field()]
