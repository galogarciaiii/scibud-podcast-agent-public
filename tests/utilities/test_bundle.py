import logging
from unittest.mock import patch

import pytest

from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_config_utility():
    """Fixture for mocking ConfigUtility."""
    with patch("podcast.utilities.bundle.ConfigUtility") as MockConfigUtility:
        mock_config_utility = MockConfigUtility.return_value
        mock_config_utility.get_config.return_value = {"project_id": "test_project"}
        yield mock_config_utility


@pytest.fixture
def real_logger():
    """Fixture to provide a real logger instance."""
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def mock_logging_utility(real_logger):
    """Fixture for mocking LoggingUtility, but providing a real logger."""
    with patch("podcast.utilities.bundle.LoggingUtility") as MockLoggingUtility:
        mock_logging_utility = MockLoggingUtility.return_value
        mock_logging_utility.logger = real_logger  # Use a real logger
        yield mock_logging_utility


@pytest.fixture
def mock_time_utility():
    """Fixture for mocking TimeUtility."""
    with patch("podcast.utilities.bundle.TimeUtility") as MockTimeUtility:
        mock_time_utility = MockTimeUtility.return_value
        mock_time_utility.current_time = "2024-01-01 00:00:00"
        yield mock_time_utility


@pytest.fixture
def utilities_bundle(mock_config_utility, mock_logging_utility, mock_time_utility):
    """Fixture to initialize UtilitiesBundle with mocked dependencies."""
    return UtilitiesBundle(
        config_path="config.json",
        timezone="America/New_York",
        logger=mock_logging_utility.logger,  # Use the real logger here
    )


def test_utilities_bundle_initialization(
    utilities_bundle, mock_logging_utility, mock_config_utility, mock_time_utility
):
    """Test that UtilitiesBundle initializes correctly."""
    assert utilities_bundle.logger == mock_logging_utility.logger
    assert utilities_bundle.config_utility == mock_config_utility
    assert utilities_bundle.time == mock_time_utility


def test_utilities_bundle_logging(mock_logging_utility, utilities_bundle):
    """Test that logging works through the bundle."""
    utilities_bundle.logger.info("Test log message")
    assert mock_logging_utility.logger.name == "test_logger"


def test_utilities_bundle_config(mock_config_utility, utilities_bundle):
    """Test that the config is correctly retrieved from ConfigUtility."""
    config = utilities_bundle.config
    mock_config_utility.get_config.assert_called_once()
    assert config == {"project_id": "test_project"}


def test_utilities_bundle_time(mock_time_utility, utilities_bundle):
    """Test that the time utility works correctly."""
    assert utilities_bundle.time.current_time == "2024-01-01 00:00:00"
    mock_time_utility.current_time = "2024-01-02 12:00:00"
    assert utilities_bundle.time.current_time == "2024-01-02 12:00:00"
