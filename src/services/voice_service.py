"""
Voice service for Speech-to-Text (STT) and Text-to-Speech (TTS).

This service integrates with Google Cloud Speech APIs to provide:
- Real-time speech-to-text transcription (Brazilian Portuguese)
- High-quality text-to-speech synthesis (WaveNet voices)
- Audio streaming support
- Accessibility features for visually impaired users
"""

import io
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Optional

from google.cloud import speech_v1, texttospeech_v1
from google.oauth2 import service_account

from src.core import get_logger
from src.core.config import settings

logger = get_logger("services.voice")


class VoiceService:
    """
    Handle speech-to-text and text-to-speech operations.

    This service uses Google Cloud Speech APIs for Brazilian Portuguese
    with optimized settings for transparency data conversations.
    """

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        language_code: Optional[str] = None,
    ):
        """
        Initialize voice service with Google Cloud credentials.

        Args:
            credentials_path: Path to Google Cloud service account JSON
            language_code: Language code (default: pt-BR for Brazilian Portuguese)
        """
        self.language_code = language_code or settings.google_speech_language_code
        self.credentials_path = credentials_path or settings.google_credentials_path

        # Initialize clients (lazy loading)
        self._stt_client: Optional[speech_v1.SpeechClient] = None
        self._tts_client: Optional[texttospeech_v1.TextToSpeechClient] = None

        logger.info(
            "voice_service_initialized",
            language=language_code,
            credentials_configured=bool(credentials_path),
        )

    def _get_credentials(self) -> Optional[service_account.Credentials]:
        """Load Google Cloud credentials from file.

        Supports both absolute and relative paths.
        Relative paths are resolved from the project root.
        """
        if not self.credentials_path:
            logger.warning(
                "google_credentials_not_configured",
                message="Voice service will use default credentials",
            )
            return None

        try:
            # Convert to Path object for easier handling
            credentials_path = Path(self.credentials_path)

            # If relative path, resolve from project root
            if not credentials_path.is_absolute():
                # Get project root (assumes src/services/voice_service.py structure)
                project_root = Path(__file__).parent.parent.parent
                credentials_path = project_root / credentials_path

            # Ensure path exists
            if not credentials_path.exists():
                logger.error(
                    "google_credentials_file_not_found",
                    path=str(credentials_path),
                    original_path=self.credentials_path,
                )
                return None

            credentials = service_account.Credentials.from_service_account_file(
                str(credentials_path),
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            logger.info(
                "google_credentials_loaded",
                path=str(credentials_path),
                relative=not Path(self.credentials_path).is_absolute(),
            )
            return credentials
        except Exception as e:
            logger.error(
                "google_credentials_load_failed",
                path=self.credentials_path,
                error=str(e),
            )
            return None

    @property
    def stt_client(self) -> speech_v1.SpeechClient:
        """Get or create STT client (lazy loading)."""
        if self._stt_client is None:
            credentials = self._get_credentials()
            if credentials:
                self._stt_client = speech_v1.SpeechClient(credentials=credentials)
            else:
                self._stt_client = speech_v1.SpeechClient()
            logger.info("stt_client_initialized")
        return self._stt_client

    @property
    def tts_client(self) -> texttospeech_v1.TextToSpeechClient:
        """Get or create TTS client (lazy loading)."""
        if self._tts_client is None:
            credentials = self._get_credentials()
            if credentials:
                self._tts_client = texttospeech_v1.TextToSpeechClient(
                    credentials=credentials
                )
            else:
                self._tts_client = texttospeech_v1.TextToSpeechClient()
            logger.info("tts_client_initialized")
        return self._tts_client

    async def transcribe_audio(
        self,
        audio_content: bytes,
        encoding: speech_v1.RecognitionConfig.AudioEncoding = speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz: int = 16000,
    ) -> str:
        """
        Transcribe audio content to text.

        Args:
            audio_content: Audio data as bytes
            encoding: Audio encoding format
            sample_rate_hertz: Audio sample rate

        Returns:
            Transcribed text in Brazilian Portuguese

        Raises:
            Exception: If transcription fails
        """
        try:
            logger.info(
                "transcription_started",
                audio_size_bytes=len(audio_content),
                encoding=encoding.name,
                sample_rate=sample_rate_hertz,
            )

            # Configure recognition
            config = speech_v1.RecognitionConfig(
                encoding=encoding,
                sample_rate_hertz=sample_rate_hertz,
                language_code=self.language_code,
                enable_automatic_punctuation=True,
                model="latest_long",  # Best for conversations
                use_enhanced=True,  # Enhanced model for better accuracy
            )

            audio = speech_v1.RecognitionAudio(content=audio_content)

            # Perform synchronous transcription
            response = self.stt_client.recognize(config=config, audio=audio)

            # Extract transcription
            transcripts = []
            for result in response.results:
                if result.alternatives:
                    transcripts.append(result.alternatives[0].transcript)

            transcription = " ".join(transcripts)

            logger.info(
                "transcription_completed",
                text_length=len(transcription),
                confidence=(
                    response.results[0].alternatives[0].confidence
                    if response.results
                    else 0
                ),
            )

            return transcription

        except Exception as e:
            logger.error(
                "transcription_failed",
                error=str(e),
                audio_size=len(audio_content),
                exc_info=True,
            )
            raise

    async def transcribe_audio_stream(
        self, audio_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[str, None]:
        """
        Transcribe audio stream in real-time.

        Args:
            audio_stream: Async generator yielding audio chunks

        Yields:
            Partial transcriptions as they become available

        Note:
            This is for real-time streaming. For complete audio,
            use transcribe_audio() instead.
        """
        try:
            logger.info("streaming_transcription_started")

            # Configure streaming recognition
            config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=self.language_code,
                enable_automatic_punctuation=True,
                model="latest_short",  # Better for streaming
            )

            streaming_config = speech_v1.StreamingRecognitionConfig(
                config=config, interim_results=True  # Real-time partial results
            )

            # Create request generator
            async def request_generator():
                async for chunk in audio_stream:
                    yield speech_v1.StreamingRecognizeRequest(audio_content=chunk)

            # Perform streaming recognition
            responses = self.stt_client.streaming_recognize(
                streaming_config, request_generator()
            )

            # Yield transcriptions as they arrive
            for response in responses:
                for result in response.results:
                    if result.alternatives and result.is_final:
                        transcript = result.alternatives[0].transcript
                        logger.debug(
                            "streaming_transcript_received", transcript=transcript
                        )
                        yield transcript

            logger.info("streaming_transcription_completed")

        except Exception as e:
            logger.error("streaming_transcription_failed", error=str(e), exc_info=True)
            raise

    async def synthesize_speech(
        self,
        text: str,
        voice_name: str = "pt-BR-Wavenet-A",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
    ) -> bytes:
        """
        Convert text to speech audio.

        Args:
            text: Text to synthesize (Brazilian Portuguese)
            voice_name: Google Cloud voice name (default: female WaveNet)
            speaking_rate: Speed of speech (0.25-4.0, default: 1.0)
            pitch: Pitch adjustment (-20.0 to 20.0, default: 0.0)

        Returns:
            Audio content as MP3 bytes

        Available voices (Brazilian Portuguese):
        - pt-BR-Wavenet-A: Female, natural
        - pt-BR-Wavenet-B: Male, natural
        - pt-BR-Neural2-A: Female, very natural (latest)
        - pt-BR-Neural2-B: Male, very natural (latest)
        """
        try:
            logger.info(
                "speech_synthesis_started",
                text_length=len(text),
                voice=voice_name,
                rate=speaking_rate,
            )

            # Configure synthesis
            input_text = texttospeech_v1.SynthesisInput(text=text)

            voice = texttospeech_v1.VoiceSelectionParams(
                language_code=self.language_code, name=voice_name
            )

            audio_config = texttospeech_v1.AudioConfig(
                audio_encoding=texttospeech_v1.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch,
            )

            # Perform synthesis
            response = self.tts_client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )

            logger.info(
                "speech_synthesis_completed",
                audio_size_bytes=len(response.audio_content),
            )

            return response.audio_content

        except Exception as e:
            logger.error(
                "speech_synthesis_failed",
                text_preview=text[:100],
                error=str(e),
                exc_info=True,
            )
            raise

    async def stream_audio_response(
        self, text: str, chunk_size: int = 4096
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream audio response in chunks for real-time playback.

        Args:
            text: Text to synthesize
            chunk_size: Size of each audio chunk in bytes

        Yields:
            Audio chunks for streaming playback
        """
        try:
            logger.info("audio_streaming_started", text_length=len(text))

            # Synthesize full audio
            audio_content = await self.synthesize_speech(text)

            # Stream in chunks
            audio_stream = io.BytesIO(audio_content)
            while True:
                chunk = audio_stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk

            logger.info("audio_streaming_completed")

        except Exception as e:
            logger.error("audio_streaming_failed", error=str(e), exc_info=True)
            raise


# Singleton instance
_voice_service: Optional[VoiceService] = None


def get_voice_service() -> VoiceService:
    """Get or create voice service singleton."""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service
