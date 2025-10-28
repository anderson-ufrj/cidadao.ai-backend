# Maritaca.ai Direct Chat API - Frontend Integration Guide

**Date**: 2025-10-28
**Status**: ✅ Production Ready
**Base URL**: `https://cidadao-api-production.up.railway.app/api/v1/chat/direct/maritaca`

---

## 📋 Quick Summary

New API endpoints for direct chat with Maritaca.ai models (Sabiazinho-3 and Sabiá-3).
Perfect for testing, benchmarking, and potential partnership demonstrations.

**4 New Endpoints**:
1. `GET /models` - Get model list for UI selector
2. `POST /` - Synchronous chat completion
3. `POST /stream` - Real-time streaming chat (SSE)
4. `GET /health` - API health check

---

## 🎨 1. Model Selector Endpoint

### GET `/models`

Get available models with UI metadata (icons, colors, descriptions).

**Request**:
```typescript
const response = await fetch(
  'https://cidadao-api-production.up.railway.app/api/v1/chat/direct/maritaca/models'
);
const data = await response.json();
```

**Response**:
```json
{
  "models": [
    {
      "id": "sabiazinho-3",
      "name": "Sabiazinho-3",
      "description": "Modelo rápido e eficiente para uso geral",
      "icon": "⚡",
      "color": "#00D9FF",
      "context_window": 8192,
      "recommended_for": ["chat", "respostas_rapidas", "perguntas_gerais"],
      "tier": "standard",
      "is_default": true
    },
    {
      "id": "sabia-3",
      "name": "Sabiá-3",
      "description": "Modelo mais avançado com raciocínio complexo",
      "icon": "🧠",
      "color": "#FF6B35",
      "context_window": 32768,
      "recommended_for": ["analise", "raciocinio_complexo", "contexto_longo"],
      "tier": "premium",
      "is_default": false
    }
  ],
  "default_model": "sabiazinho-3",
  "provider": "maritaca",
  "provider_name": "Maritaca AI",
  "provider_url": "https://maritaca.ai"
}
```

**TypeScript Types**:
```typescript
interface MaritacaModel {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  context_window: number;
  recommended_for: string[];
  tier: 'standard' | 'premium';
  is_default: boolean;
}

interface ModelsResponse {
  models: MaritacaModel[];
  default_model: string;
  provider: string;
  provider_name: string;
  provider_url: string;
}
```

---

## 💬 2. Direct Chat Endpoint (Synchronous)

### POST `/`

Send message and get complete response at once.

**Request**:
```typescript
interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface ChatRequest {
  messages: ChatMessage[];
  temperature?: number; // 0.0 to 2.0, default: 0.7
  max_tokens?: number;  // 1 to 8192, default: 2048
  stream?: boolean;     // false for sync
  model?: string;       // 'sabiazinho-3' or 'sabia-3'
}

const response = await fetch(
  'https://cidadao-api-production.up.railway.app/api/v1/chat/direct/maritaca',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: [
        {
          role: 'system',
          content: 'Você é um assistente especializado em transparência pública.',
        },
        {
          role: 'user',
          content: 'O que são licitações públicas?',
        },
      ],
      model: 'sabiazinho-3', // or 'sabia-3'
      temperature: 0.7,
      max_tokens: 1024,
    }),
  }
);

const data = await response.json();
```

**Response**:
```json
{
  "id": "maritaca-1730126400",
  "model": "sabiazinho-3",
  "content": "Licitações públicas são processos administrativos...",
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 120,
    "total_tokens": 165
  },
  "created_at": "2025-10-28T15:30:00Z",
  "finish_reason": "stop"
}
```

**TypeScript Types**:
```typescript
interface ChatResponse {
  id: string;
  model: string;
  content: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  } | null;
  created_at: string;
  finish_reason: string | null;
}
```

---

## 🌊 3. Streaming Chat Endpoint (Real-time)

### POST `/stream`

Get response in real-time using Server-Sent Events (SSE).

**Request**:
```typescript
const response = await fetch(
  'https://cidadao-api-production.up.railway.app/api/v1/chat/direct/maritaca/stream',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: [
        {
          role: 'user',
          content: 'Conte uma história sobre transparência governamental',
        },
      ],
      stream: true,
      model: 'sabiazinho-3',
      max_tokens: 500,
    }),
  }
);

// Process SSE stream
const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));

      if (data.content) {
        // Append content to UI
        console.log(data.content);
      }

      if (data.done) {
        // Stream complete
        break;
      }

      if (data.error) {
        // Handle error
        console.error(data.error);
      }
    }
  }
}
```

**SSE Event Format**:
```typescript
// Content chunk
data: {"content": "Era uma vez"}

// Content chunk
data: {"content": " um cidadão"}

// Completion marker
data: {"done": true}

// Error (if any)
data: {"error": "API timeout", "done": true}
```

---

## 🏥 4. Health Check Endpoint

### GET `/health`

Check if Maritaca.ai API is available.

**Request**:
```typescript
const response = await fetch(
  'https://cidadao-api-production.up.railway.app/api/v1/chat/direct/maritaca/health'
);
const data = await response.json();
```

**Response (Healthy)**:
```json
{
  "status": "healthy",
  "model": "sabiazinho-3",
  "api_base": "https://chat.maritaca.ai/api",
  "response_received": true,
  "checked_at": "2025-10-28T15:30:00Z"
}
```

**Response (Unhealthy)**:
```json
{
  "status": "unhealthy",
  "error": "Connection timeout",
  "api_base": "https://chat.maritaca.ai/api",
  "checked_at": "2025-10-28T15:30:00Z"
}
```

---

## 🎨 UI Implementation Examples

### 1. Model Selector Component (React/Next.js)

```tsx
'use client';

import { useState, useEffect } from 'react';

interface MaritacaModel {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  tier: string;
}

export function ModelSelector() {
  const [models, setModels] = useState<MaritacaModel[]>([]);
  const [selectedModel, setSelectedModel] = useState('sabiazinho-3');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/chat/direct/maritaca/models')
      .then((res) => res.json())
      .then((data) => {
        setModels(data.models);
        setSelectedModel(data.default_model);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load models:', err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Carregando modelos...</div>;

  return (
    <select
      value={selectedModel}
      onChange={(e) => setSelectedModel(e.target.value)}
      className="model-selector"
    >
      {models.map((model) => (
        <option key={model.id} value={model.id}>
          {model.icon} {model.name} - {model.description}
        </option>
      ))}
    </select>
  );
}
```

### 2. Simple Chat Component (React/Next.js)

```tsx
'use client';

import { useState } from 'react';

export function MaritacaChat() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState('sabiazinho-3');

  const sendMessage = async () => {
    setLoading(true);
    setResponse('');

    try {
      const res = await fetch('/api/v1/chat/direct/maritaca', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [
            { role: 'user', content: message },
          ],
          model,
          temperature: 0.7,
          max_tokens: 1024,
        }),
      });

      const data = await res.json();
      setResponse(data.content);

      // Show token usage
      console.log('Tokens used:', data.usage.total_tokens);
    } catch (error) {
      console.error('Chat failed:', error);
      setResponse('Erro ao enviar mensagem.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Digite sua mensagem..."
        rows={4}
      />

      <button onClick={sendMessage} disabled={loading}>
        {loading ? 'Enviando...' : 'Enviar'}
      </button>

      {response && (
        <div className="response">
          <strong>Resposta:</strong>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}
```

### 3. Streaming Chat Component (React/Next.js)

```tsx
'use client';

import { useState } from 'react';

export function StreamingChat() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [streaming, setStreaming] = useState(false);

  const sendStreamingMessage = async () => {
    setStreaming(true);
    setResponse('');

    try {
      const res = await fetch('/api/v1/chat/direct/maritaca/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [{ role: 'user', content: message }],
          stream: true,
          model: 'sabiazinho-3',
        }),
      });

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No reader available');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.content) {
                setResponse((prev) => prev + data.content);
              }

              if (data.done) {
                setStreaming(false);
                return;
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming failed:', error);
      setResponse('Erro durante streaming.');
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="streaming-chat">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Digite sua mensagem..."
        rows={4}
      />

      <button onClick={sendStreamingMessage} disabled={streaming}>
        {streaming ? 'Recebendo...' : 'Enviar (Streaming)'}
      </button>

      {response && (
        <div className="response streaming">
          <strong>Resposta:</strong>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}
```

---

## ⚠️ Error Handling

All endpoints return standard HTTP status codes:

**Success**: `200 OK`
**Client Error**: `400 Bad Request`, `403 Forbidden`, `404 Not Found`
**Server Error**: `500 Internal Server Error`, `503 Service Unavailable`

**Error Response Format**:
```json
{
  "detail": "Falha ao comunicar com Maritaca.ai: Connection timeout"
}
```

**Example Error Handling**:
```typescript
try {
  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  const data = await response.json();
  return data;
} catch (error) {
  console.error('Maritaca API error:', error);
  // Show user-friendly error message
}
```

---

## 🔧 Configuration

**Environment Variables** (Next.js `.env.local`):
```bash
# Backend API URL
NEXT_PUBLIC_API_URL=https://cidadao-api-production.up.railway.app

# Optional: API authentication (if required later)
NEXT_PUBLIC_API_KEY=your-api-key
```

**API Client Helper**:
```typescript
// lib/maritaca-client.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const MARITACA_BASE = `${API_BASE}/api/v1/chat/direct/maritaca`;

export const maritacaClient = {
  async getModels() {
    const res = await fetch(`${MARITACA_BASE}/models`);
    return res.json();
  },

  async chat(messages: ChatMessage[], model = 'sabiazinho-3') {
    const res = await fetch(MARITACA_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, model }),
    });
    return res.json();
  },

  async checkHealth() {
    const res = await fetch(`${MARITACA_BASE}/health`);
    return res.json();
  },
};
```

---

## 📊 Usage Recommendations

### When to Use Each Model:

**Sabiazinho-3** (⚡ Fast):
- Quick responses
- General Q&A
- Simple explanations
- Chat conversations
- **Lower cost**

**Sabiá-3** (🧠 Advanced):
- Complex analysis
- Long documents (up to 32K tokens)
- Multi-step reasoning
- Technical explanations
- **Higher quality**

### Best Practices:

1. **Model Selection**:
   - Default to `sabiazinho-3` for most use cases
   - Switch to `sabia-3` only when needed
   - Let users choose via selector

2. **Temperature Settings**:
   - `0.3-0.5`: Factual, deterministic responses
   - `0.7`: Balanced (default)
   - `0.8-1.0`: Creative, varied responses

3. **Token Limits**:
   - Chat: 500-1000 tokens
   - Analysis: 1500-2500 tokens
   - Long-form: 3000+ tokens

4. **Streaming**:
   - Use for responses > 200 tokens
   - Better UX for longer content
   - Lower perceived latency

---

## 🧪 Testing

**Quick Test** (Browser Console):
```javascript
// Test model list
fetch('https://cidadao-api-production.up.railway.app/api/v1/chat/direct/maritaca/models')
  .then(r => r.json())
  .then(console.log);

// Test chat
fetch('https://cidadao-api-production.up.railway.app/api/v1/chat/direct/maritaca', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    messages: [{role: 'user', content: 'Olá!'}],
    model: 'sabiazinho-3'
  })
}).then(r => r.json()).then(console.log);
```

---

## 📚 Additional Resources

- **API Docs**: https://cidadao-api-production.up.railway.app/docs
- **Maritaca.ai**: https://maritaca.ai
- **Support**: Open issue on GitHub repository

---

## 🎯 Summary Checklist

Frontend developers need to:

- [ ] Fetch model list from `/models` endpoint
- [ ] Create model selector UI component
- [ ] Implement synchronous chat with `/` endpoint
- [ ] (Optional) Implement streaming with `/stream` endpoint
- [ ] Add error handling for all requests
- [ ] Display token usage to users
- [ ] Add health check for monitoring

**That's it!** You're ready to integrate Maritaca.ai chat into your Next.js frontend! 🚀
