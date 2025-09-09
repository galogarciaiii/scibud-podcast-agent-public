from typing import List

from podcast.formats.article import ArticleInfo
from podcast.formats.query import QueryParams
from podcast.services.pubmed import PubmedService
from podcast.strategies.article_source import ArticleSourceStrategy
from podcast.utilities.bundle import UtilitiesBundle


class PubmedStrategy(ArticleSourceStrategy):
    """
    A strategy class to fetch articles from PubMed using the PubmedService.

    This class inherits from the `ArticleSourceStrategy` and implements a specific strategy for
    querying and fetching article data from PubMed based on certain parameters.

    Attributes:
        utilities (UtilitiesBundle): An instance of UtilitiesBundle used for utilities like
                                     logger, time management, and configuration.
        query_params (QueryParams): Contains the search query, date ranges, and max results.
        path (str): A file path where article data might be stored or retrieved from.
        pubmed_service (PubmedService): An instance of the PubmedService to handle communication
                                        with the PubMed API.
    """

    def __init__(
        self,
        utilities: UtilitiesBundle,
        query_params: QueryParams,
        path: str,
    ):
        """
        Initializes the PubmedStrategy class with the necessary parameters and
        creates an instance of the PubmedService to handle PubMed-related operations.

        Args:
            utilities (UtilitiesBundle): Utility bundle containing logger, config, and time.
            query_params (QueryParams): Contains query, date range, and result limit.
            path (str): The file path for storing/retrieving article data.
        """

        def __init__(
            self,
            path: str,
            query_params: QueryParams,
            utilities: UtilitiesBundle,
        ):
            super().__init__(
                path=path,
                query_params=query_params,
                utilities=utilities,
            )

        self.path = path
        self.query_params = query_params
        self.utilities = utilities
        # Instantiate PubmedService using the utilities and query params
        self.pubmed_service = PubmedService(utilities=self.utilities, query_params=self.query_params)
        self.utilities.logger.info("Pubmed strategy initiated")

    def fetch_articles(self) -> List[ArticleInfo]:
        """
        Fetch articles from the Pubmed service based on the initialized parameters.

        This method communicates with the PubMed API via the PubmedService instance
        to retrieve a list of articles matching the query and date filters.

        Returns:
            List[ArticleInfo]: A list of dictionaries, where each dictionary represents an article
            fetched from PubMed.
        """
        articles = self.pubmed_service.fetch_articles()
        return articles

    def fetch_full_text(self, full_text_locator: str) -> str:
        """
        Fetch the full text of an article from PubMed.

        This method retrieves the full-text article using the provided locator dictionary
        specific to the PubmedStrategy.

        Args:
            full_text_locator (Dict[str, str]): A dictionary containing the location information
            required to retrieve the full text of an article.

        Returns:
            str: The full text of the article.
        """
        return self.pubmed_service.fetch_full_text(full_text_locator=full_text_locator)
