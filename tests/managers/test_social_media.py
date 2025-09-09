from unittest.mock import MagicMock

import pytest

from podcast.managers.social_media import SocialMediaManager
from podcast.services.blue_sky import BlueSkyService
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities():
    """Mock the utility bundle and its components."""
    mock_utilities = MagicMock(spec=UtilitiesBundle)

    # Mock time utility and logger
    mock_time = MagicMock()
    mock_logger = MagicMock()

    # Mock config
    mock_config = {
        "podcast_info": {
            "title": "Test Podcast",
            "podcast_link": "https://example.com",
        },
        "bluesky": {"handle": "scibud.bsky.social", "base_url": "https://bsky.social"},
    }

    # Assign mocks
    mock_utilities.time = mock_time
    mock_utilities.logger = mock_logger
    mock_utilities.config = mock_config

    return mock_utilities


@pytest.fixture
def mock_bluesky_service():
    """Mock the BlueSkyService class."""
    service = MagicMock(spec=BlueSkyService)
    service.authenticate.return_value = None  # Mock authentication
    service.post_to_bluesky.return_value = None  # Mock posting
    return service


@pytest.fixture
def social_media_manager(mock_utilities, mock_bluesky_service):
    """Create a SocialMediaManager instance and inject the mocked BlueSkyService."""
    manager = SocialMediaManager(path="/fake/path", utilities=mock_utilities)
    manager.bluesky_service = mock_bluesky_service  # Inject mock service
    return manager


@pytest.fixture
def mock_episode():
    """Mock an episode with post content."""
    return {"post": "New episode available!"}


def test_post_to_bluesky(social_media_manager, mock_episode, mock_bluesky_service):
    """Test posting an episode to Bluesky."""
    social_media_manager.post_to_bluesky(mock_episode)
    expected_post = "New episode available!"

    # Debugging prints
    print("Mock service:", social_media_manager.bluesky_service)
    print("authenticate() called?", mock_bluesky_service.authenticate.call_count)
    print("Mock calls:", mock_bluesky_service.mock_calls)

    # Assertions
    mock_bluesky_service.authenticate.assert_called_once()
    mock_bluesky_service.post_to_bluesky.assert_called_once_with(post=expected_post)
