from unittest.mock import MagicMock, patch

import pytest

from podcast.director import Director
from podcast.strategies.article_source import ArticleSourceStrategy
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities():
    utilities = MagicMock(spec=UtilitiesBundle)
    utilities.config = {
        "general_info": {
            "db_filename": "test_db.sqlite",
            "rss_filename": "test_rss.xml",
            "private_base_url": "http://localhost/",
            "audio_file_type": ".mp3",
            "bucket_name": "test_bucket",
        },
        "podcast_info": {
            "title": "Test Podcast",
            "podcast_link": "https://example.com",
            "description": "Test description",
            "author": "Test author",
        },
        "bluesky": {"handle": "scibud.bsky.social", "base_url": "https://bsky.social"},
    }
    utilities.logger = MagicMock()
    utilities.time = MagicMock()
    utilities.time.current_time.year = 2023
    return utilities


@pytest.fixture
def mock_strategies():
    return {"strategy1": MagicMock(spec=ArticleSourceStrategy), "strategy2": MagicMock(spec=ArticleSourceStrategy)}


@pytest.fixture
def director(mock_utilities, mock_strategies):
    return Director(utilities=mock_utilities, strategies=mock_strategies, path="/test/path/")


def test_generate_podcast_episode(director):
    with patch.object(director, "download_database") as mock_download_database, patch.object(
        director, "fetch_articles"
    ) as mock_fetch_articles, patch.object(director, "filter_new_articles") as mock_filter_new_articles, patch.object(
        director, "retrieve_full_text"
    ) as mock_retrieve_full_text, patch.object(
        director, "score_articles"
    ) as mock_score_articles, patch.object(
        director, "rank_articles"
    ) as mock_rank_articles, patch.object(
        director, "get_audio_path"
    ) as mock_get_audio_path, patch.object(
        director, "update_rss_feed"
    ) as mock_update_rss_feed, patch.object(
        director, "cleanup_database_file"
    ) as mock_cleanup_database_file, patch.object(
        director.storage_assistant, "get_next_episode_number"
    ) as mock_get_next_episode_number, patch.object(
        director.editorial_assistant, "generate_episode_text"
    ) as mock_generate_episode_text, patch.object(
        director.production_assistant, "generate_audio"
    ) as mock_generate_audio, patch.object(
        director.storage_assistant, "add_episode_text_to_db"
    ) as mock_add_episode_text_to_db, patch.object(
        director.storage_assistant, "retrieve_all_episodes_info"
    ) as mock_retrieve_all_episodes_info, patch.object(
        director.storage_assistant, "upload_file"
    ) as mock_upload_file, patch.object(
        director.storage_assistant, "insert_articles_into_db"
    ) as mock_insert_articles_into_db, patch.object(
        director.communication_assistant, "post_to_social_media"
    ) as mock_post_to_social_media:

        mock_fetch_articles.return_value = [
            {"title": "Article 1", "strategy": "strategy1", "full_text_available": False}
        ]
        mock_filter_new_articles.return_value = [
            {"title": "Article 1", "strategy": "strategy1", "full_text_available": False}
        ]
        mock_retrieve_full_text.return_value = [
            {"title": "Article 1", "strategy": "strategy1", "full_text": "Full text", "full_text_available": True}
        ]
        mock_score_articles.return_value = [
            {
                "title": "Article 1",
                "strategy": "strategy1",
                "full_text": "Full text",
                "full_text_available": True,
                "score": 10,
            }
        ]
        mock_rank_articles.return_value = [
            {
                "title": "Article 1",
                "strategy": "strategy1",
                "full_text": "Full text",
                "full_text_available": True,
                "score": 10,
            }
        ]
        mock_get_audio_path.return_value = "/test/path/audio/season_2023/episode_1.mp3"
        mock_get_next_episode_number.return_value = 1
        mock_generate_episode_text.return_value = {"script": "Episode script", "voice": "default"}
        mock_retrieve_all_episodes_info.return_value = []

        director.generate_podcast_episode()

        mock_download_database.assert_called_once()
        mock_fetch_articles.assert_called_once()
        mock_filter_new_articles.assert_called_once()
        mock_retrieve_full_text.assert_called_once()
        mock_score_articles.assert_called_once()
        mock_rank_articles.assert_called_once()
        mock_get_audio_path.assert_called_once()
        mock_generate_episode_text.assert_called_once()
        mock_generate_audio.assert_called_once()
        mock_add_episode_text_to_db.assert_called_once()
        mock_retrieve_all_episodes_info.assert_called_once()
        mock_update_rss_feed.assert_called_once()
        mock_insert_articles_into_db.assert_called_once()
        mock_upload_file.assert_called_once()
        mock_cleanup_database_file.assert_called_once()
        mock_post_to_social_media.assert_called_once()
