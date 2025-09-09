from podcast.services.google_auth import GoogleAuthService
from podcast.services.google_tts import GoogleTTSService
from podcast.utilities.bundle import UtilitiesBundle


class AudioManager:
    def __init__(self, utilities: UtilitiesBundle) -> None:
        self.utilities: UtilitiesBundle = utilities
        self.audio_gen_service: GoogleTTSService = GoogleTTSService(utilities=self.utilities)
        self.auth_service: GoogleAuthService = GoogleAuthService(utilities=self.utilities)

    def generate_audio(self, script: str, file_path: str, voice_option: str) -> None:
        self.auth_service.enable_gcloud_services()
        self.utilities.logger.debug("Google Cloud services enabled.")
        self.audio_gen_service.synthesize_long_audio(script=script, file_path=file_path, voice_option=voice_option)
