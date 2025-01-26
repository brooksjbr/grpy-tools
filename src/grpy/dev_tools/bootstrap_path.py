import logging
import os
from pathlib import Path
from typing import Annotated, Callable, ClassVar, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

T = TypeVar("T")
logger = logging.getLogger(__name__)


class BootstrapPath(BaseModel, validate_assignment=True):
    model_config = ConfigDict(strict=True)
    target: Annotated[Path, Field(default_factory=Path.cwd)]

    ERROR_ABSOLUTE_PATH: ClassVar[str] = "Path must be absolute: {}"
    ERROR_PATH_EXISTS: ClassVar[str] = "Path does not exist: {}"
    ERROR_PATH_READABLE: ClassVar[str] = "Path is not readable: {}"
    ERROR_NOT_DIRECTORY: ClassVar[str] = "Path must be a directory: {}"

    def check_validation(validator_method: Callable[..., T]) -> Callable[..., T]:
        def wrapper(self, *args, **kwargs):
            try:
                return validator_method(self, *args, **kwargs)
            except ValidationError as exc:
                logger.error(f"Validation error: {exc.errors()[0]['type']}")
            return self

        return wrapper

    @model_validator(mode="after")
    @check_validation
    def validate_path(self):
        if not os.access(self.target, os.R_OK):
            raise ValueError(self.ERROR_PATH_READABLE.format(self.target))

        if not self.target.is_absolute():
            raise ValueError(self.ERROR_ABSOLUTE_PATH.format(self.target))

        if not self.target.exists():
            raise ValueError(self.ERROR_PATH_EXISTS.format(self.target))

        if not self.target.is_dir():
            raise ValueError(self.ERROR_NOT_DIRECTORY.format(self.target))

        return self
