from unittest.mock import patch

import pytest

from podcast.formats.episode import EpisodeInfo
from podcast.managers.database import DBManager
from podcast.utilities.bundle import UtilitiesBundle


@pytest.fixture
def mock_utilities_bundle(mocker):
    """Mock UtilitiesBundle, including logger and config."""
    mock_utilities = mocker.create_autospec(UtilitiesBundle)

    # Mock logger
    mock_utilities.logger = mocker.patch("logging.getLogger", autospec=True).return_value

    # Mock config
    mock_utilities.config = {"general_info": {"db_filename": "test_db.sqlite"}}

    return mock_utilities


@pytest.fixture
def db_manager(mock_utilities_bundle):
    """Fixture to create a DBManager instance with mocked utilities."""
    # Create an instance of DBManager
    return DBManager(path="/test_path/", utilities=mock_utilities_bundle)


@patch.object(DBManager, "_execute_query")
def test_article_described_in_podcast(mock_execute_query, db_manager):
    # Simulate the database returning that the article was described in the podcast
    mock_execute_query.return_value = [1]

    # Test the method
    result = db_manager.article_described_in_podcast("Test Article")

    # Assertions
    assert result is True
    mock_execute_query.assert_called_once_with(
        "SELECT described_in_podcast FROM articles WHERE title = ?", ("Test Article",), fetch="one"
    )


@patch.object(DBManager, "_execute_query")
def test_get_next_episode_number(mock_execute_query, db_manager):
    # Simulate the database returning the last episode as 5
    mock_execute_query.return_value = [5]

    # Test the method
    result = db_manager.get_next_episode_number()

    # Assertions
    assert result == 6
    mock_execute_query.assert_called_once_with(
        "SELECT episode FROM episodes ORDER BY episode DESC LIMIT 1", fetch="one"
    )


def test_add_episode_text_to_db(db_manager):
    episode_info = EpisodeInfo(
        title="Test Episode",
        description="This is a test episode.",
        citations="Test citations",
        persona="Test persona",
        voice="Test voice",
        script="Test script",
        season=1,
        episode=1,
        episode_type="Test type",
        pub_date="2025-02-11",
        post="Test post",
        guid=None,
        file_size=12345,
        articles=None,
    )

    with patch.object(db_manager, "_execute_query") as mock_execute_query:
        db_manager.add_episode_text_to_db(episode_info)

        # Check if _execute_query was called with the correct query and data
        mock_execute_query.assert_called_once()
        args, kwargs = mock_execute_query.call_args
        query = args[0]
        data = args[1]

        expected_query = """
            INSERT INTO Episodes (
                title, description, citations, persona, voice, script, season, episode,
                episode_type, pub_date, post, guid, file_size
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        assert query.strip() == expected_query.strip()
        assert data[:11] == (
            "Test Episode",
            "This is a test episode.",
            "Test citations",
            "Test persona",
            "Test voice",
            "Test script",
            1,
            1,
            "Test type",
            "2025-02-11",
            "Test post",
        )
        assert isinstance(data[11], str) and len(data[11]) == 36  # Validate that GUID is a UUID
        assert data[12] == 12345


@patch.object(DBManager, "_execute_query")
def test_insert_articles_into_db(mock_execute_query, db_manager):
    # Test article data
    articles = [
        {
            "title": "Test Article",
            "authors": ["Author 1", "Author 2"],
            "doi": "10.1234/testdoi",
            "abstract": "Test abstract",
            "full_text": "Test full text",
            "submitted_date": "2024-01-01",
            "url": "http://example.com",
            "full_text_locator": "",
            "strategy": "Test strategy",
            "score": 5,
            "score_justification": "High quality",
            "score_generated": 1,
            "full_text_available": 1,
            "described_in_podcast": 0,
        }
    ]

    # Test the method
    db_manager.insert_articles_into_db(articles)

    # Expected SQL query
    expected_query = """
        INSERT OR REPLACE INTO articles (
            title, authors, doi, abstract, full_text, submitted_date, url,
            full_text_locator, strategy, score, score_justification, score_generated,
            full_text_available, described_in_podcast
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """.replace(
        "\n", ""
    ).replace(
        " ", ""
    )  # Remove newlines and spaces for comparison

    # Expected data tuple
    data = (
        "Test Article",
        '["Author 1", "Author 2"]',
        "10.1234/testdoi",
        "Test abstract",
        "Test full text",
        "2024-01-01",
        "http://example.com",
        "",
        "Test strategy",
        5,
        "High quality",
        1,
        1,
        0,
    )

    # Get the actual query from the mock call
    actual_query = mock_execute_query.call_args[0][0].replace("\n", "").replace(" ", "")  # Strip whitespace

    # Assertions
    assert actual_query == expected_query
    mock_execute_query.assert_called_once_with(mock_execute_query.call_args[0][0], data, fetch="none")


@patch.object(DBManager, "_execute_query")
def test_get_article_score_justification(mock_execute_query, db_manager):
    # Simulate the database returning the score and justification
    mock_execute_query.return_value = [5, "High quality"]

    # Test the method
    score, justification = db_manager.get_article_score_justification("Test Article")

    # Assertions
    assert score == 5
    assert justification == "High quality"
    mock_execute_query.assert_called_once_with(
        "SELECT score, score_justification FROM articles WHERE title = ?", ("Test Article",), fetch="one"
    )


def test_retrieve_all_episodes_info(db_manager):
    mock_episodes = [
        (
            "Test Episode 1",
            "Description 1",
            "Citations 1",
            "Persona 1",
            "Voice 1",
            "Script 1",
            1,
            1,
            "Type 1",
            "2025-02-11",
            "Post 1",
            "guid-1",
            12345,
        ),
        (
            "Test Episode 2",
            "Description 2",
            "Citations 2",
            "Persona 2",
            "Voice 2",
            "Script 2",
            1,
            2,
            "Type 2",
            "2025-02-12",
            "Post 2",
            "guid-2",
            67890,
        ),
    ]

    with patch.object(db_manager, "_execute_query", return_value=mock_episodes) as mock_execute_query:
        episodes_list = db_manager.retrieve_all_episodes_info()

        # Check if _execute_query was called with the correct query
        mock_execute_query.assert_called_once_with(
            """
            SELECT
                title, description, citations, persona, voice, script, season, episode,
                episode_type, pub_date, post, guid, file_size
            FROM
                episodes
            ORDER BY
                episode DESC;
        """,
            fetch="all",
        )

        # Verify the returned episodes list
        assert len(episodes_list) == 2
        assert episodes_list[0] == {
            "title": "Test Episode 1",
            "description": "Description 1",
            "citations": "Citations 1",
            "persona": "Persona 1",
            "voice": "Voice 1",
            "script": "Script 1",
            "season": 1,
            "episode": 1,
            "episode_type": "Type 1",
            "pub_date": "2025-02-11",
            "post": "Post 1",
            "guid": "guid-1",
            "file_size": 12345,
            "articles": [],
        }
        assert episodes_list[1] == {
            "title": "Test Episode 2",
            "description": "Description 2",
            "citations": "Citations 2",
            "persona": "Persona 2",
            "voice": "Voice 2",
            "script": "Script 2",
            "season": 1,
            "episode": 2,
            "episode_type": "Type 2",
            "pub_date": "2025-02-12",
            "post": "Post 2",
            "guid": "guid-2",
            "file_size": 67890,
            "articles": [],
        }


@patch.object(DBManager, "_execute_query")
def test_fetch_full_text(mock_execute_query, db_manager):
    # Simulate the database returning the full text of an article
    mock_execute_query.return_value = ["Test full text"]

    # Test the method
    result = db_manager.fetch_full_text("Test Article")

    # Assertions
    assert result == "Test full text"
    mock_execute_query.assert_called_once_with(
        "SELECT full_text FROM articles WHERE title = ?", ("Test Article",), fetch="one"
    )
