from typing import List
from unittest.mock import MagicMock, patch

import pytest

from podcast.assistants.production import ProductionAssistant
from podcast.formats.episode import EpisodeInfo
from podcast.utilities.bundle import UtilitiesBundle


# Fixture to provide a mock logger
@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("logging.getLogger", autospec=True).return_value


# Fixture to provide a mock strategy
@pytest.fixture
def mock_strategy():
    return MagicMock()


# Fixture to provide a mock utilities bundle
@pytest.fixture
def mock_utilities_bundle(mocker):
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    # Mock config
    mock_utilities.config = {
        "general_info": {
            "public_base_url": "https://example.com/",
            "logo_filename": "logo.png",
            "audio_file_type": ".wav",
        },
        "podcast_info": {
            "title": "Test Podcast",
            "website": "https://example.com",
            "language": "en",
            "copyright": "© 2023 Test Podcast",
            "artist_name": "Test Artist",
            "description": "This is a test podcast.",
            "type": "episodic",
            "primary_category": "Technology",
        },
    }

    return mock_utilities


# Fixture to provide a mock AudioManager
@pytest.fixture
def mock_audio_manager():
    with patch("podcast.assistants.production.AudioManager", autospec=True) as mock:
        yield mock.return_value


# Fixture to provide a mock RSSManager
@pytest.fixture
def mock_rss_manager():
    with patch("podcast.assistants.production.RSSManager", autospec=True) as mock:
        yield mock.return_value


# Test case for generating audio
def test_generate_audio(mock_utilities_bundle, mock_audio_manager, mock_rss_manager):
    production_assistant = ProductionAssistant(path="/test_path/", utilities=mock_utilities_bundle)

    script = "This is a test script."
    file_path = "test_path.wav"

    production_assistant.generate_audio(script=script, file_path=file_path, voice_option="mock_voice")

    mock_audio_manager.generate_audio.assert_called_once_with(
        script=script, file_path=file_path, voice_option="mock_voice"
    )


# Test case for generating an RSS feed
def test_generate_rss_feed(mock_utilities_bundle, mock_audio_manager, mock_rss_manager):
    production_assistant = ProductionAssistant(path="/test_path/", utilities=mock_utilities_bundle)

    episodes: List[EpisodeInfo] = [
        {
            "title": "Episode 1",
            "description": "Description 1",
            "citations": "Citation 1",
            "persona": "Persona 1",
            "voice": "voice 1",
            "script": "Script 1",
            "season": 1,
            "episode": 1,
            "episode_type": "full",
            "pub_date": "Mon, 20 Jun 2022 10:00:00 GMT",
            "post": "Post 1",
            "guid": "12345-abcde-67890-fghij",
            "file_size": 123456,
            "articles": None,
        },
        {
            "title": "Episode 2",
            "description": "Description 2",
            "citations": "Citation 2",
            "persona": "Persona 2",
            "voice": "Voice 2",
            "script": "Script 2",
            "season": 1,
            "episode": 2,
            "episode_type": "full",
            "pub_date": "Mon, 27 Jun 2022 10:00:00 GMT",
            "post": "Post 2",
            "guid": "22345-bcdef-67890-ghijk",
            "file_size": 123456,
            "articles": None,
        },
    ]

    mock_rss_xml = "<rss>Mock RSS Feed</rss>"
    mock_rss_manager.generate_rss_feed.return_value = mock_rss_xml

    rss_xml = production_assistant.generate_rss_feed(episodes=episodes)

    assert rss_xml == mock_rss_xml
    mock_rss_manager.generate_rss_feed.assert_called_once_with(episodes=episodes)
