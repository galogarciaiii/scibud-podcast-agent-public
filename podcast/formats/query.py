from datetime import datetime
from typing import Optional


class QueryParams:
    """
    A class to bundle query-related parameters.
    """

    def __init__(
        self, query: str, min_date: Optional[datetime], max_date: Optional[datetime], max_results: Optional[int] = 50
    ) -> None:
        self.query = query
        self.min_date = min_date
        self.max_date = max_date
        self.max_results = max_results
