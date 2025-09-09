from datetime import datetime
from typing import List
from unittest.mock import MagicMock, call

import pytest

from podcast.formats.query import QueryParams
from podcast.services.pubmed import PubmedService
from podcast.strategies.article_source import ArticleInfo
from podcast.strategies.pubmed import PubmedStrategy
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_logger() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_config() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_time() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_utilities_bundle(mock_logger, mock_config, mock_time) -> UtilitiesBundle:
    bundle = MagicMock(spec=UtilitiesBundle)
    bundle.logger = mock_logger
    bundle.config = mock_config
    bundle.time = mock_time
    return bundle


@pytest.fixture
def mock_query_params() -> QueryParams:
    return QueryParams(query="genomics", min_date=datetime(2023, 1, 1), max_date=datetime(2023, 12, 31), max_results=10)


@pytest.fixture
def mock_pubmed_service() -> MagicMock:
    return MagicMock(spec=PubmedService)


@pytest.fixture
def pubmed_strategy(
    mock_utilities_bundle: UtilitiesBundle, mock_query_params: QueryParams, mock_pubmed_service: MagicMock
) -> PubmedStrategy:
    # Instantiate the PubmedStrategy with mock utilities and query params
    strategy = PubmedStrategy(
        utilities=mock_utilities_bundle,
        query_params=mock_query_params,
        path="some_path/",
    )
    strategy.pubmed_service = mock_pubmed_service  # Inject the mock PubmedService
    return strategy


def test_pubmed_strategy_initialization(pubmed_strategy: PubmedStrategy, mock_logger: MagicMock) -> None:
    assert pubmed_strategy.query_params.query == "genomics"
    assert pubmed_strategy.query_params.min_date == datetime(2023, 1, 1)
    assert pubmed_strategy.query_params.max_date == datetime(2023, 12, 31)
    assert pubmed_strategy.query_params.max_results == 10
    assert pubmed_strategy.pubmed_service is not None

    # Check that both log messages were called
    expected_calls = [
        call("Pubmed strategy initiated"),
    ]
    mock_logger.info.assert_has_calls(expected_calls, any_order=False)


def test_default_path(pubmed_strategy: PubmedStrategy) -> None:
    assert pubmed_strategy.path == "some_path/"


def test_fetch_articles(pubmed_strategy: PubmedStrategy, mock_pubmed_service: MagicMock) -> None:
    # Mock the return value of pubmed_service.fetch_articles
    mock_articles: List[ArticleInfo] = [
        {
            "title": "Genomics Study",
            "authors": ["A. Author"],
            "doi": "10.1234/pubmed.12345678",
            "abstract": "This paper discusses genomics.",
            "full_text": str(None),
            "submitted_date": "2024-01-01",
            "url": "https://pubmed.ncbi.nlm.nih.gov/12345678",
            "full_text_locator": "https://pubmed.ncbi.nlm.nih.gov/12345678/full-text",
            "strategy": "PubmedStrategy",
            "score": int(-1),
            "score_justification": str(None),
            "score_generated": False,
            "full_text_available": True,
            "described_in_podcast": False,
        }
    ]

    mock_pubmed_service.fetch_articles.return_value = mock_articles

    # Call fetch_articles and assert the result
    articles = pubmed_strategy.fetch_articles()

    assert articles == mock_articles
    assert isinstance(pubmed_strategy.pubmed_service.fetch_articles, MagicMock)
    pubmed_strategy.pubmed_service.fetch_articles.assert_called_once()


def test_fetch_full_text(pubmed_strategy: PubmedStrategy, mock_pubmed_service: MagicMock) -> None:
    # Mock the return value of pubmed_service.fetch_full_text
    mock_full_text = "This is the full text of the article."
    mock_pubmed_service.fetch_full_text.return_value = mock_full_text

    # Prepare the full_text_locator argument
    full_text_locator = "https://pubmed.ncbi.nlm.nih.gov/12345678/full-text"

    # Call fetch_full_text and assert the result
    full_text = pubmed_strategy.fetch_full_text(full_text_locator)
    assert full_text == mock_full_text
    assert isinstance(pubmed_strategy.pubmed_service.fetch_full_text, MagicMock)
    pubmed_strategy.pubmed_service.fetch_full_text.assert_called_once_with(full_text_locator=full_text_locator)
