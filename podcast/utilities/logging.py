import json
import logging
import logging.config
from typing import Optional


class LoggingUtility:
    """
    A utility class for configuring and managing logging in a Python application.

    The LoggingUtility allows for logging configuration via a JSON file. If a logger is passed
    during initialization, it uses that logger; otherwise, it sets up a new logger based on the
    configuration provided in a JSON file or falls back to a default logging level if the
    configuration file is not found or is invalid.

    Attributes:
        logger (logging.Logger): The logger instance being used by the utility.

    Args:
        logger (Optional[logging.Logger]): If provided, this logger will be used directly.
                                           If None, a new logger will be set up.
        config_path (str): The path to the JSON configuration file for logging.
                           Default is "config.json".
        default_level (int): The default logging level to use if the config file cannot be loaded.
                             Default is logging.INFO.
        logger_name (str): The name of the logger to be used if no logger is provided.
                           Default is "default_logger".

    Behavior:
        - If the logger is passed to the class, the provided logger is used as is.
        - If no logger is provided, the utility attempts to load logging configuration
          from the specified JSON file. If successful, it applies the configuration.
        - If the logging configuration fails to load (e.g., file missing or invalid),
          it falls back to the `default_level` specified during initialization.
        - The logging level specified in the configuration file (if present) takes precedence
          over the default level.

    Example:
        logging_utility = LoggingUtility(config_path="config.json", default_level=logging.DEBUG)

        logging_utility.debug("This is a debug message")  # Depends on the logging level in config
        logging_utility.info("This is an info message")
        logging_utility.warning("This is a warning message")
        logging_utility.error("This is an error message")
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        config_path: str = "config.json",
        default_level: int = logging.INFO,
        logger_name: str = "scibud_logger",
    ):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(logger_name)
            self._setup_logging(config_path, default_level)

        if not isinstance(self.logger, logging.Logger):
            raise TypeError("LoggingUtility.logger is not an instance of logging.Logger")

    def _setup_logging(self, default_path: str, default_level: int) -> None:
        """
        Sets up logging configuration from a JSON file. If the config file is invalid or
        missing, the logger falls back to the default logging level.

        Args:
            default_path (str): Path to the JSON configuration file.
            default_level (int): Default logging level if config file fails to load.

        Raises:
            ValueError: If no logging configuration is found in the config file.
        """
        try:
            with open(default_path, "rt") as file:
                config = json.load(file)
                logging_config = config.get("logging", None)
                if logging_config:
                    logging.config.dictConfig(logging_config)
                    self.logger.info("Logging configuration loaded successfully.")
                else:
                    raise ValueError("No logging configuration found in the config file.")
        except Exception as e:
            logging.basicConfig(level=default_level)
            self.logger = logging.getLogger(__name__)
            self.logger.error("Failed to load custom logging configuration from %s: %s", default_path, e)

    def debug(self, msg: str, *args, **kwargs) -> None:
        """Logs a message with level DEBUG."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Logs a message with level INFO."""
        self.logger.info(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """Logs a message with level ERROR."""
        self.logger.error(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Logs a message with level WARNING."""
        self.logger.warning(msg, *args, **kwargs)
