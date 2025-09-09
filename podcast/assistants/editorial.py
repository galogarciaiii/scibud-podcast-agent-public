import random
from typing import Any, Tuple

from podcast.formats.article import ArticleInfo
from podcast.formats.episode import EpisodeInfo
from podcast.managers.text_gen import TextGenerationManager
from podcast.utilities.bundle import UtilitiesBundle


class EditorialAssistant:
    """
    The EditorialAssistant class handles the generation of podcast episode content,
    including episode scripts, descriptions, citations, and ranking of articles
    based on pre-defined strategies.

    Attributes:
        logger (logging.Logger): Logger to handle logging operations.
        config (Dict[str, Any]): Configuration dictionary containing settings for the assistant.
        time (TimeUtility): Utility for managing time-related operations.
        strategy (ArticleSourceStrategy): Strategy for sourcing articles.
        prompt_manager (PromptManager): Manager for generating prompts used for text generation.
        text_generation_manager (TextGenerationManager):
            Manager for generating episode text (script, title, description).
    """

    def __init__(self, path: str, utilities: UtilitiesBundle) -> None:
        """
        Initializes the EditorialAssistant with the necessary managers and configurations.

        Args:
            logger (logging.Logger): Logger instance for logging information and errors.
            config (Dict[str, Any]): Configuration dictionary with settings.
            time (TimeUtility): Time utility instance to handle time conversions and current time retrieval.
            strategy (ArticleSourceStrategy): Strategy to handle the retrieval and processing of article data.
        """
        self.path: str = path
        self.utilities = utilities
        self.text_generation_manager: TextGenerationManager = TextGenerationManager(
            path=self.path, utilities=self.utilities
        )

    def generate_episode_text(self, article: ArticleInfo, season_number: int, episode_number: int) -> EpisodeInfo:
        """
        Generates the episode text including title, description, citations, and script based on new articles.

        Args:
            new_articles (List[ArticleDict]): List of articles to be discussed in the episode.
            season_number (int): The season number of the podcast.
            episode_number (int): The episode number within the season.

        Returns:
            EpisodeInfo: A dictionary containing all the episode text details,
                        such as title, description, script, etc.

        Raises:
            Exception: If any error occurs during the episode text generation process.
        """
        try:
            # Choose reporter persona randomly
            voice_option: dict = random.choice(self.utilities.config["google_tts"]["voice_options"])
            self.utilities.logger.info("Selected Option: %s", voice_option)
            persona = list(voice_option.keys())[0]
            voice = voice_option[persona]

            # Generate the script prompt for the provided articles
            script: str = self.text_generation_manager.generate_script(article=article, persona=persona)
            description: str = self.text_generation_manager.generate_description(script=script)
            title: str = self.text_generation_manager.generate_title(script=script)

            # Generate the social media post
            post: str = self.text_generation_manager.generate_social_media_post(script=script)

            # Get the current time in the appropriate format for publication
            current_time_object: Any = self.utilities.time.current_time
            current_time: str = self.utilities.time.convert_for_apple(current_time_object)

            episode_text: EpisodeInfo = {
                "title": title,
                "description": description,
                "citations": article["url"],
                "persona": persona,
                "voice": voice,
                "script": script,
                "season": season_number,
                "episode": episode_number,
                "episode_type": "full",
                "pub_date": current_time,
                "post": post,
                "guid": "",
                "file_size": 0,  # You can update this later when file size is known
                "articles": [article],
            }

            self.utilities.logger.info("Next season, episode numbers: %d, %d", season_number, episode_number)
            return episode_text
        except Exception as e:
            self.utilities.logger.error(f"An error occurred while generating the next episode info: {str(e)}")
            raise

    def score_article(self, article: ArticleInfo) -> Tuple[int, str]:
        """
        Ranks an article using the PromptManager and OpenAI's text generation model.

        Args:
            article (ArticleInfo): The article to be ranked.

        Returns:
            Tuple[int, str]: A tuple where the first element is the score (int),
            and the second is the justification (str).

        Raises:
            Exception: If ranking fails due to an error.
        """
        try:
            score, justification = self.text_generation_manager.generate_score(article=article)

            self.utilities.logger.info(f"Article '{article['title']}' ranked with a score of {score}.")
            return score, justification

        except Exception as e:
            self.utilities.logger.error(f"Failed to rank article '{article['title']}': {str(e)}")
            raise
