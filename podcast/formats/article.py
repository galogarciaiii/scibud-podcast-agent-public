from typing import List, Optional, TypedDict


class ArticleInfo(TypedDict):
    title: str
    authors: List[str]
    doi: str
    abstract: str
    full_text: str
    submitted_date: str
    url: str
    full_text_locator: str
    strategy: str
    score: Optional[int]
    score_justification: str
    score_generated: bool
    full_text_available: bool
    described_in_podcast: bool
