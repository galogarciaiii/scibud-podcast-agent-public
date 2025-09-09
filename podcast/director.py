from typing import Dict, List

from podcast.assistants.communication import CommunicationAssistant
from podcast.assistants.editorial import EditorialAssistant
from podcast.assistants.production import ProductionAssistant
from podcast.assistants.retrieval import RetrievalAssistant
from podcast.assistants.storage import StorageAssistant
from podcast.formats.article import ArticleInfo
from podcast.formats.episode import EpisodeInfo
from podcast.strategies.article_source import ArticleSourceStrategy
from podcast.utilities.bundle import UtilitiesBundle


class Director:
    """
    The Director class is responsible for managing the end-to-end process of generating a podcast episode.
    It coordinates the actions of various assistants (retrieval, storage, editorial, production) and implements
    the logic for downloading databases, retrieving articles, generating scripts, creating audio, and updating
    the RSS feed.
    """

    def __init__(self, utilities: UtilitiesBundle, strategies: Dict[str, ArticleSourceStrategy], path: str) -> None:
        self.utilities = utilities
        self.strategies = strategies
        self.path = path

        # Initialize assistants with the utilities bundle directly
        self.storage_assistant = StorageAssistant(path=self.path, utilities=self.utilities)
        self.production_assistant = ProductionAssistant(path=self.path, utilities=self.utilities)
        self.editorial_assistant = EditorialAssistant(path=self.path, utilities=self.utilities)
        self.communication_assistant = CommunicationAssistant(path=self.path, utilities=self.utilities)

        self.db_file_name = self.utilities.config["general_info"]["db_filename"]
        self.rss_filename = self.utilities.config["general_info"]["rss_filename"]

    def generate_podcast_episode(self) -> None:
        try:
            # Step 1: Download database from cloud storage
            self.download_database()
            self.utilities.logger.info("Database successfully downloaded.")

            # Step 2: Fetch articles from sources defined by the user.
            all_articles = self.fetch_articles()
            all_articles_count = len(all_articles)
            self.utilities.logger.info(f"Fetched {all_articles_count} articles.")

            # Step 3: Filter out any articles that have already been described in the podcast.
            new_articles = self.filter_new_articles(all_articles)
            if not new_articles:
                self.utilities.logger.warning("No new articles found. Podcast generation aborted.")
                return
            new_articles_count = len(new_articles)
            self.utilities.logger.info(f"There are {new_articles_count} articles that have not been podcasted.")

            # Step 4:: Retrieve the full text for the articles
            articles_with_full_text = self.retrieve_full_text(new_articles)
            if not articles_with_full_text:
                self.utilities.logger.warning("No articles with full text available. Podcast generation aborted.")
                return
            self.utilities.logger.info("Full text retrieved.")

            # Step 5: Score articles
            scored_articles = self.score_articles(articles_with_full_text)
            self.utilities.logger.info("Articles scored.")

            # Step 6: Rank articles
            ranked_articles_sorted = self.rank_articles(scored_articles)
            top_article = ranked_articles_sorted[0]
            top_article_title = top_article["title"]
            top_article_score = top_article["score"]
            self.utilities.logger.info(
                f"Top article chosen with score : {top_article_score}, and title: {top_article_title}."
            )

            # Step 7: Ensure the score present and 8 or above
            score = top_article.get("score")
            if score is None or score < 9:
                self.utilities.logger.warning("Top article score is below 9. Podcast generation aborted.")
                return

            # Step 8: Get episode and season numbers for the new episode
            episode_number = self.storage_assistant.get_next_episode_number()
            season_number = self.utilities.time.current_time.year

            # Step 9: Generate script for the episode
            episode = self.editorial_assistant.generate_episode_text(top_article, season_number, episode_number)
            self.utilities.logger.info("Episode script generated successfully.")

            # Step 10: Generate audio for the episode
            audio_path = self.get_audio_path(season_number, episode_number)
            # Get the single value when there's only one entry
            voice = episode["voice"]
            self.production_assistant.generate_audio(script=episode["script"], file_path=audio_path, voice_option=voice)
            self.utilities.logger.info("Audio generated successfully.")

            # Step 11: Add episode information to the database
            self.storage_assistant.add_episode_text_to_db(episode)
            self.utilities.logger.info("Episode info added to the database.")

            # Step 12: Update the RSS feed
            episodes = self.storage_assistant.retrieve_all_episodes_info()
            self.update_rss_feed(episodes)
            self.utilities.logger.info("RSS feed updated.")

            # Step 13: Post to social media
            self.communication_assistant.post_to_social_media(episode=episode)

            # Step 14: Add article info to the database
            ranked_articles_sorted[0]["described_in_podcast"] = True
            self.add_articles_to_db(articles=ranked_articles_sorted)

            # Step 15: Upload the database to the Google Cloud bucket
            self.storage_assistant.upload_file(self.db_file_name, self.db_file_name)
            self.utilities.logger.info("Database uploaded to the Google Cloud bucket.")

        finally:

            # Step 15: Delete local database file
            self.cleanup_database_file()
            self.utilities.logger.info("Local database file removed.")

    # Helper Functions

    def download_database(self) -> None:
        """
        Downloads the database from cloud storage.
        """
        self.storage_assistant.download_file(local_file_name=self.db_file_name, cloud_file_name=self.db_file_name)

    def fetch_articles(self) -> List[ArticleInfo]:
        """
        Fetches articles using the retrieval assistant for each strategy.
        """
        all_articles = []
        for strategy_name, strategy_instance in self.strategies.items():
            self.utilities.logger.info(f"Fetching articles from {strategy_name}.")
            retrieval_assistant = RetrievalAssistant(strategy=strategy_instance, utilities=self.utilities)
            articles = retrieval_assistant.fetch_articles()
            all_articles.extend(articles)
        return all_articles

    def filter_new_articles(self, articles: List[ArticleInfo]) -> List[ArticleInfo]:
        """
        Filters out articles that have already been described in the podcast.
        """
        new_articles = [
            article for article in articles if not self.storage_assistant.article_described_in_podcast(article["title"])
        ]
        return new_articles

    def retrieve_full_text(self, new_articles: List[ArticleInfo]) -> List[ArticleInfo]:
        """
        Retrieves the full text of articles, if available.
        """
        # Step 4: Retrieve full text of the articles
        try:
            articles_with_full_text = []  # Modified: list to store articles with full text
            for article in new_articles:
                full_text = self.storage_assistant.fetch_full_text(article["title"])

                if full_text is not None:
                    article["full_text"] = full_text
                    article["full_text_available"] = True
                    self.utilities.logger.debug(f"Existing full text found for '{article['title']}': {full_text}")
                else:
                    if not article["full_text_available"]:
                        strategy_key = article["strategy"]
                        strategy = self.strategies[strategy_key]
                        full_text_locator = article["full_text_locator"]
                        retrieval_assistant = RetrievalAssistant(strategy=strategy, utilities=self.utilities)
                        full_text = retrieval_assistant.fetch_full_text(full_text_locator=full_text_locator)
                        if full_text is None:  # Modified: skip article if full text is unavailable
                            self.utilities.logger.warning(
                                f"Full text not available for '{article['title']}', skipping article."
                            )
                            continue  # Skip this article if full text is not available
                        article["full_text"] = full_text
                        article["full_text_available"] = True
                        short_text = full_text[:50] + "..."
                        self.utilities.logger.info(
                            f"Full text retrieved for article '{article['title']}'. Full text: {short_text}"
                        )

                # Modified: Add article to the list if full text is available
                articles_with_full_text.append(article)
            return articles_with_full_text

        except Exception as e:
            self.utilities.logger.error(f"Error retrieving full text for articles: {e}")
            raise Exception("Failed to retrieve full text.")

    def log_score_statistics(self, articles: List[ArticleInfo]) -> None:
        scores = [article["score"] for article in articles if article["score"] is not None]
        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            self.utilities.logger.info(
                f"Score Statistics - Average: {avg_score:.2f}, Min: {min_score}, Max: {max_score}"
            )
        else:
            self.utilities.logger.info("No scores available to compute statistics.")

    def score_articles(self, articles: List[ArticleInfo]) -> List[ArticleInfo]:
        try:
            for article in articles:
                # Check if the article already has a score in the database
                score, justification = self.storage_assistant.get_article_score_justification(article["title"])
                article["score"] = score
                article["score_justification"] = justification

                if score != -1:
                    self.utilities.logger.info(f"Existing score found for '{article['title']}': {score}")
                else:
                    # If no score exists, generate one and save it
                    self.utilities.logger.info(f"No score found for article '{article['title']}', generating score.")
                    generated_score, justification = self.editorial_assistant.score_article(article=article)
                    article["score"] = generated_score
                    article["score_generated"] = True
                    article["score_justification"] = justification
                    self.utilities.logger.info(f"Generated score {generated_score} for article '{article['title']}'.")

            # Log score statistics after processing all articles
            self.log_score_statistics(articles)

            return articles
        except Exception as e:
            self.utilities.logger.error(f"An error occurred during article scoring: {str(e)}")
            raise

    def rank_articles(self, articles: List[ArticleInfo]) -> List[ArticleInfo]:
        """
        Ranks articles by their score.
        """
        ranked_articles_sorted = sorted(
            articles, key=lambda x: x["score"] if x["score"] is not None else -1, reverse=True
        )
        return ranked_articles_sorted

    def get_audio_path(self, season_number: int, episode_number: int) -> str:
        """
        Constructs the path for the audio file.
        """
        return str(
            self.utilities.config["general_info"]["private_base_url"]
            + self.path
            + "audio/season_"
            + str(season_number)
            + "/episode_"
            + str(episode_number)
            + self.utilities.config["general_info"]["audio_file_type"]
        )

    def update_rss_feed(self, episodes: List[EpisodeInfo]) -> None:
        """
        Updates and uploads the RSS feed to cloud storage.
        """
        rss_xml = self.production_assistant.generate_rss_feed(episodes=episodes)
        self.utilities.logger.info("RSS feed generated successfully.")
        self.storage_assistant.upload_string_to_file(rss_xml, cloud_file_name=self.rss_filename)
        self.utilities.logger.info("RSS feed uploaded to cloud storage.")

    def cleanup_database_file(self) -> None:
        """
        Cleans up the local database file after the process completes.
        """
        try:
            self.storage_assistant.remove_local_file(local_file_name=(self.path + self.db_file_name))
            self.utilities.logger.debug("Local database file removed.")
        except Exception as e:
            self.utilities.logger.error(f"Error removing local file: {e}")

    def add_articles_to_db(self, articles: List[ArticleInfo]) -> None:
        try:
            self.storage_assistant.insert_articles_into_db(articles=articles)
            self.utilities.logger.info("Articles added to the database successfully.")
        except Exception as e:
            self.utilities.logger.error(f"Error adding articles to the database: {e}")
            raise Exception("Failed to add articles to the database.")
