#!/usr/bin/env python3
from pathlib import Path
from typing import Union

from pydantic import BaseModel, Field, field_validator


class BootstrapDev(BaseModel):
    home_dir: str = Field(
        default_factory=lambda: str(Path.home()), description="User home directory"
    )
    project_dir: str = Field(default_factory=lambda: Path.cwd().name, description="project name")

    @field_validator("home_dir")
    def validate_path(cls, path: Union[str, Path]):
        try:
            path_obj = Path(path).resolve()
            if not path_obj.exists():
                raise ValueError(f"Path does not exist: {path_obj}")
            return str(path_obj)
        except OSError as e:
            return None
            raise ValueError(f"Path not accessible: {path} - {str(e)}")
        except (TypeError, RuntimeError) as e:
            return None
            raise ValueError(f"Invalid path format: {path} - {str(e)}")
