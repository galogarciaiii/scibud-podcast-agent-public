from typing import Any

import openai

from podcast.utilities.bundle import UtilitiesBundle


class OpenAITextGenService:
    def __init__(self, client: Any, utilities: UtilitiesBundle) -> None:
        self.client: Any = client
        self.utilities: UtilitiesBundle = utilities

    def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        try:
            # Sending the request to the OpenAI API
            response: Any = self.client.chat.completions.create(
                model=self.utilities.config["models"]["gpt_model"],  # Example model
                max_tokens=4096,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            self.utilities.logger.debug("API call to OpenAI completed successfully.")

            # Extracting the summary from the API response
            script: str = response.choices[0].message.content
            self.utilities.logger.debug("Summary extracted from the API response.")

            return script

        except openai.BadRequestError as e:
            if "context_length_exceeded" in str(e):
                self.utilities.logger.warning("Context length exceeded, skipping chat completion.")
                return ""
            else:
                self.utilities.logger.error(f"An unexpected error occurred: {e}")
                raise Exception(f"Unexpected error: {e}")
        except Exception as e:
            self.utilities.logger.error(f"An unexpected error occurred: {e}")
            raise Exception(f"Unexpected error: {e}")
