"""
Tests for Query Optimization Service.

Tests the streaming, timeout, caching, and parallel execution features.

Author: Anderson Henrique da Silva
Created: 2025-12-02
"""

import asyncio

import pytest

from src.services.query_optimization import (
    QueryComplexity,
    QueryContext,
    ThinkingStep,
    _generate_cache_key,
    classify_query_complexity,
    create_thinking_steps,
    execute_with_timeout,
    get_cached_result,
    get_query_stats,
    get_timeout_fallback_response,
    get_timeout_for_complexity,
    parallel_fetch,
    record_query_stats,
    set_cached_result,
    stream_thinking_process,
)


class TestQueryComplexityClassification:
    """Tests for query complexity classification."""

    def test_simple_greeting_queries(self):
        """Greetings should be classified as SIMPLE."""
        simple_queries = [
            "Olá",
            "oi, tudo bem?",
            "Bom dia!",
            "Boa tarde",
            "Boa noite",
            "ajuda",
            "help",
            "obrigado",
            "tchau",
        ]
        for query in simple_queries:
            result = classify_query_complexity(query)
            assert result == QueryComplexity.SIMPLE, f"Expected SIMPLE for '{query}'"

    def test_simple_intent_override(self):
        """Intent type should override query analysis for simple intents."""
        result = classify_query_complexity("alguma coisa qualquer", "greeting")
        assert result == QueryComplexity.SIMPLE

        result = classify_query_complexity("teste", "thanks")
        assert result == QueryComplexity.SIMPLE

    def test_investigation_queries(self):
        """Investigation queries should be classified as INVESTIGATION."""
        investigation_queries = [
            "Investigar contratos do Ministério da Saúde",
            "Busque anomalias nos gastos",
            "Detecte fraude em licitações",
            "Verifique corrupção no órgão",
            "Encontre irregularidades",
        ]
        for query in investigation_queries:
            result = classify_query_complexity(query)
            assert (
                result == QueryComplexity.INVESTIGATION
            ), f"Expected INVESTIGATION for '{query}'"

    def test_complex_queries(self):
        """Complex analysis queries should be classified as COMPLEX."""
        complex_queries = [
            "Comparar gastos de 2023 com 2024",
            "Evolução dos contratos ao longo dos anos",
            "Tendência de gastos em saúde",
            "Ranking dos maiores fornecedores",
            "Top 10 contratos mais caros",
        ]
        for query in complex_queries:
            result = classify_query_complexity(query)
            assert result == QueryComplexity.COMPLEX, f"Expected COMPLEX for '{query}'"

    def test_moderate_queries(self):
        """Regular queries should be classified as MODERATE."""
        moderate_queries = [
            "Contratos do Ministério da Educação",
            "Gastos em 2024",
            "Fornecedores de tecnologia",
        ]
        for query in moderate_queries:
            result = classify_query_complexity(query)
            assert (
                result == QueryComplexity.MODERATE
            ), f"Expected MODERATE for '{query}'"


class TestTimeoutConfiguration:
    """Tests for timeout configuration."""

    def test_timeout_by_complexity(self):
        """Each complexity level should have appropriate timeout."""
        assert get_timeout_for_complexity(QueryComplexity.SIMPLE) == 5.0
        assert get_timeout_for_complexity(QueryComplexity.MODERATE) == 15.0
        assert get_timeout_for_complexity(QueryComplexity.COMPLEX) == 30.0
        assert get_timeout_for_complexity(QueryComplexity.INVESTIGATION) == 45.0

    def test_fallback_responses_exist(self):
        """All complexity levels should have fallback responses."""
        for complexity in QueryComplexity:
            response = get_timeout_fallback_response(complexity)
            assert response is not None
            assert len(response) > 0


class TestThinkingSteps:
    """Tests for thinking step generation."""

    def test_simple_has_one_step(self):
        """Simple queries should have 1 thinking step."""
        steps = create_thinking_steps(QueryComplexity.SIMPLE, "Olá")
        assert len(steps) == 1

    def test_moderate_has_three_steps(self):
        """Moderate queries should have 3 thinking steps."""
        steps = create_thinking_steps(QueryComplexity.MODERATE, "contratos")
        assert len(steps) == 3

    def test_complex_has_five_steps(self):
        """Complex queries should have 5 thinking steps."""
        steps = create_thinking_steps(QueryComplexity.COMPLEX, "comparar gastos")
        assert len(steps) == 5

    def test_investigation_has_eight_steps(self):
        """Investigation queries should have 8 thinking steps."""
        steps = create_thinking_steps(QueryComplexity.INVESTIGATION, "investigar")
        assert len(steps) == 8

    def test_steps_have_required_fields(self):
        """All steps should have required fields."""
        steps = create_thinking_steps(QueryComplexity.MODERATE, "teste")
        for step in steps:
            assert isinstance(step, ThinkingStep)
            assert step.step_id > 0
            assert step.description
            assert step.status == "pending"


class TestCaching:
    """Tests for query result caching."""

    def test_cache_key_generation(self):
        """Cache keys should be deterministic."""
        key1 = _generate_cache_key("test query")
        key2 = _generate_cache_key("test query")
        key3 = _generate_cache_key("different query")

        assert key1 == key2
        assert key1 != key3

    def test_cache_key_case_insensitive(self):
        """Cache keys should be case-insensitive."""
        key1 = _generate_cache_key("Test Query")
        key2 = _generate_cache_key("test query")
        assert key1 == key2

    def test_cache_set_and_get(self):
        """Should be able to set and get cached results."""
        key = _generate_cache_key("cache test query")
        test_result = {"data": "test result"}

        set_cached_result(key, test_result)
        retrieved = get_cached_result(key)

        assert retrieved == test_result

    def test_cache_miss(self):
        """Should return None for cache miss."""
        key = _generate_cache_key("nonexistent query xyz123")
        result = get_cached_result(key)
        assert result is None


class TestTimeoutExecution:
    """Tests for timeout execution."""

    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """Should return result when execution completes in time."""

        async def quick_task():
            await asyncio.sleep(0.01)
            return {"success": True}

        result, timed_out = await execute_with_timeout(quick_task(), timeout=1.0)

        assert not timed_out
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_timeout_returns_fallback(self):
        """Should return fallback on timeout."""

        async def slow_task():
            await asyncio.sleep(10)
            return {"success": True}

        result, timed_out = await execute_with_timeout(
            slow_task(),
            timeout=0.1,
            fallback_result={"fallback": True},
        )

        assert timed_out
        assert result["fallback"] is True

    @pytest.mark.asyncio
    async def test_timeout_default_fallback(self):
        """Should use default fallback message when none provided."""

        async def slow_task():
            await asyncio.sleep(10)
            return {"success": True}

        result, timed_out = await execute_with_timeout(slow_task(), timeout=0.1)

        assert timed_out
        assert result["status"] == "timeout"
        assert "message" in result


class TestParallelFetch:
    """Tests for parallel fetch execution."""

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Should execute multiple fetchers in parallel."""

        async def fetcher1():
            await asyncio.sleep(0.05)
            return "result1"

        async def fetcher2():
            await asyncio.sleep(0.05)
            return "result2"

        results = await parallel_fetch(
            [("fetch1", fetcher1()), ("fetch2", fetcher2())],
            timeout=1.0,
        )

        assert "fetch1" in results
        assert "fetch2" in results
        assert results["fetch1"]["status"] == "success"
        assert results["fetch2"]["status"] == "success"
        assert results["fetch1"]["data"] == "result1"
        assert results["fetch2"]["data"] == "result2"

    @pytest.mark.asyncio
    async def test_partial_timeout(self):
        """Should handle partial timeouts gracefully."""

        async def quick_fetcher():
            await asyncio.sleep(0.01)
            return "quick"

        async def slow_fetcher():
            await asyncio.sleep(10)
            return "slow"

        results = await parallel_fetch(
            [("quick", quick_fetcher()), ("slow", slow_fetcher())],
            timeout=0.1,
        )

        assert results["quick"]["status"] == "success"
        assert results["slow"]["status"] == "timeout"


class TestStreamingThinking:
    """Tests for streaming thinking process."""

    @pytest.mark.asyncio
    async def test_streaming_yields_steps(self):
        """Should yield thinking step updates."""
        context = QueryContext(
            query="test query",
            complexity=QueryComplexity.MODERATE,
            thinking_steps=create_thinking_steps(QueryComplexity.MODERATE, "test"),
        )

        steps_received = []
        async for step in stream_thinking_process(context):
            steps_received.append(step)

        # Should receive 2 updates per step (in_progress, completed)
        assert len(steps_received) == 6  # 3 steps * 2 updates

    @pytest.mark.asyncio
    async def test_streaming_step_structure(self):
        """Streamed steps should have correct structure."""
        context = QueryContext(
            query="test",
            complexity=QueryComplexity.SIMPLE,
            thinking_steps=create_thinking_steps(QueryComplexity.SIMPLE, "test"),
        )

        async for step in stream_thinking_process(context):
            assert "type" in step
            assert step["type"] == "thinking"
            assert "step" in step
            assert "total_steps" in step
            assert "description" in step
            assert "status" in step


class TestQueryStats:
    """Tests for query statistics."""

    def test_record_and_get_stats(self):
        """Should record and retrieve query statistics."""
        initial_stats = get_query_stats()
        initial_total = initial_stats["total_queries"]

        record_query_stats(QueryComplexity.MODERATE)
        record_query_stats(QueryComplexity.COMPLEX, cache_hit=True)
        record_query_stats(QueryComplexity.SIMPLE, timed_out=True)

        stats = get_query_stats()
        assert stats["total_queries"] == initial_total + 3


class TestQueryContext:
    """Tests for QueryContext dataclass."""

    def test_context_creation(self):
        """Should create context with defaults."""
        context = QueryContext(
            query="test query",
            complexity=QueryComplexity.MODERATE,
        )

        assert context.query == "test query"
        assert context.complexity == QueryComplexity.MODERATE
        assert context.timeout_seconds == 30.0
        assert context.thinking_steps == []
        assert context.start_time > 0

    def test_context_with_custom_values(self):
        """Should create context with custom values."""
        steps = [ThinkingStep(1, "Step 1")]
        context = QueryContext(
            query="test",
            complexity=QueryComplexity.COMPLEX,
            timeout_seconds=60.0,
            thinking_steps=steps,
            cache_key="custom_key",
        )

        assert context.timeout_seconds == 60.0
        assert len(context.thinking_steps) == 1
        assert context.cache_key == "custom_key"
