import logging
from typing import Annotated, Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

SelfLM = TypeVar("SelfLM", bound="LogManager")


class LogManager(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    log_handle: Annotated[
        str, Field(description="Log handle", max_length=50, min_length=4, frozen=True)
    ] = "_custom_logger"

    def __new__(cls, *args, **kwargs) -> SelfLM:
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._logger = None
        return cls._instance

    def _setup_logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(self.log_handle)

    def __init__(self, log_handle: str = "_custom_logger") -> None:
        super().__init__(log_handle=log_handle)
        self._setup_logger()

        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d",
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    @property
    def get_logger(self) -> logging.Logger:
        if not self._logger:
            self._setup_logger()
        return self._logger

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def __getattr__(self, name: str) -> Any:
        return getattr(self.get_logger, name)
