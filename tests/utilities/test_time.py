from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
import pytz

from podcast.utilities.time import TimeUtility


# Fixture to freeze time for consistent testing
@pytest.fixture
def fixed_time():
    """Fixture to provide a fixed time for tests."""
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=pytz.utc)


# Test initializing TimeUtility with default timezone
def test_initialization(fixed_time):
    """Test that TimeUtility initializes with the default timezone and sets current time correctly."""
    with patch("podcast.utilities.time.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        time_utility = TimeUtility()
        assert time_utility.timezone.zone == "America/Los_Angeles"
        assert time_utility.current_time == fixed_time.astimezone(pytz.timezone("America/Los_Angeles"))


# Test initializing TimeUtility with a different timezone
def test_initialization_different_timezone(fixed_time):
    """Test that TimeUtility initializes with a custom timezone."""
    with patch("podcast.utilities.time.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        time_utility = TimeUtility(timezone="Europe/London")
        assert time_utility.timezone.zone == "Europe/London"
        assert time_utility.current_time == fixed_time.astimezone(pytz.timezone("Europe/London"))


# Test getting the current time
def test_current_time(fixed_time):
    """Test that the current time is returned correctly."""
    with patch("podcast.utilities.time.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        time_utility = TimeUtility()
        assert time_utility.current_time == fixed_time.astimezone(pytz.timezone("America/Los_Angeles"))


# Test getting the previous time with a time offset
def test_get_previous_time(fixed_time):
    """Test that getting the previous time returns the correct result."""
    with patch("podcast.utilities.time.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        time_utility = TimeUtility()
        previous_time = time_utility.get_time_offset(days=10)
        expected_time = fixed_time.astimezone(pytz.timezone("America/Los_Angeles")) - timedelta(days=10)
        assert previous_time == expected_time


# Test converting time to a string in a custom format
def test_convert_to_string(fixed_time):
    """Test that time is converted to a string in the correct format."""
    time_utility = TimeUtility()
    time_string = time_utility.convert_to_string(fixed_time)
    assert time_string == fixed_time.strftime("%Y%m%d%H%M")


# Test converting time for Apple format
def test_convert_for_apple(fixed_time):
    """Test that time is converted correctly for Apple format."""
    time_utility = TimeUtility()
    apple_string = time_utility.convert_for_apple(fixed_time)
    assert apple_string == fixed_time.strftime("%a, %-d %b %Y %H:%M:%S %z")


# Test converting time for filenames
def test_convert_for_filename(fixed_time):
    """Test that time is converted correctly for filenames."""
    time_utility = TimeUtility()
    filename_string = time_utility.convert_for_filename(fixed_time)
    assert filename_string == fixed_time.strftime("%Y%m%d%H%M")


# Test converting time for arXiv format
def test_convert_for_arxiv(fixed_time):
    """Test that time is converted correctly for arXiv format."""
    time_utility = TimeUtility()
    arxiv_string = time_utility.convert_for_arxiv(fixed_time)
    assert arxiv_string == fixed_time.strftime("%Y%m%d%H%M")


# Test converting time for bioRxiv format
def test_convert_for_biorxiv(fixed_time):
    """Test that time is converted correctly for bioRxiv format."""
    time_utility = TimeUtility()
    biorxiv_string = time_utility.convert_for_biorxiv(fixed_time)
    assert biorxiv_string == fixed_time.strftime("%Y-%m-%d")


# Test converting time for PubMed format
def test_convert_for_pubmed(fixed_time):
    """Test that time is converted correctly for PubMed format."""
    time_utility = TimeUtility()
    pubmed_string = time_utility.convert_for_pubmed(fixed_time)
    assert pubmed_string == fixed_time.strftime("%Y/%m/%d")
