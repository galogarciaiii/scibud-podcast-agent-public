from typing import Any, Dict, List

import fitz
import requests

from podcast.formats.article import ArticleInfo
from podcast.formats.query import QueryParams
from podcast.utilities.bundle import UtilitiesBundle


class BiorxivService:
    """
    Service class for fetching and parsing articles from the bioRxiv API.
    """

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
        self.min_date = self.utilities.time.convert_for_biorxiv(time=min_date)
        self.max_date = self.utilities.time.convert_for_biorxiv(time=max_date)
        self.max_results = self.query_params.max_results  # TODO This is not being used by this service yet

    def fetch_articles(self, cursor: int = 0) -> List[ArticleInfo]:
        """
        Fetch articles metadata from the bioRxiv API, filter them by keywords, and fetch full text
        for the filtered articles from their PDFs.
        """
        try:
            base_url = "https://api.biorxiv.org/details/biorxiv"
            biorxiv_query = f"/{self.min_date}/{self.max_date}/{cursor}/json"
            url = base_url + biorxiv_query
            response = requests.get(url)
            response.raise_for_status()
            self.utilities.logger.debug(f"API response status: {response.status_code}")

            # Parse article metadata
            articles = self.parse_biorxiv_response(response.json())

            # Filter articles based on keywords
            filtered_articles = self.filter_articles_by_keyword(articles, keyword=self.query)
            article_count = len(filtered_articles)

            self.utilities.logger.info(f"Fetched and filtered {article_count} articles from bioRxiv.")
            return filtered_articles

        except requests.exceptions.RequestException as e:
            self.utilities.logger.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            self.utilities.logger.error(f"Failed to fetch or process bioRxiv articles: {e}")
            raise

    def parse_biorxiv_response(self, response_json: Dict[str, Any]) -> List[ArticleInfo]:
        """
        Parse the bioRxiv API response and extract article metadata.
        """

        articles: List[ArticleInfo] = []
        for entry in response_json.get("collection", []):
            doi = entry.get("doi")
            full_text_locator = f"https://www.biorxiv.org/content/{doi}.full.pdf" if doi else ""
            article_info: ArticleInfo = {
                "title": entry.get("title"),
                "authors": entry.get("authors", "").split("; "),
                "doi": doi,
                "abstract": entry.get("abstract", ""),
                "full_text": "",
                "submitted_date": entry.get("date", ""),
                "url": f"https://doi.org/{doi}" if doi else "",
                "full_text_locator": full_text_locator,
                "strategy": "biorxiv",
                "score": None,
                "score_justification": "",
                "score_generated": False,
                "full_text_available": False,
                "described_in_podcast": False,
            }
            articles.append(article_info)
        self.utilities.logger.debug("Article data extracted and formatted.")
        return articles

    def filter_articles_by_keyword(self, articles: List[ArticleInfo], keyword: str) -> List[ArticleInfo]:
        """
        Filter articles by keywords in the title or abstract, allowing multiple keywords with "OR".

        Args:
            articles (List[Dict[str, Optional[str]]]): The list of articles to filter.
            keyword (str): The keyword string to filter by (can include OR to separate keywords).

        Returns:
            List[Dict[str, Optional[str]]]: A list of filtered articles.
        """
        # Split the keyword string by " OR " and strip any extra spaces
        keywords = [k.strip().lower() for k in keyword.split(" OR ")]

        # Filter articles that match at least one keyword in the title or abstract
        filtered_articles = [
            article
            for article in articles
            if article["title"]
            and article["abstract"]
            and any(kw in (article["title"] + article["abstract"]).lower() for kw in keywords)
        ]

        self.utilities.logger.debug(f"Filtered articles by keywords: {keywords}")
        return filtered_articles

    def fetch_full_text(self, full_text_locator: str) -> str:
        """
        Fetch the full text from the bioRxiv PDF URL.

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

            # Load the PDF using PyMuPDF in a streaming manner
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
