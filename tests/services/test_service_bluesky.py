from unittest.mock import ANY, MagicMock, patch

import pytest

from podcast.services.blue_sky import BlueSkyService
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities_bundle():
    mock_utilities = MagicMock(UtilitiesBundle)

    mock_time = MagicMock()
    mock_time.convert_for_biorxiv.side_effect = lambda time: time.strftime("%Y-%m-%d")

    mock_logger = MagicMock()
    mock_config = {
        "podcast_info": {"podcast_link": "https://scibud.media"},
        "bluesky": {"handle": "scibud.bsky.social", "base_url": "https://bsky.social"},
    }

    mock_utilities.time = mock_time
    mock_utilities.logger = mock_logger
    mock_utilities.config = mock_config

    return mock_utilities


@patch("podcast.services.blue_sky.requests.post")
@patch("podcast.services.blue_sky.load_dotenv")
@patch("podcast.services.blue_sky.os.getenv", return_value="mock_api_key")
def test_get_bluesky_api_key(mock_getenv, mock_load_dotenv, mock_post, mock_utilities_bundle):
    mock_post.return_value = MagicMock()
    service = BlueSkyService(mock_utilities_bundle)
    assert service.app_password == "mock_api_key"
    mock_getenv.assert_called_with("BLUESKY_API_KEY")


@patch("requests.post")
@patch.object(BlueSkyService, "get_bluesky_api_key", return_value="mock_password")
def test_authenticate_success(mock_get_api_key, mock_post, mock_utilities_bundle):
    mock_response = MagicMock()
    mock_response.json.return_value = {"accessJwt": "mock_token", "did": "mock_did"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    service = BlueSkyService(mock_utilities_bundle)
    assert service.session["accessJwt"] == "mock_token"
    assert service.session["did"] == "mock_did"
    mock_post.assert_called_with(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": "scibud.bsky.social", "password": "mock_password"},
    )


@patch("requests.post")
def test_refresh_auth_success(mock_post, mock_utilities_bundle):
    mock_response = MagicMock()
    mock_response.json.return_value = {"accessJwt": "new_mock_token"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    service = BlueSkyService(mock_utilities_bundle)
    service.session = {"refreshJwt": "mock_refresh_token"}
    service.refresh_auth()

    assert service.session["accessJwt"] == "new_mock_token"
    mock_post.assert_called_with(
        "https://bsky.social/xrpc/com.atproto.server.refreshSession",
        headers={"Authorization": "Bearer mock_refresh_token"},
    )


@patch("requests.post")
def test_post_to_bluesky_success(mock_post, mock_utilities_bundle):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "success"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    service = BlueSkyService(mock_utilities_bundle)
    service.session = {"accessJwt": "mock_token", "did": "mock_did"}
    service.post_to_bluesky("Test content")

    mock_post.assert_called_with(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": "Bearer mock_token"},
        json={
            "repo": "mock_did",
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": "Test content https://scibud.media",
                "createdAt": ANY,
                "facets": [
                    {
                        "index": {"byteStart": 12, "byteEnd": 33},
                        "features": [{"$type": "app.bsky.richtext.facet#link", "uri": "https://scibud.media"}],
                    }
                ],
            },
        },
    )


@pytest.mark.skip(reason="This test performs a real post to Bluesky and should only be run manually.")
def test_real_post_to_bluesky(mock_utilities_bundle):
    service = BlueSkyService(mock_utilities_bundle)
    service.authenticate()
    service.post_to_bluesky("This is a test post from an automated test.")
