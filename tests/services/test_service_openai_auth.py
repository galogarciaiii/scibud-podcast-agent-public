import os
from unittest import mock

import pytest

from podcast.services.openai_auth import OpenAIAuthService
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities_bundle(mocker):
    """Fixture to mock the UtilitiesBundle."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    return mock_utilities


@pytest.fixture
def mock_env_key():
    return "test_env_key"


@pytest.fixture
def service_with_env_key(mock_utilities_bundle, mock_env_key):
    with mock.patch.dict(os.environ, {"OPENAI_API_KEY": mock_env_key}):
        return OpenAIAuthService(utilities=mock_utilities_bundle)


def test_init_with_key(mock_utilities_bundle):
    key = "test_key"
    service = OpenAIAuthService(utilities=mock_utilities_bundle, key=key)

    assert service.key == key
    mock_utilities_bundle.logger.debug.assert_called_once_with("OpenAI API key set successfully.")
    assert hasattr(service, "client")
    assert service.client is not None


def test_init_without_key(mock_utilities_bundle, service_with_env_key):
    service = service_with_env_key

    assert service.key == "test_env_key"
    mock_utilities_bundle.logger.debug.assert_any_call("OpenAI API key set successfully.")
    mock_utilities_bundle.logger.debug.assert_any_call("OpenAI API key retrieved successfully.")
    assert hasattr(service, "client")
    assert service.client is not None


def test_init_without_key_and_env_var(mock_utilities_bundle):
    # Mock load_dotenv, os.getenv, and clear the environment
    with mock.patch("dotenv.load_dotenv"), mock.patch("os.getenv", return_value=None), mock.patch.dict(
        os.environ, {}, clear=True
    ):
        service = OpenAIAuthService(utilities=mock_utilities_bundle)

    assert service.key is None
    mock_utilities_bundle.logger.warning.assert_has_calls(
        [
            mock.call("Failed to retrieve the OpenAI API key. It may not be set."),
            mock.call("OpenAI API key was not set. OpenAI client not created"),
        ]
    )
    with pytest.raises(AttributeError):
        _ = service.client


def test_get_openai_api_key_success(mock_utilities_bundle, mock_env_key):
    with mock.patch.dict(os.environ, {"OPENAI_API_KEY": mock_env_key}):
        service = OpenAIAuthService(utilities=mock_utilities_bundle)
        key = service.get_api_key()

    assert key == mock_env_key
    mock_utilities_bundle.logger.debug.assert_called_with("OpenAI API key retrieved successfully.")


def test_get_openai_api_key_failure(mock_utilities_bundle):
    # Mock load_dotenv and os.getenv to ensure no key is retrieved
    with mock.patch("dotenv.load_dotenv"), mock.patch("os.getenv", return_value=None), mock.patch.dict(
        os.environ, {}, clear=True
    ):
        service = OpenAIAuthService(utilities=mock_utilities_bundle)
        key = service.get_api_key()

    assert key is None
    mock_utilities_bundle.logger.warning.assert_has_calls(
        [
            mock.call("Failed to retrieve the OpenAI API key. It may not be set."),
            mock.call("OpenAI API key was not set. OpenAI client not created"),
            mock.call("Failed to retrieve the OpenAI API key. It may not be set."),
        ],
        any_order=True,
    )


def test_get_openai_api_key_exception(mock_utilities_bundle):
    service = OpenAIAuthService(utilities=mock_utilities_bundle, key="test_key")

    with mock.patch("os.getenv", side_effect=Exception("Test exception")):
        with pytest.raises(RuntimeError, match="Unexpected error: Test exception"):
            service.get_api_key()

    mock_utilities_bundle.logger.error.assert_called_once_with("An unexpected error occurred: %s", "Test exception")
