from unittest.mock import MagicMock, patch

import pytest

from podcast.formats.article import ArticleInfo
from podcast.helpers.prompt import PromptHelper
from podcast.helpers.response import ResponseHelper
from podcast.managers.text_gen import TextGenerationManager
from podcast.services.openai_text_gen import OpenAITextGenService
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities_bundle(mocker):
    """Fixture to mock the UtilitiesBundle."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger
    mock_utilities.logger = MagicMock()
    mock_utilities.config = {"models": {"gpt_model": "gpt-4"}}
    return mock_utilities


@pytest.fixture
def mock_article_info() -> ArticleInfo:
    # Mock ArticleInfo with sample data
    return {
        "title": "Sample Article",
        "authors": ["Author 1", "Author 2"],
        "doi": "10.1234/sample.doi",
        "abstract": "This is a sample abstract.",
        "full_text": "Full text of the article",
        "submitted_date": "2024-01-01",
        "url": "http://sample.url",
        "full_text_locator": "http://fulltext.sample.url",
        "strategy": "SampleStrategy",
        "score": None,
        "score_justification": "",
        "score_generated": False,
        "full_text_available": True,
        "described_in_podcast": False,
    }


@pytest.fixture
def text_gen_manager(mock_utilities_bundle: UtilitiesBundle) -> TextGenerationManager:
    # Create a mocked TextGenerationManager with mocked helpers and services
    manager = TextGenerationManager(path="mock_path", utilities=mock_utilities_bundle)

    # Mock the PromptHelper and ResponseHelper methods
    manager.prompt_helper = MagicMock(spec=PromptHelper)
    manager.response_helper = MagicMock(spec=ResponseHelper)
    manager.text_gen_service = MagicMock(spec=OpenAITextGenService)

    return manager


def test_generate_script(text_gen_manager: TextGenerationManager, mock_article_info: ArticleInfo):
    # Patch the methods in the context of this test
    with patch.object(
        text_gen_manager.prompt_helper, "assemble_script_prompts", return_value=("system prompt", "user prompt")
    ) as mock_assemble_script_prompts, patch.object(
        text_gen_manager.text_gen_service, "chat_completion", return_value="Generated script"
    ) as mock_chat_completion, patch.object(
        text_gen_manager.response_helper, "remove_special_characters", return_value="Cleaned script"
    ) as mock_remove_special_characters:

        # Call the method
        result: str = text_gen_manager.generate_script(article=mock_article_info, persona="persona")

        # Assertions
        mock_assemble_script_prompts.assert_called_once_with(article=mock_article_info, persona="persona")
        mock_chat_completion.assert_called_once_with(system_prompt="system prompt", user_prompt="user prompt")
        mock_remove_special_characters.assert_called_once_with(text="Generated script")

        assert result == "Cleaned script"


def test_generate_description(text_gen_manager: TextGenerationManager):
    # Patch the methods in the context of this test
    with patch.object(
        text_gen_manager.prompt_helper, "assemble_description_prompts", return_value=("system prompt", "user prompt")
    ) as mock_assemble_description_prompts, patch.object(
        text_gen_manager.text_gen_service, "chat_completion", return_value="Generated description"
    ) as mock_chat_completion:

        # Call the method
        result: str = text_gen_manager.generate_description(script="Sample script")

        # Assertions
        mock_assemble_description_prompts.assert_called_once_with(script="Sample script")
        mock_chat_completion.assert_called_once_with(system_prompt="system prompt", user_prompt="user prompt")

        assert result == "Generated description"


def test_generate_title(text_gen_manager: TextGenerationManager):
    # Patch the methods in the context of this test
    with patch.object(
        text_gen_manager.prompt_helper, "assemble_title_prompts", return_value=("system prompt", "user prompt")
    ) as mock_assemble_title_prompts, patch.object(
        text_gen_manager.text_gen_service, "chat_completion", return_value="Generated title"
    ) as mock_chat_completion, patch.object(
        text_gen_manager.response_helper, "remove_quotes_from_title", return_value="Cleaned title"
    ) as mock_remove_quotes_from_title:

        # Call the method
        result: str = text_gen_manager.generate_title(script="Sample script")

        # Assertions
        mock_assemble_title_prompts.assert_called_once_with(script="Sample script")
        mock_chat_completion.assert_called_once_with(system_prompt="system prompt", user_prompt="user prompt")
        mock_remove_quotes_from_title.assert_called_once_with(title="Generated title")

        assert result == "Cleaned title"


def test_generate_score(text_gen_manager: TextGenerationManager, mock_article_info: ArticleInfo):
    # Patch the methods in the context of this test
    with patch.object(
        text_gen_manager.prompt_helper, "assemble_scoring_prompts", return_value=("system prompt", "user prompt")
    ) as mock_assemble_scoring_prompts, patch.object(
        text_gen_manager.text_gen_service, "chat_completion", return_value="Score: 8, Justification: Thorough review"
    ) as mock_chat_completion, patch.object(
        text_gen_manager.response_helper, "parse_score_and_justification", return_value=(8, "Thorough review")
    ) as mock_parse_score_and_justification:

        # Call the method
        score: int
        justification: str
        score, justification = text_gen_manager.generate_score(article=mock_article_info)

        # Assertions
        mock_assemble_scoring_prompts.assert_called_once_with(article=mock_article_info)
        mock_chat_completion.assert_called_once_with(system_prompt="system prompt", user_prompt="user prompt")
        mock_parse_score_and_justification.assert_called_once_with(response="Score: 8, Justification: Thorough review")

        assert score == 8
        assert justification == "Thorough review"
