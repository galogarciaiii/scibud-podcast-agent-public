from typing import List

from podcast.formats.article import ArticleInfo
from podcast.formats.query import QueryParams
from podcast.services.arxiv import ArxivService
from podcast.strategies.article_source import ArticleSourceStrategy
from podcast.utilities.bundle import UtilitiesBundle


class ArxivStrategy(ArticleSourceStrategy):
    """
    Strategy for fetching articles from the arXiv repository.

    This class implements the specific strategy to query and fetch articles
    from the arXiv API. It extends the abstract base class ArticleSourceStrategy.

    Attributes:
        utilities: An instance of UtilitiesBundle used to access utilities like
                   logger, config, and time management.
        query_params: An instance of QueryParams for managing query details.
        path: A string representing the path where data will be stored.
        arxiv_service: An instance of ArxivService used to fetch articles.
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

        # Instantiate the ArxivService using the utilities
        self.arxiv_service = ArxivService(utilities=self.utilities, query_params=self.query_params)
        self.utilities.logger.info("Arxiv strategy initiated")

    def fetch_articles(self) -> List[ArticleInfo]:
        """
        Fetch articles from the arXiv service based on the initialized parameters.

        Returns:
            A list of dictionaries where each dictionary represents an article.
            The dictionary keys are strings and the values are optional strings.
        """
        articles = self.arxiv_service.fetch_articles()
        return articles

    def fetch_full_text(self, full_text_locator: str) -> str:
        """
        Fetch the full text of an article from the arXiv service based on the PDF URL.

        Args:
            full_text_locator: A dictionary where the values represent the URL of the article's PDF.

        Returns:
            The full text of the article as a string.
        """
        full_text = self.arxiv_service.fetch_full_text(full_text_locator=full_text_locator)
        return full_text
