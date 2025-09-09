import json
import sqlite3
import uuid
from typing import Any, List, Optional, Tuple, Union

from podcast.formats.episode import EpisodeInfo
from podcast.strategies.article_source import ArticleInfo
from podcast.utilities.bundle import UtilitiesBundle


class DBManager:
    """
    A class to manage SQLite database operations for a podcast application.

    This class handles:
    - Insertion of articles and episodes into the database.
    - Checking if an article has already been described in the podcast.
    - Retrieving the next available episode number.
    - Fetching all episode information from the database.
    """

    def __init__(self, path: str, utilities: UtilitiesBundle) -> None:
        """
        Initialize the DBManager with necessary utilities and configurations.

        Args:
            time (TimeUtility): Utility class for time-related operations.
            strategy (ArticleSourceStrategy): Strategy for article source management.
            logger (logging.Logger): Logger instance for logging information.
            config (Dict[str, Any]): Configuration dictionary containing various settings.
        """
        self.utilities: UtilitiesBundle = utilities
        self.path = path
        db_path: str = self.path + self.utilities.config["general_info"]["db_filename"]
        self.db_path: str = db_path

    def _execute_query(
        self, query: str, params: Optional[Tuple[Any, ...]] = None, fetch: str = "all"
    ) -> Optional[Union[List[Tuple[Any, ...]], Tuple[Any, ...], None]]:
        """
        Helper method to execute a query and handle connection/cursor management.

        Args:
            query (str): SQL query to be executed.
            params (Optional[Tuple[Any, ...]]): Parameters for the SQL query, if any.
            fetch (str): Whether to fetch 'one', 'all', or 'none' (default is 'all').

        Returns:
            Optional[Union[List[Tuple[Any, ...]], Tuple[Any, ...], None]]:
            Query results if fetch is 'one' or 'all', otherwise None.
        """
        conn = None
        cursor = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            self.utilities.logger.debug(f"Executing query: {query} with params: {params}")

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch == "one":
                result = cursor.fetchone()
                return result if result is not None else None
            elif fetch == "all":
                result = cursor.fetchall()
                return result if result is not None else []
            elif fetch == "none":
                conn.commit()
                return None
            else:
                self.utilities.logger.error(f"Invalid fetch option: {fetch}")
                raise ValueError(f"Invalid fetch option: {fetch}")

        except sqlite3.Error as e:
            self.utilities.logger.error(f"An error occurred during query execution: {e}")
            raise Exception(f"Database query failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                self.utilities.logger.debug("Database connection closed.")

    def article_described_in_podcast(self, title: str) -> bool:
        """
        Check if an article has already been described in the podcast.

        Args:
            title (str): Title of the article.

        Returns:
            bool: True if the article is marked as described, False otherwise.
        """
        query = "SELECT described_in_podcast FROM articles WHERE title = ?"
        result = self._execute_query(query, (title,), fetch="one")

        if result is None:
            self.utilities.logger.debug(f"Article with title '{title}' not found in the database.")
            return False

        return bool(result[0])

    def get_next_episode_number(self) -> int:
        """
        Retrieve the next available episode number.

        Returns:
            int: The next episode number.
        """
        query = "SELECT episode FROM episodes ORDER BY episode DESC LIMIT 1"
        last_episode = self._execute_query(query, fetch="one")

        if last_episode is None or not isinstance(last_episode[0], int):
            last_episode_number = 0
        else:
            last_episode_number = last_episode[0]

        next_episode: int = last_episode_number + 1
        self.utilities.logger.debug("Next season and episode numbers determined successfully.")
        return next_episode

    def add_episode_text_to_db(self, episode_info: EpisodeInfo) -> None:
        """
        Add episode metadata to the database.

        Args:
            episode_info (EpisodeInfo): A TypedDict containing episode metadata.
        """
        # Prepare the data for insertion
        data = (
            episode_info["title"],
            episode_info["description"],
            episode_info["citations"],
            episode_info["persona"],
            episode_info["voice"],
            episode_info["script"],
            episode_info["season"],
            episode_info["episode"],
            episode_info["episode_type"],
            episode_info["pub_date"],
            episode_info["post"],
            episode_info.get("guid") or str(uuid.uuid4()),  # Use provided GUID or generate a new one
            episode_info.get("file_size", 0),
        )

        query = """
            INSERT INTO Episodes (
                title, description, citations, persona, voice, script, season, episode,
                episode_type, pub_date, post, guid, file_size
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        # Execute the query to insert the data
        self._execute_query(query, data, fetch="none")
        self.utilities.logger.debug("Episode inserted successfully.")

    def insert_articles_into_db(self, articles: List[ArticleInfo]) -> None:
        """
        Insert a list of articles into the database, updating any existing articles.

        Args:
            articles (List[ArticleInfo]): List of articles to be inserted or updated.
        """
        query = """
            INSERT OR REPLACE INTO articles (
                title, authors, doi, abstract, full_text, submitted_date, url,
                full_text_locator, strategy, score, score_justification, score_generated,
                full_text_available, described_in_podcast
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        for article in articles:
            if "title" not in article:
                self.utilities.logger.error("Missing 'title' in article.")
                continue

            data = (
                article["title"],
                json.dumps(article.get("authors", [])),
                article.get("doi", ""),
                article.get("abstract", ""),
                article.get("full_text", ""),
                article.get("submitted_date", ""),
                article.get("url", ""),
                article.get("full_text_locator", ""),
                article.get("strategy", ""),
                article.get("score", None),
                article.get("score_justification", ""),
                article.get("score_generated", 0),
                article.get("full_text_available", 0),
                article.get("described_in_podcast", 0),
            )
            self._execute_query(query, data, fetch="none")
            self.utilities.logger.info(f"Article titled '{article['title']}' inserted or updated successfully.")

    def get_article_score_justification(self, title: str) -> Tuple[int, str]:
        """
        Retrieve the score and justification of an article by its title.

        Args:
            title (str): Title of the article.

        Returns:
            Tuple[int, str]: The score and justification of the article.
        """
        query = "SELECT score, score_justification FROM articles WHERE title = ?"
        result = self._execute_query(query, (title,), fetch="one")
        if result is not None and isinstance(result[0], int) and isinstance(result[1], str):
            return result[0], result[1]
        return -1, "No justification found"

    def retrieve_all_episodes_info(self) -> List[EpisodeInfo]:
        """
        Retrieve all episode information from the database.

        Returns:
            List[EpisodeInfo]: List of episode metadata as EpisodeInfo TypedDicts.
        """
        query = """
            SELECT
                title, description, citations, persona, voice, script, season, episode,
                episode_type, pub_date, post, guid, file_size
            FROM
                episodes
            ORDER BY
                episode DESC;
        """
        all_episodes = self._execute_query(query, fetch="all")

        if all_episodes is None:
            return []

        # Map database rows to EpisodeInfo TypedDicts
        episodes_list: List[EpisodeInfo] = [
            {
                "title": episode[0],
                "description": episode[1],
                "citations": episode[2],
                "persona": episode[3],
                "voice": episode[4],
                "script": episode[5],
                "season": episode[6],
                "episode": episode[7],
                "episode_type": episode[8],
                "pub_date": episode[9],
                "post": episode[10],  # Assuming post is not stored in this table and needs to be fetched separately
                "guid": episode[11],  # Optional field
                "file_size": episode[12],
                "articles": [],  # Assuming articles are not stored in this table and need to be fetched separately
            }
            for episode in all_episodes
        ]

        return episodes_list

    def fetch_full_text(self, title: str) -> Any:
        """
        Retrieve the full text of an article by its title.

        Args:
            title (str): Title of the article.

        Returns:
            Any: The full text of the article if found, otherwise None.
        """
        query = "SELECT full_text FROM articles WHERE title = ?"
        result = self._execute_query(query, (title,), fetch="one")
        return result[0] if result is not None else None
