# Voice Integration Plan - Cidadão.AI

**Date**: October 30, 2025
**Status**: Planning Phase
**Priority**: High (Accessibility & User Experience)

---

## Executive Summary

Plan for integrating voice capabilities (Text-to-Speech and Speech-to-Text) into the Cidadão.AI platform, enabling citizens to interact with government transparency data through voice commands and audio responses.

### Key Benefits
- 🎯 **Accessibility**: Support for visually impaired citizens
- 📱 **Mobile-First**: Natural interaction on smartphones
- 🇧🇷 **Portuguese Native**: Focus on Brazilian Portuguese (PT-BR)
- 🚗 **Hands-Free**: Use while driving or multitasking
- 👴 **Senior-Friendly**: Easier for elderly citizens

---

## Architecture Overview

```
User Voice Input → STT (Speech-to-Text) → Drummond Agent → LLM Processing
                                               ↓
User Audio Output ← TTS (Text-to-Speech) ← Response Generation
```

### Components

1. **STT (Speech-to-Text)**: Convert voice to text
2. **NLU (Natural Language Understanding)**: Process intent (existing)
3. **Agent Processing**: Drummond handles conversation (existing)
4. **TTS (Text-to-Speech)**: Convert response to audio
5. **Audio Streaming**: Real-time audio delivery

---

## Technology Options

### Option 1: Google Cloud (Recommended for PT-BR) ⭐

**Speech-to-Text (STT)**:
- Product: Google Cloud Speech-to-Text API
- Brazilian Portuguese: ✅ Excellent support
- Real-time streaming: ✅ Yes
- Accuracy: 95%+ for PT-BR
- Cost: $0.006/15 seconds (~$1.44/hour)

**Text-to-Speech (TTS)**:
- Product: Google Cloud Text-to-Speech API
- Brazilian Portuguese voices: ✅ Multiple (WaveNet, Neural2)
- Natural quality: ✅ WaveNet (most natural)
- Cost: $16/1M characters (~$0.016/1K chars)

**Pros**:
- ✅ Best PT-BR support in the market
- ✅ WaveNet voices sound very natural
- ✅ Real-time streaming support
- ✅ Easy Python integration
- ✅ Handles accents and regional variations

**Cons**:
- ❌ Cost can add up with high usage
- ❌ Requires Google Cloud account
- ❌ Data leaves Brazil (LGPD consideration)

### Option 2: Azure Cognitive Services

**Speech-to-Text (STT)**:
- Product: Azure Speech Services
- Brazilian Portuguese: ✅ Good support
- Real-time streaming: ✅ Yes
- Accuracy: 90-95% for PT-BR
- Cost: $1/hour (standard), $2.50/hour (custom)

**Text-to-Speech (TTS)**:
- Product: Azure Neural TTS
- Brazilian Portuguese voices: ✅ Multiple neural voices
- Natural quality: ✅ Very good
- Cost: $16/1M characters

**Pros**:
- ✅ Good PT-BR support
- ✅ Neural voices sound natural
- ✅ Integration with other Azure services
- ✅ SDK bem documentado

**Cons**:
- ❌ Slightly less accurate than Google for PT-BR
- ❌ More complex pricing
- ❌ Data leaves Brazil

### Option 3: OpenAI Whisper + ElevenLabs

**Speech-to-Text (STT)**:
- Product: OpenAI Whisper (open-source) or Whisper API
- Brazilian Portuguese: ✅ Good support (multilingual)
- Real-time: ⚠️ Not real-time (batch processing)
- Accuracy: 85-90% for PT-BR
- Cost: Free (self-hosted) or $0.006/minute (API)

**Text-to-Speech (TTS)**:
- Product: ElevenLabs
- Brazilian Portuguese: ✅ Yes (custom voices)
- Natural quality: ✅ Excellent (AI-generated)
- Cost: $22/month (30K chars) to $330/month (2M chars)

**Pros**:
- ✅ Whisper is open-source (can self-host)
- ✅ ElevenLabs has very natural voices
- ✅ Custom voice training possible
- ✅ More privacy (self-hosted Whisper)

**Cons**:
- ❌ Whisper not optimized for real-time
- ❌ ElevenLabs is expensive
- ❌ Requires integration of two separate services

### Option 4: Local/Self-Hosted (Privacy-First)

**Speech-to-Text (STT)**:
- Product: Vosk (offline STT) or Mozilla DeepSpeech
- Brazilian Portuguese: ⚠️ Limited models
- Real-time: ✅ Yes (low latency)
- Accuracy: 70-80% for PT-BR
- Cost: Free (infrastructure only)

**Text-to-Speech (TTS)**:
- Product: Mozilla TTS or Coqui TTS
- Brazilian Portuguese: ⚠️ Limited voices
- Natural quality: ⚠️ Robotic (not neural)
- Cost: Free (infrastructure only)

**Pros**:
- ✅ Complete data privacy (LGPD compliant)
- ✅ No per-usage costs
- ✅ Data stays in Brazil
- ✅ Full control

**Cons**:
- ❌ Lower accuracy
- ❌ Less natural-sounding voices
- ❌ Requires ML infrastructure
- ❌ More development effort

---

## Recommended Architecture

### Phase 1: MVP (Quick Win) 🚀

**STT**: Google Cloud Speech-to-Text
**TTS**: Google Cloud Text-to-Speech (WaveNet)
**Reason**: Best PT-BR quality, fastest implementation

```python
# STT Integration
from google.cloud import speech_v1
from google.cloud.speech_v1 import types

def transcribe_audio_stream(audio_stream):
    client = speech_v1.SpeechClient()

    config = types.RecognitionConfig(
        encoding=types.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="pt-BR",
        enable_automatic_punctuation=True,
        model="latest_long",  # Best for conversations
    )

    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True  # Real-time partial results
    )

    requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                for chunk in audio_stream)

    responses = client.streaming_recognize(streaming_config, requests)

    for response in responses:
        for result in response.results:
            if result.is_final:
                return result.alternatives[0].transcript
```

```python
# TTS Integration
from google.cloud import texttospeech_v1

def synthesize_speech(text: str) -> bytes:
    client = texttospeech_v1.TextToSpeechClient()

    input_text = texttospeech_v1.SynthesisInput(text=text)

    voice = texttospeech_v1.VoiceSelectionParams(
        language_code="pt-BR",
        name="pt-BR-Wavenet-A",  # Female, natural
        # Or: "pt-BR-Neural2-A" (even more natural)
    )

    audio_config = texttospeech_v1.AudioConfig(
        audio_encoding=texttospeech_v1.AudioEncoding.MP3,
        speaking_rate=1.0,
        pitch=0.0,
    )

    response = client.synthesize_speech(
        input=input_text,
        voice=voice,
        audio_config=audio_config
    )

    return response.audio_content  # MP3 bytes
```

### Phase 2: Optimization (2-3 months)

**STT**: Hybrid (Google for real-time + Whisper for batch)
**TTS**: Google WaveNet + Cache frequently used responses
**Additions**:
- Voice activity detection (VAD)
- Noise reduction
- Speaker diarization (multi-speaker)
- Custom vocabulary for government terms

### Phase 3: Privacy-Enhanced (6+ months)

**STT**: Self-hosted Whisper with fine-tuned PT-BR model
**TTS**: Custom trained TTS model on Brazilian voices
**Infrastructure**: On-premise or Brazilian data center
**Benefits**: Full LGPD compliance, no data leaving Brazil

---

## Integration with Drummond Agent

### Current Architecture
```
User Text → Drummond.process_conversation() → LLM → Text Response
```

### New Voice-Enabled Architecture
```
User Voice → STT → Text → Drummond.process_conversation() → LLM → Text → TTS → Audio
         ↑                                                              ↓
    Audio Input                                                   Audio Output
```

### Code Changes Needed

#### 1. Add Voice Service (`src/services/voice_service.py`)

```python
"""Voice service for STT and TTS."""

from typing import AsyncGenerator
from google.cloud import speech_v1, texttospeech_v1
import asyncio

class VoiceService:
    """Handle speech-to-text and text-to-speech."""

    def __init__(self):
        self.stt_client = speech_v1.SpeechClient()
        self.tts_client = texttospeech_v1.TextToSpeechClient()

    async def transcribe_audio(
        self,
        audio_stream: AsyncGenerator[bytes, None]
    ) -> str:
        """Convert audio to text."""
        # Implementation
        pass

    async def synthesize_speech(
        self,
        text: str,
        voice_config: dict = None
    ) -> bytes:
        """Convert text to audio."""
        # Implementation
        pass

    async def stream_audio_response(
        self,
        text: str
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio in chunks for real-time playback."""
        # Implementation
        pass
```

#### 2. Update Drummond Agent

```python
# In drummond.py

class CommunicationAgent(BaseAgent):

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(...)
        self.voice_service = VoiceService()  # Add voice service

    async def process_voice_message(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        context: ConversationContext,
    ) -> dict[str, Any]:
        """Process voice input and return voice response."""

        # 1. Transcribe audio to text
        text = await self.voice_service.transcribe_audio(audio_stream)

        # 2. Process as normal conversation
        response = await self.process_conversation(text, context)

        # 3. Synthesize response to audio
        audio_bytes = await self.voice_service.synthesize_speech(
            response["content"]
        )

        return {
            "transcription": text,
            "text_response": response["content"],
            "audio_response": audio_bytes,
            "metadata": response.get("metadata", {}),
        }

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """Process with voice support."""
        action = message.action

        # Add voice action
        if action == "process_voice":
            audio_stream = message.payload.get("audio_stream")
            conv_context = ConversationContext(...)

            result = await self.process_voice_message(
                audio_stream, conv_context
            )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result=result,
            )

        # ... existing actions
```

#### 3. Add Voice API Endpoint (`src/api/routes/voice.py`)

```python
"""Voice interaction endpoints."""

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    session_id: str = None,
):
    """Transcribe audio to text."""
    # Implementation
    pass

@router.post("/speak")
async def text_to_speech(
    text: str,
    voice: str = "pt-BR-Wavenet-A",
):
    """Convert text to speech."""
    # Implementation
    pass

@router.post("/conversation")
async def voice_conversation(
    audio: UploadFile = File(...),
    session_id: str = None,
):
    """Full voice conversation (STT + Processing + TTS)."""
    # Implementation
    pass

@router.post("/conversation/stream")
async def stream_voice_conversation(
    audio: UploadFile = File(...),
    session_id: str = None,
):
    """Streaming voice conversation."""
    # Return streaming audio response
    pass
```

---

## Frontend Integration

### WebRTC for Real-Time Audio

```typescript
// frontend/lib/voice/VoiceService.ts

export class VoiceService {
  private mediaRecorder: MediaRecorder | null = null;
  private audioContext: AudioContext | null = null;

  async startRecording(): Promise<MediaStream> {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000,
      }
    });

    this.mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    });

    return stream;
  }

  async sendVoiceMessage(audioBlob: Blob): Promise<VoiceResponse> {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    formData.append('session_id', this.sessionId);

    const response = await fetch('/api/v1/voice/conversation', {
      method: 'POST',
      body: formData,
    });

    return response.json();
  }

  async playAudioResponse(audioBytes: ArrayBuffer): Promise<void> {
    this.audioContext = new AudioContext();
    const audioBuffer = await this.audioContext.decodeAudioData(audioBytes);
    const source = this.audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(this.audioContext.destination);
    source.start();
  }
}
```

### Voice Chat Component

```typescript
// frontend/components/VoiceChat.tsx

'use client';

import { useState } from 'react';
import { VoiceService } from '@/lib/voice/VoiceService';

export function VoiceChat() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const voiceService = new VoiceService();

  const handleVoiceInput = async () => {
    if (!isRecording) {
      // Start recording
      setIsRecording(true);
      await voiceService.startRecording();
    } else {
      // Stop and process
      setIsRecording(false);
      setIsProcessing(true);

      const audioBlob = await voiceService.stopRecording();
      const response = await voiceService.sendVoiceMessage(audioBlob);

      // Play audio response
      await voiceService.playAudioResponse(response.audio_response);

      setIsProcessing(false);
    }
  };

  return (
    <button onClick={handleVoiceInput} disabled={isProcessing}>
      {isRecording ? '🔴 Gravando...' : '🎤 Falar'}
    </button>
  );
}
```

---

## Cost Estimation

### Scenario: 1000 daily users

**Assumptions**:
- Average conversation: 3 exchanges
- Average input: 10 seconds audio (~100 words)
- Average output: 50 words (~5 seconds audio)

**Google Cloud Costs (per month)**:
- STT: 1000 users × 3 exchanges × 10s × 30 days = 900K seconds
  - Cost: 900K / 15 × $0.006 = **$360/month**
- TTS: 1000 users × 3 exchanges × 50 words × 30 days = 4.5M words (~27M chars)
  - Cost: 27M / 1M × $16 = **$432/month**
- **Total: ~$800/month** for voice features

**Optimization Strategies**:
1. Cache common responses (TTS): -60% cost
2. Use shorter responses: -30% cost
3. Implement voice activity detection: -20% STT cost
4. **Optimized Cost: ~$400/month**

---

## Privacy & LGPD Compliance

### Data Flow
```
User Voice → Encrypted Transport → Google STT → Text (ephemeral)
                                       ↓
                                  Drummond (Brazil)
                                       ↓
Text Response → Google TTS → Audio (ephemeral) → User
```

### LGPD Considerations
1. **Consent**: User must opt-in to voice features
2. **Data Minimization**: Audio not stored (ephemeral)
3. **Transparency**: Clear privacy policy about voice data
4. **Security**: End-to-end encryption (TLS)
5. **Right to Deletion**: No persistent voice data to delete

### Privacy-Enhanced Mode
- Option to use self-hosted Whisper (Phase 3)
- Audio processed entirely in Brazil
- No data sent to US cloud providers

---

## Implementation Roadmap

### Month 1: MVP (Google Cloud)
- [x] Research and document (this document)
- [ ] Setup Google Cloud Speech APIs
- [ ] Implement `VoiceService` class
- [ ] Add voice endpoints to API
- [ ] Basic frontend voice button
- [ ] Integration tests
- [ ] Deploy to staging

### Month 2-3: Optimization
- [ ] Add audio caching (common responses)
- [ ] Implement VAD (voice activity detection)
- [ ] Add noise reduction
- [ ] Performance testing
- [ ] User feedback collection

### Month 4-6: Privacy Enhancement
- [ ] Evaluate Whisper fine-tuning
- [ ] Setup self-hosted STT infrastructure
- [ ] Train custom TTS model
- [ ] Migrate to Brazilian data center
- [ ] LGPD audit

---

## Success Metrics

### Technical KPIs
- **STT Accuracy**: >95% word error rate (WER)
- **TTS Naturalness**: >4.0/5.0 MOS (Mean Opinion Score)
- **Latency**: <2s end-to-end (voice in → audio out)
- **Uptime**: >99.9%

### User KPIs
- **Adoption**: >20% of users try voice feature
- **Retention**: >50% use voice weekly after first use
- **Satisfaction**: >4.0/5.0 rating
- **Accessibility**: >80% of visually impaired users use voice

---

## Next Steps

1. **Get Approval**: Review this plan with stakeholders
2. **Budget Allocation**: Secure $800/month for Google Cloud
3. **Setup Google Cloud**: Create project and enable APIs
4. **Implement MVP**: Start with VoiceService implementation
5. **User Testing**: Beta test with 10-20 users
6. **Iterate**: Based on feedback and metrics

---

**Contact**: Development Team
**Last Updated**: October 30, 2025
**Status**: Awaiting Approval ⏳
