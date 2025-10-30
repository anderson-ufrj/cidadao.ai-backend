# Frontend Voice Integration Guide

**Last Updated**: 2025-10-30
**Voice System**: Chirp3-HD Premium (16 unique voices)
**Status**: Production Ready

---

## 🎯 Overview

The Cidadão.AI backend now provides a complete voice system with 16 unique premium voices using Google Cloud's Chirp3-HD. Each of the 16 AI agents has a distinct voice with mythological identity.

**Key Features**:
- ✅ 16 unique voices (10 male, 6 female)
- ✅ Automatic voice selection per agent
- ✅ Ultra-natural Brazilian Portuguese
- ✅ Mythological names (Fenrir, Zephyr, Charon, etc.)
- ✅ Speed variations (0.85x - 1.15x)
- ✅ RESTful API endpoints

---

## 📡 API Endpoints

### Base URL
```
Production: https://cidadao-api-production.up.railway.app
Development: http://localhost:8000
```

### 1. Text-to-Speech (Synthesize Voice)

**Endpoint**: `POST /api/v1/voice/synthesize`

**Request**:
```typescript
interface VoiceSynthesizeRequest {
  text: string;                    // Text to synthesize (required)
  agent_id?: string;               // Agent ID for automatic voice selection
  voice_name?: string;             // Override with specific Chirp3-HD voice
  speaking_rate?: number;          // Override speed (0.25-4.0, default: 1.0)
  language_code?: string;          // Default: "pt-BR"
  output_format?: "mp3" | "ogg_opus" | "linear16";  // Default: "mp3"
}
```

**Response**: Binary audio file (MP3)

**Example (Automatic Voice Selection)**:
```typescript
// Drummond will automatically use pt-BR-Chirp3-HD-Zephyr voice
const response = await fetch('/api/v1/voice/synthesize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Olá, sou Drummond, o poeta do povo.',
    agent_id: 'drummond'  // Automatic voice selection
  })
});

const audioBlob = await response.blob();
const audioUrl = URL.createObjectURL(audioBlob);
const audio = new Audio(audioUrl);
audio.play();
```

**Example (Manual Voice Override)**:
```typescript
// Override to use specific Chirp3-HD voice
const response = await fetch('/api/v1/voice/synthesize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Teste com voz específica',
    voice_name: 'pt-BR-Chirp3-HD-Fenrir',  // Manual override
    speaking_rate: 1.1  // Faster speech
  })
});
```

### 2. Speech-to-Text (Transcribe Audio)

**Endpoint**: `POST /api/v1/voice/transcribe`

**Request**: `multipart/form-data`
- `audio_file`: Audio file (mp3, wav, ogg, etc.)
- `language_code`: Optional (default: "pt-BR")

**Response**:
```typescript
interface TranscriptionResponse {
  transcript: string;              // Transcribed text
  confidence: number;              // Confidence score (0.0-1.0)
  language_code: string;           // Detected language
  metadata: {
    duration_seconds: number;
    audio_format: string;
  };
}
```

**Example**:
```typescript
const formData = new FormData();
formData.append('audio_file', audioBlob, 'recording.mp3');
formData.append('language_code', 'pt-BR');

const response = await fetch('/api/v1/voice/transcribe', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Transcription:', result.transcript);
console.log('Confidence:', result.confidence);
```

### 3. Conversational Voice (Chat + Voice)

**Endpoint**: `POST /api/v1/voice/conversation`

**Request**:
```typescript
interface VoiceConversationRequest {
  message: string;                 // User's text message
  agent_id: string;                // Which agent to talk to
  conversation_id?: string;        // Optional conversation tracking
  include_audio?: boolean;         // Return audio response (default: true)
}
```

**Response**:
```typescript
interface VoiceConversationResponse {
  message: string;                 // Agent's text response
  agent_id: string;                // Responding agent
  voice_used: string;              // Chirp3-HD voice name
  audio_url?: string;              // Base64 encoded audio (if include_audio=true)
  metadata: {
    response_time_ms: number;
    voice_generation_time_ms: number;
  };
}
```

**Example**:
```typescript
const response = await fetch('/api/v1/voice/conversation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Quais contratos você pode analisar?',
    agent_id: 'zumbi',  // Zumbi will use Fenrir voice
    include_audio: true
  })
});

const data = await response.json();
console.log('Agent says:', data.message);
console.log('Using voice:', data.voice_used);  // pt-BR-Chirp3-HD-Fenrir

// Play audio response
if (data.audio_url) {
  const audio = new Audio(`data:audio/mp3;base64,${data.audio_url}`);
  audio.play();
}
```

### 4. Streaming Voice Conversation

**Endpoint**: `POST /api/v1/voice/conversation/stream`

**Request**: Same as `/conversation`

**Response**: Server-Sent Events (SSE) stream

**Example**:
```typescript
const response = await fetch('/api/v1/voice/conversation/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Analise contratos recentes',
    agent_id: 'zumbi'
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));

      if (data.type === 'text_chunk') {
        console.log('Text chunk:', data.content);
      } else if (data.type === 'audio_chunk') {
        // Play audio chunk
        const audioBlob = base64ToBlob(data.content, 'audio/mp3');
        playAudioChunk(audioBlob);
      } else if (data.type === 'complete') {
        console.log('Stream complete');
      }
    }
  }
}
```

### 5. List Available Agent Voices

**Endpoint**: `GET /api/v1/voice/agent-voices`

**Response**:
```typescript
interface AgentVoice {
  agent_id: string;
  agent_name: string;
  voice_name: string;              // Chirp3-HD voice
  gender: "male" | "female";
  quality: "chirp3-hd";
  speaking_rate: number;
  pitch: number;                   // Always 0.0 for Chirp3-HD
  description: string;
  personality_traits: string[];
  mythological_meaning: string;    // Mythology behind the voice name
}

interface AgentVoicesResponse {
  total_agents: number;
  agents: AgentVoice[];
  statistics: {
    male_voices: number;
    female_voices: number;
    fastest_agent: string;
    slowest_agent: string;
  };
}
```

**Example**:
```typescript
const response = await fetch('/api/v1/voice/agent-voices');
const data = await response.json();

console.log(`Total agents: ${data.total_agents}`);
data.agents.forEach(agent => {
  console.log(`${agent.agent_name}: ${agent.voice_name}`);
  console.log(`  Mythology: ${agent.mythological_meaning}`);
  console.log(`  Speed: ${agent.speaking_rate}x`);
});
```

---

## 🎭 Agent Voice Profiles

### Complete Voice Mapping

| Agent | Voice Name | Gender | Speed | Mythology |
|-------|------------|--------|-------|-----------|
| **Abaporu** | Rasalgethi | Male | 1.0x | Head of Serpent Charmer (α Herculis) |
| **Zumbi** | Fenrir | Male | 0.95x | Norse wolf who breaks chains |
| **Anita** | Callirrhoe | Female | 1.05x | Beautiful Flow (Greek nymph) |
| **Oxóssi** | Orus | Male | 0.90x | Egyptian sky god (Horus) |
| **Lampião** | Sadachbia | Male | 1.1x | Lucky Star of Hidden Things (γ Aquarii) |
| **Ayrton Senna** | Algenib | Male | 1.15x | Wing of Pegasus (γ Pegasi) |
| **Tiradentes** | Schedar | Male | 0.95x | Breast of Cassiopeia (α Cassiopeiae) |
| **Oscar Niemeyer** | Puck | Male | 0.90x | Mischievous fairy (Uranus moon) |
| **Machado** | Iapetus | Male | 0.85x | Titan of mortality (Saturn moon) |
| **Drummond** | Zephyr | Female | 1.0x | Gentle west wind (Greek mythology) |
| **Bonifácio** | Charon | Male | 0.90x | Ferryman of the dead (Pluto moon) |
| **Maria Quitéria** | Despina | Female | 1.0x | Lady/Mistress (Neptune moon) |
| **Nanã** | Leda | Female | 0.85x | Mother of Helen of Troy (Jupiter moon) |
| **Céuci** | Aoede | Female | 0.95x | Muse of Song (Jupiter moon) |
| **Obaluaiê** | Enceladus | Male | 0.90x | Buried giant (Saturn moon) |
| **Dandara** | Gacrux | Female | 1.05x | Southern Cross star (γ Crucis) |

---

## 💻 Frontend Implementation Examples

### React Component

```typescript
import React, { useState } from 'react';

interface VoicePlayerProps {
  agentId: string;
  text: string;
}

export const VoicePlayer: React.FC<VoicePlayerProps> = ({ agentId, text }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);

  const playVoice = async () => {
    try {
      setIsPlaying(true);

      const response = await fetch('/api/v1/voice/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          agent_id: agentId
        })
      });

      if (!response.ok) {
        throw new Error('Voice synthesis failed');
      }

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      const audioElement = new Audio(audioUrl);

      audioElement.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
      };

      audioElement.play();
      setAudio(audioElement);

    } catch (error) {
      console.error('Voice playback error:', error);
      setIsPlaying(false);
    }
  };

  const stopVoice = () => {
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
      setIsPlaying(false);
    }
  };

  return (
    <div className="voice-player">
      <button
        onClick={isPlaying ? stopVoice : playVoice}
        disabled={!text}
      >
        {isPlaying ? '⏸️ Stop' : '🎤 Play Voice'}
      </button>
    </div>
  );
};
```

### Vue 3 Component

```vue
<template>
  <div class="voice-player">
    <button
      @click="toggleVoice"
      :disabled="!text || loading"
      class="voice-button"
    >
      <span v-if="loading">⏳ Loading...</span>
      <span v-else-if="isPlaying">⏸️ Stop</span>
      <span v-else>🎤 Play Voice</span>
    </button>

    <div v-if="agentVoice" class="voice-info">
      <small>Voice: {{ agentVoice.voice_name }}</small>
      <small>Speed: {{ agentVoice.speaking_rate }}x</small>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

interface Props {
  agentId: string;
  text: string;
}

const props = defineProps<Props>();

const isPlaying = ref(false);
const loading = ref(false);
const audio = ref<HTMLAudioElement | null>(null);
const agentVoice = ref<any>(null);

onMounted(async () => {
  // Fetch agent voice info
  const response = await fetch('/api/v1/voice/agent-voices');
  const data = await response.json();
  agentVoice.value = data.agents.find(a => a.agent_id === props.agentId);
});

const playVoice = async () => {
  try {
    loading.value = true;

    const response = await fetch('/api/v1/voice/synthesize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: props.text,
        agent_id: props.agentId
      })
    });

    const blob = await response.blob();
    const audioUrl = URL.createObjectURL(blob);
    const audioElement = new Audio(audioUrl);

    audioElement.onended = () => {
      isPlaying.value = false;
      URL.revokeObjectURL(audioUrl);
    };

    await audioElement.play();
    audio.value = audioElement;
    isPlaying.value = true;

  } catch (error) {
    console.error('Voice error:', error);
  } finally {
    loading.value = false;
  }
};

const stopVoice = () => {
  if (audio.value) {
    audio.value.pause();
    audio.value.currentTime = 0;
    isPlaying.value = false;
  }
};

const toggleVoice = () => {
  if (isPlaying.value) {
    stopVoice();
  } else {
    playVoice();
  }
};
</script>
```

### Svelte Component

```svelte
<script lang="ts">
  export let agentId: string;
  export let text: string;

  let isPlaying = false;
  let loading = false;
  let audio: HTMLAudioElement | null = null;

  async function playVoice() {
    try {
      loading = true;

      const response = await fetch('/api/v1/voice/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          agent_id: agentId
        })
      });

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      const audioElement = new Audio(audioUrl);

      audioElement.onended = () => {
        isPlaying = false;
        URL.revokeObjectURL(audioUrl);
      };

      await audioElement.play();
      audio = audioElement;
      isPlaying = true;

    } catch (error) {
      console.error('Voice error:', error);
    } finally {
      loading = false;
    }
  }

  function stopVoice() {
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
      isPlaying = false;
    }
  }

  function toggleVoice() {
    if (isPlaying) {
      stopVoice();
    } else {
      playVoice();
    }
  }
</script>

<div class="voice-player">
  <button
    on:click={toggleVoice}
    disabled={!text || loading}
  >
    {#if loading}
      ⏳ Loading...
    {:else if isPlaying}
      ⏸️ Stop
    {:else}
      🎤 Play Voice
    {/if}
  </button>
</div>
```

---

## 🎨 UI/UX Recommendations

### 1. Voice Player Component

```typescript
// Display agent's voice identity
<AgentVoiceCard
  agentName="Zumbi dos Palmares"
  voiceName="Fenrir"
  mythology="Norse wolf who breaks chains"
  gender="male"
  speed="0.95x"
  onPlay={() => playVoice('zumbi', text)}
/>
```

### 2. Chat Message with Voice

```typescript
interface ChatMessageProps {
  message: string;
  agentId: string;
  timestamp: Date;
}

function ChatMessage({ message, agentId, timestamp }: ChatMessageProps) {
  return (
    <div className="chat-message">
      <div className="message-header">
        <AgentAvatar agentId={agentId} />
        <span className="timestamp">{formatTime(timestamp)}</span>
        <VoicePlayButton
          agentId={agentId}
          text={message}
          size="small"
        />
      </div>
      <div className="message-body">
        {message}
      </div>
    </div>
  );
}
```

### 3. Agent Voice Selector

```typescript
function AgentVoiceSelector({ onSelectAgent }) {
  const [voices, setVoices] = useState([]);

  useEffect(() => {
    fetch('/api/v1/voice/agent-voices')
      .then(r => r.json())
      .then(data => setVoices(data.agents));
  }, []);

  return (
    <div className="voice-selector">
      <h3>Choose an Agent Voice</h3>
      <div className="voice-grid">
        {voices.map(agent => (
          <VoiceCard
            key={agent.agent_id}
            agent={agent}
            onClick={() => onSelectAgent(agent.agent_id)}
            onPreview={() => playPreview(agent)}
          />
        ))}
      </div>
    </div>
  );
}
```

---

## 🔊 Audio Playback Best Practices

### 1. Audio Context Management

```typescript
class VoiceManager {
  private audioContext: AudioContext;
  private currentAudio: HTMLAudioElement | null = null;

  constructor() {
    this.audioContext = new AudioContext();
  }

  async play(agentId: string, text: string): Promise<void> {
    // Stop any currently playing audio
    this.stop();

    try {
      const response = await fetch('/api/v1/voice/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, agent_id: agentId })
      });

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);

      this.currentAudio = new Audio(audioUrl);
      this.currentAudio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        this.currentAudio = null;
      };

      await this.currentAudio.play();
    } catch (error) {
      console.error('Voice playback failed:', error);
      throw error;
    }
  }

  stop(): void {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }
  }

  isPlaying(): boolean {
    return this.currentAudio !== null && !this.currentAudio.paused;
  }
}

// Usage
const voiceManager = new VoiceManager();
await voiceManager.play('drummond', 'Olá, sou Drummond!');
```

### 2. Caching Strategy

```typescript
class VoiceCache {
  private cache: Map<string, Blob> = new Map();
  private maxSize: number = 50; // Maximum cached audio files

  getCacheKey(agentId: string, text: string): string {
    return `${agentId}:${text.substring(0, 100)}`;
  }

  async get(agentId: string, text: string): Promise<Blob | null> {
    const key = this.getCacheKey(agentId, text);
    return this.cache.get(key) || null;
  }

  async set(agentId: string, text: string, blob: Blob): Promise<void> {
    const key = this.getCacheKey(agentId, text);

    // LRU eviction if cache full
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, blob);
  }

  clear(): void {
    this.cache.clear();
  }
}

// Usage
const voiceCache = new VoiceCache();

async function playWithCache(agentId: string, text: string) {
  // Check cache first
  let blob = await voiceCache.get(agentId, text);

  if (!blob) {
    // Fetch from API
    const response = await fetch('/api/v1/voice/synthesize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, agent_id: agentId })
    });
    blob = await response.blob();

    // Cache for future use
    await voiceCache.set(agentId, text, blob);
  }

  // Play cached audio
  const audioUrl = URL.createObjectURL(blob);
  const audio = new Audio(audioUrl);
  await audio.play();
}
```

### 3. Queue Management

```typescript
class VoiceQueue {
  private queue: Array<{ agentId: string; text: string }> = [];
  private isPlaying: boolean = false;

  add(agentId: string, text: string): void {
    this.queue.push({ agentId, text });
    if (!this.isPlaying) {
      this.processQueue();
    }
  }

  private async processQueue(): Promise<void> {
    if (this.queue.length === 0) {
      this.isPlaying = false;
      return;
    }

    this.isPlaying = true;
    const item = this.queue.shift()!;

    try {
      await playVoice(item.agentId, item.text);
    } catch (error) {
      console.error('Voice playback error:', error);
    }

    // Process next item
    this.processQueue();
  }

  clear(): void {
    this.queue = [];
    this.isPlaying = false;
  }
}
```

---

## ⚡ Performance Optimization

### 1. Preload Common Phrases

```typescript
const COMMON_PHRASES = [
  { agentId: 'drummond', text: 'Olá! Como posso ajudar?' },
  { agentId: 'zumbi', text: 'Analisando contratos...' },
  { agentId: 'anita', text: 'Processando dados estatísticos...' }
];

async function preloadVoices() {
  const promises = COMMON_PHRASES.map(async ({ agentId, text }) => {
    const response = await fetch('/api/v1/voice/synthesize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, agent_id: agentId })
    });
    const blob = await response.blob();
    await voiceCache.set(agentId, text, blob);
  });

  await Promise.all(promises);
  console.log('Common phrases preloaded');
}

// Call on app initialization
preloadVoices();
```

### 2. Lazy Loading

```typescript
import { lazy, Suspense } from 'react';

const VoicePlayer = lazy(() => import('./components/VoicePlayer'));

function App() {
  return (
    <Suspense fallback={<div>Loading voice player...</div>}>
      <VoicePlayer agentId="drummond" text="Hello" />
    </Suspense>
  );
}
```

### 3. Web Workers for Audio Processing

```typescript
// voice-worker.ts
self.addEventListener('message', async (e) => {
  const { agentId, text } = e.data;

  try {
    const response = await fetch('/api/v1/voice/synthesize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, agent_id: agentId })
    });

    const blob = await response.blob();
    self.postMessage({ success: true, blob });
  } catch (error) {
    self.postMessage({ success: false, error: error.message });
  }
});

// Main thread
const voiceWorker = new Worker('voice-worker.ts');

voiceWorker.postMessage({ agentId: 'drummond', text: 'Hello' });
voiceWorker.addEventListener('message', (e) => {
  if (e.data.success) {
    const audioUrl = URL.createObjectURL(e.data.blob);
    const audio = new Audio(audioUrl);
    audio.play();
  }
});
```

---

## 🐛 Error Handling

### 1. Network Errors

```typescript
async function playVoiceWithRetry(
  agentId: string,
  text: string,
  maxRetries: number = 3
): Promise<void> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('/api/v1/voice/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, agent_id: agentId })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      await audio.play();
      return; // Success

    } catch (error) {
      console.warn(`Attempt ${i + 1} failed:`, error);

      if (i === maxRetries - 1) {
        // Last attempt failed
        throw new Error(`Failed to play voice after ${maxRetries} attempts`);
      }

      // Wait before retry (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
    }
  }
}
```

### 2. User-Friendly Error Messages

```typescript
function getErrorMessage(error: Error): string {
  if (error.message.includes('403')) {
    return 'Você não tem permissão para usar esta funcionalidade de voz.';
  } else if (error.message.includes('500')) {
    return 'Erro no servidor de voz. Tente novamente mais tarde.';
  } else if (error.message.includes('NetworkError')) {
    return 'Sem conexão com internet. Verifique sua conexão.';
  } else {
    return 'Erro ao reproduzir áudio. Tente novamente.';
  }
}

// Usage in component
try {
  await playVoice(agentId, text);
} catch (error) {
  const userMessage = getErrorMessage(error);
  toast.error(userMessage);
}
```

---

## 🎯 Testing

### Unit Tests (Jest)

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { VoicePlayer } from './VoicePlayer';

// Mock fetch
global.fetch = jest.fn();

describe('VoicePlayer', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should synthesize and play voice', async () => {
    const mockBlob = new Blob(['audio data'], { type: 'audio/mp3' });

    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      blob: async () => mockBlob
    });

    render(<VoicePlayer agentId="drummond" text="Test" />);

    const playButton = screen.getByText(/Play Voice/i);
    fireEvent.click(playButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/v1/voice/synthesize',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            text: 'Test',
            agent_id: 'drummond'
          })
        })
      );
    });
  });

  it('should handle errors gracefully', async () => {
    (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(<VoicePlayer agentId="drummond" text="Test" />);

    const playButton = screen.getByText(/Play Voice/i);
    fireEvent.click(playButton);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

### E2E Tests (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Voice Integration', () => {
  test('should play agent voice', async ({ page }) => {
    await page.goto('/chat');

    // Send message
    await page.fill('[data-testid="chat-input"]', 'Olá');
    await page.click('[data-testid="send-button"]');

    // Wait for agent response
    await page.waitForSelector('[data-testid="agent-message"]');

    // Click voice play button
    await page.click('[data-testid="voice-play-button"]');

    // Check audio element is playing
    const audioElement = page.locator('audio');
    await expect(audioElement).toHaveCount(1);
  });

  test('should display agent voice info', async ({ page }) => {
    await page.goto('/agents');

    // Click on Drummond agent
    await page.click('[data-testid="agent-drummond"]');

    // Check voice info is displayed
    await expect(page.locator('text=Zephyr')).toBeVisible();
    await expect(page.locator('text=Gentle west wind')).toBeVisible();
  });
});
```

---

## 📚 Additional Resources

- **API Documentation**: `/api/v1/docs` (Swagger UI)
- **Voice Samples**: Test all 16 voices at `/api/v1/voice/agent-voices`
- **Google Cloud TTS Docs**: https://cloud.google.com/text-to-speech/docs
- **Chirp3-HD Info**: Latest premium multilingual voices

---

## 🆘 Troubleshooting

### Issue: "Voice sounds robotic"
**Solution**: Ensure you're using Chirp3-HD voices (not Standard or WaveNet)

### Issue: "Audio doesn't play on mobile"
**Solution**: Require user interaction before playing audio (mobile browser restriction)

### Issue: "403 Forbidden on voice endpoint"
**Solution**: Check API authentication and Google Cloud credentials

### Issue: "Slow voice generation"
**Solution**: Implement caching and preloading for common phrases

---

## 📞 Support

For issues or questions about voice integration:
- GitHub Issues: https://github.com/anderson-ufrj/cidadao.ai-backend/issues
- API Status: Check `/health` endpoint

---

**Last Updated**: 2025-10-30
**Version**: 1.0 (Chirp3-HD Premium)
