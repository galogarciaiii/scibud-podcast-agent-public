import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from podcast.services.google_auth import GoogleAuthService
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities(mocker):
    # Create a standard mock for the UtilitiesBundle
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock the logger
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    # Mock the time utility and its methods
    mock_time = mocker.Mock()
    mock_utilities.time = mock_time

    # Mock the config utility
    mock_utilities.config = {"general_info": {"tool": "MyTestTool", "email": "test@example.com"}}

    return mock_utilities


# Test case for the initialization of GoogleAuthService
@patch.dict(os.environ, {}, clear=True)
def test_initialization_with_key(mock_utilities):
    service = GoogleAuthService(utilities=mock_utilities, key="dummy_key")
    assert service.key == "dummy_key"
    mock_utilities.logger.debug.assert_called_with("Google API key set successfully.")


@patch.dict(os.environ, {}, clear=True)
@patch("podcast.services.google_auth.load_dotenv")
def test_initialization_without_key(mock_load_dotenv, mock_utilities):
    with patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "sci-bud-c962e85010ff.json"}):
        service = GoogleAuthService(utilities=mock_utilities)
        assert service.key == "sci-bud-c962e85010ff.json"
        mock_utilities.logger.debug.assert_any_call("Google API key set successfully.")


# Test case for get_google_api_key method
@patch.dict(os.environ, {}, clear=True)
@patch("podcast.services.google_auth.load_dotenv")
def test_get_google_api_key(mock_load_dotenv, mock_utilities):
    with patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "sci-bud-c962e85010ff.json"}):
        service = GoogleAuthService(utilities=mock_utilities)
        key = service.get_google_api_key()
        assert key == "sci-bud-c962e85010ff.json"
        mock_utilities.logger.debug.assert_called_with("Google API key retrieved successfully.")


# Test case for enable_gcloud_services method
@patch("podcast.services.google_auth.subprocess.run")
def test_enable_gcloud_services(mock_subprocess_run, mock_utilities):
    mock_result = MagicMock()
    mock_result.stdout = "Service enabled successfully."
    mock_subprocess_run.return_value = mock_result

    service = GoogleAuthService(utilities=mock_utilities)
    service.enable_gcloud_services()

    mock_subprocess_run.assert_called_once_with(
        ["gcloud", "services", "enable", "texttospeech.googleapis.com"],
        check=True,
        capture_output=True,
        text=True,
    )
    mock_utilities.logger.debug.assert_called_with(
        "Service enabled successfully. Output: Service enabled successfully."
    )


@patch(
    "podcast.services.google_auth.subprocess.run",
    side_effect=subprocess.CalledProcessError(1, "cmd", "error output"),
)
def test_enable_gcloud_services_subprocess_error(mock_subprocess_run, mock_utilities):
    service = GoogleAuthService(utilities=mock_utilities)
    with pytest.raises(RuntimeError, match="Failed to enable Google Cloud service."):
        service.enable_gcloud_services()
    mock_utilities.logger.error.assert_called_with(
        "Failed to enable service: Command 'cmd' returned non-zero exit status 1.. Output: error output, Error: None"
    )


@patch("podcast.services.google_auth.subprocess.run", side_effect=Exception("Unexpected error"))
def test_enable_gcloud_services_generic_error(mock_subprocess_run, mock_utilities):
    service = GoogleAuthService(utilities=mock_utilities)
    with pytest.raises(RuntimeError, match="An unexpected error occurred while enabling Google Cloud service."):
        service.enable_gcloud_services()
    mock_utilities.logger.error.assert_called_with("An unexpected error occurred: Unexpected error")
