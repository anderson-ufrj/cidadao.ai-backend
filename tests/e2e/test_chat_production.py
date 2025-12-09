#!/usr/bin/env python3
"""
Cidadão.AI Production Chat Test Suite

Comprehensive test suite for validating the chat streaming endpoint
in production environment with 100 scenarios covering:
- Identity & About System
- Greetings
- Help Requests
- Contract Investigations
- Anomaly Detection
- Specific Queries
- Agent-Specific Interactions
- Complex Queries
- Edge Cases
- Follow-up Simulation

Author: Anderson Henrique da Silva
Date: 2025-12-01

Usage:
    # Run all tests
    python tests/e2e/test_chat_production.py

    # Run with custom URL
    PROD_URL=https://your-api.com python tests/e2e/test_chat_production.py

    # Run specific category
    python tests/e2e/test_chat_production.py --category investigate
"""

import argparse
import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

# Production URL (can be overridden via environment variable or --url flag)
DEFAULT_URL = "https://cidadao-api-production.up.railway.app"


def get_base_url() -> str:
    """Get the base URL for API calls."""
    return os.environ.get("PROD_URL", DEFAULT_URL)


# =============================================================================
# TEST SCENARIOS (100 total)
# =============================================================================

TEST_SCENARIOS = [
    # === IDENTITY & ABOUT (10) ===
    ("identity", "Quem criou o Cidadão.AI?"),
    ("identity", "Quem desenvolveu esse sistema?"),
    ("identity", "Quem é o autor do projeto?"),
    ("identity", "O que é o Cidadão.AI?"),
    ("identity", "Para que serve essa plataforma?"),
    ("identity", "Qual é a história do Cidadão.AI?"),
    ("identity", "Quem idealizou o projeto?"),
    ("identity", "Esse sistema foi feito por qual empresa?"),
    ("identity", "A Maritaca AI criou o Cidadão.AI?"),
    ("identity", "Conte sobre o TCC do Cidadão.AI"),
    # === GREETINGS (10) ===
    ("greeting", "Olá"),
    ("greeting", "Oi, tudo bem?"),
    ("greeting", "Bom dia!"),
    ("greeting", "Boa tarde, como posso usar o sistema?"),
    ("greeting", "E aí!"),
    ("greeting", "Opa, beleza?"),
    ("greeting", "Olá, sou novo aqui"),
    ("greeting", "Oi, preciso de ajuda"),
    ("greeting", "Hey"),
    ("greeting", "Olá Cidadão.AI"),
    # === HELP REQUESTS (10) ===
    ("help", "Como funciona?"),
    ("help", "O que você pode fazer?"),
    ("help", "Me ajuda a entender o sistema"),
    ("help", "Quais são suas funcionalidades?"),
    ("help", "Como posso investigar contratos?"),
    ("help", "Me explica como usar"),
    ("help", "Preciso de ajuda"),
    ("help", "Não sei o que fazer"),
    ("help", "Quais comandos posso usar?"),
    ("help", "Tutorial básico"),
    # === CONTRACT INVESTIGATIONS (15) ===
    ("investigate", "Quero investigar contratos do Ministério da Saúde"),
    ("investigate", "Busque contratos da educação em 2024"),
    ("investigate", "Contratos do Ministério da Defesa"),
    ("investigate", "Investigar gastos da Fazenda"),
    ("investigate", "Contratos de tecnologia do governo"),
    ("investigate", "Quero ver contratos de limpeza"),
    ("investigate", "Contratos acima de 1 milhão"),
    ("investigate", "Buscar contratos de 2023"),
    ("investigate", "Contratos do Ministério do Meio Ambiente"),
    ("investigate", "Investigar licitações de saúde"),
    ("investigate", "Contratos de alimentação escolar"),
    ("investigate", "Gastos com medicamentos"),
    ("investigate", "Contratos de obras públicas"),
    ("investigate", "Investigar terceirizados"),
    ("investigate", "Contratos de consultoria"),
    # === ANOMALY DETECTION (10) ===
    ("anomaly", "Detecte anomalias nos contratos da saúde"),
    ("anomaly", "Há fraudes nos gastos de educação?"),
    ("anomaly", "Busque irregularidades em licitações"),
    ("anomaly", "Contratos suspeitos do governo"),
    ("anomaly", "Encontre sobrepreço em contratos"),
    ("anomaly", "Anomalias em pagamentos"),
    ("anomaly", "Contratos com valores atípicos"),
    ("anomaly", "Detectar corrupção"),
    ("anomaly", "Fornecedores com muitos contratos"),
    ("anomaly", "Contratos sem licitação"),
    # === SPECIFIC QUERIES (10) ===
    ("specific", "Qual o maior contrato de 2024?"),
    ("specific", "Quantos contratos a saúde tem?"),
    ("specific", "Valor total de contratos da educação"),
    ("specific", "Fornecedor com mais contratos"),
    ("specific", "Média de valor dos contratos"),
    ("specific", "Contratos vencendo este mês"),
    ("specific", "Último contrato assinado"),
    ("specific", "Contratos por modalidade"),
    ("specific", "Quais órgãos você monitora?"),
    ("specific", "Dados do IBGE sobre população"),
    # === AGENT-SPECIFIC (10) ===
    ("agent", "Fale com o Zumbi"),
    ("agent", "Quero conversar com Anita"),
    ("agent", "O que o Tiradentes faz?"),
    ("agent", "Chame o Drummond"),
    ("agent", "Quais agentes existem?"),
    ("agent", "Me apresente os agentes"),
    ("agent", "O Machado pode analisar um documento?"),
    ("agent", "Oxóssi pode buscar dados?"),
    ("agent", "Fale como poeta"),
    ("agent", "Use o agente de segurança"),
    # === COMPLEX QUERIES (10) ===
    ("complex", "Compare gastos de saúde e educação"),
    ("complex", "Evolução de contratos nos últimos 3 anos"),
    ("complex", "Análise regional de gastos no Nordeste"),
    ("complex", "Correlação entre eleições e contratos"),
    ("complex", "Principais fornecedores do governo federal"),
    ("complex", "Tendência de gastos públicos"),
    ("complex", "Ranking de órgãos por volume de contratos"),
    ("complex", "Sazonalidade nos gastos"),
    ("complex", "Impacto da pandemia nos contratos"),
    ("complex", "Previsão de gastos para 2025"),
    # === EDGE CASES (10) ===
    ("edge", ""),  # Empty message
    ("edge", "a"),  # Single char
    ("edge", "🇧🇷 contratos"),  # With emoji
    ("edge", "CONTRATOS DA SAÚDE"),  # All caps
    ("edge", "contratossaudelicitacao"),  # No spaces
    ("edge", "   espaços   extras   "),  # Extra spaces
    ("edge", "SELECT * FROM contratos"),  # SQL injection attempt
    ("edge", "<script>alert('xss')</script>"),  # XSS attempt
    ("edge", "a" * 500),  # Long message
    ("edge", "私は契約を調査したい"),  # Japanese
    # === FOLLOW-UP SIMULATION (5) ===
    ("followup", "Me conte mais sobre isso"),
    ("followup", "Pode detalhar?"),
    ("followup", "E o que mais?"),
    ("followup", "Continue"),
    ("followup", "Próximo"),
]


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class ChatChatTestResult:
    """Result of a single test case (renamed to avoid pytest collection)."""

    category: str
    message: str
    success: bool
    response_time: float
    status_code: int
    intent_detected: str = ""
    agent_used: str = ""
    has_data: bool = False
    error: str = ""
    response_preview: str = ""


# =============================================================================
# TEST EXECUTION
# =============================================================================


def _parse_sse_event(data: dict[str, Any]) -> tuple[str, str, bool, str]:
    """Parse a single SSE event and extract intent, agent, has_data, and text."""
    intent = ""
    agent = ""
    has_data = False
    text = ""

    event_type = data.get("type", "")

    if event_type == "intent":
        intent_data = data.get("intent", {})
        if isinstance(intent_data, dict):
            intent = intent_data.get("type", "unknown")
        elif isinstance(intent_data, str):
            intent = intent_data
    elif event_type == "agent_selected":
        agent = data.get("agent_id", "") or data.get("agent", "")
    elif event_type == "found":
        has_data = True
    elif event_type == "chunk":
        text = data.get("content", "") or ""
    elif event_type == "complete":
        text = data.get("message", "")

    return intent, agent, has_data, text


def _parse_sse_response(content: str) -> tuple[str, str, bool, str]:
    """Parse full SSE response and extract aggregated data."""
    intent = ""
    agent = ""
    has_data = False
    response_text = ""

    for line in content.split("\n"):
        if not line.startswith("data: "):
            continue
        try:
            data = json.loads(line[6:])
            if not isinstance(data, dict):
                continue
            ev_intent, ev_agent, ev_has_data, ev_text = _parse_sse_event(data)
            if ev_intent:
                intent = ev_intent
            if ev_agent:
                agent = ev_agent
            if ev_has_data:
                has_data = True
            if ev_text:
                response_text += ev_text
        except json.JSONDecodeError:
            pass

    return intent, agent, has_data, response_text


async def test_single_message(
    client: httpx.AsyncClient, category: str, message: str, session_id: str
) -> ChatTestResult:
    """
    Test a single message against the streaming endpoint.

    Args:
        client: HTTP client instance
        category: Test category (for reporting)
        message: The message to send
        session_id: Session ID for the conversation

    Returns:
        ChatTestResult with success/failure info and metrics
    """
    start = time.time()

    # Handle empty message
    if not message or not message.strip():
        return ChatTestResult(
            category=category,
            message=message or "(empty)",
            success=False,
            response_time=0,
            status_code=0,
            error="Empty message - skipped",
        )

    try:
        response = await client.post(
            f"{get_base_url()}/api/v1/chat/stream",
            json={"message": message, "session_id": session_id},
            timeout=45.0,
        )
        elapsed = time.time() - start

        if response.status_code != 200:
            return ChatTestResult(
                category=category,
                message=message[:50],
                success=False,
                response_time=elapsed,
                status_code=response.status_code,
                error=f"HTTP {response.status_code}",
            )

        intent, agent, has_data, response_text = _parse_sse_response(response.text)

        return ChatTestResult(
            category=category,
            message=message[:50],
            success=True,
            response_time=elapsed,
            status_code=200,
            intent_detected=intent,
            agent_used=agent,
            has_data=has_data,
            response_preview=response_text[:100] if response_text else "",
        )

    except httpx.TimeoutException:
        return ChatTestResult(
            category=category,
            message=message[:50],
            success=False,
            response_time=time.time() - start,
            status_code=0,
            error="Timeout",
        )
    except Exception as e:
        return ChatTestResult(
            category=category,
            message=message[:50],
            success=False,
            response_time=time.time() - start,
            status_code=0,
            error=str(e)[:50],
        )


async def run_all_tests(
    category_filter: str | None = None,
) -> list[ChatTestResult]:
    """
    Run all test scenarios against production.

    Args:
        category_filter: Optional filter to run only specific category

    Returns:
        List of ChatTestResult objects
    """
    print("=" * 70)
    print("🧪 CIDADÃO.AI PRODUCTION TEST SUITE")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: {get_base_url()}")

    # Filter scenarios if category specified
    scenarios = TEST_SCENARIOS
    if category_filter:
        scenarios = [(c, m) for c, m in TEST_SCENARIOS if c == category_filter]

    print(f"📊 Total scenarios: {len(scenarios)}")
    print("=" * 70)

    results = []
    session_id = f"test-suite-{int(time.time())}"

    async with httpx.AsyncClient() as client:
        # Test in batches to avoid overwhelming the server
        batch_size = 5
        for i in range(0, len(scenarios), batch_size):
            batch = scenarios[i : i + batch_size]

            tasks = [
                test_single_message(client, cat, msg, f"{session_id}-{i + j}")
                for j, (cat, msg) in enumerate(batch)
            ]

            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            # Progress
            done = min(i + batch_size, len(scenarios))
            pct = 100 * done // len(scenarios)
            print(
                f"\r⏳ Progress: {done}/{len(scenarios)} ({pct}%)", end="", flush=True
            )

            # Small delay between batches
            await asyncio.sleep(0.5)

    print("\n")
    return results


# =============================================================================
# ANALYSIS AND REPORTING
# =============================================================================


def _compute_basic_stats(results: list[ChatTestResult]) -> dict[str, Any]:
    """Compute basic statistics from results."""
    total = len(results)
    successful = sum(1 for r in results if r.success)
    successful_times = [r.response_time for r in results if r.success]
    return {
        "total": total,
        "successful": successful,
        "failed": total - successful,
        "success_rate": 100 * successful // total if total > 0 else 0,
        "avg_time": sum(successful_times) / max(len(successful_times), 1),
        "max_time": max(successful_times, default=0),
        "min_time": min(successful_times, default=0),
    }


def _compute_category_stats(results: list[ChatTestResult]) -> dict[str, dict[str, Any]]:
    """Compute per-category statistics."""
    categories: dict[str, dict[str, Any]] = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = {"total": 0, "success": 0, "times": []}
        categories[r.category]["total"] += 1
        if r.success:
            categories[r.category]["success"] += 1
            categories[r.category]["times"].append(r.response_time)
    return categories


def _compute_intent_stats(results: list[ChatTestResult]) -> dict[str, int]:
    """Compute intent detection statistics."""
    intents: dict[str, int] = {}
    for r in results:
        if r.intent_detected:
            intents[r.intent_detected] = intents.get(r.intent_detected, 0) + 1
    return intents


def _compute_agent_stats(results: list[ChatTestResult]) -> dict[str, int]:
    """Compute agent usage statistics."""
    agents: dict[str, int] = {}
    for r in results:
        if r.agent_used:
            agents[r.agent_used] = agents.get(r.agent_used, 0) + 1
    return agents


def _print_summary(
    stats: dict[str, Any], categories: dict[str, dict[str, Any]]
) -> None:
    """Print results summary section."""
    print("=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)
    print(
        f"\n✅ Success Rate: {stats['successful']}/{stats['total']} ({stats['success_rate']}%)"
    )
    print(f"❌ Failures: {stats['failed']}")
    print("\n⏱️  Response Times:")
    print(f"   Average: {stats['avg_time']:.2f}s")
    print(f"   Min: {stats['min_time']:.2f}s")
    print(f"   Max: {stats['max_time']:.2f}s")

    print("\n📁 BY CATEGORY:")
    print("-" * 50)
    for cat, data in sorted(categories.items()):
        rate = 100 * data["success"] // data["total"] if data["total"] > 0 else 0
        cat_avg = sum(data["times"]) / len(data["times"]) if data["times"] else 0
        status = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "❌"
        print(
            f"   {status} {cat:12} {data['success']:2}/{data['total']:2} ({rate:3}%) avg:{cat_avg:.2f}s"
        )


def _print_intents_and_agents(intents: dict[str, int], agents: dict[str, int]) -> None:
    """Print intent detection and agent usage sections."""
    print("\n🎯 INTENT DETECTION:")
    print("-" * 50)
    for intent, count in sorted(intents.items(), key=lambda x: -x[1]):
        print(f"   {intent:20} {count:3} times")

    print("\n🤖 AGENT USAGE:")
    print("-" * 50)
    for agent, count in sorted(agents.items(), key=lambda x: -x[1]):
        print(f"   {agent:20} {count:3} times")


def _print_analysis(
    stats: dict[str, Any],
    categories: dict[str, dict[str, Any]],
    intents: dict[str, int],
    results: list[ChatTestResult],
) -> None:
    """Print SWOT-style analysis section."""
    print("\n" + "=" * 70)
    print("💡 ANALYSIS")
    print("=" * 70)

    # Strengths
    print("\n🌟 STRENGTHS:")
    strong_cats = [c for c, d in categories.items() if d["success"] == d["total"]]
    if strong_cats:
        print(f"   • 100% success in: {', '.join(strong_cats)}")
    if stats["avg_time"] < 3:
        print(f"   • Fast average response time ({stats['avg_time']:.2f}s)")
    if stats["successful"] / stats["total"] >= 0.9:
        print(f"   • High overall success rate ({stats['success_rate']}%)")

    # Weaknesses
    print("\n⚠️  WEAKNESSES:")
    weak_cats = [
        c
        for c, d in categories.items()
        if d["total"] > 0 and d["success"] / d["total"] < 0.7
    ]
    if weak_cats:
        print(f"   • Low success in: {', '.join(weak_cats)}")
    if stats["max_time"] > 10:
        print(f"   • Some slow responses (max: {stats['max_time']:.2f}s)")
    if "unknown" in intents and intents["unknown"] > stats["total"] * 0.2:
        print(f"   • High unknown intent rate ({intents.get('unknown', 0)} times)")

    # Opportunities
    print("\n🚀 OPPORTUNITIES:")
    if intents.get("unknown", 0) > 5:
        print("   • Improve intent classification for edge cases")
    if not any(r.has_data for r in results if r.category == "investigate"):
        print("   • Add more real data integration")
    slow_cats = [
        c
        for c, d in categories.items()
        if d["times"] and sum(d["times"]) / len(d["times"]) > 5
    ]
    if slow_cats:
        print(f"   • Optimize response time for: {', '.join(slow_cats)}")


def analyze_results(results: list[ChatTestResult]) -> dict[str, Any]:
    """
    Analyze test results and generate comprehensive report.

    Args:
        results: List of ChatTestResult objects

    Returns:
        Dictionary with analysis statistics
    """
    stats = _compute_basic_stats(results)
    categories = _compute_category_stats(results)
    intents = _compute_intent_stats(results)
    agents = _compute_agent_stats(results)
    errors = [r for r in results if not r.success]

    # Print report sections
    _print_summary(stats, categories)
    _print_intents_and_agents(intents, agents)

    if errors:
        print(f"\n❌ FAILURES ({len(errors)}):")
        print("-" * 50)
        for e in errors[:10]:
            print(f"   [{e.category}] {e.message[:30]}... → {e.error}")

    _print_analysis(stats, categories, intents, results)

    return {
        **stats,
        "categories": categories,
        "intents": intents,
        "agents": agents,
        "errors": [
            {"category": e.category, "message": e.message, "error": e.error}
            for e in errors
        ],
    }


def save_report(stats: dict[str, Any], filename: str | None = None) -> str:
    """
    Save analysis report to JSON file.

    Args:
        stats: Analysis statistics dictionary
        filename: Optional custom filename

    Returns:
        Path to saved report
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_test_report_{timestamp}.json"

    # Add metadata
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "base_url": get_base_url(),
            "total_scenarios": len(TEST_SCENARIOS),
        },
        "results": stats,
    }

    filepath = os.path.join(
        os.path.dirname(__file__), "..", "..", "docs", "reports", filename
    )

    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📄 Report saved to: {filepath}")
    return filepath


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main():
    """Main entry point for the test suite."""
    parser = argparse.ArgumentParser(
        description="Cidadão.AI Production Chat Test Suite"
    )
    parser.add_argument(
        "--category",
        "-c",
        type=str,
        help="Run only specific category (e.g., investigate, greeting)",
    )
    parser.add_argument(
        "--save",
        "-s",
        action="store_true",
        help="Save report to JSON file",
    )
    parser.add_argument(
        "--url",
        "-u",
        type=str,
        help="Override production URL",
    )

    args = parser.parse_args()

    if args.url:
        os.environ["PROD_URL"] = args.url

    # Run tests
    results = asyncio.run(run_all_tests(category_filter=args.category))

    # Analyze
    stats = analyze_results(results)

    # Save if requested
    if args.save:
        save_report(stats)

    print("\n" + "=" * 70)
    print("✅ Test suite completed!")
    print("=" * 70)

    # Exit with error code if failure rate > 20%
    if stats["failed"] / stats["total"] > 0.2:
        sys.exit(1)


if __name__ == "__main__":
    main()
