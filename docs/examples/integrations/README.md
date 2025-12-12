# Integration Examples

This directory contains practical examples for integrating with the Cidadao.AI API.

## Quick Start

### Chat with Agents (SSE Streaming)

```python
import httpx

async def chat_with_agent():
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "https://cidadao-api-production.up.railway.app/api/v1/chat/stream",
            json={"message": "Investigue contratos do Ministério da Educação"}
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    print(line[5:])
```

### JavaScript (Browser)

```javascript
const eventSource = new EventSource(
  'https://cidadao-api-production.up.railway.app/api/v1/chat/stream'
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Agent response:', data);
};
```

## Available Integrations

| Integration | Description | Docs |
|-------------|-------------|------|
| Chat API | Real-time agent conversations | [Chat Docs](../../api/CHAT_API_DOCUMENTATION.md) |
| Transparency APIs | 30+ government data sources | [API Catalog](../../api/01-INDEX-catalog.md) |
| Streaming | SSE and WebSocket support | [Streaming](../../api/03-STREAMING-sse-websocket.md) |

## See Also

- [Frontend Integration Guide](../../FRONTEND_INTEGRATION_GUIDE.md)
- [API Usage Guide](../../api/02-README-usage-guide.md)
