#!/usr/bin/env python3
from pathlib import Path

from pydantic import BaseModel, Field


class BootstrapDev(BaseModel):
    home: str = Field(default_factory=lambda: str(Path.home()), description="User home directory")
