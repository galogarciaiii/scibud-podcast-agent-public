import hashlib
from unittest.mock import MagicMock, mock_open

import pytest

from podcast.services.google_cloud import GoogleCloudService
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities_bundle(mocker):
    """Fixture to mock the UtilitiesBundle."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    # Mock configuration
    mock_utilities.config = {"general_info": {"bucket_name": "test-bucket"}}

    return mock_utilities


@pytest.fixture
def mock_storage_client(mocker):
    """Fixture to mock Google Cloud storage client."""
    mock_client = mocker.patch("google.cloud.storage.Client", autospec=True)
    mock_bucket = mock_client.return_value.bucket.return_value
    return mock_bucket


@pytest.fixture
def google_cloud_service(mock_utilities_bundle, mock_storage_client):
    """Fixture to initialize GoogleCloudService with mock dependencies."""
    service = GoogleCloudService(path="/test/path/", utilities=mock_utilities_bundle)
    service.bucket = mock_storage_client  # Inject mock bucket for GCS operations
    return service


def test_calculate_md5(mocker, google_cloud_service):
    """Test the MD5 hash calculation of a local file."""
    mock_file_data = b"test data"
    mock_open_file = mock_open(read_data=mock_file_data)
    mocker.patch("builtins.open", mock_open_file)

    # Call the real calculate_md5 function to compute the hash of the file data
    result = google_cloud_service.calculate_md5("/path/to/file")

    # Calculate expected MD5 from the mock data
    expected_md5 = hashlib.md5(mock_file_data).hexdigest()

    # Assert that the calculated MD5 matches the expected MD5
    assert result == expected_md5


def test_download_file_no_local_file(mocker, google_cloud_service, mock_utilities_bundle):
    """Test that the file is downloaded if it does not exist locally."""
    mock_blob = google_cloud_service.bucket.blob.return_value
    mock_blob.md5_hash = "mock_md5"
    mock_blob.download_to_filename = MagicMock()

    mocker.patch("os.path.exists", return_value=False)
    google_cloud_service.download_file("local_file.txt", "cloud_file.txt")

    mock_blob.download_to_filename.assert_called_once_with("/test/path/local_file.txt")
    mock_utilities_bundle.logger.debug.assert_called_with("File downloaded successfully to %s", "local_file.txt")


def test_download_file_local_file_up_to_date(mocker, google_cloud_service, mock_utilities_bundle):
    """Test that the file is not downloaded if the local file is already up to date."""
    mock_blob = google_cloud_service.bucket.blob.return_value
    mock_blob.md5_hash = "mock_md5"

    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("podcast.services.google_cloud.GoogleCloudService.calculate_md5", return_value="mock_md5")

    google_cloud_service.download_file("local_file.txt", "cloud_file.txt")

    mock_blob.download_to_filename.assert_not_called()
    mock_utilities_bundle.logger.debug.assert_called_with("Local file 'local_file.txt' is already up to date.")


def test_upload_file(mocker, google_cloud_service, mock_utilities_bundle):
    """Test uploading a local file to Google Cloud Storage."""
    mock_blob = google_cloud_service.bucket.blob.return_value
    mock_blob.upload_from_filename = MagicMock()

    google_cloud_service.upload_file("local_file.txt", "cloud_file.txt")

    mock_blob.upload_from_filename.assert_called_once_with("/test/path/local_file.txt")
    mock_utilities_bundle.logger.info.assert_called_with("File uploaded successfully.")


def test_upload_string_to_file(mocker, google_cloud_service, mock_utilities_bundle):
    """Test uploading string content to Google Cloud Storage."""
    mock_blob = google_cloud_service.bucket.blob.return_value
    mock_blob.upload_from_string = MagicMock()

    google_cloud_service.upload_string_to_file("some content", "cloud_file.txt")

    mock_blob.upload_from_string.assert_called_once_with("some content")
    mock_utilities_bundle.logger.debug.assert_called_with(
        f"String uploaded successfully to file on Google Cloud Storage. MD5 hash: {mock_blob.md5_hash}"
    )
