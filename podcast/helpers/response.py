import re
from typing import Tuple

from podcast.utilities.bundle import UtilitiesBundle


class ResponseHelper:
    def __init__(self, utilities: UtilitiesBundle) -> None:
        self.utilities: UtilitiesBundle = utilities

    def parse_score_and_justification(self, response: str) -> Tuple[int, str]:
        """
        Extracts the total score and the textual response from the LLM response.
        The format expected is 'TOTAL_SCORE = X' for the score and accompanying
        textual explanation.

        Args:
            response (str): The LLM response containing the score and text.

        Returns:
            tuple[int, str]: The extracted score and the textual response.
                            Returns (-1, "") if no score or text is found or an error occurs.
        """
        try:
            # Check if response is a non-empty string
            if not isinstance(response, str) or not response.strip():
                self.utilities.logger.error("Invalid response: Response is either not a string or empty.")
                return -1, ""

            # Use regular expression to find "TOTAL_SCORE = X" pattern
            score_match = re.search(r"TOTAL_SCORE\s*=\s*(\d+)", response)
            if score_match:
                score = int(score_match.group(1))
            else:
                self.utilities.logger.error(f"No score found in response: {response}")
                return -1, ""

            # Extract the textual part by removing the TOTAL_SCORE part
            text_response = re.sub(r"TOTAL_SCORE\s*=\s*\d+", "", response).strip()

            return score, text_response
        except ValueError:
            # Handle unexpected integer conversion errors
            self.utilities.logger.error(f"Failed to convert extracted score to integer in response: {response}")
            return -1, ""
        except Exception as e:
            # Log if an unexpected exception occurred
            self.utilities.logger.error(f"Exception occurred while extracting score and text from response: {e}")
            return -1, ""

    def remove_special_characters(self, text: str) -> str:
        """
        Removes only '#' and '*' characters from the input text.
        """
        cleaned_text = re.sub(r"[#*]", "", text)
        return cleaned_text

    def remove_quotes_from_title(self, title: str) -> str:
        """
        Removes single quotes (') and double quotes (") from the input title.
        """
        cleaned_title = re.sub(r"[\'\"]", "", title)
        return cleaned_title
