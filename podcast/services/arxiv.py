import xml.etree.ElementTree as ET
from typing import Dict, List, Union

import fitz
import requests

from podcast.formats.article import ArticleInfo
from podcast.formats.query import QueryParams
from podcast.utilities.bundle import UtilitiesBundle


class ArxivService:
    """
    Service class for fetching and parsing articles from the arXiv API.

    This class handles the construction of queries, fetching articles from the arXiv API,
    and parsing the XML responses into a structured format. Additionally, it retrieves the
    full text from arXiv PDFs.

    Attributes:
        NAMESPACE (dict): XML namespace for parsing arXiv API responses.
        logger: Logging utility instance for logging.
        time: Time utility instance for date conversions.
        query (str): Query string for searching articles.
        min_date (str): Minimum date for article search.
        max_date (str): Maximum date for article search.
        max_results (int): Maximum number of results to fetch.
    """

    NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}

    def __init__(
        self,
        utilities: UtilitiesBundle,
        query_params: QueryParams,
    ):
        self.utilities: UtilitiesBundle = utilities
        self.query_params: QueryParams = query_params
        self.query = self.query_params.query
        min_date = self.query_params.min_date
        max_date = self.query_params.max_date
        self.min_date = self.utilities.time.convert_for_arxiv(time=min_date)
        self.max_date = self.utilities.time.convert_for_arxiv(time=max_date)
        self.max_results = self.query_params.max_results or 50

    def fetch_articles(self) -> List[ArticleInfo]:
        """
        Fetch articles from the arXiv API based on the initialized parameters.

        Constructs the arXiv API query and retrieves the articles,
        handling any HTTP or parsing errors.

        Returns:
            List[Dict[str, Union[Optional[str], List[Optional[str]]]]]:
                A list of dictionaries containing article information.

        Raises:
            requests.exceptions.RequestException: If an HTTP error occurs during the API request.
            ET.ParseError: If an error occurs while parsing the XML response.
            Exception: For any other errors that occur during the fetch or parse process.
        """
        try:
            base_url = "http://export.arxiv.org/api/query"
            arxiv_query = f"(({self.query}) AND submittedDate:[{self.min_date} TO {self.max_date}])"
            params: Dict[str, Union[str, int]] = {
                "search_query": arxiv_query,  # This is a string
                "sortBy": "submittedDate",  # This is a string
                "max_results": self.max_results,  # Keep this as an int
            }
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            self.utilities.logger.debug(f"API response status: {response.status_code}")
            articles = self.parse_arxiv_response(response.text)
            self.utilities.logger.info("Articles fetched and parsed from arXiv.")
            return articles

        except requests.exceptions.RequestException as e:
            self.utilities.logger.error(f"HTTP error occurred: {e}")
            raise
        except ET.ParseError as e:
            self.utilities.logger.error(f"XML parsing error occurred: {e}")
            raise
        except Exception as e:
            self.utilities.logger.error(f"Failed to fetch or process arXiv articles: {e}")
            raise

    def fetch_full_text(self, full_text_locator: str) -> str:
        """
        Fetch the full text from the arXiv PDF URL.

        Args:
            full_text_locator (str): URL to the PDF file.

        Returns:
            str: Full text extracted from the PDF file.
        """
        try:
            # Stream the PDF file to save memory
            response = requests.get(full_text_locator, stream=True)
            response.raise_for_status()

            # Check if the response contains a valid PDF
            if response.headers.get("Content-Type") != "application/pdf":
                self.utilities.logger.error("Invalid content type: not a PDF")
                return "Full text retrieval failed"

            # Load the PDF using PyMuPDF
            full_text = ""
            with fitz.open(stream=response.content, filetype="pdf") as pdf_document:
                for page_num in range(pdf_document.page_count):
                    page = pdf_document.load_page(page_num)
                    full_text += page.get_text("text")

            return full_text.strip() if full_text else "Full text not available"

        except requests.exceptions.RequestException as e:
            self.utilities.logger.error(f"Error fetching PDF: {e}")
            return "Full text retrieval failed"
        except Exception as e:
            self.utilities.logger.error(f"Failed to extract text from PDF: {e}")
            return "Text extraction failed"

    def parse_arxiv_response(self, response_text: str) -> List[ArticleInfo]:
        """
        Parse the arXiv API response and extract article information.

        Args:
            response_text (str): The XML response from the arXiv API.

        Returns:
            List[Dict[str, Optional[str]]]: A list of dictionaries containing article information.
        """
        root = ET.fromstring(response_text)
        articles: List[ArticleInfo] = []

        for entry in root.findall("atom:entry", self.NAMESPACE):
            title_element = entry.find("atom:title", self.NAMESPACE)
            title = title_element.text if title_element is not None else "No title available"
            title = str(title)

            doi_element = entry.find("atom:doi", self.NAMESPACE)
            doi = doi_element.text if doi_element is not None else "No doi available"
            doi = str(doi)

            abstract_element = entry.find("atom:summary", self.NAMESPACE)
            abstract = abstract_element.text if abstract_element is not None else "No abstract available"
            abstract = str(abstract)

            published_element = entry.find("atom:published", self.NAMESPACE)
            published_date = published_element.text if published_element is not None else "No published date available"
            published_date = str(published_date)

            id_element = entry.find("atom:id", self.NAMESPACE)
            url = id_element.text if id_element is not None else "No URL available"
            url = str(url)

            full_text_locator = url.replace("abs", "pdf") + ".pdf"  # PDF link for the article

            authors = [
                name_element.text
                for author in entry.findall("atom:author", self.NAMESPACE)
                if (name_element := author.find("atom:name", self.NAMESPACE)) is not None
                and name_element.text is not None
            ]
            article_info: ArticleInfo = {
                "title": title,
                "authors": authors,
                "doi": doi,
                "abstract": abstract,
                "full_text": "",
                "submitted_date": published_date,
                "url": url,
                "full_text_locator": full_text_locator,
                "strategy": "arxiv",
                "score": None,
                "score_justification": "",
                "score_generated": False,
                "full_text_available": False,
                "described_in_podcast": False,
            }

            articles.append(article_info)

        self.utilities.logger.debug("Article data extracted and formatted.")
        return articles
