#!/usr/bin/env python3
import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

from pathlib import Path
from pydantic import BaseModel, Field

class BootstrapDev(BaseModel):
    home: str = Field(default_factory=lambda: str(Path.home()), description="User home directory")
