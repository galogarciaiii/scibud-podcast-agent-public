from datetime import datetime, timedelta
from typing import Optional

import pytz


class TimeUtility:
    def __init__(self, timezone: str = "America/Los_Angeles") -> None:
        """
        Initialize the TimeUtility with a specific timezone.
        The time will be fixed at the moment of instantiation.
        """
        self.timezone = pytz.timezone(timezone)
        self._current_time = datetime.now(pytz.utc).astimezone(self.timezone)

    @property
    def current_time(self) -> datetime:
        """Return the fixed current time in the configured timezone."""
        return self._current_time

    def get_time_offset(self, days: int = 0, hours: int = 0, minutes: int = 0) -> datetime:
        """Return the time with a given offset in days, hours, and minutes."""
        return self.current_time - timedelta(days=days, hours=hours, minutes=minutes)

    def format_time(self, time: datetime, format_string: str) -> str:
        """Format the given time according to the provided format string."""
        return time.strftime(format_string)

    def convert_to_string(self, time: Optional[datetime] = None) -> str:
        """Convert the given time or fixed current time to string format YYYYMMDDHHMM."""
        if time is None:
            time = self.current_time
        return self.format_time(time, "%Y%m%d%H%M")

    def convert_for_apple(self, time: Optional[datetime] = None) -> str:
        """Convert the given time or fixed current time to Apple format."""
        if time is None:
            time = self.current_time
        return self.format_time(time, "%a, %-d %b %Y %H:%M:%S %z")

    def convert_for_filename(self, time: Optional[datetime] = None) -> str:
        """Convert the given time or fixed current time for filenames (YYYYMMDDHHMM)."""
        if time is None:
            time = self.current_time
        return self.format_time(time, "%Y%m%d%H%M")

    def convert_for_arxiv(self, time: Optional[datetime] = None) -> str:
        """Convert the given time or fixed current time to arXiv format (YYYYMMDDHHMM)."""
        if time is None:
            time = self.current_time
        return self.format_time(time, "%Y%m%d%H%M")

    def convert_for_biorxiv(self, time: Optional[datetime] = None) -> str:
        """Convert the given time or fixed current time to bioRxiv format (YYYY-MM-DD)."""
        if time is None:
            time = self.current_time
        return self.format_time(time, "%Y-%m-%d")

    def convert_for_pubmed(self, time: Optional[datetime] = None) -> str:
        """Convert the given time or fixed current time to PubMed format (YYYY/MM/DD)."""
        if time is None:
            time = self.current_time
        return self.format_time(time, "%Y/%m/%d")

    def convert_timezone(self, time: datetime, from_tz: str, to_tz: str) -> datetime:
        """Convert time from one timezone to another."""
        from_zone = pytz.timezone(from_tz)
        to_zone = pytz.timezone(to_tz)
        return time.astimezone(from_zone).astimezone(to_zone)
