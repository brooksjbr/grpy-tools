import logging

import pytest

from grpy.tools.log_handler import LogHandler


class TestLogHandler:
    def test_handler_type_default(self):
        handler = LogHandler()
        assert handler.handler_type == "STREAM"

    def test_create_handler_returns_stream_handler(self):
        handler = LogHandler()
        result = handler.create()
        assert isinstance(result, logging.StreamHandler)

    def test_create_handler_with_explicit_stream_type(self):
        handler = LogHandler()
        result = handler.create(handler_type="STREAM")
        assert isinstance(result, logging.StreamHandler)

    def test_create_handler_invalid_type(self):
        handler = LogHandler()
        with pytest.raises(KeyError):
            handler.create(handler_type="INVALID")
