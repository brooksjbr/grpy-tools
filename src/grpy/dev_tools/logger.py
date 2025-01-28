import logging
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class Logger(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _instance: Annotated[Optional["Logger"], "Singleton instance of Logger", Field()] = None
    _logger: Annotated[Optional[logging.Logger], "Global logger instance", Field()] = None

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        if Logger._logger is None:
            self._setup_logger()

    def _setup_logger(self) -> None:
        Logger._logger = logging.getLogger("grpy.tools.logger")
        Logger._logger.setLevel(logging.INFO)

        # Only add handler if none exist
        if not Logger._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d",
            )
            handler.setFormatter(formatter)
            Logger._logger.addHandler(handler)

    @property
    def logger(self) -> logging.Logger:
        if Logger._logger is None:
            self._setup_logger()
        return Logger._logger
