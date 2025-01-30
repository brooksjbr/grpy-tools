import logging
from typing import Annotated, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Defining a return type for instances of this class
# This implemention is required to support Python version 3.9 and 3.10
# Typing includes type Self beginning in version 3.11
SelfLM = TypeVar("SelfLM", bound="LogManager")


class LogManager(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _instance: Annotated[Optional["LogManager"], "Singleton instance of LogManager", Field()] = None
    _logger: Annotated[Optional[logging.Logger], "Global logger instance", Field()] = None

    def __new__(cls, *args, **kwargs) -> SelfLM:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        if LogManager._logger is None:
            self._setup_logger()

    def _setup_logger(self) -> None:
        LogManager._logger = logging.getLogger("grpy.tools.log_manager")
        LogManager._logger.setLevel(logging.INFO)

        # Only add handler if none exist
        if not LogManager._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d",
            )
            handler.setFormatter(formatter)
            LogManager._logger.addHandler(handler)

    @property
    def logger(self) -> logging.Logger:
        if LogManager._logger is None:
            self._setup_logger()
        return LogManager._logger
