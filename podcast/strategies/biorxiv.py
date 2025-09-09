from typing import List

from podcast.formats.article import ArticleInfo
from podcast.formats.query import QueryParams
from podcast.services.biorxiv import BiorxivService
from podcast.strategies.article_source import ArticleSourceStrategy
from podcast.utilities.bundle import UtilitiesBundle


class BiorxivStrategy(ArticleSourceStrategy):
    """
    Strategy for fetching articles from the bioRxiv repository.

    This class implements the specific strategy to query and fetch articles
    from the bioRxiv API. It extends the abstract base class ArticleSourceStrategy.
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

        # Instantiate BiorxivService using the utilities and query params
        self.biorxiv_service = BiorxivService(utilities=self.utilities, query_params=self.query_params)
        self.utilities.logger.info("Biorxiv strategy initiated")

    def fetch_articles(self) -> List[ArticleInfo]:
        """
        Fetch articles from the Biorxiv service based on the initialized parameters.
        """
        articles = self.biorxiv_service.fetch_articles()
        return articles

    def fetch_full_text(self, full_text_locator: str) -> str:
        """
        Fetch the full text of an article from the Biorxiv service based on the locator provided.

        Args:
            full_text_locator: A dictionary where the values represent the URL of the article's full text.

        Returns:
            The full text of the article as a string.
        """
        full_text = self.biorxiv_service.fetch_full_text(full_text_locator=full_text_locator)
        return full_text
