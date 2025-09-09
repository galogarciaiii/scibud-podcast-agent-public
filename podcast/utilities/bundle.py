import logging
from typing import Any, Mapping, Optional

from podcast.utilities.config import ConfigUtility
from podcast.utilities.logging import LoggingUtility
from podcast.utilities.time import TimeUtility


class UtilitiesBundle:
    """
    A utility bundle class that provides centralized access to configuration, logging, and time utilities.

    This class consolidates three utility classes into a single bundle:
    - `LoggingUtility`: Manages logging configuration and provides a logger instance.
    - `ConfigUtility`: Loads and manages the application configuration.
    - `TimeUtility`: Handles time-related operations based on a specific timezone.

    Attributes:
        logger (logging.Logger): The logger instance used by the application.
        config_utility (ConfigUtility): An instance of ConfigUtility to manage the configuration.
        time (TimeUtility): An instance of TimeUtility to handle time-related operations.

    Args:
        config_path (str): The path to the configuration file (default: "config.json").
        timezone (str): The timezone to be used for time-related operations
            (default: "America/Los_Angeles").
        default_logging_level (int):
            The default logging level to be used if the configuration is not loaded
            (default: logging.INFO).
        logger (Optional[logging.Logger]): An optional pre-configured logger.
            If provided, this logger will be used. If not, a new logger is created.

    Example:
        # Create an instance of the UtilitiesBundle
        bundle = UtilitiesBundle(config_path="path/to/config.json", timezone="America/New_York")

        # Access the logger
        logger = bundle.logger
        logger.info("Application started")

        # Access the configuration
        config = bundle.config
        project_id = config.get("project_id")

        # Access time-related utilities
        current_time = bundle.time.current_time
    """

    def __init__(
        self,
        config_path: str = "config.json",
        timezone: str = "America/Los_Angeles",
        default_logging_level: int = logging.INFO,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize the UtilitiesBundle class.

        This method initializes the logging, configuration, and time utilities. It creates instances of:
        - `LoggingUtility`: If no logger is passed,
            a new logger is configured using the logging configuration in the provided config file.
        - `ConfigUtility`: Loads the configuration from the provided file.
        - `TimeUtility`: Initializes time-related operations based on the provided timezone.

        Args:
            config_path (str): The path to the configuration file (default: "config.json").
            timezone (str): The timezone to be used for time-related operations (default: "America/Los_Angeles").
            default_logging_level (int): The default logging level (default: logging.INFO).
            logger (Optional[logging.Logger]): An optional logger. If None, a new logger is created.
        """
        # Initialize LoggingUtility instance and store logger
        self.logger = LoggingUtility(
            logger=logger, config_path=config_path, default_level=default_logging_level, logger_name="scibud_logger"
        ).logger

        # Initialize ConfigUtility instance with the logger
        self.config_utility = ConfigUtility(logger=self.logger, config_path=config_path)

        # Initialize TimeUtility instance
        self.time = TimeUtility(timezone=timezone)

    @property
    def config(self) -> Mapping[str, Any]:
        """
        Retrieve the loaded configuration.

        This method returns the application configuration as an immutable mapping.
        The configuration is loaded from the config file specified during initialization.

        Returns:
            Mapping[str, Any]: The loaded configuration as an immutable dictionary.

        Example:
            config = bundle.config
            project_id = config.get("project_id")
        """
        return self.config_utility.get_config()
