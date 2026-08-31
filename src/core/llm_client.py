"""
LLM Client wrapper.

Thin async client that the query planner (IntentClassifier) and the semantic
router (Ayrton Senna) use for their LLM fallback paths. It wraps the production
MaritacaClient (primary) with an Anthropic fallback, selecting credentials from
settings / environment so behaviour matches the deployed Maritaca -> Anthropic
chain.
"""

from __future__ import annotations

import os

from src.core import get_logger
from src.core.config import settings
from src.services.maritaca_client import MaritacaClient, MaritacaModel

logger = get_logger(__name__)


def _resolve_key(secret_attr: str, env_name: str) -> str | None:
    """Read a key from settings (SecretStr) falling back to the environment."""
    value = getattr(settings, secret_attr, None)
    if value is not None:
        # pydantic SecretStr exposes get_secret_value(); plain str passes through
        getter = getattr(value, "get_secret_value", None)
        return getter() if callable(getter) else str(value)
    return os.getenv(env_name)


class LLMClient:
    """Async LLM client with Maritaca primary and Anthropic fallback."""

    def __init__(self) -> None:
        self._maritaca_key = _resolve_key("maritaca_api_key", "MARITACA_API_KEY")
        self._anthropic_key = _resolve_key("anthropic_api_key", "ANTHROPIC_API_KEY")
        self._maritaca: MaritacaClient | None = None
        self.logger = logger

    def _get_maritaca(self) -> MaritacaClient | None:
        if not self._maritaca_key:
            return None
        if self._maritaca is None:
            model = getattr(settings, "maritaca_model", MaritacaModel.SABIA_3_1)
            self._maritaca = MaritacaClient(api_key=self._maritaca_key, model=model)
        return self._maritaca

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ) -> str:
        """Generate text, trying Maritaca first, then Anthropic.

        Returns the generated text. Raises RuntimeError only if no provider is
        configured or all configured providers fail.
        """
        messages = [{"role": "user", "content": prompt}]

        # --- Primary: Maritaca (Brazilian Portuguese) ---
        client = self._get_maritaca()
        if client is not None:
            try:
                resp = await client.chat_completion(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False,
                )
                return resp.content
            except Exception as e:  # noqa: BLE001 - fall through to Anthropic
                self.logger.warning(
                    "llm_client_maritaca_failed", error=str(e), falling_back=True
                )

        # --- Fallback: Anthropic ---
        if self._anthropic_key:
            try:
                return await self._anthropic_generate(
                    prompt, temperature=temperature, max_tokens=max_tokens
                )
            except Exception as e:  # noqa: BLE001
                self.logger.error("llm_client_anthropic_failed", error=str(e))
                raise RuntimeError(f"All LLM providers failed: {e}") from e

        raise RuntimeError(
            "No LLM provider configured (set MARITACA_API_KEY or ANTHROPIC_API_KEY)"
        )

    async def _anthropic_generate(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> str:
        """Call Anthropic via the official async SDK."""
        from anthropic import AsyncAnthropic

        model = getattr(
            settings, "anthropic_model", "claude-sonnet-4-20250514"
        )
        client = AsyncAnthropic(api_key=self._anthropic_key)
        try:
            msg = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            # messages API returns a list of content blocks
            parts = [b.text for b in msg.content if getattr(b, "type", None) == "text"]
            return "".join(parts)
        finally:
            close = getattr(client, "close", None)
            if callable(close):
                await close()

    async def close(self) -> None:
        if self._maritaca is not None:
            await self._maritaca.close()


__all__ = ["LLMClient"]
