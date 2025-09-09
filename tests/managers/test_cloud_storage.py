from unittest.mock import MagicMock

import pytest

from podcast.managers.cloud_storage import CloudStorageManager
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_google_auth_service(mocker):
    """Mock GoogleAuthService."""
    return mocker.patch("podcast.managers.cloud_storage.GoogleAuthService", autospec=True)


@pytest.fixture
def mock_google_cloud_service(mocker):
    """Mock GoogleCloudService."""
    return mocker.patch("podcast.managers.cloud_storage.GoogleCloudService", autospec=True)


@pytest.fixture
def mock_utilities_bundle(mocker):
    """Mock UtilitiesBundle."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    return mock_utilities


def test_cloud_storage_manager_initialization(
    mock_google_auth_service, mock_google_cloud_service, mock_utilities_bundle
):
    # Create mock instances
    mock_auth_service_instance = mock_google_auth_service.return_value
    mock_cloud_service_instance = mock_google_cloud_service.return_value

    # Mock the API key
    mock_auth_service_instance.key = "mock_api_key"

    # Create an instance of CloudStorageManager
    manager = CloudStorageManager(path="/test/path/", utilities=mock_utilities_bundle)

    # Assertions
    assert manager.key == "mock_api_key"
    mock_utilities_bundle.logger.info.assert_called_once_with("Cloud API key set successfully.")

    # Ensure the cloud service is initialized with the correct path and utilities
    mock_google_cloud_service.assert_called_once_with(path="/test/path/", utilities=mock_utilities_bundle)


def test_download_file(mock_google_cloud_service, mock_utilities_bundle):
    # Create mock instance
    mock_cloud_service_instance = mock_google_cloud_service.return_value

    # Create an instance of CloudStorageManager
    manager = CloudStorageManager(path="/test/path/", utilities=mock_utilities_bundle)

    # Define test file names
    local_file_name = "local_file.txt"
    cloud_file_name = "cloud_file.txt"

    # Call the method to test
    manager.download_file(local_file_name, cloud_file_name)

    # Assert that the download_file method was called with the correct parameters
    mock_cloud_service_instance.download_file.assert_called_once_with(local_file_name, cloud_file_name)


def test_upload_string_to_file(mock_google_cloud_service, mock_utilities_bundle):
    # Create mock instance
    mock_cloud_service_instance = mock_google_cloud_service.return_value

    # Create an instance of CloudStorageManager
    manager = CloudStorageManager(path="/test/path/", utilities=mock_utilities_bundle)

    # Define test string content and file name
    string_content = "This is a test string."
    cloud_file_name = "cloud_file.txt"

    # Call the method to test
    manager.upload_string_to_file(string_content, cloud_file_name)

    # Assert that the upload_string_to_file method was called with the correct parameters
    mock_cloud_service_instance.upload_string_to_file.assert_called_once_with(
        string_content=string_content, cloud_file_name=cloud_file_name
    )


def test_upload_file(mock_google_cloud_service, mock_utilities_bundle):
    # Create mock instance
    mock_cloud_service_instance = mock_google_cloud_service.return_value

    # Create an instance of CloudStorageManager
    manager = CloudStorageManager(path="/test/path/", utilities=mock_utilities_bundle)

    # Define test file names
    local_file_name = "local_file.txt"
    cloud_file_name = "cloud_file.txt"

    # Call the method to test
    manager.upload_file(local_file_name, cloud_file_name)

    # Assert that the upload_file method was called with the correct parameters
    mock_cloud_service_instance.upload_file.assert_called_once_with(local_file_name, cloud_file_name)
