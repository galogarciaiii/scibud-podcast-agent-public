from typing import List
from unittest.mock import patch

import pytest

from podcast.assistants.storage import StorageAssistant
from podcast.formats.article import ArticleInfo
from podcast.formats.episode import EpisodeInfo
from podcast.utilities.bundle import UtilitiesBundle


# Fixture to provide a mock UtilitiesBundle
@pytest.fixture
def mock_utilities_bundle(mocker):
    """Creates a mock UtilitiesBundle, including logger and other utilities."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger within UtilitiesBundle
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    return mock_utilities


# Fixture to provide a mock CloudStorageManager
@pytest.fixture
def mock_cloud_storage_manager():
    with patch("podcast.assistants.storage.CloudStorageManager", autospec=True) as mock:
        yield mock.return_value


# Fixture to provide a mock DBManager
@pytest.fixture
def mock_db_manager():
    with patch("podcast.assistants.storage.DBManager", autospec=True) as mock:
        yield mock.return_value


# Fixture to provide a mock LocalStorageManager
@pytest.fixture
def mock_local_storage_manager():
    with patch("podcast.assistants.storage.LocalStorageManager", autospec=True) as mock:
        yield mock.return_value


# Test case for downloading a file
def test_download_file(
    mock_utilities_bundle,
    mock_cloud_storage_manager,
    mock_db_manager,
    mock_local_storage_manager,
):
    storage_assistant = StorageAssistant(
        path="/mock/path/",
        utilities=mock_utilities_bundle,
    )

    local_file_name = "local_file.txt"
    cloud_file_name = "cloud_file.txt"

    storage_assistant.download_file(local_file_name, cloud_file_name)

    mock_cloud_storage_manager.download_file.assert_called_once_with(local_file_name, cloud_file_name)


# Test case for inserting articles into the database
def test_insert_articles_into_db(
    mock_utilities_bundle,
    mock_cloud_storage_manager,
    mock_db_manager,
    mock_local_storage_manager,
):
    storage_assistant = StorageAssistant(
        path="/mock/path/",
        utilities=mock_utilities_bundle,
    )

    articles: List[ArticleInfo] = [
        {
            "title": "Article 1",
            "authors": ["Author 1"],
            "doi": "10.1000/article1",
            "abstract": "Abstract 1",
            "full_text": "Full text 1",
            "submitted_date": "2023-01-01",
            "url": "https://example.com/article1",
            "full_text_locator": "locator1",
            "strategy": "strategy1",
            "score": None,
            "score_justification": "Justification 1",
            "score_generated": False,
            "full_text_available": True,
            "described_in_podcast": False,
        },
        {
            "title": "Article 2",
            "authors": ["Author 2"],
            "doi": "10.1000/article2",
            "abstract": "Abstract 2",
            "full_text": "Full text 2",
            "submitted_date": "2023-01-02",
            "url": "https://example.com/article2",
            "full_text_locator": "locator2",
            "strategy": "strategy2",
            "score": None,
            "score_justification": "Justification 2",
            "score_generated": False,
            "full_text_available": True,
            "described_in_podcast": False,
        },
    ]

    mock_new_articles: List[ArticleInfo] = [articles[0]]

    mock_db_manager.insert_articles_into_db.return_value = mock_new_articles

    storage_assistant.insert_articles_into_db(articles)

    mock_db_manager.insert_articles_into_db.assert_called_once_with(articles=articles)


# Test case for adding episode text to the database
def test_add_episode_text_to_db(
    mock_utilities_bundle,
    mock_cloud_storage_manager,
    mock_db_manager,
    mock_local_storage_manager,
):
    storage_assistant = StorageAssistant(
        path="/mock/path/",
        utilities=mock_utilities_bundle,
    )

    episode_info: EpisodeInfo = {
        "title": "Episode 1",
        "description": "Description 1",
        "citations": "citation text",
        "persona": "Persona 1",
        "voice": "Voice 1",
        "script": "Script 1",
        "season": 1,
        "episode": 1,
        "episode_type": "full",
        "pub_date": "2023-06-24T10:00:00Z",
        "post": "Post 1",
        "guid": None,
        "file_size": 0,
        "articles": None,
    }

    storage_assistant.add_episode_text_to_db(episode_info)

    mock_db_manager.add_episode_text_to_db.assert_called_once_with(episode_info=episode_info)


# Test case for getting the next season and episode numbers
def test_get_next_episode_number(
    mock_utilities_bundle,
    mock_cloud_storage_manager,
    mock_db_manager,
    mock_local_storage_manager,
):
    storage_assistant = StorageAssistant(
        path="/mock/path/",
        utilities=mock_utilities_bundle,
    )

    mock_db_manager.get_next_episode_number.return_value = (1, 2)

    episode_number = storage_assistant.get_next_episode_number()

    assert episode_number == (1, 2)
    mock_db_manager.get_next_episode_number.assert_called_once()


# Test case for retrieving all episodes info
def test_retrieve_all_episodes_info(
    mock_utilities_bundle,
    mock_cloud_storage_manager,
    mock_db_manager,
    mock_local_storage_manager,
):
    storage_assistant = StorageAssistant(
        path="/mock/path/",
        utilities=mock_utilities_bundle,
    )

    mock_episodes: List[EpisodeInfo] = [
        {
            "title": "Episode 1",
            "description": "Description 1",
            "citations": "citation text",
            "persona": "Persona 1",
            "voice": "Voice 1",
            "script": "Script 1",
            "season": 1,
            "episode": 1,
            "episode_type": "full",
            "pub_date": "2023-06-24T10:00:00Z",
            "post": "Post 1",
            "guid": None,
            "file_size": 0,
            "articles": None,
        },
        {
            "title": "Episode 2",
            "description": "Description 2",
            "citations": "citation text",
            "persona": "Persona 2",
            "voice": "Voice 2",
            "script": "Script 1",
            "season": 1,
            "episode": 1,
            "episode_type": "full",
            "pub_date": "2023-06-24T10:00:00Z",
            "post": "Post 2",
            "guid": None,
            "file_size": 0,
            "articles": None,
        },
    ]

    mock_db_manager.retrieve_all_episodes_info.return_value = mock_episodes

    episodes = storage_assistant.retrieve_all_episodes_info()

    assert episodes == mock_episodes
    mock_db_manager.retrieve_all_episodes_info.assert_called_once()


# Test case for uploading a string to a file
def test_upload_string_to_file(
    mock_utilities_bundle,
    mock_cloud_storage_manager,
    mock_db_manager,
    mock_local_storage_manager,
):
    storage_assistant = StorageAssistant(
        path="/mock/path/",
        utilities=mock_utilities_bundle,
    )

    string_content = "This is a test string."
    cloud_file_name = "cloud_file.txt"

    storage_assistant.upload_string_to_file(string_content, cloud_file_name)

    mock_cloud_storage_manager.upload_string_to_file.assert_called_once_with(
        string_content=string_content, cloud_file_name=cloud_file_name
    )


# Test case for uploading a file
def test_upload_file(
    mock_utilities_bundle,
    mock_cloud_storage_manager,
    mock_db_manager,
    mock_local_storage_manager,
):
    storage_assistant = StorageAssistant(
        path="/mock/path/",
        utilities=mock_utilities_bundle,
    )

    local_file_name = "local_file.txt"
    cloud_file_name = "cloud_file.txt"

    storage_assistant.upload_file(local_file_name, cloud_file_name)

    mock_cloud_storage_manager.upload_file.assert_called_once_with(
        local_file_name=local_file_name, cloud_file_name=cloud_file_name
    )


# Test case for removing a local file
def test_remove_local_file(
    mock_utilities_bundle,
    mock_cloud_storage_manager,
    mock_db_manager,
    mock_local_storage_manager,
):
    storage_assistant = StorageAssistant(
        path="/mock/path/",
        utilities=mock_utilities_bundle,
    )

    local_file_name = "local_file.txt"

    storage_assistant.remove_local_file(local_file_name)

    mock_local_storage_manager.remove_local_file.assert_called_once_with(local_file_name=local_file_name)


# New test case for getting article score and justification
def test_get_article_score_justification(
    mock_utilities_bundle,
    mock_cloud_storage_manager,
    mock_db_manager,
    mock_local_storage_manager,
):
    storage_assistant = StorageAssistant(
        path="/mock/path/",
        utilities=mock_utilities_bundle,
    )

    mock_db_manager.get_article_score_justification.return_value = (8, "Solid methodology")

    score, justification = storage_assistant.get_article_score_justification(title="Test Article")

    assert score == 8
    assert justification == "Solid methodology"
    mock_db_manager.get_article_score_justification.assert_called_once_with(title="Test Article")


# New test case for fetching full text
def test_fetch_full_text(
    mock_utilities_bundle,
    mock_cloud_storage_manager,
    mock_db_manager,
    mock_local_storage_manager,
):
    storage_assistant = StorageAssistant(
        path="/mock/path/",
        utilities=mock_utilities_bundle,
    )

    mock_db_manager.fetch_full_text.return_value = "Full text content here."

    full_text = storage_assistant.fetch_full_text(title="Test Article")

    assert full_text == "Full text content here."
    mock_db_manager.fetch_full_text.assert_called_once_with(title="Test Article")
