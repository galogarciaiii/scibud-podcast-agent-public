from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from podcast.formats.query import QueryParams
from podcast.services.pubmed import PubmedService
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities_bundle():
    # Mock the utility bundle and its components
    mock_utilities = Mock(UtilitiesBundle)

    # Create a mock time utility and assign it to the utilities bundle
    mock_time = Mock()
    mock_time.convert_for_pubmed.side_effect = lambda time: time.strftime("%Y%m%d")
    mock_utilities.time = mock_time

    mock_logger = Mock()
    mock_utilities.logger = mock_logger

    mock_utilities.config = {"general_info": {"tool": "MyTestTool", "email": "test@example.com"}}

    return mock_utilities


@pytest.fixture
def mock_query_params():
    return QueryParams(
        query="machine learning",
        min_date=datetime(2024, 8, 31),
        max_date=datetime(2024, 10, 1),
        max_results=100,
    )


@pytest.fixture
def pubmed_service(mock_utilities_bundle, mock_query_params):
    # Initialize PubmedService with mocked utilities and query params
    return PubmedService(
        utilities=mock_utilities_bundle,
        query_params=mock_query_params,
    )


@patch("os.getenv")
def test_get_pubmed_api_key(mock_getenv, pubmed_service):
    mock_getenv.return_value = "mock_pubmed_api_key"
    assert pubmed_service._get_pubmed_api_key() == "mock_pubmed_api_key"
    mock_getenv.assert_called_once_with("PUBMED_API_KEY")


def test_get_tool(pubmed_service):
    assert pubmed_service._get_tool() == "MyTestTool"


def test_get_email(pubmed_service):
    assert pubmed_service._get_email() == "test@example.com"


def test_date_formatting(mock_utilities_bundle):
    test_date = datetime(2024, 10, 1)
    formatted_date = mock_utilities_bundle.time.convert_for_pubmed(test_date)
    assert formatted_date == "20241001"


@patch("requests.get")
def test_fetch_articles(mock_get, pubmed_service):
    # Mock the response from PubMed API for article search
    mock_search_response = MagicMock()
    mock_search_response.status_code = 200
    mock_search_response.text = """<eSearchResult>
                                      <IdList>
                                        <Id>12345</Id>
                                        <Id>67890</Id>
                                      </IdList>
                                    </eSearchResult>"""
    mock_get.return_value = mock_search_response

    # Mock the response from PubMed API for fetching article details (efetch)
    mock_efetch_response = MagicMock()
    mock_efetch_response.status_code = 200
    mock_efetch_response.content = b"<root><article><article-id pub-id-type='pmc'>12345</article-id></article></root>"

    # When fetch_article_details is called, it will trigger the second request
    mock_get.side_effect = [mock_search_response, mock_efetch_response]

    # Call the method to test
    articles = pubmed_service.fetch_articles()

    # Validate the results
    assert len(articles) == 1
    assert articles[0]["url"] == "https://www.ncbi.nlm.nih.gov/pmc/articles/12345/"


@patch("requests.get")
def test_fetch_article_details(mock_get, pubmed_service):
    # Mock the response from PubMed API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"<root><article><article-id pub-id-type='pmc'>12345</article-id></article></root>"
    mock_get.return_value = mock_response

    article_ids = ["12345"]
    articles = pubmed_service.fetch_article_details(article_ids=article_ids)

    assert len(articles) == 1
    assert articles[0]["url"] == "https://www.ncbi.nlm.nih.gov/pmc/articles/12345/"

    # Use the actual values from pubmed_service for tool and email
    mock_get.assert_called_once_with(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        params={
            "db": "pmc",
            "retmode": "xml",
            "api_key": pubmed_service.pubmed_key,
            "tool": pubmed_service.tool,
            "email": pubmed_service.email,
            "id": "12345",
        },
    )


def test_parse_efetch_result(pubmed_service):
    # Mock XML result
    xml_result = b"<root><article><article-id pub-id-type='pmc'>12345</article-id><title-group><article-title>Test Title</article-title></title-group></article></root>"

    # Call the actual method without mocking the service
    articles = pubmed_service.parse_efetch_result(xml_result)

    # Assert that the article was parsed correctly
    assert len(articles) == 1
    assert articles[0]["url"] == "https://www.ncbi.nlm.nih.gov/pmc/articles/12345/"
    assert articles[0]["title"] == "Test Title"


@patch("requests.get")
def test_fetch_full_text(mock_get, pubmed_service):
    # Mock the response from Pubmed API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"<root><article><article-id pub-id-type='pmc'>12345</article-id><body><p>Full text content</p></body></article></root>"
    mock_get.return_value = mock_response

    full_text = pubmed_service.fetch_full_text(full_text_locator="12345")
    assert full_text == "Full text content"
    mock_get.assert_called_once()


@pytest.mark.skip(reason="This test queries the actual PMC API and is skipped by default.")
def test_fetch_articles_actual_api(pubmed_service):
    """
    Test that queries the actual PMC API.
    This test is skipped by default to avoid unnecessary external API calls.
    """
    articles = pubmed_service.fetch_articles()

    # Assert that some articles were fetched
    assert len(articles) > 0
    for article in articles:
        # Ensure each article contains necessary fields
        assert "title" in article
        assert "url" in article
        assert "full_text" in article
