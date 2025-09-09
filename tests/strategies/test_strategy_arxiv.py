from datetime import datetime
from typing import List
from unittest.mock import MagicMock

import pytest

from podcast.formats.query import QueryParams
from podcast.services.arxiv import ArxivService
from podcast.strategies.article_source import ArticleInfo
from podcast.strategies.arxiv import ArxivStrategy
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
    return QueryParams(
        query="quantum physics", min_date=datetime(2023, 1, 1), max_date=datetime(2023, 12, 31), max_results=5
    )


@pytest.fixture
def mock_arxiv_service() -> MagicMock:
    return MagicMock(spec=ArxivService)


@pytest.fixture
def arxiv_strategy(
    mock_utilities_bundle: UtilitiesBundle,
    mock_query_params: QueryParams,
    mock_arxiv_service: MagicMock,  # Pass the fixture as an argument
) -> ArxivStrategy:
    path = "some_path/"
    strategy = ArxivStrategy(
        utilities=mock_utilities_bundle,
        query_params=mock_query_params,
        path=path,
    )
    strategy.arxiv_service = mock_arxiv_service  # Use the mock_arxiv_service provided by pytest
    return strategy


def test_arxiv_strategy_initialization(arxiv_strategy: ArxivStrategy, mock_utilities_bundle: UtilitiesBundle) -> None:
    assert arxiv_strategy.query_params.query == "quantum physics"
    assert arxiv_strategy.query_params.min_date == datetime(2023, 1, 1)
    assert arxiv_strategy.query_params.max_date == datetime(2023, 12, 31)
    assert arxiv_strategy.query_params.max_results == 5
    assert arxiv_strategy.arxiv_service is not None

    # Suppress mypy type check here
    mock_utilities_bundle.logger.info.assert_called_once_with("Arxiv strategy initiated")  # type: ignore


def test_default_path(arxiv_strategy: ArxivStrategy) -> None:
    assert arxiv_strategy.path == "some_path/"


def test_fetch_articles(arxiv_strategy: ArxivStrategy, mock_arxiv_service: MagicMock) -> None:
    # Mock the return value of arxiv_service.fetch_articles
    mock_articles: List[ArticleInfo] = [
        {
            "title": "Quantum Mechanics",
            "authors": ["A. Author"],
            "doi": "10.1234/arxiv.12345678",
            "abstract": "This paper discusses quantum mechanics.",
            "full_text": str(None),
            "submitted_date": "2024-01-01",
            "url": "https://arxiv.org/abs/1234.56789",
            "full_text_locator": "https://arxiv.org/pdf/1234.56789.pdf",
            "strategy": "ArxivStrategy",
            "score": int(-1),
            "score_justification": str(None),
            "score_generated": False,
            "full_text_available": True,
            "described_in_podcast": False,
        }
    ]

    mock_arxiv_service.fetch_articles.return_value = mock_articles

    # Call fetch_articles and assert the result
    articles = arxiv_strategy.fetch_articles()

    assert articles == mock_articles
    assert isinstance(arxiv_strategy.arxiv_service.fetch_articles, MagicMock)
    arxiv_strategy.arxiv_service.fetch_articles.assert_called_once()


def test_fetch_full_text(arxiv_strategy: ArxivStrategy, mock_arxiv_service: MagicMock) -> None:
    # Mock the return value of arxiv_service.fetch_full_text
    mock_full_text = "This is the full text of the article."
    mock_arxiv_service.fetch_full_text.return_value = mock_full_text

    # Prepare the full_text_locator argument
    full_text_locator = "https://arxiv.org/pdf/1234.56789.pdf"

    # Call fetch_full_text and assert the result
    full_text = arxiv_strategy.fetch_full_text(full_text_locator)
    assert full_text == mock_full_text
    assert isinstance(arxiv_strategy.arxiv_service.fetch_full_text, MagicMock)
    arxiv_strategy.arxiv_service.fetch_full_text.assert_called_once_with(full_text_locator=full_text_locator)
