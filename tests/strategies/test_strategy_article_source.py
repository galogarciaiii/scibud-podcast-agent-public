import logging
from datetime import datetime
from typing import List
from unittest.mock import Mock

import pytest

from podcast.formats.article import ArticleInfo
from podcast.formats.query import QueryParams
from podcast.strategies.article_source import ArticleSourceStrategy
from podcast.utilities.bundle import UtilitiesBundle


# Mock implementation of the ArticleSourceStrategy to test the base class behavior
class MockArticleSourceStrategy(ArticleSourceStrategy):
    def fetch_articles(self) -> List[ArticleInfo]:
        return [
            {
                "title": "Sample Article",
                "authors": ["Author 1", "Author 2"],
                "doi": "10.1234/example.doi",
                "abstract": "This is a sample abstract.",
                "full_text": "Full article text.",
                "submitted_date": str(datetime(2020, 1, 1)),
                "url": "https://example.com/article",
                "full_text_locator": "https://example.com/fulltext",
                "strategy": "MockStrategy",
                "score": 8,
                "score_justification": "Well-written article.",
                "score_generated": False,
                "full_text_available": True,
                "described_in_podcast": False,
            }
        ]

    def fetch_full_text(self, full_text_locator: str) -> str:
        return "Full text of the article."


@pytest.fixture
def mock_logger():
    return logging.getLogger("test_logger")


@pytest.fixture
def mock_time_utility():
    return Mock()


@pytest.fixture
def mock_config():
    return {"general_info": {"bucket_name": "test-bucket"}}


@pytest.fixture
def mock_utilities_bundle(mock_logger, mock_config, mock_time_utility):
    # Mock the UtilitiesBundle
    bundle = Mock(spec=UtilitiesBundle)
    bundle.logger = mock_logger
    bundle.config = mock_config
    bundle.time = mock_time_utility
    return bundle


@pytest.fixture
def mock_query_params():
    return QueryParams(
        query="test query",
        min_date=datetime(2020, 1, 1),
        max_date=datetime(2021, 1, 1),
        max_results=10,
    )


@pytest.fixture
def strategy(mock_utilities_bundle, mock_query_params):
    # Mock the required attributes and return the mock strategy
    return MockArticleSourceStrategy(
        utilities=mock_utilities_bundle,
        path="test/path",
        query_params=mock_query_params,
    )


def test_initialization(strategy):
    """Test that the strategy initializes correctly with the expected attributes."""
    assert strategy.utilities.logger.name == "test_logger"
    assert strategy.utilities.config["general_info"]["bucket_name"] == "test-bucket"
    assert strategy.utilities.time == strategy.utilities.time  # Ensuring the time utility was passed correctly
    assert strategy.query_params.query == "test query"
    assert strategy.query_params.min_date == datetime(2020, 1, 1)
    assert strategy.query_params.max_date == datetime(2021, 1, 1)
    assert strategy.query_params.max_results == 10
    assert strategy.path == "test/path"


def test_fetch_articles(strategy):
    """Test the fetch_articles method of the mock implementation."""
    articles = strategy.fetch_articles()
    assert len(articles) == 1
    assert articles[0]["title"] == "Sample Article"


def test_fetch_full_text(strategy):
    """Test the fetch_full_text method of the mock implementation."""
    full_text = strategy.fetch_full_text({"id": "123"})
    assert full_text == "Full text of the article."


def test_bucket_name(strategy):
    """Test that the bucket name is being set correctly from config."""
    assert strategy.utilities.config["general_info"]["bucket_name"] == "test-bucket"
