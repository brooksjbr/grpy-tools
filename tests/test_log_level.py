import logging

import pytest

from src.grpy.tools.log_level import LogLevel


@pytest.mark.parametrize(
    "level,expected",
    [
        (LogLevel.DEBUG, "DEBUG"),
        (LogLevel.INFO, "INFO"),
        (LogLevel.WARNING, "WARNING"),
        (LogLevel.ERROR, "ERROR"),
        (LogLevel.CRITICAL, "CRITICAL"),
    ],
)
def test_log_level_values(level, expected):
    assert level == expected


@pytest.mark.parametrize(
    "level,expected",
    [
        (LogLevel.DEBUG, logging.DEBUG),
        (LogLevel.INFO, logging.INFO),
        (LogLevel.WARNING, logging.WARNING),
        (LogLevel.ERROR, logging.ERROR),
        (LogLevel.CRITICAL, logging.CRITICAL),
    ],
)
def test_log_level_int_values(level, expected):
    assert level.value_int == expected


@pytest.mark.parametrize(
    "level",
    [
        LogLevel.DEBUG,
        LogLevel.INFO,
        LogLevel.WARNING,
        LogLevel.ERROR,
        LogLevel.CRITICAL,
    ],
)
def test_log_level_type(level):
    assert isinstance(level, LogLevel)
    assert issubclass(LogLevel, str)


def test_get_level_invalid():
    with pytest.raises(AttributeError) as exc_info:
        LogLevel.INVALID_LEVEL

    assert "INVALID_LEVEL" in str(exc_info.value)
