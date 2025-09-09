import os
import subprocess
from typing import Optional

from dotenv import load_dotenv

from podcast.utilities.bundle import UtilitiesBundle


class GoogleAuthService:
    def __init__(self, utilities: UtilitiesBundle, key: Optional[str] = None) -> None:
        self.utilities: UtilitiesBundle = utilities
        self.key: Optional[str] = key or self.get_google_api_key()
        if self.key:
            self.utilities.logger.debug("Google API key set successfully.")
        else:
            self.utilities.logger.warning("Google API key was not set.")

    def get_google_api_key(self) -> Optional[str]:
        load_dotenv()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sci-bud-c962e85010ff.json"
        key: str = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

        if key:
            self.utilities.logger.debug("Google API key retrieved successfully.")
            return key
        return None

    def enable_gcloud_services(self) -> None:
        command = ["gcloud", "services", "enable", "texttospeech.googleapis.com"]
        try:
            self.utilities.logger.debug(f"Running command: {' '.join(command)}")
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            self.utilities.logger.debug(f"Service enabled successfully. Output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            self.utilities.logger.error(f"Failed to enable service: {e}. Output: {e.output}, Error: {e.stderr}")
            raise RuntimeError("Failed to enable Google Cloud service.") from e
        except Exception as e:
            self.utilities.logger.error(f"An unexpected error occurred: {e}")
            raise RuntimeError("An unexpected error occurred while enabling Google Cloud service.") from e
