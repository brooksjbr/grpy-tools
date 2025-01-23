from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class BootstrapPath(BaseModel, validate_assignment=True):
    model_config = ConfigDict(strict=True)
    current: Annotated[Path, Field(strict=True, default_factory=Path.cwd)]
    target: Annotated[Path, Field(strict=True, default_factory=Path.cwd)]
    subdirectory: Annotated[str, Field(strict=True, default=None)]

    def check_validation(validator_method):
        def wrapper(self, *args, **kwargs):
            try:
                return validator_method(self, *args, **kwargs)
            except ValidationError as exc:
                print(repr(exc.errors()[0]["type"]))

        return wrapper

    @model_validator(mode="after")
    @check_validation
    def validate_path(self):
        path_fields = self.get_path_attributes()

        for field in path_fields:
            path_value = getattr(self, field)
            if not path_value.exists():
                raise ValueError(f"This path does not exist: {path_value}")

        return self

    def get_path_attributes(self):
        path_fields = [
            field_name
            for field_name, field_info in self.model_fields.items()
            if field_info.annotation == Path
        ]
        return path_fields
