from datetime import datetime
from unittest.mock import patch

import pytest

from podcast.managers.rss import RSSManager
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def sample_episodes():
    """Fixture to provide a sample list of episodes."""
    return [
        {
            "title": "Episode 1",
            "description": "This is the first episode.",
            "season": 1,
            "episode": 1,
            "guid": "episode-1-guid",
            "pub_date": "Mon, 08 Jan 2024 00:00:00 +0000",
            "file_size": 123456,
            "citations": "Citation for episode 1",
        },
        {
            "title": "Episode 2",
            "description": "This is the second episode.",
            "season": 1,
            "episode": 2,
            "guid": "episode-2-guid",
            "pub_date": "Mon, 15 Jan 2024 00:00:00 +0000",
            "file_size": 234567,
            "citations": "",
        },
    ]


@pytest.fixture
def mock_utilities_bundle(mocker):
    """Fixture to mock UtilitiesBundle, including logger and config."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger inside utilities bundle
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    # Mock config inside utilities bundle, combining the previous sample_config
    mock_utilities.config = {
        "general_info": {
            "public_base_url": "https://example.com/",
            "logo_filename": "logo.png",
            "audio_file_type": ".mp3",
        },
        "podcast_info": {
            "title": "Sample Podcast",
            "podcast_link": "https://example.com/podcast",
            "language": "en",
            "copyright": "2023 Sample Podcast",
            "artist_name": "Sample Author",
            "description": "This is a sample podcast description.",
            "primary_category": "Science",
            "type": "episodic",
            "episode_type": "full",
        },
    }

    return mock_utilities


@pytest.fixture
def rss_manager(mock_utilities_bundle):
    """Fixture to provide an RSSManager instance."""
    return RSSManager(path="/mockpath/", utilities=mock_utilities_bundle)


def test_generate_rss_feed_success(rss_manager, sample_episodes, mock_utilities_bundle):
    """Test generating an RSS feed successfully."""
    # Call the generate_rss_feed method
    rss_feed = rss_manager.generate_rss_feed(sample_episodes)

    # Verify that the RSS feed is a non-empty string
    assert isinstance(rss_feed, str)
    assert "<rss" in rss_feed
    assert "</rss>" in rss_feed

    # Check if the logger debug method was called
    mock_utilities_bundle.logger.debug.assert_called_once_with("RSS XML string generated.")


def test_generate_rss_feed_no_citations(rss_manager, sample_episodes, mock_utilities_bundle):
    """Test generating an RSS feed where some episodes have no citations."""
    sample_episodes[1]["citations"] = ""  # Ensure episode 2 has no citations

    # Call the generate_rss_feed method
    rss_feed = rss_manager.generate_rss_feed(sample_episodes)

    # Check that the 'comments' field for episode 2 defaults to 'None'
    assert "None" in rss_feed

    # Check that the RSS feed contains valid data for both episodes
    assert "Episode 1" in rss_feed
    assert "Episode 2" in rss_feed


def test_generate_rss_feed_handles_error(rss_manager, mock_utilities_bundle):
    """Test that an error during RSS feed generation raises a RuntimeError."""
    # Mock a faulty configuration that raises an exception
    rss_manager.utilities.config["podcast_info"] = None

    # Call the method and expect a RuntimeError
    with pytest.raises(RuntimeError, match="An error occurred during the RSS feed generation"):
        rss_manager.generate_rss_feed([])

    # Verify that the logger error method was called
    mock_utilities_bundle.logger.error.assert_called_once()


def test_rss_feed_has_required_episode_fields(rss_manager, sample_episodes):
    """Test that each episode in the RSS feed contains the required fields."""
    rss_feed = rss_manager.generate_rss_feed(sample_episodes)

    # Verify that the feed contains titles, descriptions, and publication dates for episodes
    for episode in sample_episodes:
        assert episode["title"] in rss_feed
        assert episode["description"] in rss_feed

        # Parse the pub_date using the correct format with %z for numeric timezones
        pub_date = datetime.strptime(episode["pub_date"], "%a, %d %b %Y %H:%M:%S %z")

        # Convert the parsed datetime back to the string format used in the RSS feed
        pub_date_formatted = pub_date.strftime("%a, %d %b %Y %H:%M:%S %z")

        # Assert that the formatted pub_date is in the rss_feed
        assert pub_date_formatted in rss_feed


@patch("feedgen.feed.FeedGenerator.rss_str")
def test_generate_rss_feed_calls_rss_str(mock_rss_str, rss_manager, sample_episodes):
    """Test that the FeedGenerator's rss_str method is called."""
    rss_manager.generate_rss_feed(sample_episodes)

    # Verify that rss_str is called once
    mock_rss_str.assert_called_once()


def test_audio_url_formatting(rss_manager, sample_episodes):
    """Test that the audio URLs are formatted correctly in the RSS feed."""
    rss_feed = rss_manager.generate_rss_feed(sample_episodes)

    # Check that the audio URL format is correct for each episode
    for episode in sample_episodes:
        expected_audio_url = (
            f"https://example.com//mockpath/audio/season_{episode['season']}/episode_{episode['episode']}.mp3"
        )
        assert expected_audio_url in rss_feed
