from typing import Any, List, Tuple

from podcast.formats.article import ArticleInfo
from podcast.formats.episode import EpisodeInfo
from podcast.managers.cloud_storage import CloudStorageManager
from podcast.managers.database import DBManager
from podcast.managers.local_storage import LocalStorageManager
from podcast.utilities.bundle import UtilitiesBundle


class StorageAssistant:
    """
    The StorageAssistant class handles all file and database operations related to podcast generation.
    It serves as a middle layer that coordinates between different managers such as CloudStorageManager,
    DBManager, and LocalStorageManager.

    Attributes:
        strategy (ArticleSourceStrategy): Strategy for managing article source and configurations.
        time (TimeUtility): Utility for managing time-related operations.
        logger (logging.Logger): Logger for logging operations and errors.
        config (Dict[str, Any]): Configuration settings for the podcast.
        cloud_storage_manager (CloudStorageManager): Manager for interacting with cloud storage.
        db_manager (DBManager): Manager for interacting with the database.
        local_storage_manager (LocalStorageManager): Manager for handling local file storage.
    """

    def __init__(self, path: str, utilities: UtilitiesBundle) -> None:
        self.path = path
        self.utilities = utilities
        self.cloud_storage_manager = CloudStorageManager(path=self.path, utilities=self.utilities)
        self.db_manager = DBManager(path=self.path, utilities=self.utilities)
        self.local_storage_manager = LocalStorageManager(utilities=self.utilities)

    def download_file(self, local_file_name: str, cloud_file_name: str) -> None:
        self.cloud_storage_manager.download_file(local_file_name, cloud_file_name)

    def article_described_in_podcast(self, title: str) -> bool:
        return self.db_manager.article_described_in_podcast(title=title)

    def insert_articles_into_db(self, articles: List[ArticleInfo]) -> None:
        return self.db_manager.insert_articles_into_db(articles=articles)

    def add_episode_text_to_db(self, episode_info: EpisodeInfo) -> None:
        self.db_manager.add_episode_text_to_db(episode_info=episode_info)
        pass

    def get_next_episode_number(self) -> int:
        episode_number = self.db_manager.get_next_episode_number()
        return episode_number

    def retrieve_all_episodes_info(self) -> List[EpisodeInfo]:
        episodes = self.db_manager.retrieve_all_episodes_info()
        return episodes

    def upload_string_to_file(self, string_content: str, cloud_file_name: str) -> None:
        self.cloud_storage_manager.upload_string_to_file(string_content=string_content, cloud_file_name=cloud_file_name)

    def upload_file(self, local_file_name: str, cloud_file_name: str) -> None:
        self.cloud_storage_manager.upload_file(local_file_name=local_file_name, cloud_file_name=cloud_file_name)

    def remove_local_file(self, local_file_name: str) -> None:
        self.local_storage_manager.remove_local_file(local_file_name=local_file_name)

    def get_article_score_justification(self, title: str) -> Tuple[int, str]:
        return self.db_manager.get_article_score_justification(title=title)

    def fetch_full_text(self, title: str) -> Any:
        return self.db_manager.fetch_full_text(title=title)
