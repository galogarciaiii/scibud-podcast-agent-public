from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from podcast.formats.query import QueryParams
from podcast.services.biorxiv import BiorxivService
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities_bundle():
    # Mock the utility bundle and its components
    mock_utilities = Mock(UtilitiesBundle)

    # Create a mock time utility and assign it to the utilities bundle
    mock_time = Mock()
    mock_time.convert_for_biorxiv.side_effect = lambda time: time.strftime("%Y-%m-%d")

    mock_logger = Mock()
    mock_config = Mock()

    # Assign the mock time utility to the mock utilities bundle
    mock_utilities.time = mock_time
    mock_utilities.logger = mock_logger
    mock_utilities.config = mock_config

    return mock_utilities


@pytest.fixture
def mock_query_params():
    return QueryParams(
        query="machine learning OR deep learning",
        min_date=datetime(2023, 1, 1),
        max_date=datetime(2023, 12, 31),
        max_results=10,
    )


@pytest.fixture
def biorxiv_service(mock_utilities_bundle, mock_query_params):
    # Initialize BiorxivService with mocked utilities and query params
    return BiorxivService(
        utilities=mock_utilities_bundle,
        query_params=mock_query_params,
    )


@patch("requests.get")
def test_fetch_articles_success(mock_get, biorxiv_service):
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "collection": [
            {
                "title": "Machine Learning and Biology",
                "authors": "Author 1; Author 2",
                "doi": "10.1101/2023.01.01",
                "abstract": "This is an article about machine learning.",
            },
            {
                "title": "Deep Learning in Biology",
                "authors": "Author 3; Author 4",
                "doi": "10.1101/2023.01.02",
                "abstract": "This is an article about deep learning.",
            },
        ]
    }
    mock_get.return_value = mock_response

    # Fetch articles
    articles = biorxiv_service.fetch_articles()

    # Ensure that both articles match the query and are not filtered out
    assert len(articles) == 2
    assert articles[0]["title"] == "Machine Learning and Biology"
    assert articles[0]["authors"] == ["Author 1", "Author 2"]
    assert articles[1]["title"] == "Deep Learning in Biology"
    assert articles[1]["authors"] == ["Author 3", "Author 4"]


@patch("requests.get")
def test_fetch_articles_http_error(mock_get, biorxiv_service):
    mock_get.side_effect = requests.exceptions.RequestException("API request failed")

    with pytest.raises(requests.exceptions.RequestException):
        biorxiv_service.fetch_articles()


def test_parse_biorxiv_response(biorxiv_service):
    mock_response_json = {
        "collection": [
            {
                "title": "Test Article",
                "authors": "Author A; Author B",
                "doi": "10.1101/2023.01.01",
                "abstract": "This is an abstract.",
                "date": "2023-01-01",
            }
        ]
    }

    articles = biorxiv_service.parse_biorxiv_response(mock_response_json)

    assert len(articles) == 1
    assert articles[0]["title"] == "Test Article"
    assert articles[0]["authors"] == ["Author A", "Author B"]
    assert articles[0]["doi"] == "10.1101/2023.01.01"
    assert articles[0]["abstract"] == "This is an abstract."


def test_filter_articles_by_keyword(biorxiv_service):
    articles = [
        {
            "title": "Machine Learning in Biology",
            "abstract": "This study explores ML.",
            "doi": "10.1101/2023.01.01",
        },
        {
            "title": "Random Title",
            "abstract": "Unrelated content.",
            "doi": "10.1101/2023.01.02",
        },
    ]

    filtered_articles = biorxiv_service.filter_articles_by_keyword(articles, "machine learning")

    assert len(filtered_articles) == 1
    assert filtered_articles[0]["title"] == "Machine Learning in Biology"


@patch("requests.get")
@patch("fitz.open")
def test_fetch_full_text_success(mock_fitz_open, mock_get, biorxiv_service):
    # Mock PDF download
    mock_pdf_response = MagicMock()
    mock_pdf_response.status_code = 200
    mock_pdf_response.headers = {"Content-Type": "application/pdf"}
    mock_get.return_value = mock_pdf_response

    # Mock PyMuPDF document
    mock_pdf = MagicMock()
    mock_pdf.page_count = 2
    mock_pdf.load_page.side_effect = lambda page_num: MagicMock(get_text=lambda _: f"Page {page_num + 1} text")
    mock_fitz_open.return_value.__enter__.return_value = mock_pdf

    full_text = biorxiv_service.fetch_full_text("https://www.biorxiv.org/content/10.1101/2023.01.01.full.pdf")

    assert full_text == "Page 1 textPage 2 text"


@patch("requests.get")
def test_fetch_full_text_failure(mock_get, biorxiv_service):
    mock_get.side_effect = requests.exceptions.RequestException("PDF request failed")

    full_text = biorxiv_service.fetch_full_text("https://www.biorxiv.org/content/10.1101/2023.01.01.full.pdf")

    assert full_text == "Full text retrieval failed"


@pytest.mark.skip(reason="External API call - run this test manually when needed")
def test_fetch_articles_from_biorxiv_api(biorxiv_service):
    # Set up service with a valid query and date range
    service = biorxiv_service
    service.query = "machine learning"
    service.min_date = "2023-01-01"
    service.max_date = "2023-12-31"

    # Perform the actual API call
    articles = service.fetch_articles()

    # Ensure some articles are returned (or adjust based on expected API behavior)
    assert len(articles) > 0
    for article in articles:
        assert "title" in article
        assert "doi" in article
        assert "abstract" in article


def test_date_formatting(mock_utilities_bundle):
    test_date = datetime(2024, 10, 1)
    formatted_date = mock_utilities_bundle.time.convert_for_biorxiv(test_date)
    assert formatted_date == "2024-10-01"
