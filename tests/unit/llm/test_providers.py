"""
Unit tests for src/llm/providers.py.

The behaviour that matters here is the failure path: what happens when the
primary provider is down, when every provider is down, and when no API key is
configured. A silent degradation in this chain is invisible in production and
shows up only as bad answers, so each test asserts which providers were
actually contacted, not just the returned value.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from pydantic import ValidationError

from src.core.exceptions import LLMError, LLMRateLimitError
from src.llm import providers as providers_mod
from src.llm.providers import (
    GroqProvider,
    HuggingFaceProvider,
    LLMManager,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    MaritacaProvider,
    TogetherProvider,
    create_llm_manager,
)


def make_response(provider: str, content: str = "resposta") -> LLMResponse:
    return LLMResponse(
        content=content,
        provider=provider,
        model=f"{provider}-model",
        usage={"total_tokens": 42},
        metadata={},
        response_time=0.1,
        timestamp=datetime.now(UTC),
    )


class RecordingProvider:
    """A provider double that records every interaction and can really fail."""

    def __init__(self, name: str, error: Exception | None = None, chunks=None):
        self.name = name
        self.error = error
        self.chunks = chunks if chunks is not None else [f"{name}-chunk"]
        self.complete_calls = 0
        self.stream_calls = 0
        self.enter_calls = 0
        self.exit_calls = 0
        self.close_calls = 0

    async def __aenter__(self):
        self.enter_calls += 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exit_calls += 1
        return False

    async def complete(self, request):
        self.complete_calls += 1
        if self.error:
            raise self.error
        return make_response(self.name)

    async def stream_complete(self, request):
        self.stream_calls += 1
        if self.error:
            raise self.error
        for chunk in self.chunks:
            yield chunk

    async def close(self):
        self.close_calls += 1


def build_manager(primary, providers, fallbacks=None, enable_fallback=True):
    """Create an LLMManager without instantiating the real HTTP providers."""
    with (
        patch.object(providers_mod, "GroqProvider"),
        patch.object(providers_mod, "TogetherProvider"),
        patch.object(providers_mod, "HuggingFaceProvider"),
        patch.object(providers_mod, "MaritacaProvider"),
    ):
        manager = LLMManager(
            primary_provider=primary,
            fallback_providers=fallbacks,
            enable_fallback=enable_fallback,
        )
    manager.providers = providers
    return manager


@pytest.fixture
def request_obj():
    return LLMRequest(messages=[{"role": "user", "content": "quem gastou mais?"}])


@pytest.fixture
def no_sleep():
    """Retry backoff must not actually sleep during unit tests."""
    with patch.object(providers_mod.asyncio, "sleep", new=AsyncMock()) as slept:
        yield slept


# ---------------------------------------------------------------------------
# LLMManager — the fallback chain
# ---------------------------------------------------------------------------


class TestLLMManagerCompletionFallback:
    async def test_primary_success_never_touches_the_fallbacks(self, request_obj):
        primary = RecordingProvider("groq")
        fallback = RecordingProvider("maritaca")
        manager = build_manager(
            LLMProvider.GROQ,
            {LLMProvider.GROQ: primary, LLMProvider.MARITACA: fallback},
            fallbacks=[LLMProvider.MARITACA],
        )

        response = await manager.complete(request_obj)

        assert response.provider == "groq"
        assert primary.complete_calls == 1
        assert fallback.complete_calls == 0

    async def test_primary_failure_is_served_by_the_next_provider(self, request_obj):
        primary = RecordingProvider("groq", error=LLMError("groq is down"))
        fallback = RecordingProvider("maritaca")
        manager = build_manager(
            LLMProvider.GROQ,
            {LLMProvider.GROQ: primary, LLMProvider.MARITACA: fallback},
            fallbacks=[LLMProvider.MARITACA],
        )

        response = await manager.complete(request_obj)

        assert response.provider == "maritaca"
        assert primary.complete_calls == 1, "the primary must have been tried first"
        assert fallback.complete_calls == 1

    async def test_maritaca_primary_still_falls_back_with_the_default_chain(
        self, request_obj
    ):
        # This is the documented production configuration: Maritaca is primary
        # and also appears in the default fallback list. The chain must not
        # collapse into "primary only" because of that overlap.
        maritaca = RecordingProvider("maritaca", error=LLMError("503 from maritaca"))
        together = RecordingProvider("together")
        huggingface = RecordingProvider("huggingface")
        manager = build_manager(
            LLMProvider.MARITACA,
            {
                LLMProvider.MARITACA: maritaca,
                LLMProvider.TOGETHER: together,
                LLMProvider.HUGGINGFACE: huggingface,
            },
            fallbacks=None,  # defaults to [TOGETHER, HUGGINGFACE, MARITACA]
        )

        response = await manager.complete(request_obj)

        assert response.provider == "together"
        assert maritaca.complete_calls == 1
        assert together.complete_calls == 1

    async def test_a_provider_is_never_retried_twice_in_one_chain(self, request_obj):
        maritaca = RecordingProvider("maritaca", error=LLMError("down"))
        together = RecordingProvider("together", error=LLMError("down"))
        huggingface = RecordingProvider("huggingface", error=LLMError("down"))
        manager = build_manager(
            LLMProvider.MARITACA,
            {
                LLMProvider.MARITACA: maritaca,
                LLMProvider.TOGETHER: together,
                LLMProvider.HUGGINGFACE: huggingface,
            },
            fallbacks=None,
        )

        with pytest.raises(LLMError):
            await manager.complete(request_obj)

        assert maritaca.complete_calls == 1, "duplicated provider must not be re-tried"

    async def test_fallback_order_is_respected(self, request_obj):
        first = RecordingProvider("together", error=LLMError("down"))
        second = RecordingProvider("huggingface")
        primary = RecordingProvider("groq", error=LLMError("down"))
        manager = build_manager(
            LLMProvider.GROQ,
            {
                LLMProvider.GROQ: primary,
                LLMProvider.TOGETHER: first,
                LLMProvider.HUGGINGFACE: second,
            },
            fallbacks=[LLMProvider.TOGETHER, LLMProvider.HUGGINGFACE],
        )

        response = await manager.complete(request_obj)

        assert response.provider == "huggingface"
        assert first.complete_calls == 1

    async def test_all_providers_down_raises_instead_of_returning_empty(
        self, request_obj
    ):
        primary = RecordingProvider("groq", error=LLMError("groq down"))
        fallback = RecordingProvider(
            "maritaca", error=LLMRateLimitError("maritaca quota exhausted")
        )
        manager = build_manager(
            LLMProvider.GROQ,
            {LLMProvider.GROQ: primary, LLMProvider.MARITACA: fallback},
            fallbacks=[LLMProvider.MARITACA],
        )

        with pytest.raises(LLMError) as exc_info:
            await manager.complete(request_obj)

        assert "All LLM providers failed" in str(exc_info.value)
        assert "maritaca quota exhausted" in str(
            exc_info.value
        ), "the last error must survive so the outage is diagnosable"
        assert exc_info.value.details == {"provider": "all"}
        assert fallback.complete_calls == 1

    async def test_fallback_disabled_means_the_backup_is_never_contacted(
        self, request_obj
    ):
        primary = RecordingProvider("groq", error=LLMError("groq down"))
        fallback = RecordingProvider("maritaca")
        manager = build_manager(
            LLMProvider.GROQ,
            {LLMProvider.GROQ: primary, LLMProvider.MARITACA: fallback},
            fallbacks=[LLMProvider.MARITACA],
            enable_fallback=False,
        )

        with pytest.raises(LLMError):
            await manager.complete(request_obj)

        assert fallback.complete_calls == 0
        assert fallback.enter_calls == 0

    async def test_context_manager_is_exited_even_when_the_provider_fails(
        self, request_obj
    ):
        primary = RecordingProvider("groq", error=LLMError("boom"))
        fallback = RecordingProvider("maritaca")
        manager = build_manager(
            LLMProvider.GROQ,
            {LLMProvider.GROQ: primary, LLMProvider.MARITACA: fallback},
            fallbacks=[LLMProvider.MARITACA],
        )

        await manager.complete(request_obj)

        assert primary.enter_calls == 1
        assert primary.exit_calls == 1, "a failed provider must still be closed"

    async def test_a_crashing_provider_is_treated_as_a_failure_not_propagated(
        self, request_obj
    ):
        # A bug inside a provider (not an LLMError) must not escape as-is;
        # the manager is expected to move on to the next provider.
        primary = RecordingProvider("groq", error=RuntimeError("bad json"))
        fallback = RecordingProvider("maritaca")
        manager = build_manager(
            LLMProvider.GROQ,
            {LLMProvider.GROQ: primary, LLMProvider.MARITACA: fallback},
            fallbacks=[LLMProvider.MARITACA],
        )

        response = await manager.complete(request_obj)

        assert response.provider == "maritaca"


class TestLLMManagerStreamingFallback:
    async def test_stream_uses_the_primary_when_it_works(self, request_obj):
        primary = RecordingProvider("groq", chunks=["a", "b"])
        fallback = RecordingProvider("maritaca")
        manager = build_manager(
            LLMProvider.GROQ,
            {LLMProvider.GROQ: primary, LLMProvider.MARITACA: fallback},
            fallbacks=[LLMProvider.MARITACA],
        )

        chunks = [c async for c in manager.stream_complete(request_obj)]

        assert chunks == ["a", "b"]
        assert fallback.stream_calls == 0

    async def test_stream_falls_back_when_the_primary_fails(self, request_obj):
        primary = RecordingProvider("groq", error=LLMError("stream down"))
        fallback = RecordingProvider("maritaca", chunks=["oi", " mundo"])
        manager = build_manager(
            LLMProvider.GROQ,
            {LLMProvider.GROQ: primary, LLMProvider.MARITACA: fallback},
            fallbacks=[LLMProvider.MARITACA],
        )

        chunks = [c async for c in manager.stream_complete(request_obj)]

        assert chunks == ["oi", " mundo"]
        assert primary.stream_calls == 1

    async def test_stream_with_all_providers_down_raises(self, request_obj):
        primary = RecordingProvider("groq", error=LLMError("down"))
        fallback = RecordingProvider("maritaca", error=LLMError("also down"))
        manager = build_manager(
            LLMProvider.GROQ,
            {LLMProvider.GROQ: primary, LLMProvider.MARITACA: fallback},
            fallbacks=[LLMProvider.MARITACA],
        )

        with pytest.raises(LLMError) as exc_info:
            [c async for c in manager.stream_complete(request_obj)]

        assert "All LLM providers failed for streaming" in str(exc_info.value)
        assert "also down" in str(exc_info.value)

    async def test_stream_with_fallback_disabled_does_not_contact_the_backup(
        self, request_obj
    ):
        primary = RecordingProvider("groq", error=LLMError("down"))
        fallback = RecordingProvider("maritaca")
        manager = build_manager(
            LLMProvider.GROQ,
            {LLMProvider.GROQ: primary, LLMProvider.MARITACA: fallback},
            fallbacks=[LLMProvider.MARITACA],
            enable_fallback=False,
        )

        with pytest.raises(LLMError):
            [c async for c in manager.stream_complete(request_obj)]

        assert fallback.stream_calls == 0


class TestLLMManagerLifecycle:
    async def test_close_closes_every_provider(self):
        providers = {
            LLMProvider.GROQ: RecordingProvider("groq"),
            LLMProvider.MARITACA: RecordingProvider("maritaca"),
        }
        manager = build_manager(LLMProvider.GROQ, providers)

        await manager.close()

        assert all(p.close_calls == 1 for p in providers.values())


class TestCreateLLMManager:
    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("maritaca", LLMProvider.MARITACA),
            ("MARITACA", LLMProvider.MARITACA),
            ("groq", LLMProvider.GROQ),
            ("Together", LLMProvider.TOGETHER),
        ],
    )
    def test_provider_name_is_resolved_case_insensitively(self, name, expected):
        with (
            patch.object(providers_mod, "GroqProvider"),
            patch.object(providers_mod, "TogetherProvider"),
            patch.object(providers_mod, "HuggingFaceProvider"),
            patch.object(providers_mod, "MaritacaProvider"),
        ):
            manager = create_llm_manager(primary_provider=name)

        assert manager.primary_provider is expected

    def test_unknown_provider_name_fails_loudly(self):
        with pytest.raises(ValueError):
            create_llm_manager(primary_provider="does-not-exist")

    def test_anthropic_is_not_a_provider_in_this_module(self):
        # The architecture doc describes Anthropic as the Maritaca fallback,
        # but this module only knows groq/together/huggingface/maritaca.
        # If Anthropic is ever added here, this test should be updated.
        with pytest.raises(ValueError):
            create_llm_manager(primary_provider="anthropic")


# ---------------------------------------------------------------------------
# BaseLLMProvider — HTTP error handling and retries
# ---------------------------------------------------------------------------


def http_response(status_code: int, payload=None, headers=None) -> httpx.Response:
    return httpx.Response(
        status_code,
        json=payload if payload is not None else {"detail": "err"},
        headers=headers or {},
        request=httpx.Request("POST", "https://example.test/chat/completions"),
    )


@pytest.fixture
def groq_without_pool():
    provider = GroqProvider(api_key="gsk-unit-test")
    provider._use_pool = False
    return provider


class TestNonStreamRequest:
    async def test_successful_response_is_parsed_and_not_retried(
        self, groq_without_pool, no_sleep
    ):
        client = AsyncMock()
        client.post = AsyncMock(return_value=http_response(200, {"ok": True}))
        groq_without_pool.client = client

        result = await groq_without_pool._non_stream_request("/chat/completions", {})

        assert result == {"ok": True}
        assert client.post.await_count == 1
        no_sleep.assert_not_awaited()

    async def test_persistent_server_error_raises_after_exhausting_retries(
        self, groq_without_pool, no_sleep
    ):
        client = AsyncMock()
        client.post = AsyncMock(return_value=http_response(500, {"error": "boom"}))
        groq_without_pool.client = client

        with pytest.raises(LLMError) as exc_info:
            await groq_without_pool._non_stream_request("/chat/completions", {})

        assert "500" in str(exc_info.value)
        assert client.post.await_count == groq_without_pool.max_retries + 1

    async def test_transient_server_error_is_retried_and_then_succeeds(
        self, groq_without_pool, no_sleep
    ):
        client = AsyncMock()
        client.post = AsyncMock(
            side_effect=[
                http_response(500, {"error": "boom"}),
                http_response(200, {"ok": True}),
            ]
        )
        groq_without_pool.client = client

        result = await groq_without_pool._non_stream_request("/chat/completions", {})

        assert result == {"ok": True}
        assert client.post.await_count == 2

    async def test_rate_limit_raises_a_dedicated_error_with_retry_after(
        self, groq_without_pool, no_sleep
    ):
        client = AsyncMock()
        client.post = AsyncMock(
            return_value=http_response(
                429, {"error": "slow down"}, {"Retry-After": "7"}
            )
        )
        groq_without_pool.client = client

        with pytest.raises(LLMRateLimitError) as exc_info:
            await groq_without_pool._non_stream_request("/chat/completions", {})

        assert exc_info.value.details["retry_after"] == 7
        assert (
            no_sleep.await_args_list[0].args[0] == 7
        ), "the server-provided Retry-After must drive the backoff"

    async def test_rate_limit_followed_by_success_is_transparent(
        self, groq_without_pool, no_sleep
    ):
        client = AsyncMock()
        client.post = AsyncMock(
            side_effect=[
                http_response(429, {"error": "slow down"}, {"Retry-After": "1"}),
                http_response(200, {"ok": True}),
            ]
        )
        groq_without_pool.client = client

        assert await groq_without_pool._non_stream_request("/x", {}) == {"ok": True}

    async def test_timeout_is_retried_then_reported_as_llm_error(
        self, groq_without_pool, no_sleep
    ):
        client = AsyncMock()
        client.post = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
        groq_without_pool.client = client

        with pytest.raises(LLMError) as exc_info:
            await groq_without_pool._non_stream_request("/chat/completions", {})

        assert "timeout" in str(exc_info.value).lower()
        assert client.post.await_count == groq_without_pool.max_retries + 1

    async def test_timeout_then_success_recovers(self, groq_without_pool, no_sleep):
        client = AsyncMock()
        client.post = AsyncMock(
            side_effect=[
                httpx.TimeoutException("timed out"),
                http_response(200, {"ok": True}),
            ]
        )
        groq_without_pool.client = client

        assert await groq_without_pool._non_stream_request("/x", {}) == {"ok": True}

    async def test_connection_error_is_wrapped_in_llm_error(
        self, groq_without_pool, no_sleep
    ):
        client = AsyncMock()
        client.post = AsyncMock(side_effect=httpx.ConnectError("dns failure"))
        groq_without_pool.client = client

        with pytest.raises(LLMError) as exc_info:
            await groq_without_pool._non_stream_request("/x", {})

        assert "dns failure" in str(exc_info.value)
        assert exc_info.value.details["provider"] == "GroqProvider"

    async def test_auth_header_carries_the_configured_key(self, groq_without_pool):
        headers = groq_without_pool._get_headers()

        assert headers["Authorization"] == "Bearer gsk-unit-test"
        assert headers["Content-Type"] == "application/json"


class TestConnectionPoolPath:
    async def test_pool_is_used_when_available(self, no_sleep):
        provider = GroqProvider(api_key="gsk-unit-test")
        client = AsyncMock()
        provider.client = client
        pool = MagicMock()
        pool.post = AsyncMock(return_value={"from": "pool"})

        with patch.object(providers_mod, "get_llm_pool", AsyncMock(return_value=pool)):
            result = await provider._non_stream_request("/chat/completions", {"a": 1})

        assert result == {"from": "pool"}
        pool.post.assert_awaited_once_with("groq", "/chat/completions", {"a": 1})
        client.post.assert_not_awaited()

    async def test_pool_failure_degrades_to_the_direct_client(self, no_sleep):
        provider = GroqProvider(api_key="gsk-unit-test")
        client = AsyncMock()
        client.post = AsyncMock(return_value=http_response(200, {"from": "direct"}))
        provider.client = client

        with patch.object(
            providers_mod,
            "get_llm_pool",
            AsyncMock(side_effect=RuntimeError("pool exhausted")),
        ):
            result = await provider._non_stream_request("/chat/completions", {})

        assert result == {"from": "direct"}
        assert client.post.await_count == 1


class FakeStreamResponse:
    """Minimal stand-in for an httpx streaming response."""

    def __init__(self, status_code: int, lines=(), payload=None, headers=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.text = "upstream error"
        self._lines = list(lines)
        self._payload = payload

    async def aiter_lines(self):
        for line in self._lines:
            yield line

    def json(self):
        if self._payload is None:
            raise ValueError("no json body")
        return self._payload


class FakeStreamingClient:
    """Client whose .stream() replays scripted responses or raises."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0

    def stream(self, method, url, **kwargs):
        self.calls += 1
        item = self.script[min(self.calls - 1, len(self.script) - 1)]
        if isinstance(item, Exception):
            raise item

        class _Ctx:
            async def __aenter__(_self):
                return item

            async def __aexit__(_self, *exc):
                return False

        return _Ctx()


class TestStreamRequest:
    async def test_sse_chunks_are_parsed_and_done_terminates_the_stream(
        self, groq_without_pool, no_sleep
    ):
        groq_without_pool.client = FakeStreamingClient(
            [
                FakeStreamResponse(
                    200,
                    lines=[
                        'data: {"choices": [{"delta": {"content": "Oi"}}]}',
                        "",
                        "data: {not valid json",
                        'data: {"choices": [{"delta": {"content": " Brasil"}}]}',
                        "data: [DONE]",
                        'data: {"choices": [{"delta": {"content": "nunca"}}]}',
                    ],
                )
            ]
        )

        chunks = [c async for c in groq_without_pool._stream_request("/x", {})]

        assert [c["choices"][0]["delta"]["content"] for c in chunks] == [
            "Oi",
            " Brasil",
        ]

    async def test_streaming_rate_limit_keeps_its_type(
        self, groq_without_pool, no_sleep
    ):
        groq_without_pool.client = FakeStreamingClient(
            [FakeStreamResponse(429, headers={"Retry-After": "3"})]
        )

        with pytest.raises(LLMRateLimitError):
            [c async for c in groq_without_pool._stream_request("/x", {})]

    async def test_streaming_upstream_error_raises_after_retries(
        self, groq_without_pool, no_sleep
    ):
        client = FakeStreamingClient([FakeStreamResponse(502)])
        groq_without_pool.client = client

        with pytest.raises(LLMError) as exc_info:
            [c async for c in groq_without_pool._stream_request("/x", {})]

        assert "502" in str(exc_info.value)
        assert client.calls == groq_without_pool.max_retries + 1

    async def test_streaming_timeout_raises_a_dedicated_message(
        self, groq_without_pool, no_sleep
    ):
        groq_without_pool.client = FakeStreamingClient(
            [httpx.TimeoutException("timed out")]
        )

        with pytest.raises(LLMError) as exc_info:
            [c async for c in groq_without_pool._stream_request("/x", {})]

        assert "Stream request timeout" in str(exc_info.value)

    async def test_streaming_recovers_after_a_transient_failure(
        self, groq_without_pool, no_sleep
    ):
        groq_without_pool.client = FakeStreamingClient(
            [
                httpx.TimeoutException("timed out"),
                FakeStreamResponse(
                    200, lines=['data: {"choices": [{"delta": {"content": "ok"}}]}']
                ),
            ]
        )

        chunks = [c async for c in groq_without_pool._stream_request("/x", {})]

        assert len(chunks) == 1


class TestProviderLifecycle:
    async def test_close_releases_the_http_client(self):
        provider = GroqProvider(api_key="k")
        client = AsyncMock()
        provider.client = client

        await provider.close()

        client.aclose.assert_awaited_once()

    async def test_close_is_safe_when_no_client_was_created(self):
        provider = GroqProvider(api_key="k")
        provider.client = None

        await provider.close()  # must not raise

    async def test_context_manager_builds_a_client_when_the_pool_is_disabled(self):
        provider = GroqProvider(api_key="k")
        provider._use_pool = False

        async with provider as entered:
            assert entered is provider
            assert provider.client is not None

        assert provider.client.is_closed


# ---------------------------------------------------------------------------
# Provider payload shaping
# ---------------------------------------------------------------------------


class TestGroqProvider:
    def test_system_prompt_is_prepended_to_the_conversation(self):
        provider = GroqProvider(api_key="k")
        request = LLMRequest(
            messages=[{"role": "user", "content": "oi"}],
            system_prompt="voce e um auditor",
            temperature=0.1,
            max_tokens=128,
        )

        data = provider._prepare_request_data(request)

        assert data["messages"][0] == {
            "role": "system",
            "content": "voce e um auditor",
        }
        assert data["messages"][1] == {"role": "user", "content": "oi"}
        assert data["temperature"] == 0.1
        assert data["max_tokens"] == 128
        assert data["model"] == provider.default_model

    def test_explicit_model_overrides_the_default(self):
        provider = GroqProvider(api_key="k")
        request = LLMRequest(messages=[], model="llama-3.1-70b")

        assert provider._prepare_request_data(request)["model"] == "llama-3.1-70b"

    def test_response_is_mapped_to_the_common_shape(self):
        provider = GroqProvider(api_key="k")
        payload = {
            "id": "resp-1",
            "model": "mixtral",
            "choices": [
                {"message": {"content": "achei 3 anomalias"}, "finish_reason": "stop"}
            ],
            "usage": {"total_tokens": 99},
        }

        response = provider._parse_response(payload, response_time=1.5)

        assert response.content == "achei 3 anomalias"
        assert response.provider == "groq"
        assert response.model == "mixtral"
        assert response.usage == {"total_tokens": 99}
        assert response.metadata["finish_reason"] == "stop"
        assert response.metadata["response_id"] == "resp-1"
        assert response.response_time == 1.5

    async def test_complete_goes_through_the_http_layer(self, request_obj):
        provider = GroqProvider(api_key="k")
        payload = {
            "model": "mixtral",
            "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
            "usage": {},
        }
        provider._make_request = AsyncMock(return_value=payload)

        response = await provider.complete(request_obj)

        assert response.content == "ok"
        assert provider._make_request.await_args.args[0] == "/chat/completions"

    async def test_stream_yields_only_content_deltas(self, request_obj):
        provider = GroqProvider(api_key="k")

        async def fake_stream(endpoint, data, stream=False):
            assert data["stream"] is True
            for chunk in [
                {"choices": [{"delta": {"role": "assistant"}}]},
                {"choices": [{"delta": {"content": "Oi"}}]},
                {"choices": []},
                {"choices": [{"delta": {"content": " Brasil"}}]},
            ]:
                yield chunk

        provider._make_request = fake_stream

        chunks = [c async for c in provider.stream_complete(request_obj)]

        assert chunks == ["Oi", " Brasil"]


class TestTogetherProvider:
    def test_response_is_tagged_with_the_right_provider(self):
        provider = TogetherProvider(api_key="k")
        payload = {
            "model": "llama-2",
            "choices": [{"message": {"content": "x"}, "finish_reason": "length"}],
            "usage": {"total_tokens": 5},
        }

        response = provider._parse_response(payload, response_time=0.2)

        assert response.provider == "together"
        assert response.metadata["finish_reason"] == "length"

    def test_system_prompt_is_prepended(self):
        provider = TogetherProvider(api_key="k")
        request = LLMRequest(
            messages=[{"role": "user", "content": "oi"}], system_prompt="seja formal"
        )

        data = provider._prepare_request_data(request)

        assert data["messages"][0]["role"] == "system"
        assert data["model"] == provider.default_model

    async def test_complete_posts_to_the_chat_endpoint(self, request_obj):
        provider = TogetherProvider(api_key="k")
        provider._make_request = AsyncMock(
            return_value={
                "model": "llama-2",
                "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
                "usage": {},
            }
        )

        response = await provider.complete(request_obj)

        assert response.provider == "together"
        assert provider._make_request.await_args.args[0] == "/chat/completions"

    async def test_stream_yields_content_deltas(self, request_obj):
        provider = TogetherProvider(api_key="k")

        async def fake_stream(endpoint, data, stream=False):
            yield {"choices": [{"delta": {"content": "a"}}]}
            yield {"choices": [{"delta": {}}]}
            yield {"choices": [{"delta": {"content": "b"}}]}

        provider._make_request = fake_stream

        assert [c async for c in provider.stream_complete(request_obj)] == ["a", "b"]

    def test_together_does_not_use_the_shared_pool(self):
        # Only Groq declares a pool name; the others must not silently try to
        # route through a pool entry that does not exist.
        assert not hasattr(TogetherProvider(api_key="k"), "_provider_name")


class TestHuggingFaceProvider:
    def test_conversation_is_flattened_into_a_single_prompt(self):
        provider = HuggingFaceProvider(api_key="k")
        request = LLMRequest(
            messages=[
                {"role": "user", "content": "oi"},
                {"role": "assistant", "content": "ola"},
            ],
            system_prompt="seja breve",
            max_tokens=64,
        )

        data = provider._prepare_request_data(request)

        assert data["inputs"] == (
            "System: seja breve\n\nUser: oi\nAssistant: ola\nAssistant: "
        )
        assert data["parameters"]["max_new_tokens"] == 64
        assert data["parameters"]["return_full_text"] is False

    def test_list_shaped_response_is_understood(self):
        provider = HuggingFaceProvider(api_key="k")

        response = provider._parse_response(
            [{"generated_text": "resposta"}], response_time=0.3, model="mistral"
        )

        assert response.content == "resposta"
        assert response.provider == "huggingface"
        assert response.model == "mistral"

    def test_dict_shaped_response_is_understood(self):
        provider = HuggingFaceProvider(api_key="k")

        response = provider._parse_response(
            {"generated_text": "resposta"}, response_time=0.3, model="mistral"
        )

        assert response.content == "resposta"

    async def test_complete_targets_the_model_specific_endpoint(self):
        provider = HuggingFaceProvider(api_key="k")
        provider._make_request = AsyncMock(return_value=[{"generated_text": "ok"}])
        request = LLMRequest(messages=[], model="meta-llama/Llama-3-8B")

        response = await provider.complete(request)

        assert provider._make_request.await_args.args[0] == (
            "/models/meta-llama/Llama-3-8B"
        )
        assert response.model == "meta-llama/Llama-3-8B"
        assert response.content == "ok"

    def test_headers_carry_the_bearer_token(self):
        headers = HuggingFaceProvider(api_key="hf-key")._get_headers()

        assert headers["Authorization"] == "Bearer hf-key"

    async def test_streaming_degrades_to_a_single_chunk(self, request_obj):
        provider = HuggingFaceProvider(api_key="k")
        provider.complete = AsyncMock(return_value=make_response("huggingface", "tudo"))

        chunks = [c async for c in provider.stream_complete(request_obj)]

        assert chunks == ["tudo"]


# ---------------------------------------------------------------------------
# MaritacaProvider — key handling and error propagation
# ---------------------------------------------------------------------------


class TestMaritacaProviderKeys:
    def test_explicit_key_wins_over_settings(self):
        with patch.object(providers_mod, "MaritacaClient") as client_cls:
            provider = MaritacaProvider(api_key="explicit-key")

        assert provider.api_key == "explicit-key"
        assert client_cls.call_args.kwargs["api_key"] == "explicit-key"

    def test_configured_key_is_read_from_settings(self):
        secret = MagicMock()
        secret.get_secret_value.return_value = "settings-key"

        with (
            patch.object(providers_mod, "MaritacaClient"),
            patch.object(providers_mod.settings, "maritaca_api_key", secret),
        ):
            provider = MaritacaProvider()

        assert provider.api_key == "settings-key"

    def test_missing_key_falls_back_to_a_dummy_key_and_warns(self):
        # Documented behaviour: the provider does NOT refuse to start without a
        # key, it builds a client with a placeholder that will 401 at call
        # time. The warning is the only signal, so it must be emitted.
        with (
            patch.object(providers_mod, "MaritacaClient"),
            patch.object(providers_mod.settings, "maritaca_api_key", None),
            patch.object(providers_mod, "get_logger") as get_logger,
        ):
            logger = MagicMock()
            get_logger.return_value = logger
            provider = MaritacaProvider()

        assert provider.api_key == "sk-test-dummy-key"
        logger.warning.assert_called_once()
        assert "MARITACA_API_KEY" in logger.warning.call_args.args[0]

    def test_client_is_configured_for_fast_failure(self):
        with patch.object(providers_mod, "MaritacaClient") as client_cls:
            MaritacaProvider(api_key="k")

        kwargs = client_cls.call_args.kwargs
        assert kwargs["timeout"] == 30
        assert kwargs["max_retries"] == 2


class TestMaritacaProviderCompletion:
    def _provider(self, chat_completion):
        with patch.object(providers_mod, "MaritacaClient") as client_cls:
            client_cls.return_value.chat_completion = chat_completion
            return MaritacaProvider(api_key="k")

    async def test_client_response_is_mapped_to_the_common_shape(self, request_obj):
        client_response = MagicMock(
            content="tres contratos suspeitos",
            model="sabia-4",
            usage={"total_tokens": 120},
            metadata={"finish_reason": "stop"},
            response_time=0.9,
            timestamp=datetime.now(UTC),
        )
        provider = self._provider(AsyncMock(return_value=client_response))

        response = await provider.complete(request_obj)

        assert response.content == "tres contratos suspeitos"
        assert response.provider == "maritaca"
        assert response.model == "sabia-4"
        assert response.usage == {"total_tokens": 120}

    async def test_system_prompt_is_sent_first(self):
        provider = self._provider(
            AsyncMock(
                return_value=MagicMock(
                    content="x",
                    model="sabia-4",
                    usage={},
                    metadata={},
                    response_time=0.1,
                    timestamp=datetime.now(UTC),
                )
            )
        )
        request = LLMRequest(
            messages=[{"role": "user", "content": "oi"}],
            system_prompt="voce e o Zumbi",
        )

        await provider.complete(request)

        messages = provider.maritaca_client.chat_completion.await_args.kwargs[
            "messages"
        ]
        assert messages[0]["role"] == "system"
        assert messages[1]["content"] == "oi"

    async def test_client_failure_is_not_swallowed(self, request_obj):
        provider = self._provider(AsyncMock(side_effect=LLMError("maritaca 500")))

        with pytest.raises(LLMError, match="maritaca 500"):
            await provider.complete(request_obj)

    async def test_rate_limit_from_the_client_keeps_its_type(self, request_obj):
        provider = self._provider(
            AsyncMock(side_effect=LLMRateLimitError("too many requests"))
        )

        with pytest.raises(LLMRateLimitError):
            await provider.complete(request_obj)

    async def test_streaming_degrades_to_a_single_chunk(self, request_obj):
        provider = self._provider(AsyncMock())
        provider.complete = AsyncMock(return_value=make_response("maritaca", "texto"))

        chunks = [c async for c in provider.stream_complete(request_obj)]

        assert chunks == ["texto"]


# ---------------------------------------------------------------------------
# LLMRequest validation
# ---------------------------------------------------------------------------


class TestLLMRequestValidation:
    @pytest.mark.parametrize(
        "kwargs",
        [
            {"temperature": 2.5},
            {"temperature": -0.1},
            {"max_tokens": 0},
            {"max_tokens": 40000},
            {"top_p": 1.5},
        ],
    )
    def test_out_of_range_parameters_are_rejected(self, kwargs):
        with pytest.raises(ValidationError):
            LLMRequest(messages=[{"role": "user", "content": "oi"}], **kwargs)

    def test_defaults_are_conservative(self):
        request = LLMRequest(messages=[{"role": "user", "content": "oi"}])

        assert request.temperature == 0.7
        assert request.max_tokens == 2048
        assert request.stream is False
        assert request.model is None
