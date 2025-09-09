import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

from podcast.utilities.bundle import UtilitiesBundle


class BlueSkyService:

    def __init__(self, utilities: UtilitiesBundle) -> None:
        self.utilities: UtilitiesBundle = utilities
        self.handle: str = self.utilities.config["bluesky"]["handle"]
        self.app_password: Optional[str] = self.get_bluesky_api_key()
        self.base_url: str = self.utilities.config["bluesky"]["base_url"]
        self.session: Dict = self.authenticate()
        self.link: str = self.utilities.config["podcast_info"]["podcast_link"]

    def get_bluesky_api_key(self) -> Optional[str]:
        try:
            load_dotenv()
            bluesky_api_key: Optional[str] = os.getenv("BLUESKY_API_KEY")
            if bluesky_api_key:
                self.utilities.logger.debug("OpenAI API key retrieved successfully.")
            else:
                self.utilities.logger.warning("Failed to retrieve the OpenAI API key. It may not be set.")
            return bluesky_api_key
        except Exception as e:
            self.utilities.logger.error("An unexpected error occurred: %s", str(e))
            raise RuntimeError(f"Unexpected error: {e}")

    def authenticate(self) -> Dict[Any, Any]:
        """
        Authenticates with the Bluesky API and returns a session containing the access token.
        """
        try:
            response = requests.post(
                f"{self.base_url}/xrpc/com.atproto.server.createSession",
                json={"identifier": self.handle, "password": self.app_password},
            )
            response.raise_for_status()
            session: Dict[Any, Any] = response.json()
            self.utilities.logger.info("Authenticated successfully with Bluesky.")
            return session
        except requests.RequestException as e:
            self.utilities.logger.error("Failed to authenticate with Bluesky: %s", str(e))
            raise RuntimeError(f"Authentication failed: {e}")

    def refresh_auth(self) -> None:
        """
        Refreshes the access token if needed.
        """
        if "refreshJwt" in self.session:
            try:
                response = requests.post(
                    f"{self.base_url}/xrpc/com.atproto.server.refreshSession",
                    headers={"Authorization": f"Bearer {self.session['refreshJwt']}"},
                )
                response.raise_for_status()
                self.session.update(response.json())
                self.utilities.logger.info("Refreshed Bluesky session token.")
            except requests.RequestException as e:
                self.utilities.logger.error("Failed to refresh Bluesky session: %s", str(e))
                raise RuntimeError(f"Failed to refresh session: {e}")

    def post_to_bluesky(self, post: str, link: Optional[str] = None) -> None:
        """
        Posts content to Bluesky, optionally including a link.

        :param post: The text content of the post.
        :param link: An optional URL to include in the post (default: https://scibud.media).
        """
        try:
            # Ensure authentication is valid
            self.refresh_auth()
            if not link:
                link = self.link

            # Generate timestamp
            now: str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Append the link properly if present
            if link:
                post += f" {link}"  # Ensure a space before the link

            # Use regex to find the start index of the link
            facets: List[dict] = []
            if link:
                match = re.search(re.escape(link), post)
                if match:
                    start_index = match.start()
                    byte_end = match.end()

                    facets.append(
                        {
                            "index": {
                                "byteStart": start_index,
                                "byteEnd": byte_end,
                            },
                            "features": [
                                {
                                    "$type": "app.bsky.richtext.facet#link",
                                    "uri": link,
                                }
                            ],
                        }
                    )

            # Construct the record with the facet if present
            record: dict = {
                "$type": "app.bsky.feed.post",
                "text": post,
                "createdAt": now,
            }

            if facets:
                record["facets"] = facets

            response = requests.post(
                f"{self.base_url}/xrpc/com.atproto.repo.createRecord",
                headers={"Authorization": f"Bearer {self.session['accessJwt']}"},
                json={
                    "repo": self.session["did"],
                    "collection": "app.bsky.feed.post",
                    "record": record,
                },
            )
            response.raise_for_status()

            self.utilities.logger.info("Posted to Bluesky successfully")
        except requests.RequestException as e:
            self.utilities.logger.error("Failed to post to Bluesky: %s", str(e))
            raise RuntimeError(f"Failed to post to Bluesky: {e}")
        except requests.exceptions.JSONDecodeError as e:
            self.utilities.logger.error("Failed to decode JSON response: %s", str(e))
        except ValueError as e:
            self.utilities.logger.error("Invalid response format: %s", str(e))


# Example usage
# base_url = "https://example.com"
# session = {"accessJwt": "your_access_jwt", "did": "your_did"}
# utilities = YourUtilitiesClass()
# service = BlueSkyService(base_url, session, utilities)
# result = service.post_to_bluesky("Hello, Bluesky!")
