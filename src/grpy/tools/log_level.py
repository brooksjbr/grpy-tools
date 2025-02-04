import logging
from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @property
    def value_int(self) -> int:
        level_mapping = {
            self.DEBUG: logging.DEBUG,
            self.INFO: logging.INFO,
            self.WARNING: logging.WARNING,
            self.ERROR: logging.ERROR,
            self.CRITICAL: logging.CRITICAL,
        }
        return level_mapping[self]
