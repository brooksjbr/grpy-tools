import logging
from typing import Literal

HANDLER_TYPE = Literal["STREAM"]
HANDLER_MAPPING = dict[HANDLER_TYPE, type[logging.Handler]]


class LogHandler:
    handler_type: HANDLER_TYPE = "STREAM"
    handlers: HANDLER_MAPPING = {"STREAM": logging.StreamHandler}

    def create(self, handler_type: HANDLER_TYPE = "STREAM") -> logging.Handler:
        return self.handlers[handler_type]()
