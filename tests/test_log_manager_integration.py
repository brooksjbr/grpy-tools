import logging

import pytest
from pydantic import BaseModel, ConfigDict

from grpy.tools import LogManager


class ServiceWithLogger(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    log_manager: LogManager

    def service_method(self):
        self.log_manager.logger.info("service_method log info")
        return


@pytest.fixture(autouse=True)
def cleanup():
    LogManager._logger = None
    yield


def test_service_logger_initialization() -> None:
    """
    Test that ServiceWithLogger properly initializes with LogManager instance
    and creates a valid logging.Logger object.
    """
    lm = LogManager()
    srv = ServiceWithLogger(log_manager=lm)
    assert isinstance(srv.log_manager, LogManager)
    assert isinstance(srv.log_manager.logger, logging.Logger)
    assert srv.log_manager.logger.name == "_custom_logger"


def test_custom_logger_name():
    """
    Test LogManager initialization with custom logger name.
    """
    custom_name = "_test_log_handle"
    lm = LogManager(log_handle=custom_name)
    srv = ServiceWithLogger(log_manager=lm)
    assert srv.log_manager.logger.name == custom_name


def test_service_method_logging(caplog):
    """
    Test that ServiceWithLogger properly logs messages when service_method is called.
    """
    lm = LogManager()
    srv = ServiceWithLogger(log_manager=lm)

    with caplog.at_level(logging.INFO):
        srv.service_method()

    assert "service_method log info" in caplog.text
