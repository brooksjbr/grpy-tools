#!/usr/bin/env python3
from pathlib import Path
from typing import Union
from pydantic import BaseModel, Field, field_validator


class BootstrapDev(BaseModel):
    home: str = Field(default_factory=lambda: str(Path.home()), description="User home directory")

    @field_validator("home")
    def validate_path(cls, value: Union[str, Path]):
        try:
            path_obj = Path(value).resolve()
            if not path_obj.exists():
                raise ValueError(f"Path does not exist: {path_obj}")
            return str(path_obj)
        except OSError as e:
            return None
            raise ValueError(f"Path not accessible: {path} - {str(e)}")
        except (TypeError, RuntimeError) as e:
            return None
            raise ValueError(f"Invalid path format: {path} - {str(e)}")
