import os
import time
from typing import List, Optional
from xml.etree import ElementTree as ET

import requests
from dotenv import load_dotenv
from requests import Request
from requests.exceptions import RequestException

from podcast.formats.query import QueryParams
from podcast.strategies.article_source import ArticleInfo
from podcast.utilities.bundle import UtilitiesBundle

# Load environment variables from a .env file
load_dotenv()


class PubmedService:
    """
    A service class to interact with the Pubmed API for retrieving scientific articles from PubMed Central (PMC).

    This class allows constructing search queries, converting PubMed IDs (PMIDs) to PubMed Central IDs (PMCIDs),
    and fetching article details in a structured format compatible with the ArticleInfo format.

    Attributes:
        logger (logging.Logger): A logger instance to log messages and errors.
        time (TimeUtility): A utility class to handle time and date conversions.
        query (str): A string representing the search query for fetching articles.
        min_date (str): The minimum date of articles to be retrieved in Pubmed date format.
        max_date (str): The maximum date of articles to be retrieved in Pubmed date format.
        max_results (int): The maximum number of results to fetch from the API.
        pubmed_key (str): The Pubmed API key used for authentication.
        tool (str): The name of the tool (application) used in API requests.
        email (str): Email address to be passed to the Pubmed API.
    """

    def __init__(
        self,
        utilities: UtilitiesBundle,
        query_params: QueryParams,
        pubmed_key: Optional[str] = None,
        tool: Optional[str] = None,
        email: Optional[str] = None,
    ):
        """
        Initializes the PubmedService class with required attributes.

        Args:
            logger (logging.Logger): A logger instance to handle logging.
            time (TimeUtility): A time utility for converting dates to Pubmed's format.
            config (Dict): A dictionary containing configuration data, including tool and email information.
            query (str): The search query string for retrieving articles.
            min_date (datetime): The minimum date for the article search.
            max_date (datetime): The maximum date for the article search.
            max_results (int): The maximum number of results to return.
            pubmed_key (Optional[str]): Pubmed API key, if provided.
            tool (Optional[str]): Tool name for the API request.
            email (Optional[str]): Email address for the API request.
        """
        self.utilities: UtilitiesBundle = utilities
        self.query_params: QueryParams = query_params
        self.query = self.query_params.query
        min_date = self.query_params.min_date
        max_date = self.query_params.max_date
        self.min_date = self.utilities.time.convert_for_pubmed(time=min_date)
        self.max_date = self.utilities.time.convert_for_pubmed(time=max_date)
        self.max_results = self.query_params.max_results
        self.pubmed_key = pubmed_key or self._get_pubmed_api_key()
        self.tool = tool or self._get_tool()
        self.email = email or self._get_email()

    def _get_pubmed_api_key(self) -> str:
        """
        Retrieve the Pubmed API key from environment variables.

        Returns:
            str: The Pubmed API key.

        Raises:
            ValueError: If the API key is not found in the environment.
        """
        try:
            pubmed_key = os.getenv("PUBMED_API_KEY")
            if pubmed_key:
                self.utilities.logger.debug("Pubmed API key retrieved successfully.")
                return pubmed_key
            else:
                self.utilities.logger.error("Pubmed API key not found.")
                raise ValueError("Pubmed API key must be set in the environment.")
        except Exception as e:
            self.utilities.logger.error(f"An error occurred while retrieving the Pubmed API key: {e}")
            raise

    def _get_tool(self) -> str:
        """
        Retrieve the tool name from the configuration.

        Returns:
            str: The tool name for the API request.
        """
        return str(self.utilities.config["general_info"]["tool"])

    def _get_email(self) -> str:
        """
        Retrieve the email address from the configuration.

        Returns:
            str: The email address for the API request.
        """
        return str(self.utilities.config["general_info"]["email"])

    def fetch_articles(self) -> List[ArticleInfo]:
        """
        Fetches articles from PubMed Central using the specified search query.

        This method constructs a query to the PubMed API, fetches article IDs (PMCIDs),
        and retrieves the details of the articles.

        Returns:
            List[ArticleInfo]: A list of articles retrieved from PubMed Central in the ArticleInfo format.
        """
        try:
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            query = {
                "db": "pmc",
                "term": f'{self.query} AND "open access"[filter]',
                "retmax": str(self.max_results),
                "usehistory": "n",
                "datetype": "pdat",
                "mindate": str(self.min_date),
                "maxdate": str(self.max_date),
                "api_key": self.pubmed_key,
                "tool": self.tool,
                "email": self.email,
            }

            # Prepare the request URL for debugging purposes
            req = Request("GET", base_url, params=query)
            prepared = req.prepare()

            # Log the full URL for debugging
            self.utilities.logger.debug(f"Full URL sent to PubMed API: {prepared.url}")

            # Make the request to PubMed API
            response = requests.get(base_url, params=query)
            response.raise_for_status()  # Raise an error for non-200 responses
            self.utilities.logger.debug(f"API response status: {response.status_code}")

            # Parse the response as XML
            search_results = ET.fromstring(response.text)
            # Before passing to fetch_article_details, filter out any None values
            article_ids = [id_tag.text for id_tag in search_results.findall(".//IdList/Id") if id_tag.text]
            article_count = len(article_ids)
            first_article = article_ids[0]
            self.utilities.logger.info(f"Found {article_count} article IDs (PMCIDs), such as {first_article}")

            if not article_ids:
                self.utilities.logger.warning("No corresponding PMCIDs found.")
                return []

            # Fetch the details of the articles using the fetched article IDs
            articles = self.fetch_article_details(article_ids=article_ids)
            self.utilities.logger.info("Articles fetched and parsed from PubMed Central.")
            return articles

        except RequestException as e:
            self.utilities.logger.error(f"HTTP error occurred: {e}")
            raise
        except ET.ParseError as e:
            self.utilities.logger.error(f"Failed to parse XML response: {e}")
            raise
        except Exception as e:
            self.utilities.logger.error(f"Failed to fetch or process PubMed Central articles: {e}")
            raise

    def fetch_article_details(self, article_ids: List[str]) -> List[ArticleInfo]:
        """
        Fetches the full details of articles from PubMed Central by their IDs.

        Args:
            article_ids (List[str]): A list of article IDs (PMCIDs) to fetch details for.

        Returns:
            List[ArticleInfo]: A list of articles in the ArticleInfo format.
        """
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        query = {
            "db": "pmc",
            "retmode": "xml",
            "api_key": self.pubmed_key,
            "tool": self.tool,
            "email": self.email,
            "id": ",".join(article_ids),
        }

        try:
            time.sleep(1)
            response = requests.get(base_url, params=query)
            response.raise_for_status()
            self.utilities.logger.debug(f"API response status: {response.status_code}")

            xml_result = response.content
            # TODO I may need to try multiple attempts if no full text is retrieved
            articles = self.parse_efetch_result(xml_result)
            self.utilities.logger.debug("Article data extracted and formatted.")
            return articles
        except RequestException as e:
            self.utilities.logger.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            self.utilities.logger.error(f"Failed to fetch article details from PubMed Central: {e}")
            raise

    def parse_efetch_result(self, xml_result: bytes) -> List[ArticleInfo]:
        """
        Parses the XML result from the PubMed Central efetch API and extracts article details.
        This function is updated based on the DTD structure provided for PubMed XML.

        Args:
            xml_result (bytes): The XML content returned from the PubMed Central efetch API.

        Returns:
            List[ArticleInfo]: A list of parsed articles in the ArticleInfo format.
        """
        articles = []

        try:
            # Parse the XML content
            root = ET.fromstring(xml_result)

            # Loop through each article in the XML
            for article in root.findall(".//article"):
                article_info: ArticleInfo = {
                    "title": "",
                    "authors": [],
                    "doi": "",
                    "abstract": "",
                    "full_text": "",
                    "submitted_date": "",
                    "url": "",
                    "full_text_locator": "",
                    "strategy": "pubmed",
                    "score": None,
                    "score_justification": "",
                    "score_generated": False,
                    "full_text_available": False,
                    "described_in_podcast": False,
                }

                # Extract the title, supporting MathML elements
                title_elem = article.find(".//article-title")
                if title_elem is not None:
                    title_text = "".join(title_elem.itertext())  # Handle possible MathML or other inline tags
                    article_info["title"] = title_text
                else:
                    article_info["title"] = "No title"

                # Extract the authors (handling multiple author elements)
                authors = []
                for author in article.findall(".//contrib[@contrib-type='author']"):
                    lastname = author.find(".//surname")
                    firstname = author.find(".//given-names")
                    if lastname is not None and firstname is not None:
                        authors.append(f"{firstname.text} {lastname.text}")
                article_info["authors"] = authors

                # Extract the DOI, if available
                doi_elem = article.find(".//article-id[@pub-id-type='doi']")
                article_info["doi"] = str(doi_elem.text) if doi_elem is not None else "No DOI"

                # Extract the abstract, including support for possible MathML elements
                abstract_elem = article.find(".//abstract")
                if abstract_elem is not None:
                    abstract_text = "".join(abstract_elem.itertext())  # Handle inline tags
                    article_info["abstract"] = abstract_text
                else:
                    article_info["abstract"] = "No abstract available"

                # Extract full text or its URL (e.g., from <body> or <ext-link>)
                full_text_elem = article.find(".//body")
                if full_text_elem is not None:
                    article_info["full_text"] = "".join(full_text_elem.itertext())
                    article_info["full_text_available"] = True
                else:
                    article_info["full_text"] = "Full text not available"

                # Extract the submitted date (received date)
                submitted_date_elem = article.find(".//date[@date-type='received']")
                if submitted_date_elem is not None:
                    year_elem = submitted_date_elem.find(".//year")
                    month_elem = submitted_date_elem.find(".//month")
                    day_elem = submitted_date_elem.find(".//day")
                    article_info["submitted_date"] = (
                        f"{year_elem.text if year_elem is not None else 'Unknown'}-"
                        f"{month_elem.text if month_elem is not None else 'Unknown'}-"
                        f"{day_elem.text if day_elem is not None else 'Unknown'}"
                    )

                else:
                    article_info["submitted_date"] = "Unknown date"

                # Extract URL using the PMC ID
                pmc_id_elem = article.find(".//article-id[@pub-id-type='pmc']")
                article_info["url"] = (
                    f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id_elem.text}/"
                    if pmc_id_elem is not None
                    else "No PMC URL"
                )

                # Placeholder for full-text locator logic
                article_info["full_text_locator"] = (
                    f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id_elem.text}/"
                    if pmc_id_elem is not None
                    else "No PMC URL"
                )

                # Add the extracted article information to the list
                articles.append(article_info)

            return articles
        except ET.ParseError as e:
            self.utilities.logger.error(f"Error parsing XML: {e}")
            raise Exception(f"Failed to parse PubMed Central XML: {e}")
        except Exception as e:
            self.utilities.logger.error(f"An unexpected error occurred: {e}")
            raise

    # The function is now successfully updated to parse more robustly based on DTD insights.

    def fetch_full_text(self, full_text_locator: str) -> str:
        """
        Fetches the full text of an article based on the full text locator.

        Args:
            full_text_locator (str): The ID or locator for the article's full text.

        Returns:
            str: The full text of the article.
        """
        articles = self.fetch_article_details(article_ids=[full_text_locator])
        full_text = articles[0]["full_text"]
        return full_text
