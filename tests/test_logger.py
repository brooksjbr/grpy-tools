import logging
import unittest

from src.grpy.tools.logger import Logger


class TestLogger(unittest.TestCase):
    def setUp(self):
        # Reset the singleton instance between tests
        Logger._instance = None
        Logger._logger = None
        # Clear any existing handlers from the root logger
        if Logger._logger:
            Logger._logger.handlers.clear()

    def test_singleton_pattern(self):
        logger1 = Logger()
        logger2 = Logger()
        self.assertIs(logger1, logger2)

    def test_logger_initialization(self):
        logger = Logger()
        self.assertIsNotNone(logger.logger)
        self.assertIsInstance(logger.logger, logging.Logger)
        self.assertEqual(logger.logger.name, "grpy.tools.logger")

    def test_logger_configuration(self):
        logger = Logger()
        self.assertEqual(logger.logger.level, logging.INFO)
        self.assertEqual(len(logger.logger.handlers), 1)

        handler = logger.logger.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)

        formatter = handler.formatter
        self.assertEqual(formatter._fmt, "%(asctime)s - %(levelname)s - %(message)s")
        self.assertEqual(formatter.datefmt, "%Y-%m-%d")

    def test_logger_property_access(self):
        logger = Logger()
        logger_instance1 = logger.logger
        logger_instance2 = logger.logger
        self.assertIs(logger_instance1, logger_instance2)

    def test_multiple_logger_creation(self):
        logger1 = Logger()
        logger2 = Logger()
        logger3 = Logger()

        self.assertIs(logger1.logger, logger2.logger)
        self.assertIs(logger2.logger, logger3.logger)
        # Verify only one handler exists
        self.assertEqual(len(logger1.logger.handlers), 1)


if __name__ == "__main__":
    unittest.main()
