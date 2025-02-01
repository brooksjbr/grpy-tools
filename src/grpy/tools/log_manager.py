import logging
from typing import Annotated, Any, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

SelfLM = TypeVar("SelfLM", bound="LogManager")


class LogManager(BaseModel):
    """
    LogManager is a singleton wrapper to manage a custom logger.

    Args:

    Returns:

    """

    model_config = ConfigDict({"validate_assignment": True, "arbitrary_types_allowed": True})

    _instance: Annotated[Optional["LogManager"], "Singleton instance of LogManager", Field()] = None
    _logger: Annotated[Optional[logging.Logger], "Global logger instance", Field()] = None
    log_handle: Annotated[
        Optional[str],
        "Log handle",
        Field(default="_custom_logger", min_length=4, max_length=50, frozen=True),
    ]

    def __new__(cls, *args, **kwargs) -> SelfLM:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_logger(self):
        if LogManager._logger is None:
            LogManager._logger = logging.getLogger(self.log_handle)

    def __init__(self, log_handle: Optional[str] = "_custom_logger") -> None:
        super().__init__(log_handle=log_handle)
        self.get_logger()

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

    def __getattr__(self, name: str) -> Any:
        return getattr(self.logger, name)
