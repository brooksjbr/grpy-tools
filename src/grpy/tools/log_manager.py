import logging
from typing import Annotated, Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

SelfLM = TypeVar("SelfLM", bound="LogManager")

from .log_handler import LogHandler
from .log_level import LogLevel


class LogManagerSingleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(LogManagerSingleton, cls).__new__(cls)
        return cls.instance


class LogManager(BaseModel, LogManagerSingleton):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        str_min_length=4,
        str_max_length=50,
        str_strip_whitespace=True,
    )

    log_handle: Annotated[str, Field(frozen=True)] = "_custom_logger"
    log_level: Annotated[LogLevel, Field()] = LogLevel.INFO
    log_handler: Annotated[LogHandler, Field(default=LogHandler())]

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._setup_logger()
        self._logger.setLevel(self.log_level.value_int)
        self._setup_handler()

    def set_level(self, level: LogLevel) -> None:
        self.log_level = level
        self._logger.setLevel(self.log_level.value_int)

    def _setup_handler(self):
        handler = self.log_handler.create()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d",
        )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def _setup_logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(self.log_handle)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._logger, name)

    @property
    def logger(self) -> logging.Logger:
        return self._logger
