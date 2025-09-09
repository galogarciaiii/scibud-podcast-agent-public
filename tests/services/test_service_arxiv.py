from datetime import datetime
from typing import List
from unittest.mock import MagicMock, Mock, patch
from xml.etree.ElementTree import ParseError

import pytest
import requests

from podcast.formats.article import ArticleInfo
from podcast.formats.query import QueryParams
from podcast.services.arxiv import ArxivService
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities_bundle():
    # Mock the utility bundle and its components
    mock_utilities = Mock(UtilitiesBundle)

    # Create a mock time utility and assign it to the utilities bundle
    mock_time = Mock()
    mock_time.convert_for_biorxiv.side_effect = lambda time: time.strftime("%Y%m%d%H%M")

    mock_logger = Mock()
    mock_config = Mock()

    # Assign the mock time utility to the mock utilities bundle
    mock_utilities.time = mock_time
    mock_utilities.logger = mock_logger
    mock_utilities.config = mock_config

    return mock_utilities


@pytest.fixture
def mock_query_params():
    # Set up the QueryParams object with default test values
    return QueryParams(
        query="quantum computing",
        min_date=datetime(2022, 1, 1),
        max_date=datetime(2023, 1, 1),
        max_results=10,
    )


@pytest.fixture
def arxiv_service(mock_utilities_bundle, mock_query_params):
    # Initialize the service with default test values
    return ArxivService(mock_utilities_bundle, mock_query_params)


@patch("requests.get")
def test_fetch_articles_success(mock_get, arxiv_service):
    # Mocking a successful API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
    <feed xmlns='http://www.w3.org/2005/Atom'>
        <entry>
            <title>Test Article</title>
            <id>http://arxiv.org/abs/1234.5678</id>
            <summary>This is a test abstract.</summary>
            <published>2023-01-01T00:00:00Z</published>
            <author><name>John Doe</name></author>
        </entry>
    </feed>
    """
    mock_get.return_value = mock_response

    with patch.object(arxiv_service, "parse_arxiv_response", return_value=[{}]) as mock_parse:
        articles = arxiv_service.fetch_articles()
        assert len(articles) == 1
        mock_parse.assert_called_once()
        mock_get.assert_called_once()


@patch("requests.get", side_effect=requests.exceptions.RequestException)
def test_fetch_articles_http_error(mock_get, arxiv_service):
    # Mocking an HTTP error
    with pytest.raises(requests.exceptions.RequestException):
        arxiv_service.fetch_articles()


@patch("requests.get")
def test_fetch_articles_parse_error(mock_get, arxiv_service):
    # Mocking a parsing error in XML
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<invalid>XML</invalid>"
    mock_get.return_value = mock_response

    with patch("xml.etree.ElementTree.fromstring", side_effect=ParseError), pytest.raises(ParseError):
        arxiv_service.fetch_articles()


@patch("requests.get")
@patch("fitz.open")
def test_fetch_full_text_success(mock_fitz_open, mock_get, arxiv_service):
    # Mock PDF download
    mock_pdf_response = MagicMock()
    mock_pdf_response.status_code = 200
    mock_pdf_response.headers = {"Content-Type": "application/pdf"}
    mock_get.return_value = mock_pdf_response

    # Mock PyMuPDF document
    mock_pdf = MagicMock()
    mock_pdf.page_count = 2
    # Simulate loading pages and returning text for each page
    mock_pdf.load_page.side_effect = lambda page_num: MagicMock(get_text=lambda _: f"Page {page_num + 1} text")
    # Mock the context manager for fitz.open
    mock_fitz_open.return_value.__enter__.return_value = mock_pdf

    # Call the method being tested
    full_text = arxiv_service.fetch_full_text("http://arxiv.org/pdf/test.pdf")

    # Assert that the full text contains text from all pages
    assert full_text == "Page 1 textPage 2 text"


@patch("requests.get")
def test_fetch_full_text_invalid_pdf(mock_get, arxiv_service):
    # Mocking an invalid content type for PDF fetch
    mock_response = Mock()
    mock_response.headers = {"Content-Type": "text/html"}
    mock_get.return_value = mock_response

    full_text = arxiv_service.fetch_full_text("http://arxiv.org/pdf/test.pdf")
    assert full_text == "Full text retrieval failed"


@patch("requests.get", side_effect=requests.exceptions.RequestException)
def test_fetch_full_text_http_error(mock_get, arxiv_service):
    # Mocking an HTTP error during PDF fetch
    full_text = arxiv_service.fetch_full_text("http://arxiv.org/pdf/test.pdf")
    assert full_text == "Full text retrieval failed"


def test_parse_arxiv_response(arxiv_service):
    # Test parsing of a valid XML response to match ArticleInfo structure
    response_text = """
    <feed xmlns='http://www.w3.org/2005/Atom'>
        <entry>
            <title>Test Article</title>
            <id>http://arxiv.org/abs/1234.5678</id>
            <summary>This is a test abstract.</summary>
            <published>2023-01-01T00:00:00Z</published>
            <author><name>John Doe</name></author>
        </entry>
    </feed>
    """
    articles: List[ArticleInfo] = arxiv_service.parse_arxiv_response(response_text)

    # Verify that the parsed output matches the ArticleInfo structure
    assert len(articles) == 1
    article = articles[0]

    # Check each field of the ArticleInfo
    assert article["title"] == "Test Article"
    assert article["abstract"] == "This is a test abstract."
    assert article["authors"] == ["John Doe"]
    assert article["url"] == "http://arxiv.org/abs/1234.5678"
    assert article["full_text_locator"] == "http://arxiv.org/pdf/1234.5678.pdf"
    assert article["strategy"] == "arxiv"
    assert article["score"] is None
    assert article["score_justification"] == ""
    assert not article["score_generated"]
    assert not article["full_text_available"]
    assert not article["described_in_podcast"]


def test_parse_arxiv_response_empty(arxiv_service):
    # Test parsing of an empty XML response to match ArticleInfo structure
    response_text = "<feed xmlns='http://www.w3.org/2005/Atom'></feed>"
    articles: List[ArticleInfo] = arxiv_service.parse_arxiv_response(response_text)
    assert len(articles) == 0


def test_date_formatting(mock_utilities_bundle):
    test_date = datetime(2024, 10, 1, 14, 30)
    formatted_date = mock_utilities_bundle.time.convert_for_biorxiv(test_date)
    assert formatted_date == "202410011430"
