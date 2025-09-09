import json
import logging
from unittest.mock import mock_open, patch

import pytest

from podcast.utilities.logging import LoggingUtility


# Fixture to reset logger state between tests
@pytest.fixture(autouse=True)
def reset_logger():
    logger = logging.getLogger("test_logger")
    level = logger.level
    handlers = logger.handlers[:]  # Make a copy of existing handlers
    yield
    # Reset the logger to its original state
    logger.setLevel(level)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    for handler in handlers:
        logger.addHandler(handler)


@pytest.fixture
def logger():
    return logging.getLogger("test_logger")


@pytest.fixture
def valid_logging_config():
    return {
        "logging": {
            "version": 1,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                }
            },
            "root": {
                "handlers": ["console"],
                "level": "DEBUG",
            },
        }
    }


@pytest.fixture
def invalid_logging_config():
    return '{"logging":'  # Malformed JSON


def test_logging_utility_with_provided_logger(logger):
    logger.setLevel(logging.NOTSET)  # Ensure the logger starts with NOTSET level
    log_util = LoggingUtility(logger=logger)
    assert log_util.logger == logger
    log_util.info("This is a test info message.")
    assert log_util.logger.level == logging.NOTSET  # Adjust this if the logger is expected to be at DEBUG level


def test_logging_utility_with_valid_json_config(valid_logging_config):
    m = mock_open(read_data=json.dumps(valid_logging_config))
    with patch("builtins.open", m):
        with patch("logging.config.dictConfig") as mock_dict_config:
            log_util = LoggingUtility(config_path="valid_config.json", default_level=logging.INFO)
            assert isinstance(log_util.logger, logging.Logger)
            mock_dict_config.assert_called_once_with(valid_logging_config["logging"])


def test_logging_utility_with_invalid_json_config(invalid_logging_config):
    m = mock_open(read_data=invalid_logging_config)
    with patch("builtins.open", m):
        with patch("logging.basicConfig") as mock_basic_config:
            log_util = LoggingUtility(config_path="invalid_config.json", default_level=logging.WARNING)
            assert isinstance(log_util.logger, logging.Logger)
            mock_basic_config.assert_called_once_with(level=logging.WARNING)
            assert log_util.logger.level == logging.NOTSET  # Default logger level


def test_logging_utility_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        with patch("logging.basicConfig") as mock_basic_config:
            log_util = LoggingUtility(config_path="non_existent_config.json", default_level=logging.ERROR)
            assert isinstance(log_util.logger, logging.Logger)
            mock_basic_config.assert_called_once_with(level=logging.ERROR)
            assert log_util.logger.level == logging.NOTSET  # Default logger level


def test_logging_at_different_levels(logger):
    log_util = LoggingUtility(logger=logger)

    with patch.object(logger, "debug") as mock_debug:
        log_util.debug("Debug message")
        mock_debug.assert_called_once_with("Debug message")

    with patch.object(logger, "info") as mock_info:
        log_util.info("Info message")
        mock_info.assert_called_once_with("Info message")

    with patch.object(logger, "warning") as mock_warning:
        log_util.warning("Warning message")
        mock_warning.assert_called_once_with("Warning message")

    with patch.object(logger, "error") as mock_error:
        log_util.error("Error message")
        mock_error.assert_called_once_with("Error message")


def test_type_error_for_invalid_logger():
    with pytest.raises(TypeError):
        LoggingUtility(logger="invalid_logger")  # type: ignore


def test_logging_fallback_to_default(logger):
    with patch("logging.basicConfig") as mock_basic_config:
        log_util = LoggingUtility(logger=None, config_path="non_existent_config.json", default_level=logging.DEBUG)
        mock_basic_config.assert_called_once_with(level=logging.DEBUG)
        assert isinstance(log_util.logger, logging.Logger)
