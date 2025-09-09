from unittest.mock import MagicMock

import pytest

from podcast.managers.audio import AudioManager
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_google_auth_service(mocker):
    """Mock GoogleAuthService."""
    return mocker.patch("podcast.managers.audio.GoogleAuthService", autospec=True)


@pytest.fixture
def mock_google_tts_service(mocker):
    """Mock GoogleTTSService."""
    return mocker.patch("podcast.managers.audio.GoogleTTSService", autospec=True)


@pytest.fixture
def mock_utilities_bundle(mocker):
    """Mock UtilitiesBundle."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    return mock_utilities


def test_generate_audio(mock_google_auth_service, mock_google_tts_service, mock_utilities_bundle):
    # Create mock instances for services
    mock_auth_service_instance = mock_google_auth_service.return_value
    mock_audio_gen_service_instance = mock_google_tts_service.return_value

    # Mock the synthesize_long_audio method to simulate a successful response
    mock_audio_gen_service_instance.synthesize_long_audio = MagicMock()

    # Initialize AudioManager with mocked utilities
    audio_manager = AudioManager(utilities=mock_utilities_bundle)

    # Define test script and file path
    test_script = "This is a test script."
    test_file_path = "gs://scibud/ai_and_biology/audio/test_output.wav"

    # Call the generate_audio method
    audio_manager.generate_audio(script=test_script, file_path=test_file_path, voice_option="mock_voice")

    # Assert that Google Cloud services were enabled
    mock_auth_service_instance.enable_gcloud_services.assert_called_once()

    # Assert that audio synthesis was called with the correct parameters
    mock_audio_gen_service_instance.synthesize_long_audio.assert_called_once_with(
        script=test_script, file_path=test_file_path, voice_option="mock_voice"
    )

    # Assert logging
    mock_utilities_bundle.logger.debug.assert_any_call("Google Cloud services enabled.")
