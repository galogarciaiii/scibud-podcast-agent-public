from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from podcast.creator import PodcastCreator
from podcast.strategies.arxiv import ArxivStrategy
from podcast.strategies.biorxiv import BiorxivStrategy
from podcast.strategies.pubmed import PubmedStrategy
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_config():
    # Add "db_filename" to the mock config to avoid KeyError
    return {
        "general_info": {
            "bucket_name": "test-bucket",
            "tool": "mock_tool",
            "email": "mock_email",
            "db_filename": "test.db",
            "rss_filename": "rss.xml",
        }
    }


@pytest.fixture
def mock_time_utility():
    mock_time = MagicMock()
    mock_time.current_time = datetime.now()
    mock_time.get_time_offset = lambda days: datetime.now() - timedelta(days=days)
    return mock_time


@pytest.fixture
def mock_utilities_bundle(mock_logger, mock_config, mock_time_utility):
    bundle = MagicMock(spec=UtilitiesBundle)
    bundle.logger = mock_logger
    bundle.config = mock_config
    bundle.time = mock_time_utility
    return bundle


def test_initialization_with_default_values(mock_utilities_bundle):
    # Set one of the sources to True (e.g., arxiv)
    creator = PodcastCreator(query="test query", utilities=mock_utilities_bundle, path="some_path", arxiv=True)

    assert creator.query == "test query"
    assert creator.utilities == mock_utilities_bundle
    assert creator.path == "some_path"
    assert creator.min_date.replace(microsecond=0) == mock_utilities_bundle.time.get_time_offset(7).replace(
        microsecond=0
    )
    assert creator.max_date == mock_utilities_bundle.time.current_time
    assert creator.max_results == 50
    assert creator.bucket_name == "test-bucket"


def test_initialization_with_custom_values(mock_utilities_bundle):
    custom_min_date = datetime(2022, 1, 1)
    custom_max_date = datetime(2023, 1, 1)

    creator = PodcastCreator(
        query="test query",
        utilities=mock_utilities_bundle,
        path="some_path",
        arxiv=True,
        biorxiv=True,
        pubmed=True,
        min_date=custom_min_date,
        max_date=custom_max_date,
        max_results=100,
    )

    assert creator.arxiv is True
    assert creator.biorxiv is True
    assert creator.pubmed is True
    assert creator.min_date == custom_min_date
    assert creator.max_date == custom_max_date
    assert creator.max_results == 100
    assert creator.bucket_name == "test-bucket"


def test_assemble_strategies_arxiv(mock_utilities_bundle):
    creator = PodcastCreator(query="test query", arxiv=True, utilities=mock_utilities_bundle, path="some_path")
    strategies = creator.assemble_strategies()

    assert len(strategies) == 1
    assert isinstance(strategies["arxiv"], ArxivStrategy)


def test_assemble_strategies_multiple_sources(mock_utilities_bundle):
    creator = PodcastCreator(
        query="test query",
        arxiv=True,
        biorxiv=True,
        pubmed=True,
        utilities=mock_utilities_bundle,
        path="some_path",
    )
    strategies = creator.assemble_strategies()

    assert len(strategies) == 3
    assert isinstance(strategies["arxiv"], ArxivStrategy)
    assert isinstance(strategies["biorxiv"], BiorxivStrategy)
    assert isinstance(strategies["pubmed"], PubmedStrategy)


def test_generate_podcast_with_strategies(mock_utilities_bundle):
    creator = PodcastCreator(query="test query", arxiv=True, utilities=mock_utilities_bundle, path="some_path")

    with patch("podcast.creator.Director") as mock_director:
        mock_director_instance = mock_director.return_value
        creator.generate_podcast()
        mock_director.assert_called_once()
        mock_director_instance.generate_podcast_episode.assert_called_once()
