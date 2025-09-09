from unittest.mock import MagicMock

import pytest

from podcast.assistants.communication import CommunicationAssistant
from podcast.managers.social_media import SocialMediaManager
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
def mock_social_media_manager():
    """Mock the SocialMediaManager class."""
    mock_manager = MagicMock(spec=SocialMediaManager)
    return mock_manager


@pytest.fixture
def communication_assistant(mock_utilities, mock_social_media_manager):
    """Create a CommunicationAssistant instance with a mocked SocialMediaManager."""
    assistant = CommunicationAssistant(path="/fake/path", utilities=mock_utilities)
    assistant.social_media_manager = mock_social_media_manager  # Inject mock
    return assistant


@pytest.fixture
def mock_episode():
    """Mock an episode with post content."""
    return {"post": "New episode available!"}


def test_communication_assistant_initialization(mock_utilities):
    """Test that CommunicationAssistant initializes correctly."""
    assistant = CommunicationAssistant(path="/test/path", utilities=mock_utilities)

    assert assistant.path == "/test/path"
    assert assistant.utilities is mock_utilities
    assert isinstance(assistant.social_media_manager, SocialMediaManager)


def test_post_to_social_media(communication_assistant, mock_social_media_manager, mock_episode):
    """Test that post_to_social_media calls post_to_bluesky on SocialMediaManager."""
    communication_assistant.post_to_social_media(mock_episode)

    # Assert that the method was called with the expected argument
    mock_social_media_manager.post_to_bluesky.assert_called_once_with(episode=mock_episode)
