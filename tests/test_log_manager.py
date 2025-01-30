import logging
import unittest

from src.grpy.tools.log_manager import LogManager


class TestLogManafer(unittest.TestCase):
    def setUp(self):
        # Reset the singleton instance between tests
        LogManager._instance = None
        LogManager._logger = None
        # Clear any existing handlers from the root logger
        if LogManager._logger:
            LogManager._logger.handlers.clear()

    def test_singleton_pattern(self):
        lm1 = LogManager()
        lm2 = LogManager()
        self.assertIs(lm1, lm2)
        self.assertEqual(len(lm1.logger.handlers), 1)

    def test_logger_initialization(self):
        lm = LogManager()
        self.assertIsNotNone(lm.logger)
        self.assertIsInstance(lm, LogManager)
        self.assertEqual(lm.logger.name, "grpy.tools.log_manager")

    def test_logger_configuration(self):
        lm = LogManager()
        self.assertEqual(lm.logger.level, logging.INFO)
        self.assertEqual(len(lm.logger.handlers), 1)

        handler = lm.logger.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)

        formatter = handler.formatter
        self.assertEqual(formatter._fmt, "%(asctime)s - %(levelname)s - %(message)s")
        self.assertEqual(formatter.datefmt, "%Y-%m-%d")

    def test_logger_property_access(self):
        lm = LogManager()
        logger_instance1 = lm.logger
        logger_instance2 = lm.logger
        self.assertIs(logger_instance1, logger_instance2)


if __name__ == "__main__":
    unittest.main()
