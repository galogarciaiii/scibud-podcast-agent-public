from typing import List

from feedgen.feed import FeedGenerator

from podcast.formats.episode import EpisodeInfo
from podcast.utilities.bundle import UtilitiesBundle


class RSSManager:
    """
    A manager class to generate an RSS feed for a podcast based on a given strategy for retrieving episode data.

    Attributes:
        strategy (ArticleSourceStrategy): A strategy for retrieving episode data from various article sources.
        config (Dict[str, Any]):
            A dictionary containing podcast configuration such as title, author, base URL, and artwork paths.
        logger (logging.Logger): Logger for logging errors, debugging, and information messages.

    Methods:
        generate_rss_feed(episodes: List[Dict[str, Any]]) -> str:
            Generates and returns an RSS feed XML string based on the given episodes data.
    """

    def __init__(self, path: str, utilities: UtilitiesBundle) -> None:
        """
        Initialize the RSSManager with a strategy for retrieving episodes, podcast configuration, and a logger.

        Args:
            strategy (ArticleSourceStrategy): A strategy for retrieving article data used to generate episode content.
            config (Dict[str, Any]):
                A dictionary containing various configuration options for the podcast,
                including base URL, logo path, and podcast metadata.
            logger (logging.Logger): A logging instance for recording activity and errors during RSS feed generation.
        """
        self.path: str = path
        self.utilities: UtilitiesBundle = utilities

    def generate_rss_feed(self, episodes: List[EpisodeInfo]) -> str:
        """
        Generates an RSS feed XML string based on a list of episodes.

        Args:
            episodes (List[Dict[str, Any]]):
                A list of dictionaries where each dictionary represents an episode and its metadata.
                Each episode dictionary must contain keys such as:
                - 'title': The title of the episode.
                - 'description': A description of the episode.
                - 'season': The season number of the episode.
                - 'episode': The episode number.
                - 'guid': A globally unique identifier for the episode.
                - 'pub_date': The publication date of the episode.
                - 'file_size': The size of the episode's audio file.
                - 'citations' (optional): Citations related to the episode content.

        Returns:
            str: The generated RSS feed as a formatted XML string.

        Raises:
            RuntimeError: If an error occurs during the feed generation process.
        """
        try:
            # Base URLs
            base_url = self.utilities.config["general_info"]["public_base_url"]
            artwork_path = f"{base_url}{self.path}{self.utilities.config['general_info']['logo_filename']}"
            audio_base_url = f"{base_url}{self.path}audio/"
            episode_artwork_path = "https://storage.googleapis.com/bucket-sci-bud/combined/artwork/logo_episode.png"

            # Create the FeedGenerator object
            fg = FeedGenerator()
            fg.load_extension("podcast")

            # Set the feed-level metadata
            fg.title(self.utilities.config["podcast_info"]["title"])
            fg.link(href=self.utilities.config["podcast_info"]["podcast_link"])
            fg.language(self.utilities.config["podcast_info"]["language"])
            fg.copyright(f"© {self.utilities.config['podcast_info']['copyright']}")
            fg.podcast.itunes_author(self.utilities.config["podcast_info"]["artist_name"])
            fg.description(self.utilities.config["podcast_info"]["description"])

            # Set the image for the feed
            fg.image(
                url=artwork_path,
                title=self.utilities.config["podcast_info"]["title"],
            )

            fg.category({"term": self.utilities.config["podcast_info"]["primary_category"]})
            fg.podcast.itunes_explicit("no")
            fg.podcast.itunes_image(artwork_path)
            fg.podcast.itunes_type(self.utilities.config["podcast_info"]["type"])

            # Add episodes to the feed
            for episode in episodes:
                fe = fg.add_entry()
                fe.title(episode["title"])

                # Build the episode link
                link: str = (
                    "www.scibud.media"
                    + "/podcast/season/"
                    + str(episode["season"])
                    + "/episode/"
                    + str(episode["episode"])
                )

                # Append episode link to the description
                description_with_episode_link = (
                    episode["description"] + " Link to episode page with article citation: " + link
                )
                fe.description(description_with_episode_link)

                # Set episode-specific metadata
                fe.guid(episode["guid"])
                fe.pubDate(episode["pub_date"])

                # Generate audio URL
                audio_url = (
                    f"{audio_base_url}season_{episode['season']}/episode_{episode['episode']}"
                    f"{self.utilities.config['general_info']['audio_file_type']}"
                )
                fe.enclosure(audio_url, str(episode["file_size"]), "audio/wav")
                fe.author({"name": self.utilities.config["podcast_info"]["artist_name"]})

                # iTunes-specific metadata
                fe.podcast.itunes_author(self.utilities.config["podcast_info"]["artist_name"])
                fe.podcast.itunes_image(episode_artwork_path)
                fe.podcast.itunes_explicit("no")
                fe.podcast.itunes_episode(str(episode["episode"]))
                fe.podcast.itunes_season(str(episode["season"]))
                fe.podcast.itunes_episode_type(self.utilities.config["podcast_info"]["episode_type"])
                fe.link(href=link)

                # Add citations if available, otherwise default to "None"
                citations = episode.get("citations", "")
                if citations:
                    fe.comments(citations)
                else:
                    fe.comments("None")

            # Generate the RSS feed
            rss_feed: str = fg.rss_str(pretty=True).decode("utf-8")

            self.utilities.logger.debug("RSS XML string generated.")
            return rss_feed

        except Exception as e:
            self.utilities.logger.error(f"An error occurred: {e}")
            raise RuntimeError(f"An error occurred during the RSS feed generation: {e}")
