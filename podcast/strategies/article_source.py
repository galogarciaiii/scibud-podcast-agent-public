from abc import ABC, abstractmethod
from typing import List

from podcast.formats.article import ArticleInfo
from podcast.formats.query import QueryParams
from podcast.utilities.bundle import UtilitiesBundle


class ArticleSourceStrategy(ABC):
    """
    Abstract base class for article source strategies.

    This class provides a framework for defining strategies to fetch articles
    from various sources.

    Attributes:
        utilities: An instance of UtilitiesBundle containing logger, config, and time utilities.
        path: A string representing the path where article-related data is stored or fetched from.
        query_params: An instance of QueryParams containing search parameters.
    """

    def __init__(
        self,
        utilities: UtilitiesBundle,
        path: str,
        query_params: QueryParams,
    ):
        self.utilities = utilities
        self.path: str = path
        self.query_params: QueryParams = query_params

    @abstractmethod
    def fetch_articles(self) -> List[ArticleInfo]:
        """
        Abstract method to fetch articles from the source.

        Subclasses must implement this method to define how articles are fetched.

        Returns:
            List[ArticleInfo]: A list of dictionaries containing article information.
        """
        pass

    @abstractmethod
    def fetch_full_text(self, full_text_locator: str) -> str:
        """
        Abstract method to fetch the full text of an article from the source.

        Subclasses must implement this method to define how full text is fetched.

        Args:
            full_text_locator: A dictionary where the values represent the URL or identifier
            needed to fetch the article's full text.

        Returns:
            str: The full text of the article.
        """
        pass
