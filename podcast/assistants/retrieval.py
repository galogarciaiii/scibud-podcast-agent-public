from typing import List

from podcast.formats.article import ArticleInfo
from podcast.strategies.article_source import ArticleSourceStrategy
from podcast.utilities.bundle import UtilitiesBundle


class RetrievalAssistant:
    def __init__(self, strategy: ArticleSourceStrategy, utilities: UtilitiesBundle) -> None:
        self.strategy: ArticleSourceStrategy = strategy
        self.utilities: UtilitiesBundle = utilities

    def fetch_articles(self) -> List[ArticleInfo]:
        articles = self.strategy.fetch_articles()
        return articles

    def fetch_full_text(self, full_text_locator: str) -> str:
        full_text = self.strategy.fetch_full_text(full_text_locator=full_text_locator)
        return full_text
