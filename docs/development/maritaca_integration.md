# Maritaca AI Integration Guide

## Overview

This guide covers the integration of Maritaca AI's Sabiá-3 language model with the Cidadão.AI backend, specifically for use with the Drummond agent for conversational AI and natural language generation in Brazilian Portuguese.

## Features

The `MaritacaClient` provides:

- **Async/await support** for all operations
- **Streaming responses** for real-time text generation
- **Automatic retry** with exponential backoff
- **Rate limit handling** with smart retries
- **Circuit breaker pattern** for resilience
- **Comprehensive error handling** and logging
- **Type hints** for better development experience
- **Context manager support** for proper resource cleanup

## Configuration

### Environment Variables

Add the following to your `.env` file:

```env
# Maritaca AI Configuration
MARITACA_API_KEY=your-api-key-here
MARITACA_API_BASE_URL=https://chat.maritaca.ai/api
MARITACA_MODEL=sabia-3
```

### Available Models

- `sabia-3` - Standard Sabiá-3 model
- `sabia-3-medium` - Medium-sized variant
- `sabia-3-large` - Large variant for complex tasks

## Usage Examples

### Basic Chat Completion

```python
from src.services.maritaca_client import create_maritaca_client

async def example():
    async with create_maritaca_client(api_key="your-key") as client:
        response = await client.chat_completion(
            messages=[
                {"role": "user", "content": "Olá, como você está?"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        print(response.content)
```

### Streaming Response

```python
async def streaming_example():
    async with create_maritaca_client(api_key="your-key") as client:
        async for chunk in await client.chat_completion(
            messages=[{"role": "user", "content": "Conte uma história"}],
            stream=True
        ):
            print(chunk, end="", flush=True)
```

### Integration with LLM Manager

```python
from src.llm.providers import LLMManager, LLMProvider, LLMRequest

# Configure with Maritaca as primary provider
manager = LLMManager(
    primary_provider=LLMProvider.MARITACA,
    fallback_providers=[LLMProvider.GROQ, LLMProvider.TOGETHER]
)

request = LLMRequest(
    messages=[{"role": "user", "content": "Analyze government spending"}],
    temperature=0.7,
    max_tokens=500
)

response = await manager.complete(request)
```

### Drummond Agent Integration

The Drummond agent can now use Maritaca AI for natural language generation:

```python
from src.agents.drummond import CommunicationAgent, AgentContext

context = AgentContext(
    user_id="user123",
    session_id="session456",
    metadata={
        "llm_provider": "maritaca",
        "llm_model": "sabia-3"
    }
)

drummond = CommunicationAgent()
# Agent will automatically use Maritaca for NLG tasks
```

## API Reference

### MaritacaClient

#### Constructor Parameters

- `api_key` (str): Your Maritaca AI API key
- `base_url` (str): API base URL (default: "https://chat.maritaca.ai/api")
- `model` (str): Default model to use (default: "sabia-3")
- `timeout` (int): Request timeout in seconds (default: 60)
- `max_retries` (int): Maximum retry attempts (default: 3)
- `circuit_breaker_threshold` (int): Failures before circuit opens (default: 5)
- `circuit_breaker_timeout` (int): Circuit reset time in seconds (default: 60)

#### Methods

##### `chat_completion()`

Create a chat completion with Maritaca AI.

**Parameters:**
- `messages`: List of conversation messages
- `model`: Optional model override
- `temperature`: Sampling temperature (0.0-2.0)
- `max_tokens`: Maximum tokens to generate
- `top_p`: Top-p sampling parameter
- `frequency_penalty`: Frequency penalty (-2.0 to 2.0)
- `presence_penalty`: Presence penalty (-2.0 to 2.0)
- `stop`: List of stop sequences
- `stream`: Enable streaming response

**Returns:**
- `MaritacaResponse` for non-streaming
- `AsyncGenerator[str, None]` for streaming

##### `health_check()`

Check Maritaca AI service health.

**Returns:**
- Dictionary with status information

## Error Handling

The client handles various error scenarios:

```python
from src.core.exceptions import LLMError, LLMRateLimitError

try:
    response = await client.chat_completion(messages)
except LLMRateLimitError as e:
    # Handle rate limiting
    retry_after = e.details.get("retry_after", 60)
    await asyncio.sleep(retry_after)
except LLMError as e:
    # Handle other API errors
    logger.error(f"Maritaca error: {e}")
```

## Circuit Breaker

The circuit breaker protects against cascading failures:

1. **Closed State**: Normal operation
2. **Open State**: After threshold failures, requests fail immediately
3. **Reset**: After timeout, circuit closes and requests resume

## Performance Considerations

- **Connection Pooling**: Client maintains up to 20 connections
- **Keep-alive**: Connections stay alive for 30 seconds
- **Streaming**: Use for long responses to improve perceived latency
- **Retry Strategy**: Exponential backoff prevents overwhelming the API

## Testing

Run the test suite:

```bash
# Unit tests
pytest tests/unit/test_maritaca_client.py -v

# Integration example
python examples/maritaca_drummond_integration.py
```

## Best Practices

1. **Always use context managers** to ensure proper cleanup
2. **Set appropriate timeouts** based on expected response times
3. **Use streaming** for long-form content generation
4. **Monitor circuit breaker status** in production
5. **Implement proper error handling** for all API calls
6. **Cache responses** when appropriate to reduce API calls

## Troubleshooting

### Common Issues

1. **Circuit Breaker Open**
   - Check API status
   - Review recent error logs
   - Wait for circuit reset timeout

2. **Rate Limiting**
   - Implement request queuing
   - Use retry-after header
   - Consider upgrading API plan

3. **Timeout Errors**
   - Increase timeout for complex requests
   - Use streaming for long responses
   - Check network connectivity

### Debug Logging

Enable debug logs:

```python
import logging
logging.getLogger("src.services.maritaca_client").setLevel(logging.DEBUG)
```

## Security Notes

- **Never commit API keys** to version control
- **Use environment variables** for sensitive data
- **Rotate keys regularly** in production
- **Monitor API usage** for anomalies

## Support

For Maritaca AI specific issues:
- Documentation: https://docs.maritaca.ai
- Support: suporte@maritaca.ai

For Cidadão.AI integration issues:
- Create an issue in the project repository
- Check the logs for detailed error information