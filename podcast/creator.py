from datetime import datetime
from typing import Dict, Optional

from podcast.director import Director
from podcast.formats.query import QueryParams
from podcast.strategies.article_source import ArticleSourceStrategy
from podcast.strategies.arxiv import ArxivStrategy
from podcast.strategies.biorxiv import BiorxivStrategy
from podcast.strategies.pubmed import PubmedStrategy
from podcast.utilities.bundle import UtilitiesBundle


class PodcastCreator:
    """
    PodcastCreator is responsible for orchestrating the creation of podcast episodes
    by selecting the appropriate strategies and directing the process through the Director class.
    """

    def __init__(
        self,
        query: str,
        utilities: UtilitiesBundle,
        path: str,
        arxiv: Optional[bool] = False,
        biorxiv: Optional[bool] = False,
        pubmed: Optional[bool] = False,
        min_date: Optional[datetime] = None,
        max_date: Optional[datetime] = None,
        max_results: Optional[int] = 50,
    ) -> None:
        """
        Initializes the PodcastCreator with the provided parameters and assembles the strategies.
        """
        if not (arxiv or biorxiv or pubmed):
            raise ValueError("At least one source (arxiv, biorxiv, pubmed) must be selected.")

        self.query: str = query
        self.utilities: UtilitiesBundle = utilities
        self.path: str = path  # Use the path parameter provided by the user
        self.arxiv: Optional[bool] = arxiv
        self.biorxiv: Optional[bool] = biorxiv
        self.pubmed: Optional[bool] = pubmed

        # Set the date ranges using the utilities
        self.min_date: datetime = min_date if min_date else self.utilities.time.get_time_offset(days=7)
        self.max_date: datetime = max_date if max_date else self.utilities.time.current_time
        self.max_results: Optional[int] = max_results

        # Bundle query parameters into a single object
        self.query_params = QueryParams(
            query=self.query, min_date=self.min_date, max_date=self.max_date, max_results=self.max_results
        )

        # Assemble strategies based on the flags (arxiv, biorxiv, pubmed)
        self.strategies: Dict[str, ArticleSourceStrategy] = self.assemble_strategies()

        # Extract bucket name directly from the utilities config
        try:
            self.bucket_name: str = self.utilities.config["general_info"]["bucket_name"]
        except KeyError as e:
            self.utilities.logger.error(f"Config missing expected key: {e}")
            raise

    def assemble_strategies(self) -> Dict[str, ArticleSourceStrategy]:
        """
        Assembles a list of strategies based on the boolean flags provided during initialization.
        """
        strategies: Dict[str, ArticleSourceStrategy] = {}

        if self.arxiv:
            strategies["arxiv"] = ArxivStrategy(
                utilities=self.utilities,
                query_params=self.query_params,
                path=self.path,
            )
        if self.biorxiv:
            strategies["biorxiv"] = BiorxivStrategy(
                utilities=self.utilities,
                query_params=self.query_params,
                path=self.path,
            )
        if self.pubmed:
            strategies["pubmed"] = PubmedStrategy(
                utilities=self.utilities,
                query_params=self.query_params,
                path=self.path,
            )
        return strategies

    def generate_podcast(self) -> None:
        """
        Generates podcast episodes by passing the list of strategies to the Director.
        """
        if not self.strategies:
            self.utilities.logger.error("No strategies were assembled, cannot generate podcast.")
            return

        self.utilities.logger.info(f"Using strategies: {list(self.strategies.keys())}")

        # Instantiate Director with utilities, strategies, and the base path
        director = Director(utilities=self.utilities, strategies=self.strategies, path=self.path)
        director.generate_podcast_episode()

        self.utilities.logger.info("Podcast episode generated successfully.")
