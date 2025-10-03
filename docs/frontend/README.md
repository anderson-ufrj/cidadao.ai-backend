# 🎨 Frontend Integration Guide - Cidadão.AI Backend

**Author**: Anderson Henrique da Silva
**Last Updated**: 2025-10-03 (São Paulo, Brazil)

This directory contains comprehensive guides for integrating frontend applications with the Cidadão.AI Backend API.

## 📚 Integration Guides

### General Integration

- **[FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)** - Complete integration overview
  - API architecture and endpoints
  - Authentication and authorization flow
  - Error handling patterns
  - Best practices and recommendations

- **[FRONTEND_STABLE_INTEGRATION.md](./FRONTEND_STABLE_INTEGRATION.md)** - Stable production integration
  - Production-ready patterns
  - Tested integration strategies
  - Performance optimizations
  - Reliability patterns

- **[FRONTEND_INTEGRATION_PLAN.md](./FRONTEND_INTEGRATION_PLAN.md)** - Integration roadmap
  - Step-by-step implementation plan
  - Feature prioritization
  - Timeline and milestones
  - Testing strategy

### Chat Integration

- **[FRONTEND_CHAT_INTEGRATION.md](./FRONTEND_CHAT_INTEGRATION.md)** - Chat implementation guide
  - Real-time chat setup
  - SSE (Server-Sent Events) streaming
  - Message handling and display
  - Agent response rendering

- **[FRONTEND_CHATBOT_PROMPT.md](./FRONTEND_CHATBOT_PROMPT.md)** - Chatbot UX design
  - User interaction patterns
  - Prompt engineering guidelines
  - Response formatting
  - Error messages and fallbacks

### Code Examples

- **[examples/](./examples/)** - Working frontend examples
  - React component examples
  - Integration patterns
  - API client implementations
  - Hooks and utilities

## 🚀 Quick Start

### 1. Basic Setup

```typescript
// Install dependencies
npm install axios
// or
npm install @tanstack/react-query

// Create API client
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'https://neural-thinker-cidadao-ai-backend.hf.space',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 2. Authentication Flow

```typescript
// Login
async function login(email: string, password: string) {
  const response = await api.post('/api/v1/auth/login', {
    username: email,
    password,
  });

  const { access_token } = response.data;
  localStorage.setItem('token', access_token);
  return response.data;
}

// Register
async function register(email: string, password: string, fullName: string) {
  const response = await api.post('/api/v1/auth/register', {
    email,
    password,
    full_name: fullName,
  });
  return response.data;
}
```

### 3. Chat Integration (SSE)

```typescript
import { useState, useEffect } from 'react';

function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);

  async function sendMessage(content: string) {
    const eventSource = new EventSource(
      `${API_URL}/api/v1/chat/stream?message=${encodeURIComponent(content)}`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'chunk') {
        // Update streaming message
        setMessages(prev => updateLastMessage(prev, data.content));
      } else if (data.type === 'complete') {
        // Message complete
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      // Handle error
    };
  }

  return { messages, sendMessage };
}
```

### 4. Agent Interaction

```typescript
// Start an investigation
async function startInvestigation(params: InvestigationParams) {
  const response = await api.post('/api/v1/investigations', {
    agent_name: 'zumbi',
    parameters: params,
    context: {
      user_intent: 'detect_anomalies',
    },
  });

  return response.data.investigation_id;
}

// Get investigation status
async function getInvestigationStatus(investigationId: string) {
  const response = await api.get(`/api/v1/investigations/${investigationId}`);
  return response.data;
}
```

## 📦 Available Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user

### Chat
- `POST /api/v1/chat` - Send chat message (JSON response)
- `GET /api/v1/chat/stream` - Send chat message (SSE streaming)
- `GET /api/v1/chat/history` - Get chat history

### Investigations
- `POST /api/v1/investigations` - Start new investigation
- `GET /api/v1/investigations` - List investigations
- `GET /api/v1/investigations/{id}` - Get investigation details
- `DELETE /api/v1/investigations/{id}` - Cancel investigation

### Agents
- `GET /api/v1/agents` - List available agents
- `GET /api/v1/agents/{name}` - Get agent details
- `POST /api/v1/agents/{name}/analyze` - Direct agent analysis

### Portal da Transparência
- `GET /api/v1/transparency/contracts` - Search contracts
- `GET /api/v1/transparency/servants` - Search public servants
- `GET /api/v1/transparency/agencies` - List government agencies

For complete endpoint documentation, see [API Reference](../api/README.md).

## 🎨 UI/UX Recommendations

### Chat Interface
- **Streaming responses**: Show typing indicator during agent processing
- **Agent avatars**: Visual identity for each agent (Brazilian cultural themes)
- **Message types**: Differentiate user messages, agent responses, system messages
- **Code blocks**: Syntax highlighting for JSON/code in responses
- **Charts/graphs**: Render data visualizations when provided
- **Export options**: Allow users to export investigation results

### Error Handling
- **Network errors**: Show retry option
- **Rate limiting**: Display wait time
- **Agent unavailable**: Suggest alternative agents
- **Invalid input**: Clear validation messages

### Performance
- **Lazy loading**: Load messages on scroll
- **Debouncing**: Debounce search inputs
- **Caching**: Cache agent metadata and common queries
- **Optimistic UI**: Update UI before API response

## 🔒 Security Best Practices

1. **Never expose API keys** in frontend code
2. **Use HTTPS** for all API calls
3. **Validate inputs** before sending to API
4. **Handle tokens securely** (HttpOnly cookies preferred over localStorage)
5. **Implement CSRF protection** for state-changing operations
6. **Rate limit user actions** on the client side

## 🧪 Testing Frontend Integration

```typescript
// Example test with MSW (Mock Service Worker)
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.post('/api/v1/chat', (req, res, ctx) => {
    return res(
      ctx.json({
        response: 'Test response',
        agent: 'zumbi',
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## 📊 Real-time Updates

### WebSocket (Partial Implementation)

```typescript
// WebSocket for real-time investigation updates
const ws = new WebSocket('wss://neural-thinker-cidadao-ai-backend.hf.space/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    investigation_id: 'inv-123',
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle real-time updates
};
```

**Note**: WebSocket implementation is currently 60% complete. Use SSE for production.

## 🌐 CORS Configuration

The backend is configured with CORS for:
- **Development**: `http://localhost:3000`, `http://localhost:3001`
- **Production**: Vercel domains, HuggingFace Spaces

If you encounter CORS issues:
1. Check your origin is whitelisted in backend configuration
2. Ensure credentials mode is set correctly
3. Review [CORS_CONFIGURATION.md](../development/CORS_CONFIGURATION.md)

## 📱 Progressive Web App (PWA)

For PWA integration with offline support:
1. Cache API responses using service workers
2. Queue failed requests for retry
3. Sync data when connection restored
4. Provide offline-first UI

## 🔗 Related Documentation

- [API Complete Reference](../api/README.md)
- [API Endpoints Map](../api/API_ENDPOINTS_MAP.md)
- [Backend Development Guide](../development/README.md)
- [Architecture Overview](../architecture/README.md)

## 🐛 Common Issues

### 1. CORS Errors
**Solution**: Ensure API URL is correct and origin is whitelisted

### 2. Authentication Issues
**Solution**: Check token expiration, refresh token flow

### 3. SSE Connection Drops
**Solution**: Implement reconnection logic with exponential backoff

### 4. Rate Limiting
**Solution**: Implement client-side throttling and retry with backoff

## 💡 Tips for Next.js Integration

```typescript
// app/api/chat/route.ts (Next.js App Router)
export async function POST(request: Request) {
  const { message } = await request.json();

  // Proxy to backend with authentication
  const response = await fetch(`${BACKEND_URL}/api/v1/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getServerToken()}`,
    },
    body: JSON.stringify({ message }),
  });

  return response;
}
```

## 🎯 Integration Checklist

- [ ] Set up API client with base URL
- [ ] Implement authentication flow
- [ ] Add token refresh logic
- [ ] Create chat interface with SSE
- [ ] Handle agent selection
- [ ] Display investigation results
- [ ] Implement error handling
- [ ] Add loading states
- [ ] Test all endpoints
- [ ] Optimize performance
- [ ] Add monitoring/analytics

---

**Need help?** Check the [examples](./examples/) directory for complete working implementations!
