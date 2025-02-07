import logging
from typing import Annotated, Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

SelfLM = TypeVar("SelfLM", bound="LogManager")

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
    handler: Annotated[
        logging.Handler, Field(default_factory=logging.StreamHandler)
    ] = logging.StreamHandler()

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.init_logger()
        self.set_level()
        self._setup_handler()

    def set_level(self) -> None:
        self._logger.setLevel(self.log_level.value_int)

    def _setup_handler(self):
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d",
        )
        self.handler.setFormatter(formatter)
        self._logger.addHandler(self.handler)

    def init_logger(self):
        self._logger = logging.getLogger(self.log_handle)

    def __getattr__(self, name: str) -> Any:
        if name == "_logger":
            return None
        if hasattr(self, "_logger") and self._logger is not None:
            return getattr(self._logger, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    @property
    def logger(self) -> logging.Logger:
        return self._logger
