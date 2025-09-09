from typing import Optional, Tuple

from podcast.formats.article import ArticleInfo
from podcast.utilities.bundle import UtilitiesBundle


class PromptHelper:
    def __init__(self, path: str, utilities: UtilitiesBundle) -> None:
        self.path: str = path
        self.utilities: UtilitiesBundle = utilities

    def assemble_script_prompts(self, article: ArticleInfo, persona: str) -> Tuple[str, str]:
        """Generates the script prompt based on the articles."""
        try:
            self.utilities.logger.debug("Starting to generate podcast script prompt.")

            # Read the system and user prompt templates from files
            system_prompt = self.read_prompt_from_file(
                path=self.path + self.utilities.config["general_info"]["script_system_prompt_filename"]
            )
            prompt_without_article = self.read_prompt_from_file(
                path=self.path + self.utilities.config["general_info"]["script_user_prompt_filename"]
            )

            # Ensure neither prompt is None
            if system_prompt is None:
                raise ValueError("System prompt could not be read from file.")
            if prompt_without_article is None:
                raise ValueError("User prompt could not be read from file.")

            if not all(key in article for key in ["title", "abstract", "full_text"]):
                self.utilities.logger.error(f"Missing data in article: {article}")

            # Using the first article for demonstration; adjust logic for multiple articles as needed
            title = article["title"]
            abstract = article["abstract"]
            full_text = article["full_text"]
            critique = article["score_justification"]
            reporter_name = persona

            # Dynamically insert article information into the prompt template
            user_prompt = prompt_without_article.format(
                title=title, abstract=abstract, full_text=full_text, critique=critique, reporter_name=reporter_name
            )

            self.utilities.logger.debug("Script prompt generated successfully.")
            return system_prompt, user_prompt

        except Exception as e:
            self.utilities.logger.error(f"Failed to generate script prompt: {e}")
            raise Exception(f"Error generating prompt: {e}")

    def assemble_description_prompts(self, script: str) -> Tuple[str, str]:
        """Generates the description prompt based on the articles."""
        try:
            self.utilities.logger.debug("Starting to generate podcast description prompt.")

            # Read the system and user prompt templates from files
            system_prompt = self.read_prompt_from_file(
                path=self.path + self.utilities.config["general_info"]["description_system_prompt_filename"]
            )
            prompt_without_script = self.read_prompt_from_file(
                path=self.path + self.utilities.config["general_info"]["description_user_prompt_filename"]
            )

            # Ensure neither prompt is None
            if system_prompt is None:
                raise ValueError("System prompt could not be read from file.")
            if prompt_without_script is None:
                raise ValueError("User prompt could not be read from file.")

            # Dynamically insert script into the prompt template
            user_prompt = prompt_without_script.format(script=script)

            self.utilities.logger.debug("Description prompt generated successfully.")
            return system_prompt, user_prompt

        except Exception as e:
            self.utilities.logger.error(f"Failed to generate description prompt: {e}")
            raise Exception(f"Error generating prompt: {e}")

    def assemble_scoring_prompts(self, article: ArticleInfo) -> Tuple[str, str]:
        """Generates the scoring prompt based on the articles."""
        try:
            self.utilities.logger.debug("Starting to generate podcast scoring prompt.")

            # Read the system and user prompt templates from files
            system_prompt = self.read_prompt_from_file(
                path=self.path + self.utilities.config["general_info"]["scoring_system_prompt_filename"]
            )
            prompt_without_article = self.read_prompt_from_file(
                path=self.path + self.utilities.config["general_info"]["scoring_user_prompt_filename"]
            )

            # Ensure neither prompt is None
            if system_prompt is None:
                raise ValueError("System prompt could not be read from file.")
            if prompt_without_article is None:
                raise ValueError("User prompt could not be read from file.")

            if not all(key in article for key in ["title", "abstract", "full_text"]):
                self.utilities.logger.error(f"Missing data in article: {article}")

            # Using the first article for demonstration; adjust logic for multiple articles as needed
            title = article["title"]
            abstract = article["abstract"]
            full_text = article["full_text"]

            # Dynamically insert article information into the prompt template
            user_prompt = prompt_without_article.format(title=title, abstract=abstract, full_text=full_text)

            self.utilities.logger.debug("Scoring prompt generated successfully.")
            return system_prompt, user_prompt

        except Exception as e:
            self.utilities.logger.error(f"Failed to generate scoring prompt: {e}")
            raise Exception(f"Error generating prompt: {e}")

    def assemble_title_prompts(self, script: str) -> Tuple[str, str]:
        """Generates the title prompt based on the articles."""
        try:
            self.utilities.logger.debug("Starting to generate podcast title prompt.")

            # Read the system and user prompt templates from files
            system_prompt = self.read_prompt_from_file(
                path=self.path + self.utilities.config["general_info"]["title_system_prompt_filename"]
            )
            prompt_without_script = self.read_prompt_from_file(
                path=self.path + self.utilities.config["general_info"]["title_user_prompt_filename"]
            )

            # Ensure neither prompt is None
            if system_prompt is None:
                raise ValueError("System prompt could not be read from file.")
            if prompt_without_script is None:
                raise ValueError("User prompt could not be read from file.")

            # Dynamically insert script into the prompt template
            user_prompt = prompt_without_script.format(script=script)

            self.utilities.logger.debug("Title prompt generated successfully.")
            return system_prompt, user_prompt

        except Exception as e:
            self.utilities.logger.error(f"Failed to generate title prompt: {e}")
            raise Exception(f"Error generating prompt: {e}")

    def assemble_social_media_prompts(self, script: str) -> Tuple[str, str]:
        """Generates the social media prompts based on the articles."""
        try:
            self.utilities.logger.debug("Starting to generate podcast social media prompts.")

            # Read the system and user prompt templates from files
            system_prompt = self.read_prompt_from_file(
                path=self.path + self.utilities.config["general_info"]["post_system_prompt_filename"]
            )
            prompt_without_script = self.read_prompt_from_file(
                path=self.path + self.utilities.config["general_info"]["post_user_prompt_filename"]
            )

            # Ensure neither prompt is None
            if system_prompt is None:
                raise ValueError("System prompt could not be read from file.")
            if prompt_without_script is None:
                raise ValueError("User prompt could not be read from file.")

            # Dynamically insert script into the prompt template
            user_prompt = prompt_without_script.format(script=script)

            self.utilities.logger.debug("Social media prompt generated successfully.")
            return system_prompt, user_prompt

        except Exception as e:
            self.utilities.logger.error(f"Failed to generate social media prompt: {e}")
            raise Exception(f"Error generating prompt: {e}")

    def read_prompt_from_file(self, path: str) -> Optional[str]:
        """Reads a prompt from a file and returns it as a string. Returns None if no valid string is found."""
        try:
            with open(path, "r", encoding="utf-8") as file:
                prompt: str = file.read().strip()  # Use .strip() to remove any leading/trailing whitespace
                if prompt:  # Check if the prompt is not empty
                    self.utilities.logger.debug("Prompt read successfully.")
                    return prompt
                else:
                    self.utilities.logger.warning("Read an empty prompt.")
                    return None  # Or return a default prompt if needed
        except FileNotFoundError:
            self.utilities.logger.error(f"The file at {path} was not found.")
            return None
        except Exception as e:
            self.utilities.logger.error(f"An error occurred while reading the file: {e}")
            return None
