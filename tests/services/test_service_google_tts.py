from unittest import mock

import pytest
from google.api_core.operation import Operation
from google.cloud import texttospeech

from podcast.services.google_tts import GoogleTTSService
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities_bundle(mocker):
    """Fixture to mock the UtilitiesBundle."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    # Mock configuration
    mock_utilities.config = {
        "google_tts": {
            "voice_options": ["en-US-Wavenet-D", "en-US-Wavenet-E"],
            "language": "en-US",
        },
        "general_info": {"project_path": "projects/your-project-id"},
    }

    return mock_utilities


@pytest.fixture
def service(mock_utilities_bundle):
    """Fixture to initialize GoogleTTSService with mock dependencies."""
    return GoogleTTSService(utilities=mock_utilities_bundle)


@pytest.fixture
def mock_tts_client():
    """Fixture to mock the TextToSpeechLongAudioSynthesizeClient."""
    return mock.create_autospec(texttospeech.TextToSpeechLongAudioSynthesizeClient, instance=True)


@pytest.fixture
def mock_operation():
    """Fixture to mock the operation object."""
    mock_op = mock.create_autospec(Operation, instance=True)
    mock_op.result.return_value = "synthesis result"
    mock_op.done.return_value = True
    return mock_op


def test_synthesize_long_audio_success(service, mock_tts_client, mock_operation, mock_utilities_bundle):
    """Test successful audio synthesis."""
    with mock.patch(
        "google.cloud.texttospeech.TextToSpeechLongAudioSynthesizeClient",
        return_value=mock_tts_client,
    ):
        mock_tts_client.synthesize_long_audio.return_value = mock_operation

        script = "This is a test script."
        file_path = "gs://your-bucket/output.wav"
        response = service.synthesize_long_audio(script=script, file_path=file_path, voice_option="en-US-Wavenet-D")

        mock_tts_client.synthesize_long_audio.assert_called_once()
        mock_operation.result.assert_called_once_with(timeout=300)
        assert response == "synthesis result"
        mock_utilities_bundle.logger.info.assert_any_call("Selected Option: %s", mock.ANY)
        mock_utilities_bundle.logger.debug.assert_any_call("Long audio synthesis requested.")
        mock_utilities_bundle.logger.debug.assert_any_call("Audio synthesis completed successfully.")


def test_synthesize_long_audio_timeout(service, mock_tts_client, mock_operation, mock_utilities_bundle):
    """Test audio synthesis timing out."""
    with mock.patch(
        "google.cloud.texttospeech.TextToSpeechLongAudioSynthesizeClient",
        return_value=mock_tts_client,
    ):
        mock_operation.done.return_value = False
        mock_tts_client.synthesize_long_audio.return_value = mock_operation

        script = "This is a test script."
        file_path = "gs://your-bucket/output.wav"
        response = service.synthesize_long_audio(script=script, file_path=file_path, voice_option="en-US-Wavenet-D")

        mock_tts_client.synthesize_long_audio.assert_called_once()
        mock_operation.result.assert_called_once_with(timeout=300)
        assert response is None
        mock_utilities_bundle.logger.warning.assert_called_once_with(
            "The audio synthesis operation did not complete within the timeout."
        )


def test_synthesize_long_audio_exception(service, mock_tts_client, mock_utilities_bundle):
    """Test exception handling during audio synthesis."""
    with mock.patch(
        "google.cloud.texttospeech.TextToSpeechLongAudioSynthesizeClient",
        return_value=mock_tts_client,
    ):
        mock_tts_client.synthesize_long_audio.side_effect = Exception("Test exception")

        script = "This is a test script."
        file_path = "gs://your-bucket/output.wav"

        with pytest.raises(RuntimeError, match="Unexpected error: Test exception"):
            service.synthesize_long_audio(script=script, file_path=file_path, voice_option="en-US-Wavenet-D")

        mock_tts_client.synthesize_long_audio.assert_called_once()
        mock_utilities_bundle.logger.error.assert_called_once_with("An unexpected error occurred: %s", "Test exception")
