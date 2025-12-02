"""
Query Optimization Service for Complex Queries

This module provides:
1. Streaming thought process for complex queries
2. Parallel API calls with asyncio.gather
3. Graceful timeout with fallback responses
4. Query result caching

Author: Anderson Henrique da Silva
Created: 2025-12-02
"""

import asyncio
import hashlib
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from src.core import get_logger

logger = get_logger(__name__)


class QueryComplexity(Enum):
    """Query complexity levels."""

    SIMPLE = "simple"  # Greetings, help - instant response
    MODERATE = "moderate"  # Single data source query
    COMPLEX = "complex"  # Multiple data sources, analysis required
    INVESTIGATION = "investigation"  # Full investigation with multiple agents


@dataclass
class ThinkingStep:
    """Represents a step in the agent's thinking process."""

    step_id: int
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: Any = None
    error: str | None = None


@dataclass
class QueryContext:
    """Context for query execution."""

    query: str
    complexity: QueryComplexity
    timeout_seconds: float = 30.0
    thinking_steps: list[ThinkingStep] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    cache_key: str | None = None


# In-memory cache for query results (simple implementation)
# In production, use Redis or similar
_query_cache: dict[str, tuple[Any, float]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


def _generate_cache_key(query: str, context: dict | None = None) -> str:
    """Generate a cache key for a query."""
    key_data = query.lower().strip()
    if context:
        key_data += str(sorted(context.items()))
    return hashlib.md5(key_data.encode()).hexdigest()  # noqa: S324


# Maximum cache entries before cleanup
MAX_CACHE_ENTRIES = 1000


def get_cached_result(cache_key: str) -> dict | list | str | None:  # noqa: ANN401
    """Get a cached result if it exists and is not expired."""
    if cache_key in _query_cache:
        result, timestamp = _query_cache[cache_key]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            logger.info(f"Cache hit for key: {cache_key[:8]}...")
            return result
        # Expired, remove from cache
        del _query_cache[cache_key]
    return None


def set_cached_result(
    cache_key: str, result: dict | list | str
) -> None:  # noqa: ANN401
    """Cache a query result."""
    _query_cache[cache_key] = (result, time.time())
    logger.info(f"Cached result for key: {cache_key[:8]}...")

    # Simple cache cleanup - remove oldest if too many entries
    if len(_query_cache) > MAX_CACHE_ENTRIES:
        oldest_key = min(_query_cache.keys(), key=lambda k: _query_cache[k][1])
        del _query_cache[oldest_key]


def classify_query_complexity(  # noqa: PLR0911
    query: str, intent_type: str | None = None
) -> QueryComplexity:
    """
    Classify the complexity of a query.

    Args:
        query: The user's query
        intent_type: Detected intent type

    Returns:
        QueryComplexity level
    """
    query_lower = query.lower()

    # Simple queries - instant response
    simple_indicators = [
        "olá",
        "oi",
        "bom dia",
        "boa tarde",
        "boa noite",
        "ajuda",
        "help",
        "obrigado",
        "tchau",
    ]
    simple_intents = ["greeting", "thanks", "goodbye", "help"]

    if (
        any(ind in query_lower for ind in simple_indicators)
        or intent_type in simple_intents
    ):
        return QueryComplexity.SIMPLE

    # Investigation queries - complex
    investigation_indicators = [
        "investigar",
        "investigue",
        "investigação",
        "anomalia",
        "fraude",
        "corrupção",
        "irregularidade",
        "desvio",
    ]
    investigation_intents = ["investigate", "fraud_detection", "corruption_indicators"]

    if (
        any(ind in query_lower for ind in investigation_indicators)
        or intent_type in investigation_intents
    ):
        return QueryComplexity.INVESTIGATION

    # Complex queries - multiple data sources
    complex_indicators = [
        "comparar",
        "comparação",
        "evolução",
        "tendência",
        "análise completa",
        "todos os",
        "ranking",
        "top 10",
        "maiores",
        "menores",
    ]
    complex_intents = ["analyze", "statistical", "report"]

    if (
        any(ind in query_lower for ind in complex_indicators)
        or intent_type in complex_intents
    ):
        return QueryComplexity.COMPLEX

    # Default to moderate
    return QueryComplexity.MODERATE


def get_timeout_for_complexity(complexity: QueryComplexity) -> float:
    """Get appropriate timeout based on query complexity."""
    timeouts = {
        QueryComplexity.SIMPLE: 5.0,
        QueryComplexity.MODERATE: 15.0,
        QueryComplexity.COMPLEX: 30.0,
        QueryComplexity.INVESTIGATION: 45.0,
    }
    return timeouts.get(complexity, 15.0)


def create_thinking_steps(
    complexity: QueryComplexity, query: str
) -> list[ThinkingStep]:
    """Create thinking steps based on query complexity."""
    if complexity == QueryComplexity.SIMPLE:
        return [
            ThinkingStep(1, "Processando sua mensagem"),
        ]

    if complexity == QueryComplexity.MODERATE:
        return [
            ThinkingStep(1, "Analisando sua solicitação"),
            ThinkingStep(2, "Buscando dados relevantes"),
            ThinkingStep(3, "Preparando resposta"),
        ]

    if complexity == QueryComplexity.COMPLEX:
        return [
            ThinkingStep(1, "Analisando sua solicitação"),
            ThinkingStep(2, "Identificando fontes de dados necessárias"),
            ThinkingStep(3, "Consultando múltiplas bases de dados"),
            ThinkingStep(4, "Processando e correlacionando dados"),
            ThinkingStep(5, "Gerando análise consolidada"),
        ]

    # Investigation
    return [
        ThinkingStep(1, "Recebendo solicitação de investigação"),
        ThinkingStep(2, "Identificando entidades e órgãos relevantes"),
        ThinkingStep(3, "Consultando Portal da Transparência"),
        ThinkingStep(4, "Buscando contratos relacionados"),
        ThinkingStep(5, "Analisando padrões e anomalias"),
        ThinkingStep(6, "Verificando indicadores de irregularidade"),
        ThinkingStep(7, "Consolidando descobertas"),
        ThinkingStep(8, "Preparando relatório da investigação"),
    ]


async def stream_thinking_process(
    context: QueryContext,
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Stream the thinking process for a query.

    Yields:
        Dict with thinking step updates
    """
    for step in context.thinking_steps:
        step.status = "in_progress"
        step.started_at = datetime.now(UTC)

        yield {
            "type": "thinking",
            "step": step.step_id,
            "total_steps": len(context.thinking_steps),
            "description": step.description,
            "status": "in_progress",
        }

        # Simulate processing time based on complexity
        if context.complexity == QueryComplexity.SIMPLE:
            await asyncio.sleep(0.05)
        elif context.complexity == QueryComplexity.MODERATE:
            await asyncio.sleep(0.2)
        elif context.complexity == QueryComplexity.COMPLEX:
            await asyncio.sleep(0.3)
        else:  # Investigation
            await asyncio.sleep(0.4)

        step.status = "completed"
        step.completed_at = datetime.now(UTC)

        yield {
            "type": "thinking",
            "step": step.step_id,
            "total_steps": len(context.thinking_steps),
            "description": step.description,
            "status": "completed",
        }


async def execute_with_timeout(
    coro: Any,  # noqa: ANN401
    timeout: float,
    fallback_result: Any = None,  # noqa: ANN401
    fallback_message: str = "A operação demorou mais que o esperado. Tente uma consulta mais específica.",
) -> tuple[Any, bool]:  # noqa: ANN401
    """
    Execute a coroutine with timeout and graceful fallback.

    Args:
        coro: Coroutine to execute
        timeout: Timeout in seconds
        fallback_result: Result to return on timeout
        fallback_message: Message to include in fallback

    Returns:
        Tuple of (result, timed_out)
    """
    try:
        result = await asyncio.wait_for(coro, timeout=timeout)
        return result, False
    except asyncio.TimeoutError:
        logger.warning(f"Query timed out after {timeout}s")
        if fallback_result is None:
            fallback_result = {
                "status": "timeout",
                "message": fallback_message,
                "partial_results": True,
            }
        return fallback_result, True
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        return {
            "status": "error",
            "message": f"Erro ao processar consulta: {str(e)}",
        }, True


async def parallel_fetch(
    fetchers: list[tuple[str, Any]],
    timeout: float = 10.0,
) -> dict[str, Any]:
    """
    Execute multiple fetch operations in parallel.

    Args:
        fetchers: List of (name, coroutine) tuples
        timeout: Timeout for each operation

    Returns:
        Dict mapping names to results
    """
    results = {}

    async def fetch_with_name(name: str, coro: Any) -> tuple[str, Any]:  # noqa: ANN401
        try:
            result = await asyncio.wait_for(coro, timeout=timeout)
            return name, {"status": "success", "data": result}
        except asyncio.TimeoutError:
            return name, {"status": "timeout", "data": None}
        except Exception as e:
            return name, {"status": "error", "error": str(e), "data": None}

    tasks = [fetch_with_name(name, coro) for name, coro in fetchers]
    completed = await asyncio.gather(*tasks, return_exceptions=True)

    for item in completed:
        if isinstance(item, tuple):
            name, result = item
            results[name] = result
        elif isinstance(item, Exception):
            logger.error(f"Parallel fetch exception: {item}")

    return results


# Fallback responses for timeout scenarios
TIMEOUT_FALLBACK_RESPONSES = {
    QueryComplexity.SIMPLE: "Desculpe, houve uma demora inesperada. Como posso ajudá-lo?",
    QueryComplexity.MODERATE: (
        "A consulta está demorando mais que o esperado. "
        "Você pode tentar uma busca mais específica, por exemplo: "
        "'contratos do Ministério da Saúde em 2024'."
    ),
    QueryComplexity.COMPLEX: (
        "A análise complexa está demorando. "
        "Enquanto isso, posso ajudar com consultas mais específicas. "
        "Tente focar em um órgão ou período específico."
    ),
    QueryComplexity.INVESTIGATION: (
        "A investigação completa pode demorar alguns minutos. "
        "Você pode acompanhar o progresso ou fazer perguntas mais específicas "
        "enquanto o sistema processa os dados."
    ),
}


def get_timeout_fallback_response(complexity: QueryComplexity) -> str:
    """Get appropriate fallback response for timeout based on complexity."""
    return TIMEOUT_FALLBACK_RESPONSES.get(
        complexity,
        "A operação demorou mais que o esperado. Por favor, tente novamente.",
    )


# Statistics for monitoring
_query_stats = {
    "total_queries": 0,
    "cache_hits": 0,
    "timeouts": 0,
    "by_complexity": {c.value: 0 for c in QueryComplexity},
}


def record_query_stats(
    complexity: QueryComplexity,
    cache_hit: bool = False,
    timed_out: bool = False,
) -> None:
    """Record query statistics for monitoring."""
    _query_stats["total_queries"] += 1
    _query_stats["by_complexity"][complexity.value] += 1
    if cache_hit:
        _query_stats["cache_hits"] += 1
    if timed_out:
        _query_stats["timeouts"] += 1


def get_query_stats() -> dict[str, Any]:
    """Get query statistics."""
    return _query_stats.copy()
