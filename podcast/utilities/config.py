import json
import logging
from types import MappingProxyType
from typing import Any, Dict, Optional


class ConfigUtility:
    """
    A utility class for loading and managing configuration from a JSON file.
    """

    def __init__(
        self,
        logger: logging.Logger,
        config: Optional[Dict[str, Any]] = None,  # Clearer type hint for dictionary
        config_path: Optional[str] = "config.json",
    ) -> None:
        """
        Initialize the ConfigUtility with a logger and optional config dictionary.

        Args:
            logger (logging.Logger): Logger instance for logging information and errors.
            config (Optional[Dict[str, Any]]): Optional config dictionary to use directly.
            config_path (Optional[str]): Path to the JSON configuration file. Default is "config.json".
        """
        self.logger = logger
        self.config_path = config_path

        if config is not None and not isinstance(config, dict):
            raise TypeError("Provided config must be a dictionary.")
        self.config = MappingProxyType(config) if config is not None else self._load_config()

    def _load_config(self) -> MappingProxyType[str, Any]:
        """
        Load configuration from the JSON file and return it as an immutable MappingProxyType.

        Returns:
            MappingProxyType[str, Any]: The loaded configuration.

        Raises:
            FileNotFoundError: If the config file is not found.
            ValueError: If the config file is not valid JSON.
            TypeError: If the config file does not contain a valid dictionary.
        """
        if not self.config_path:  # Check if config_path is None or empty
            raise ValueError("Config path is not provided.")

        try:
            with open(self.config_path, "r") as file:  # Ensure config_path is a valid string
                config = json.load(file)
                if not isinstance(config, dict):
                    raise TypeError("Config file does not contain a valid dictionary.")
                self.logger.info("Config loaded successfully.")
                return MappingProxyType(config)  # Return as immutable mapping
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError:
            self.logger.error(f"Config file is not valid JSON: {self.config_path}")
            raise ValueError(f"Config file is not valid JSON: {self.config_path}")
        except Exception as e:
            self.logger.error(f"Unexpected error loading config: {e}")
            raise RuntimeError(f"Unexpected error loading config: {e}")

    def get_config(self) -> MappingProxyType[str, Any]:
        """
        Return the loaded configuration.

        Returns:
            MappingProxyType[str, Any]: The configuration as an immutable dictionary.
        """
        return self.config

    def reload_config(self) -> None:
        """
        Reload the configuration from the file.

        This method forces a reload of the configuration from the file specified by config_path.
        It updates the current config with the newly loaded values and logs the successful reload.
        """
        self.config = self._load_config()
        self.logger.info("Config reloaded successfully.")

    def get_with_default(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value with a default fallback.

        This method allows you to retrieve a value from the configuration safely. If the key
        does not exist, it returns the specified default value instead of raising an error.

        Args:
            key (str): The key to look up in the configuration.
            default (Any): The value to return if the key is not found. Defaults to None.

        Returns:
            Any: The value associated with the key, or the default value if the key is not found.

        Example:
            project_id = config_utility.get_with_default("project_id", "default_project_id")
        """
        return self.config.get(key, default)
