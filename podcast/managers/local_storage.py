import os

from podcast.utilities.bundle import UtilitiesBundle


class LocalStorageManager:
    """
    Manages local file operations such as file removal.

    Attributes:
        utilities (UtilitiesBundle): A bundle of utility instances including logging and config utilities.
    """

    def __init__(self, utilities: UtilitiesBundle) -> None:
        """
        Initializes the LocalStorageManager with utility bundle.

        Args:
            utilities (UtilitiesBundle): A bundle of utility instances including logging and config utilities.
        """
        self.utilities: UtilitiesBundle = utilities

    def remove_local_file(self, local_file_name: str) -> None:
        """
        Removes a local file from the system.

        Args:
            local_file_name (str): The name of the local file to be removed.

        Raises:
            FileNotFoundError: If the file does not exist.
            OSError: If there is an error while removing the file.
        """
        try:
            self.utilities.logger.debug(f"Attempting to remove file: {local_file_name}")
            os.remove(local_file_name)
            self.utilities.logger.debug(f"File successfully removed: {local_file_name}")
        except FileNotFoundError:
            self.utilities.logger.error(f"File not found: {local_file_name}")
            raise
        except OSError as e:
            self.utilities.logger.error(f"Error removing file {local_file_name}: {e}")
            raise
