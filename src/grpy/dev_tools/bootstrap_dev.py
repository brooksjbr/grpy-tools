#!/usr/bin/env python3
import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

from pydantic import BaseModel, Field
class BootstrapDev(BaseModel):
    home: str = Field(None,description="Home directory of your project")
    venv_path: str = Field(None,description="Virtual environment path")
    project: str = Field(None,description="Name of the project")
