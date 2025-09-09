from typing import Optional

from google.cloud import texttospeech

from podcast.utilities.bundle import UtilitiesBundle


class GoogleTTSService:
    def __init__(self, utilities: UtilitiesBundle) -> None:
        self.utilities: UtilitiesBundle = utilities

    def synthesize_long_audio(
        self, script: str, file_path: str, voice_option: str
    ) -> Optional[texttospeech.SynthesizeLongAudioResponse]:
        """
        Synthesizes long input, writing the resulting audio to `output_gcs_uri`.

        Example usage: synthesize_long_audio('script', 'gs://{BUCKET_NAME}/{OUTPUT_FILE_NAME}.wav')
        """

        client: texttospeech.TextToSpeechLongAudioSynthesizeClient = (
            texttospeech.TextToSpeechLongAudioSynthesizeClient()
        )
        input_text: texttospeech.SynthesisInput = texttospeech.SynthesisInput(text=script)

        # Currently long audio output can only be in the Linear16 output
        audio_config: texttospeech.AudioConfig = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        voice: texttospeech.VoiceSelectionParams = texttospeech.VoiceSelectionParams(
            language_code=self.utilities.config["google_tts"]["language"], name=voice_option
        )

        request: texttospeech.SynthesizeLongAudioRequest = texttospeech.SynthesizeLongAudioRequest(
            parent=self.utilities.config["general_info"]["project_path"],
            input=input_text,
            audio_config=audio_config,
            voice=voice,
            output_gcs_uri=file_path,
        )

        try:
            # Log the selected voice option
            self.utilities.logger.info("Selected Option: %s", voice_option)

            # Starting the long-running operation
            operation = client.synthesize_long_audio(request=request)
            self.utilities.logger.debug("Long audio synthesis requested.")

            # Wait for the operation to complete with a timeout
            response = operation.result(timeout=300)  # type: ignore

            if operation.done():  # type:ignore
                self.utilities.logger.debug("Audio synthesis completed successfully.")
                return response  # type: ignore
            else:
                self.utilities.logger.warning("The audio synthesis operation did not complete within the timeout.")
                return None

        except Exception as e:
            # Catch-all for any other errors that may occur
            self.utilities.logger.error("An unexpected error occurred: %s", str(e))
            raise RuntimeError(f"Unexpected error: {e}")
