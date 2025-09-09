from podcast.formats.episode import EpisodeInfo
from podcast.managers.social_media import SocialMediaManager
from podcast.utilities.bundle import UtilitiesBundle


class CommunicationAssistant:
    def __init__(self, path: str, utilities: UtilitiesBundle) -> None:
        self.path: str = path
        self.utilities: UtilitiesBundle = utilities
        self.social_media_manager: SocialMediaManager = SocialMediaManager(path=self.path, utilities=self.utilities)

    def post_to_social_media(self, episode: EpisodeInfo) -> None:
        self.social_media_manager.post_to_bluesky(episode=episode)
