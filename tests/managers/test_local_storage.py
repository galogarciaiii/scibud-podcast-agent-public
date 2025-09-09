from unittest.mock import patch

import pytest

from podcast.managers.local_storage import LocalStorageManager
from podcast.utilities.bundle import UtilitiesBundle


# Fixture to provide a mock UtilitiesBundle
@pytest.fixture
def mock_utilities_bundle(mocker):
    """Fixture to mock UtilitiesBundle, including logger."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger inside utilities bundle
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    return mock_utilities


def test_remove_local_file(mock_utilities_bundle):
    # Initialize LocalStorageManager with the mocked utilities bundle
    local_storage_manager = LocalStorageManager(utilities=mock_utilities_bundle)

    local_file_name = "test_file.txt"

    # Patch os.remove to avoid actual file system modification
    with patch("os.remove") as mock_remove:
        local_storage_manager.remove_local_file(local_file_name)

        # Assert that os.remove was called with the correct file name
        mock_remove.assert_called_once_with(local_file_name)

        # Assert that the logger logged the correct messages
        mock_utilities_bundle.logger.debug.assert_any_call(f"Attempting to remove file: {local_file_name}")
        mock_utilities_bundle.logger.debug.assert_any_call(f"File successfully removed: {local_file_name}")

        # Assert that no error was logged
        mock_utilities_bundle.logger.error.assert_not_called()


def test_remove_local_file_file_not_found(mock_utilities_bundle):
    # Initialize LocalStorageManager with the mocked utilities bundle
    local_storage_manager = LocalStorageManager(utilities=mock_utilities_bundle)

    local_file_name = "test_file.txt"

    # Patch os.remove to raise a FileNotFoundError
    with patch("os.remove", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            local_storage_manager.remove_local_file(local_file_name)

        # Assert that the logger logged the file not found error
        mock_utilities_bundle.logger.error.assert_called_once_with(f"File not found: {local_file_name}")


def test_remove_local_file_os_error(mock_utilities_bundle):
    # Initialize LocalStorageManager with the mocked utilities bundle
    local_storage_manager = LocalStorageManager(utilities=mock_utilities_bundle)

    local_file_name = "test_file.txt"
    os_error = OSError("Test OS error")

    # Patch os.remove to raise an OSError
    with patch("os.remove", side_effect=os_error):
        with pytest.raises(OSError):
            local_storage_manager.remove_local_file(local_file_name)

        # Assert that the logger logged the correct error message
        mock_utilities_bundle.logger.error.assert_called_once_with(f"Error removing file {local_file_name}: {os_error}")


if __name__ == "__main__":
    pytest.main()
