"""
LLM Client wrapper for backward compatibility.

This module provides a simple wrapper around LLMConnectionPool
for backward compatibility with code expecting LLMClient.
"""

from src.core.llm_pool import LLMConnectionPool


class LLMClient:
    """
    LLM Client wrapper for backward compatibility.

    Provides a simple interface wrapping LLMConnectionPool.
    """

    def __init__(self):
        self.pool = LLMConnectionPool()

    async def generate(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000, **kwargs
    ) -> str:
        """
        Generate text using LLM.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments

        Returns:
            Generated text
        """
        # Use the pool's client to make the request
        # This is a simplified implementation - adjust based on actual llm_pool implementation
        async with self.pool.get_client() as client:
            # Placeholder implementation - adjust based on actual API
            # This would need to be implemented based on your LLM provider
            response = await client.post(
                "/v1/completions",
                json={
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    **kwargs,
                },
            )
            return response.json().get("text", "")

    async def close(self):
        """Close the connection pool."""
        await self.pool.close()


__all__ = ["LLMClient"]
