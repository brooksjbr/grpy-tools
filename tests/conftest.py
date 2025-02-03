import pytest

from grpy.tools import LogManager


@pytest.fixture(autouse=True)
def cleanup():
    LogManager._logger = None
    yield
