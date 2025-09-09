from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from podcast.formats.query import QueryParams
from podcast.strategies.biorxiv import BiorxivStrategy
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_config():
    return MagicMock()


@pytest.fixture
def mock_time():
    return MagicMock()


@pytest.fixture
def mock_utilities_bundle(mock_logger, mock_config, mock_time):
    bundle = MagicMock(spec=UtilitiesBundle)
    bundle.logger = mock_logger
    bundle.config = mock_config
    bundle.time = mock_time
    return bundle


@pytest.fixture
def mock_query_params():
    return QueryParams(query="cancer", min_date=datetime(2023, 1, 1), max_date=datetime(2023, 12, 31), max_results=10)


@pytest.fixture
def biorxiv_service_mock():
    with patch("podcast.strategies.biorxiv.BiorxivService", autospec=True) as mock_service:
        yield mock_service


@pytest.fixture
def biorxiv_strategy(mock_utilities_bundle, mock_query_params, biorxiv_service_mock):
    # Initialize BiorxivStrategy with mock utilities and query params
    strategy = BiorxivStrategy(
        path="biorxiv/",
        query_params=mock_query_params,
        utilities=mock_utilities_bundle,
    )
    strategy.biorxiv_service = biorxiv_service_mock  # Inject the mock BiorxivService
    return strategy


def test_biorxiv_strategy_initialization(biorxiv_service_mock, biorxiv_strategy):
    # Test if BiorxivStrategy is initialized correctly
    assert biorxiv_strategy.query_params.query == "cancer"
    assert biorxiv_strategy.query_params.min_date == datetime(2023, 1, 1)
    assert biorxiv_strategy.query_params.max_date == datetime(2023, 12, 31)
    assert biorxiv_strategy.query_params.max_results == 10
    assert biorxiv_strategy.path == "biorxiv/"

    # Ensure BiorxivService is initialized with correct parameters
    biorxiv_service_mock.assert_called_once_with(
        utilities=biorxiv_strategy.utilities,
        query_params=biorxiv_strategy.query_params,
    )


def test_default_path(biorxiv_strategy):
    # Test if default_path returns the correct value
    assert biorxiv_strategy.path == "biorxiv/"


def test_fetch_articles(biorxiv_strategy, biorxiv_service_mock):
    # Mock the fetch_articles method of BiorxivService
    mock_articles = [{"title": "Sample Article"}]
    biorxiv_strategy.biorxiv_service.fetch_articles = MagicMock(return_value=mock_articles)

    # Call fetch_articles and check if the correct result is returned
    articles = biorxiv_strategy.fetch_articles()
    assert articles == mock_articles
    biorxiv_strategy.biorxiv_service.fetch_articles.assert_called_once()


def test_fetch_full_text(biorxiv_strategy):
    # Mock the fetch_full_text method of BiorxivService
    mock_full_text = "This is the full text of the article."
    biorxiv_strategy.biorxiv_service.fetch_full_text = MagicMock(return_value=mock_full_text)

    # Prepare the full_text_locator dictionary
    full_text_locator = "some_locator"

    # Call fetch_full_text and check if the correct result is returned
    full_text = biorxiv_strategy.fetch_full_text(full_text_locator)
    assert full_text == mock_full_text
    biorxiv_strategy.biorxiv_service.fetch_full_text.assert_called_once_with(full_text_locator="some_locator")
