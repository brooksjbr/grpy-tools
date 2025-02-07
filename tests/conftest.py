import logging

import pytest

from grpy.tools import LogManager


@pytest.fixture
def log_handler():
    return logging.StreamHandler()


@pytest.fixture
def log_manager(log_handler):
    return LogManager(handler=log_handler)


@pytest.fixture
def log_manager_with_level(request, log_handler):
    return LogManager(handler=log_handler, log_level=request.param)
