from typing import List

from podcast.formats.episode import EpisodeInfo
from podcast.managers.audio import AudioManager
from podcast.managers.rss import RSSManager
from podcast.utilities.bundle import UtilitiesBundle


class ProductionAssistant:
    def __init__(self, path: str, utilities: UtilitiesBundle) -> None:
        self.path: str = path
        self.utilities: UtilitiesBundle = utilities
        self.audio_manager: AudioManager = AudioManager(utilities=self.utilities)
        self.rss_manager: RSSManager = RSSManager(path=self.path, utilities=self.utilities)

    def generate_audio(self, script: str, file_path: str, voice_option: str) -> None:
        self.audio_manager.generate_audio(script=script, file_path=file_path, voice_option=voice_option)

    def generate_rss_feed(self, episodes: List[EpisodeInfo]) -> str:
        rss_xml: str = self.rss_manager.generate_rss_feed(episodes=episodes)
        return rss_xml
