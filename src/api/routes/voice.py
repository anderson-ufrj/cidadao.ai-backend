"""
Voice API routes for Speech-to-Text and Text-to-Speech.

This module provides RESTful endpoints for:
- Transcribing audio to text (STT)
- Synthesizing speech from text (TTS)
- Real-time voice conversations with agents
- Streaming audio responses

All voice features are optimized for Brazilian Portuguese.
"""

from collections.abc import AsyncGenerator
from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.core import get_logger
from src.services.voice_service import get_voice_service

logger = get_logger("api.voice")

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================


class TranscribeRequest(BaseModel):
    """Request model for audio transcription."""

    audio_format: str = Field(
        default="wav",
        description="Audio format (wav, mp3, ogg, flac)",
    )
    sample_rate: int = Field(
        default=16000,
        description="Audio sample rate in Hz (8000-48000)",
        ge=8000,
        le=48000,
    )


class TranscribeResponse(BaseModel):
    """Response model for audio transcription."""

    transcription: str = Field(description="Transcribed text in Brazilian Portuguese")
    confidence: float = Field(
        description="Transcription confidence score (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    language_detected: str = Field(
        default="pt-BR",
        description="Detected language code",
    )
    duration_ms: float = Field(
        description="Audio duration in milliseconds",
    )


class SpeakRequest(BaseModel):
    """Request model for text-to-speech synthesis."""

    text: str = Field(
        description="Text to synthesize (Brazilian Portuguese)",
        min_length=1,
        max_length=5000,
    )
    voice_name: str = Field(
        default="pt-BR-Wavenet-A",
        description="Google Cloud TTS voice name",
    )
    speaking_rate: float = Field(
        default=1.0,
        description="Speaking rate (0.25-4.0)",
        ge=0.25,
        le=4.0,
    )
    pitch: float = Field(
        default=0.0,
        description="Pitch adjustment (-20.0 to 20.0)",
        ge=-20.0,
        le=20.0,
    )


class ConversationRequest(BaseModel):
    """Request model for full voice conversation."""

    query: str = Field(
        description="Text query or transcribed audio to process",
        min_length=1,
        max_length=1000,
    )
    agent_id: str = Field(
        default="drummond",
        description="Agent to process the query (default: drummond for NLG)",
    )
    return_audio: bool = Field(
        default=True,
        description="Whether to return audio response (TTS)",
    )
    voice_name: str = Field(
        default="pt-BR-Wavenet-A",
        description="TTS voice for audio response",
    )


class ConversationResponse(BaseModel):
    """Response model for voice conversation."""

    query: str = Field(description="Original query text")
    response_text: str = Field(description="Agent response in text")
    audio_available: bool = Field(description="Whether audio response is included")
    audio_format: str = Field(
        default="mp3",
        description="Audio format if audio_available=true",
    )
    processing_time_ms: float = Field(
        description="Total processing time in milliseconds",
    )


# ============================================================================
# Voice Endpoints
# ============================================================================


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    sample_rate: int = Form(16000, description="Audio sample rate in Hz"),
) -> TranscribeResponse:
    """
    Transcribe audio file to text using Google Cloud Speech-to-Text.

    Supports multiple audio formats optimized for Brazilian Portuguese.
    Returns transcribed text with confidence score.

    **Example Usage:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/voice/transcribe" \\
         -F "audio=@recording.wav" \\
         -F "sample_rate=16000"
    ```
    """
    try:
        logger.info(
            "transcribe_audio_request",
            filename=audio.filename,
            content_type=audio.content_type,
            sample_rate=sample_rate,
        )

        # Read audio content
        audio_content = await audio.read()

        if not audio_content:
            raise HTTPException(status_code=400, detail="Empty audio file")

        # Get voice service
        voice_service = get_voice_service()

        # Determine encoding from content type
        from google.cloud import speech_v1

        encoding_map = {
            "audio/wav": speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            "audio/x-wav": speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            "audio/mp3": speech_v1.RecognitionConfig.AudioEncoding.MP3,
            "audio/mpeg": speech_v1.RecognitionConfig.AudioEncoding.MP3,
            "audio/ogg": speech_v1.RecognitionConfig.AudioEncoding.OGG_OPUS,
            "audio/flac": speech_v1.RecognitionConfig.AudioEncoding.FLAC,
        }

        encoding = encoding_map.get(
            audio.content_type or "audio/wav",
            speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        )

        # Transcribe audio
        import time

        start_time = time.time()
        transcription = await voice_service.transcribe_audio(
            audio_content=audio_content,
            encoding=encoding,
            sample_rate_hertz=sample_rate,
        )
        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "transcription_success",
            text_length=len(transcription),
            duration_ms=duration_ms,
        )

        # Return response
        return TranscribeResponse(
            transcription=transcription,
            confidence=0.95,  # TODO: Extract actual confidence from response
            language_detected="pt-BR",
            duration_ms=duration_ms,
        )

    except Exception as e:
        logger.error(
            "transcribe_audio_failed",
            filename=audio.filename,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe audio: {str(e)}",
        )


@router.post("/speak")
async def synthesize_speech(request: SpeakRequest) -> StreamingResponse:
    """
    Convert text to speech using Google Cloud Text-to-Speech.

    Returns MP3 audio stream optimized for Brazilian Portuguese.
    Supports multiple WaveNet voices and adjustable parameters.

    **Available Voices:**
    - pt-BR-Wavenet-A (female, natural)
    - pt-BR-Wavenet-B (male, natural)
    - pt-BR-Neural2-A (female, very natural - latest)
    - pt-BR-Neural2-B (male, very natural - latest)

    **Example Usage:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/voice/speak" \\
         -H "Content-Type: application/json" \\
         -d '{"text": "Olá! Como posso ajudar com transparência pública?", "voice_name": "pt-BR-Wavenet-A"}' \\
         --output response.mp3
    ```
    """
    try:
        logger.info(
            "synthesize_speech_request",
            text_length=len(request.text),
            voice=request.voice_name,
            rate=request.speaking_rate,
            pitch=request.pitch,
        )

        # Get voice service
        voice_service = get_voice_service()

        # Synthesize speech
        audio_content = await voice_service.synthesize_speech(
            text=request.text,
            voice_name=request.voice_name,
            speaking_rate=request.speaking_rate,
            pitch=request.pitch,
        )

        logger.info(
            "speech_synthesis_success",
            audio_size_bytes=len(audio_content),
        )

        # Return audio as streaming response
        audio_stream = BytesIO(audio_content)

        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Content-Length": str(len(audio_content)),
            },
        )

    except Exception as e:
        logger.error(
            "synthesize_speech_failed",
            text_preview=request.text[:100],
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to synthesize speech: {str(e)}",
        )


@router.post("/conversation", response_model=ConversationResponse)
async def voice_conversation(request: ConversationRequest) -> ConversationResponse:
    """
    Process a full voice conversation: query → agent processing → audio response.

    This endpoint combines:
    1. Query processing by specified agent (default: Drummond for NLG)
    2. Optional TTS synthesis of agent response

    **Example Usage:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/voice/conversation" \\
         -H "Content-Type: application/json" \\
         -d '{
           "query": "Quais são os principais indicadores de corrupção?",
           "agent_id": "drummond",
           "return_audio": true
         }'
    ```
    """
    try:
        import time

        start_time = time.time()

        logger.info(
            "voice_conversation_request",
            query_length=len(request.query),
            agent=request.agent_id,
            return_audio=request.return_audio,
        )

        # Integrate with agent pool to process query
        from src.agents.deodoro import AgentContext
        from src.agents.drummond import DrummondAgent
        from src.agents.simple_agent_pool import get_agent_pool
        from src.memory.conversational import ConversationContext
        from src.services.agent_voice_profiles import get_agent_voice_profile

        # Get agent pool
        agent_pool = await get_agent_pool()

        # Get voice profile for the agent
        voice_profile = get_agent_voice_profile(request.agent_id)

        # Create agent context
        context = AgentContext(
            user_id="voice_user",
            session_id=f"voice_session_{int(time.time())}",
            request_id=f"voice_req_{int(time.time())}",
        )

        # Process with Drummond agent for conversational responses
        response_text = ""
        try:
            async with agent_pool.acquire(DrummondAgent, context) as agent:
                # Create conversation context
                conv_context = ConversationContext(
                    session_id=context.session_id,
                    user_id=context.user_id,
                )

                # Process conversation with Drummond
                result = await agent.process_conversation(
                    message=request.query, context=conv_context, intent=None
                )

                # Extract response text
                response_text = result.get(
                    "response", "Desculpe, não consegui processar sua pergunta."
                )

                logger.info(
                    "agent_processing_complete",
                    response_length=len(response_text),
                )

        except Exception as agent_error:
            logger.error(
                "agent_processing_failed",
                error=str(agent_error),
                exc_info=True,
            )
            # Fallback response
            response_text = (
                "Desculpe, houve um problema ao processar sua pergunta. "
                "Por favor, tente novamente."
            )

        # Generate audio if requested
        audio_available = False
        if request.return_audio and response_text:
            try:
                voice_service = get_voice_service()
                # Use agent's voice profile (personality-matched voice)
                await voice_service.synthesize_speech(
                    text=response_text,
                    voice_name=voice_profile.voice_name,
                    speaking_rate=voice_profile.speaking_rate,
                    pitch=voice_profile.pitch,
                )
                audio_available = True
                logger.info(
                    "tts_synthesis_complete",
                    agent_voice=voice_profile.voice_name,
                    speaking_rate=voice_profile.speaking_rate,
                )
            except Exception as tts_error:
                logger.error(
                    "tts_synthesis_failed",
                    error=str(tts_error),
                    exc_info=True,
                )
                # Continue without audio

        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(
            "voice_conversation_success",
            processing_time_ms=processing_time_ms,
            response_length=len(response_text),
            audio_generated=audio_available,
        )

        return ConversationResponse(
            query=request.query,
            response_text=response_text,
            audio_available=audio_available,
            audio_format="mp3",
            processing_time_ms=processing_time_ms,
        )

    except Exception as e:
        logger.error(
            "voice_conversation_failed",
            query=request.query,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process voice conversation: {str(e)}",
        )


@router.post("/conversation/stream")
async def voice_conversation_stream(
    request: ConversationRequest,
) -> StreamingResponse:
    """
    Real-time streaming voice conversation with agent.

    Returns Server-Sent Events (SSE) stream with:
    - Partial text responses as agent processes
    - Final audio response (if return_audio=true)

    **Example Usage:**
    ```bash
    curl -N -X POST "http://localhost:8000/api/v1/voice/conversation/stream" \\
         -H "Content-Type: application/json" \\
         -d '{"query": "Explique contratos públicos", "return_audio": true}'
    ```
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for streaming conversation."""
        try:
            import json
            import time

            from src.agents.deodoro import AgentContext
            from src.agents.drummond import DrummondAgent
            from src.agents.simple_agent_pool import get_agent_pool
            from src.memory.conversational import ConversationContext
            from src.services.agent_voice_profiles import get_agent_voice_profile

            logger.info(
                "voice_conversation_stream_started",
                query=request.query,
                agent=request.agent_id,
            )

            # Get voice profile for the agent
            voice_profile = get_agent_voice_profile(request.agent_id)

            # Send initial event with agent info
            yield f"event: start\ndata: {json.dumps({'status': 'processing', 'query': request.query, 'agent': request.agent_id, 'voice': voice_profile.voice_name})}\n\n"

            # Get agent pool
            agent_pool = await get_agent_pool()

            # Create agent context
            context = AgentContext(
                user_id="voice_stream_user",
                session_id=f"voice_stream_{int(time.time())}",
                request_id=f"voice_stream_req_{int(time.time())}",
            )

            # Send progress event
            yield f"event: progress\ndata: {json.dumps({'message': 'Conectando com agente Drummond...'})}\n\n"

            response_text = ""
            try:
                async with agent_pool.acquire(DrummondAgent, context) as agent:
                    # Create conversation context
                    conv_context = ConversationContext(
                        session_id=context.session_id,
                        user_id=context.user_id,
                    )

                    # Send progress event
                    yield f"event: progress\ndata: {json.dumps({'message': 'Processando pergunta...'})}\n\n"

                    # Process conversation with Drummond
                    result = await agent.process_conversation(
                        message=request.query, context=conv_context, intent=None
                    )

                    # Extract response text
                    response_text = result.get(
                        "response", "Desculpe, não consegui processar sua pergunta."
                    )

                    # Stream response in chunks (simulate streaming)
                    words = response_text.split()
                    chunk_size = 5  # Words per chunk
                    for i in range(0, len(words), chunk_size):
                        chunk = " ".join(words[i : i + chunk_size])
                        yield f"event: text\ndata: {json.dumps({'text': chunk})}\n\n"

                    logger.info(
                        "agent_streaming_complete",
                        response_length=len(response_text),
                    )

            except Exception as agent_error:
                logger.error(
                    "agent_streaming_failed",
                    error=str(agent_error),
                    exc_info=True,
                )
                # Send error event but continue
                error_msg = "Desculpe, houve um problema. Por favor, tente novamente."
                yield f"event: error\ndata: {json.dumps({'error': str(agent_error), 'fallback': error_msg})}\n\n"
                response_text = error_msg

            # Generate audio if requested
            if request.return_audio and response_text:
                try:
                    yield f"event: progress\ndata: {json.dumps({'message': f'Gerando áudio com voz de {voice_profile.agent_name}...'})}\n\n"

                    voice_service = get_voice_service()
                    # Use agent's personality-matched voice
                    audio_content = await voice_service.synthesize_speech(
                        text=response_text,
                        voice_name=voice_profile.voice_name,
                        speaking_rate=voice_profile.speaking_rate,
                        pitch=voice_profile.pitch,
                    )

                    # Convert audio to base64 for streaming
                    import base64

                    audio_base64 = base64.b64encode(audio_content).decode("utf-8")

                    # Stream audio in chunks (4KB per chunk)
                    chunk_size = 4096
                    for i in range(0, len(audio_base64), chunk_size):
                        chunk = audio_base64[i : i + chunk_size]
                        is_final = i + chunk_size >= len(audio_base64)
                        yield f"event: audio\ndata: {json.dumps({'chunk': chunk, 'final': is_final})}\n\n"

                    logger.info("audio_streaming_complete")

                except Exception as tts_error:
                    logger.error(
                        "audio_streaming_failed",
                        error=str(tts_error),
                        exc_info=True,
                    )
                    # Continue without audio
                    yield f"event: warning\ndata: {json.dumps({'message': 'Áudio não disponível'})}\n\n"

            # Send completion event
            yield f"event: done\ndata: {json.dumps({'status': 'completed', 'total_length': len(response_text)})}\n\n"

            logger.info("voice_conversation_stream_completed")

        except Exception as e:
            logger.error(
                "voice_conversation_stream_failed",
                error=str(e),
                exc_info=True,
            )
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/voices")
async def list_available_voices():
    """
    List all available Google Cloud TTS voices for Brazilian Portuguese.

    Returns voice names, gender, and quality information.

    **Example Usage:**
    ```bash
    curl http://localhost:8000/api/v1/voice/voices
    ```
    """
    return {
        "voices": [
            {
                "name": "pt-BR-Wavenet-A",
                "gender": "female",
                "quality": "high",
                "type": "wavenet",
                "description": "Natural female voice, warm and clear",
            },
            {
                "name": "pt-BR-Wavenet-B",
                "gender": "male",
                "quality": "high",
                "type": "wavenet",
                "description": "Natural male voice, professional and confident",
            },
            {
                "name": "pt-BR-Neural2-A",
                "gender": "female",
                "quality": "very_high",
                "type": "neural2",
                "description": "Latest female voice, extremely natural (recommended)",
            },
            {
                "name": "pt-BR-Neural2-B",
                "gender": "male",
                "quality": "very_high",
                "type": "neural2",
                "description": "Latest male voice, extremely natural (recommended)",
            },
            {
                "name": "pt-BR-Standard-A",
                "gender": "female",
                "quality": "standard",
                "type": "standard",
                "description": "Standard female voice (basic quality)",
            },
            {
                "name": "pt-BR-Standard-B",
                "gender": "male",
                "quality": "standard",
                "type": "standard",
                "description": "Standard male voice (basic quality)",
            },
        ],
        "recommended": ["pt-BR-Neural2-A", "pt-BR-Neural2-B"],
        "default": "pt-BR-Wavenet-A",
    }


@router.get("/agent-voices")
async def list_agent_voice_profiles():
    """
    List voice profiles for all AI agents.

    Each agent has a personality-matched voice with specific characteristics:
    - Voice name (Google Cloud TTS voice)
    - Speaking rate (faster/slower based on personality)
    - Pitch adjustment (higher/lower for character)
    - Voice description explaining the choice

    **Example Usage:**
    ```bash
    curl http://localhost:8000/api/v1/voice/agent-voices
    ```

    **Example Response:**
    ```json
    {
      "agents": {
        "drummond": {
          "agent_name": "Carlos Drummond de Andrade",
          "voice_name": "pt-BR-Wavenet-A",
          "gender": "female",
          "quality": "wavenet",
          "speaking_rate": 1.0,
          "pitch": 0.0,
          "description": "Voz feminina calorosa...",
          "personality_traits": ["Poetic", "Conversational"]
        }
      },
      "statistics": {
        "total_agents": 16,
        "gender_distribution": {"male": 10, "female": 6},
        "quality_distribution": {"neural2": 6, "wavenet": 10},
        "fastest_agent": "ayrton_senna",
        "slowest_agent": "machado"
      }
    }
    ```
    """
    from src.services.agent_voice_profiles import (
        get_voice_statistics,
        list_all_agent_voices,
    )

    profiles = list_all_agent_voices()
    stats = get_voice_statistics()

    # Convert profiles to dict format
    agents_data = {}
    for agent_id, profile in profiles.items():
        agents_data[agent_id] = {
            "agent_id": profile.agent_id,
            "agent_name": profile.agent_name,
            "voice_name": profile.voice_name,
            "gender": profile.gender.value,
            "quality": profile.quality.value,
            "speaking_rate": profile.speaking_rate,
            "pitch": profile.pitch,
            "description": profile.description,
            "personality_traits": profile.personality_traits,
        }

    return {
        "agents": agents_data,
        "statistics": stats,
        "total_voices": len(agents_data),
    }


@router.get("/health")
async def voice_service_health():
    """
    Check voice service health and configuration status.

    Returns service status, Google Cloud credentials status, and features.
    """
    try:
        voice_service = get_voice_service()

        return {
            "status": "healthy",
            "service": "voice",
            "features": {
                "speech_to_text": True,
                "text_to_speech": True,
                "streaming": True,
                "conversations": True,
            },
            "configuration": {
                "language": voice_service.language_code,
                "credentials_configured": bool(voice_service.credentials_path),
            },
            "endpoints": {
                "transcribe": "/api/v1/voice/transcribe",
                "speak": "/api/v1/voice/speak",
                "conversation": "/api/v1/voice/conversation",
                "stream": "/api/v1/voice/conversation/stream",
                "voices": "/api/v1/voice/voices",
            },
        }

    except Exception as e:
        logger.error("voice_health_check_failed", error=str(e), exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Voice service initialization failed",
        }
