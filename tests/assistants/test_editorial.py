from unittest.mock import Mock, patch

import pytest

from podcast.assistants.editorial import EditorialAssistant
from podcast.managers.text_gen import TextGenerationManager
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities():
    utilities = Mock(spec=UtilitiesBundle)
    utilities.config = {"google_tts": {"voice_options": [{"persona1": "voice1"}, {"persona2": "voice2"}]}}
    utilities.logger = Mock()
    utilities.time = Mock()  # Add this line to mock the time attribute
    utilities.time.current_time = Mock()
    utilities.time.convert_for_apple = Mock(return_value="2025-02-11T00:00:00Z")
    return utilities


@pytest.fixture
def mock_text_generation_manager():
    manager = Mock(spec=TextGenerationManager)
    manager.generate_script = Mock(return_value="Generated script")
    manager.generate_description = Mock(return_value="Generated description")
    manager.generate_title = Mock(return_value="Generated title")
    manager.generate_score = Mock(return_value=(85, "Justification for score"))
    return manager


@pytest.fixture
def editorial_assistant(mock_utilities, mock_text_generation_manager):
    with patch("podcast.assistants.editorial.TextGenerationManager", return_value=mock_text_generation_manager):
        return EditorialAssistant(path="/some/path", utilities=mock_utilities)


def test_generate_episode_text(editorial_assistant, mock_utilities):
    article = {"url": "http://example.com", "title": "Example Article"}
    season_number = 1
    episode_number = 1

    episode_info = editorial_assistant.generate_episode_text(article, season_number, episode_number)

    assert episode_info["title"] == "Generated title"
    assert episode_info["description"] == "Generated description"
    assert episode_info["citations"] == "http://example.com"
    assert episode_info["persona"] in ["persona1", "persona2"]
    assert episode_info["voice"] in ["voice1", "voice2"]
    assert episode_info["script"] == "Generated script"
    assert episode_info["season"] == season_number
    assert episode_info["episode"] == episode_number
    assert episode_info["pub_date"] == "2025-02-11T00:00:00Z"


def test_generate_episode_text_exception(editorial_assistant, mock_utilities):
    article = {"url": "http://example.com", "title": "Example Article"}
    season_number = 1
    episode_number = 1

    editorial_assistant.text_generation_manager.generate_script.side_effect = Exception("Test exception")

    with pytest.raises(Exception, match="Test exception"):
        editorial_assistant.generate_episode_text(article, season_number, episode_number)

    mock_utilities.logger.error.assert_called_with(
        "An error occurred while generating the next episode info: Test exception"
    )


def test_score_article(editorial_assistant, mock_utilities):
    article = {"url": "http://example.com", "title": "Example Article"}

    score, justification = editorial_assistant.score_article(article)

    assert score == 85
    assert justification == "Justification for score"
    mock_utilities.logger.info.assert_called_with("Article 'Example Article' ranked with a score of 85.")


def test_score_article_exception(editorial_assistant, mock_utilities):
    article = {"url": "http://example.com", "title": "Example Article"}

    editorial_assistant.text_generation_manager.generate_score.side_effect = Exception("Test exception")

    with pytest.raises(Exception, match="Test exception"):
        editorial_assistant.score_article(article)

    mock_utilities.logger.error.assert_called_with("Failed to rank article 'Example Article': Test exception")
