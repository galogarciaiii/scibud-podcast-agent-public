from unittest.mock import MagicMock

import pytest

from podcast.services.openai_text_gen import OpenAITextGenService
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def utilities_bundle(mocker):
    """Fixture to mock the UtilitiesBundle."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger
    mock_utilities.logger = MagicMock()
    mock_utilities.config = {"models": {"gpt_model": "gpt-4"}}
    return mock_utilities


@pytest.fixture
def openai_service(utilities_bundle: UtilitiesBundle) -> OpenAITextGenService:
    # Mock the client
    mock_client = MagicMock()
    return OpenAITextGenService(client=mock_client, utilities=utilities_bundle)


def test_chat_completion_success(openai_service: OpenAITextGenService, utilities_bundle: UtilitiesBundle):
    # Mock the API response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Generated script"))]

    # Set the mock response for the client
    openai_service.client.chat.completions.create.return_value = mock_response

    # Call the chat_completion method
    system_prompt = "You are a helpful assistant."
    user_prompt = "Summarize the latest AI trends."
    result = openai_service.chat_completion(system_prompt, user_prompt)

    # Assert that the response was processed correctly
    assert result == "Generated script"
    openai_service.client.chat.completions.create.assert_called_once_with(
        model=utilities_bundle.config["models"]["gpt_model"],
        max_tokens=4096,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )


def test_chat_completion_failure(openai_service: OpenAITextGenService, utilities_bundle: UtilitiesBundle):
    # Mock an exception being raised by the API
    openai_service.client.chat.completions.create.side_effect = Exception("API failure")

    system_prompt = "You are a helpful assistant."
    user_prompt = "Summarize the latest AI trends."

    # Assert that an exception is raised
    with pytest.raises(Exception, match="Unexpected error: API failure"):
        openai_service.chat_completion(system_prompt, user_prompt)

    # Assert that the API was called once before the error occurred
    openai_service.client.chat.completions.create.assert_called_once_with(
        model=utilities_bundle.config["models"]["gpt_model"],
        max_tokens=4096,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )


def test_logging_on_api_call(openai_service: OpenAITextGenService, utilities_bundle: UtilitiesBundle):
    # Mock the API response
    mock_response = MagicMock()
    utilities_bundle.logger = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Generated script"))]

    # Set the mock response for the client
    openai_service.client.chat.completions.create.return_value = mock_response

    # Call the chat_completion method
    system_prompt = "You are a helpful assistant."
    user_prompt = "Summarize the latest AI trends."
    openai_service.chat_completion(system_prompt, user_prompt)

    # Assert that logging was called
    utilities_bundle.logger.debug.assert_any_call("API call to OpenAI completed successfully.")
    utilities_bundle.logger.debug.assert_any_call("Summary extracted from the API response.")
