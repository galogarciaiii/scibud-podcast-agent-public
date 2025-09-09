from unittest.mock import MagicMock

import pytest

from podcast.assistants.retrieval import RetrievalAssistant
from podcast.utilities.bundle import UtilitiesBundle


# Fixture to provide a mock UtilitiesBundle
@pytest.fixture
def mock_utilities_bundle(mocker):
    """Creates a mock UtilitiesBundle, including logger and other utilities."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger within UtilitiesBundle
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    return mock_utilities


# Fixture to provide a mock strategy
@pytest.fixture
def mock_strategy():
    """Creates a mock ArticleSourceStrategy."""
    return MagicMock()


# Test case for fetching articles
def test_fetch_articles(mock_strategy, mock_utilities_bundle):
    """Tests the fetch_articles method of RetrievalAssistant."""
    retrieval_assistant = RetrievalAssistant(strategy=mock_strategy, utilities=mock_utilities_bundle)

    # Mock articles to be returned by the strategy
    mock_articles = [
        {"title": "Article 1", "abstract": "Abstract 1"},
        {"title": "Article 2", "abstract": "Abstract 2"},
    ]

    mock_strategy.fetch_articles.return_value = mock_articles

    # Call the fetch_articles method
    articles = retrieval_assistant.fetch_articles()

    # Assertions
    assert articles == mock_articles
    mock_strategy.fetch_articles.assert_called_once_with()


# Test case for fetching full text
def test_fetch_full_text(mock_strategy, mock_utilities_bundle):
    """Tests the fetch_full_text method of RetrievalAssistant."""
    retrieval_assistant = RetrievalAssistant(strategy=mock_strategy, utilities=mock_utilities_bundle)

    # Mock the full text to be returned by the strategy
    full_text_locator = "http://example.com/full_text"
    mock_full_text = "This is the full text of the article."

    mock_strategy.fetch_full_text.return_value = mock_full_text

    # Call the fetch_full_text method
    full_text = retrieval_assistant.fetch_full_text(full_text_locator=full_text_locator)

    # Assertions
    assert full_text == mock_full_text
    mock_strategy.fetch_full_text.assert_called_once_with(full_text_locator=full_text_locator)
