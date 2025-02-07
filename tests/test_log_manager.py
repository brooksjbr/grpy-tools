import logging

import pytest

from grpy.tools.log_manager import LogManager


def test_log_manager_initialization_defaults():
    lm = LogManager()
    assert lm.log_handle == "_custom_logger"
    assert lm.log_level == "INFO"


def test_log_handle_custom_handle_init():
    lm = LogManager(log_handle="_test")
    assert lm.log_handle == "_test"
    assert lm.log_level == "INFO"


def test_log_handle_default_value():
    lm = LogManager()
    assert isinstance(lm.log_handle, str)
    assert len(lm.log_handle) >= 4
    assert len(lm.log_handle) <= 50
    assert lm.log_handle == "_custom_logger"


def test_log_handle_validation_min_length():
    with pytest.raises(ValueError) as exc_info:
        LogManager(log_handle="abc")
    assert "string_too_short" in str(exc_info.value).lower()
    assert "4" in str(exc_info.value)


def test_log_handle_validation_max_length():
    with pytest.raises(ValueError) as exc_info:
        LogManager(log_handle="a" * 51)
    assert "string_too_long" in str(exc_info.value).lower()
    assert "50" in str(exc_info.value)

    valid_handle = "a" * 50
    lm = LogManager(log_handle=valid_handle)
    assert len(lm.log_handle) == 50


def test_log_handle_value_frozen():
    lm = LogManager()
    with pytest.raises(ValueError) as exc_info:
        lm.log_handle = "_test"
    assert "frozen" in str(exc_info.value).lower()
    assert lm.log_handle == "_custom_logger"


def test_log_handle_exactly_min_length():
    lm = LogManager(log_handle="abcd")
    assert lm.log_handle == "abcd"


def test_log_handle_exactly_max_length():
    handle_50_chars = "a" * 50
    lm = LogManager(log_handle=handle_50_chars)
    assert lm.log_handle == handle_50_chars


def test_singleton_pattern():
    lm1 = LogManager()
    lm2 = LogManager()
    assert lm1 is lm2


def test_logger_property_access():
    lm = LogManager()
    logger_instance1 = lm.logger
    logger_instance2 = lm.logger
    assert logger_instance1 is logger_instance2


def test_log_manager_debug_level():
    lm = LogManager(log_level="DEBUG")
    assert lm.log_level == "DEBUG"


def test_update_log_level():
    lm = LogManager()
    assert lm.log_level == "INFO"
    lm.log_level = "DEBUG"
    assert lm.log_level == "DEBUG"


def test_invalid_log_level():
    with pytest.raises(ValueError) as exc_info:
        LogManager(log_level="UNKNOWN_LEVEL")
    assert "UNKNOWN_LEVEL" in str(exc_info.value)


def test_log_manager_handler_type():
    lm = LogManager()
    assert isinstance(lm.handler, logging.StreamHandler)
    assert isinstance(lm.logger.handlers[0], logging.StreamHandler)


def test_log_manager_add_handler():
    lm = LogManager()
    lm.add_handler(logging.StreamHandler())

    assert len(lm.handlers) == 1
