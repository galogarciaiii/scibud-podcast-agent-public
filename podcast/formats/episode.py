from typing import List, Optional, TypedDict

from podcast.formats.article import ArticleInfo


class EpisodeInfo(TypedDict):
    title: str
    description: str
    citations: str
    persona: str
    voice: str
    script: str
    season: int
    episode: int
    episode_type: str
    pub_date: str
    post: str
    guid: Optional[str]
    file_size: int
    articles: Optional[List[ArticleInfo]]
