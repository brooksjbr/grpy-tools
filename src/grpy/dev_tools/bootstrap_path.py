from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, ValidationError, model_validator


class BootstrapPath(BaseModel):
    working_path: Annotated[Path, Field(strict=True)]

    def check_validation(validator_method):
        def wrapper(self, *args, **kwargs):
            try:
                return validator_method(self, *args, **kwargs)
            except ValidationError as exc:
                print(repr(exc.errors()[0]["type"]))

        return wrapper

    @model_validator(mode="after")
    @check_validation
    def is_valid_path(self):
        if self.working_path.exists() is False:
            raise ValueError("work path is not a valid path")

        return self
