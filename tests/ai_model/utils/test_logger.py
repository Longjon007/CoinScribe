import pytest
import os
import logging
from ai_model.utils.logger import setup_logger

class TestLogger:
    def test_setup_logger_console(self):
        logger = setup_logger(name='test_console')
        assert logger.name == 'test_console'
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_logger_file(self, tmp_path):
        log_file = tmp_path / "test.log"
        logger = setup_logger(name='test_file', log_file=str(log_file))

        assert len(logger.handlers) == 2
        assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)

        logger.info("Test message")

        assert log_file.exists()
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Test message" in content
