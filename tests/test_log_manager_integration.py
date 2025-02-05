import logging
from contextlib import contextmanager

import pytest
from pydantic import BaseModel, ConfigDict

from grpy.tools import LogManager


class ServiceWithLogger(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    log_manager: LogManager

    def service_method(self):
        self.log_manager.logger.info("service_method log info")
        return


@pytest.fixture
def log_manager():
    return LogManager()


@pytest.fixture
def log_manager_with_level(request):
    return LogManager(log_level=request.param)


@pytest.fixture
def service_with_logger(log_manager):
    return ServiceWithLogger(log_manager=log_manager)


@pytest.fixture
def service_with_level(log_manager_with_level):
    return ServiceWithLogger(log_manager=log_manager_with_level)


@pytest.fixture
def capture_logs(caplog):
    @contextmanager
    def _capture_at_level(level=logging.DEBUG):
        with caplog.at_level(level):
            yield caplog

    return _capture_at_level


def test_initializing_logger_passing_to_service(log_manager):
    log_manager.logger.info("Init logger object")
    srv = ServiceWithLogger(log_manager=log_manager)
    srv.log_manager.logger.info("logging from service object")


def test_service_logger_initialization(service_with_logger) -> None:
    assert isinstance(service_with_logger.log_manager, LogManager)
    assert isinstance(service_with_logger.log_manager.logger, logging.Logger)
    assert service_with_logger.log_manager.logger.name == "_custom_logger"


def test_custom_logger_name():
    """
    Test LogManager initialization with custom logger name.
    """
    custom_name = "_test_log_handle"
    lm = LogManager(log_handle=custom_name)
    srv = ServiceWithLogger(log_manager=lm)
    assert srv.log_manager.logger.name == custom_name


def test_service_method_logging(caplog, service_with_logger):
    with caplog.at_level(logging.INFO):
        service_with_logger.service_method()
    assert "service_method log info" in caplog.text


def test_service_logger_level_debug(caplog):
    """
    Test ServiceWithLogger logs DEBUG level messages when configured for DEBUG
    """
    lm = LogManager(log_level="DEBUG")
    srv = ServiceWithLogger(log_manager=lm)

    with caplog.at_level(logging.DEBUG):
        srv.log_manager.logger.debug("Debug message")
        srv.log_manager.logger.info("Info message")

    assert "Debug message" in caplog.text
    assert "Info message" in caplog.text
    assert srv.log_manager.logger.level == logging.DEBUG


@pytest.mark.parametrize("log_manager_with_level", ["ERROR"], indirect=True)
def test_service_logger_level_error(caplog, service_with_level):
    with caplog.at_level(logging.DEBUG):
        service_with_level.log_manager.logger.info("Info message")
        service_with_level.log_manager.logger.error("Error message")
        service_with_level.log_manager.logger.critical("Critical message")

    assert "Info message" not in caplog.text
    assert "Error message" in caplog.text
    assert "Critical message" in caplog.text
    assert service_with_level.log_manager.logger.level == logging.ERROR


def test_service_logger_level_change(caplog):
    """
    Test ServiceWithLogger handles log level changes correctly
    """
    lm = LogManager(log_level="INFO")
    srv = ServiceWithLogger(log_manager=lm)
    assert srv.log_manager.logger.level == logging.INFO

    with caplog.at_level(logging.DEBUG):
        srv.log_manager.logger.debug("Initial debug message")
        srv.log_manager.logger.info("Initial info message")
        assert "Initial debug message" not in caplog.text
        assert "Initial info message" in caplog.text

        srv.log_manager.logger.setLevel(logging.DEBUG)
        assert srv.log_manager.logger.level == logging.DEBUG
        srv.log_manager.logger.debug("Second debug message")
        assert "Second debug message" in caplog.text


@pytest.mark.parametrize(
    "log_level,message,severity,should_appear",
    [
        # Test all levels against WARNING threshold
        ("WARNING", "Debug message", logging.DEBUG, False),
        ("WARNING", "Info message", logging.INFO, False),
        ("WARNING", "Warning message", logging.WARNING, True),
        ("WARNING", "Error message", logging.ERROR, True),
        ("WARNING", "Critical message", logging.CRITICAL, True),
        # Test all levels against INFO threshold
        ("INFO", "Debug message", logging.DEBUG, False),
        ("INFO", "Info message", logging.INFO, True),
        ("INFO", "Warning message", logging.WARNING, True),
        ("INFO", "Error message", logging.ERROR, True),
        ("INFO", "Critical message", logging.CRITICAL, True),
        # Test all levels against DEBUG threshold
        ("DEBUG", "Debug message", logging.DEBUG, True),
        ("DEBUG", "Info message", logging.INFO, True),
        ("DEBUG", "Warning message", logging.WARNING, True),
        ("DEBUG", "Error message", logging.ERROR, True),
        ("DEBUG", "Critical message", logging.CRITICAL, True),
        # Test all levels against CRITICAL threshold
        ("CRITICAL", "Debug message", logging.DEBUG, False),
        ("CRITICAL", "Info message", logging.INFO, False),
        ("CRITICAL", "Warning message", logging.WARNING, False),
        ("CRITICAL", "Error message", logging.ERROR, False),
        ("CRITICAL", "Critical message", logging.CRITICAL, True),
    ],
)
def test_service_logger_severity_boundaries_parameterized(
    caplog, log_level, message, severity, should_appear
):
    """
    Test logging attempts at different severities relative to configured log level
    """
    lm = LogManager(log_level=log_level)
    srv = ServiceWithLogger(log_manager=lm)

    with caplog.at_level(logging.DEBUG):
        getattr(srv.log_manager.logger, logging.getLevelName(severity).lower())(message)

    if should_appear:
        assert message in caplog.text
    else:
        assert message not in caplog.text

    assert srv.log_manager.logger.level == getattr(logging, log_level)
