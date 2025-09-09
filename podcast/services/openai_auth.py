import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from podcast.utilities.bundle import UtilitiesBundle


class OpenAIAuthService:
    def __init__(self, utilities: UtilitiesBundle, key: Optional[str] = None) -> None:
        self.utilities: UtilitiesBundle = utilities
        self.key: Optional[str] = key or self.get_api_key()
        if self.key:
            self.client: OpenAI = OpenAI(api_key=self.key)
            self.utilities.logger.debug("OpenAI API key set successfully.")
        else:
            self.utilities.logger.warning("OpenAI API key was not set. OpenAI client not created")

    def get_api_key(self) -> Optional[str]:
        try:
            load_dotenv()
            openai_key: Optional[str] = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.utilities.logger.debug("OpenAI API key retrieved successfully.")
            else:
                self.utilities.logger.warning("Failed to retrieve the OpenAI API key. It may not be set.")
            return openai_key

        except Exception as e:
            self.utilities.logger.error("An unexpected error occurred: %s", str(e))
            raise RuntimeError(f"Unexpected error: {e}")
