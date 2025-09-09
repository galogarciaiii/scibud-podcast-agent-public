from podcast.formats.episode import EpisodeInfo
from podcast.services.blue_sky import BlueSkyService
from podcast.utilities.bundle import UtilitiesBundle


class SocialMediaManager:
    def __init__(self, path: str, utilities: UtilitiesBundle) -> None:
        self.utilities: UtilitiesBundle = utilities
        self.path = path
        self.bluesky_service: BlueSkyService = BlueSkyService(utilities=self.utilities)

    def post_to_bluesky(self, episode: EpisodeInfo) -> None:
        post = episode["post"]
        self.bluesky_service.authenticate()
        self.bluesky_service.post_to_bluesky(post=post)
