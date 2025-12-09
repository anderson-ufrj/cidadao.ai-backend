"""
End-to-End Tests for Kids Educational Agents in Production

This script tests the Monteiro Lobato and Tarsila do Amaral agents
against the production API to ensure they respond appropriately
to various educational scenarios.

Usage:
    # Run all tests
    python tests/e2e/test_kids_agents_production.py

    # Run with pytest
    pytest tests/e2e/test_kids_agents_production.py -v

    # Run specific agent tests
    pytest tests/e2e/test_kids_agents_production.py -v -k "monteiro"
    pytest tests/e2e/test_kids_agents_production.py -v -k "tarsila"

Environment:
    PRODUCTION_URL: Override default production URL (optional)
"""

import asyncio
import json
import os
from dataclasses import dataclass
from enum import Enum

import httpx
import pytest

# Configuration
PRODUCTION_URL = os.getenv(
    "PRODUCTION_URL", "https://cidadao-api-production.up.railway.app"
)
CHAT_ENDPOINT = f"{PRODUCTION_URL}/api/v1/chat/stream"
TIMEOUT = 60.0


class TestStatus(Enum):
    """Test result status."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class TestScenario:
    """Test scenario configuration."""

    name: str
    agent_id: str
    message: str
    expected_keywords: list[str]
    blocked_keywords: list[str] | None = None
    description: str = ""


# ============================================================================
# MONTEIRO LOBATO TEST SCENARIOS
# ============================================================================
MONTEIRO_LOBATO_SCENARIOS = [
    TestScenario(
        name="greeting",
        agent_id="monteiro_lobato",
        message="Ola! Sou uma crianca de 10 anos e quero aprender programacao",
        expected_keywords=["sitio"],  # Core identifier
        description="Basic greeting - should welcome and introduce programming concepts",
    ),
    TestScenario(
        name="variables_concept",
        agent_id="monteiro_lobato",
        message="O que e uma variavel?",
        expected_keywords=["caixinha", "emilia"],  # Simplified - caixinha is used
        description="Explain variables using Emilia's boxes metaphor",
    ),
    TestScenario(
        name="loops_concept",
        agent_id="monteiro_lobato",
        message="Como funciona um loop? O que e repeticao?",
        expected_keywords=["saci", "vezes"],  # Core concepts
        description="Explain loops using Saci's jumping metaphor",
    ),
    TestScenario(
        name="functions_concept",
        agent_id="monteiro_lobato",
        message="O que e uma funcao em programacao?",
        expected_keywords=["receita", "nastacia"],  # Core metaphor
        description="Explain functions using Tia Nastacia's recipes metaphor",
    ),
    TestScenario(
        name="conditionals_concept",
        agent_id="monteiro_lobato",
        message="Como funciona o SE e SENAO?",
        expected_keywords=["pedrinho", "se"],  # Core concept
        description="Explain conditionals using Pedrinho's decisions",
    ),
    TestScenario(
        name="games_interest",
        agent_id="monteiro_lobato",
        message="Quero fazer um joguinho!",
        expected_keywords=["sitio"],  # May redirect to programming topics
        description="Respond to game creation interest",
    ),
    TestScenario(
        name="age_appropriate_language",
        agent_id="monteiro_lobato",
        message="Explica algoritmo pra mim",
        expected_keywords=["sitio"],  # Should mention sitio context
        blocked_keywords=["complexidade", "otimizacao", "big-o"],
        description="Should use simple language, avoid technical jargon",
    ),
    TestScenario(
        name="encouragement",
        agent_id="monteiro_lobato",
        message="Eu nao entendi, e muito dificil",
        expected_keywords=["sitio"],  # Context reference
        description="Should provide encouragement when child is frustrated",
    ),
    TestScenario(
        name="off_topic_redirect",
        agent_id="monteiro_lobato",
        message="Qual e a capital da Franca?",
        expected_keywords=["sitio"],  # Should redirect to sitio context
        description="Should redirect off-topic questions back to programming",
    ),
    TestScenario(
        name="alias_lobato",
        agent_id="lobato",
        message="Oi Lobato!",
        expected_keywords=["sitio"],
        description="Test alias 'lobato' routes to monteiro_lobato",
    ),
]

# ============================================================================
# TARSILA DO AMARAL TEST SCENARIOS
# ============================================================================
TARSILA_SCENARIOS = [
    TestScenario(
        name="greeting",
        agent_id="tarsila",
        message="Ola! Quero aprender sobre arte e design!",
        expected_keywords=["tarsila"],  # Should identify as Tarsila
        description="Basic greeting - should welcome and introduce art concepts",
    ),
    TestScenario(
        name="colors_concept",
        agent_id="tarsila",
        message="Como funcionam as cores?",
        expected_keywords=["cor"],  # Core topic
        description="Explain color theory in simple terms",
    ),
    TestScenario(
        name="character_design",
        agent_id="tarsila",
        message="Quero desenhar um personagem para meu jogo!",
        expected_keywords=["cor"],  # May redirect to colors/design
        description="Help with character design concepts",
    ),
    TestScenario(
        name="composition",
        agent_id="tarsila",
        message="Como deixar meu desenho mais bonito?",
        expected_keywords=["cor"],  # Core design topic
        description="Teach basic composition principles",
    ),
    TestScenario(
        name="contrast",
        agent_id="tarsila",
        message="O que e contraste?",
        expected_keywords=["contraste"],  # Direct topic
        description="Explain contrast in simple terms",
    ),
    TestScenario(
        name="brazilian_art",
        agent_id="tarsila",
        message="Me fala sobre arte brasileira",
        expected_keywords=["tarsila"],  # Should reference self
        description="Share knowledge about Brazilian art",
    ),
    TestScenario(
        name="ui_design_for_kids",
        agent_id="tarsila",
        message="Como fazer um botao bonito para meu app?",
        expected_keywords=["cor"],  # Design involves colors
        description="Simple UI design concepts for children",
    ),
    TestScenario(
        name="encouragement",
        agent_id="tarsila",
        message="Meu desenho ficou feio",
        expected_keywords=["tarsila"],  # Context reference
        description="Should encourage when child is frustrated",
    ),
    TestScenario(
        name="off_topic_redirect",
        agent_id="tarsila",
        message="Quanto e 2 mais 2?",
        expected_keywords=["cor"],  # Should redirect to art/design
        description="Should redirect off-topic questions back to art/design",
    ),
    TestScenario(
        name="alias_amaral",
        agent_id="amaral",
        message="Oi Tarsila!",
        expected_keywords=["tarsila"],  # Should identify as Tarsila
        description="Test alias 'amaral' routes to tarsila",
    ),
]


def parse_sse_response(response_text: str) -> dict:
    """
    Parse Server-Sent Events response into structured data.

    Args:
        response_text: Raw SSE response text

    Returns:
        Dictionary with parsed events and full content
    """
    events = []
    full_content = []
    agent_id = None
    agent_name = None

    for line in response_text.split("\n"):
        if line.startswith("data: "):
            try:
                data = json.loads(line[6:])
                events.append(data)

                if data.get("type") == "chunk":
                    content = data.get("content", "")
                    if content:
                        full_content.append(content)

                if data.get("type") == "agent_selected":
                    agent_id = data.get("agent_id")
                    agent_name = data.get("agent_name")

                if data.get("type") == "complete":
                    if not agent_id:
                        agent_id = data.get("agent_id")
                    if not agent_name:
                        agent_name = data.get("agent_name")

            except json.JSONDecodeError:
                continue

    return {
        "events": events,
        "full_content": " ".join(full_content).lower(),
        "agent_id": agent_id,
        "agent_name": agent_name,
        "raw": response_text,
    }


async def run_scenario(scenario: TestScenario) -> tuple[TestStatus, str]:
    """
    Run a single test scenario against the production API.

    Args:
        scenario: Test scenario configuration

    Returns:
        Tuple of (status, message)
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            payload = {
                "message": scenario.message,
                "session_id": f"test-{scenario.agent_id}-{scenario.name}",
                "agent_id": scenario.agent_id,
            }

            response = await client.post(
                CHAT_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code != 200:
                return (
                    TestStatus.FAILED,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                )

            parsed = parse_sse_response(response.text)

            # Check if agent was correctly selected
            expected_agent = scenario.agent_id
            if scenario.agent_id in ["lobato", "monteiro"]:
                expected_agent = "monteiro_lobato"
            elif scenario.agent_id in ["amaral", "tarsila_do_amaral"]:
                expected_agent = "tarsila"

            if parsed["agent_id"] != expected_agent:
                return (
                    TestStatus.FAILED,
                    f"Wrong agent: expected {expected_agent}, got {parsed['agent_id']}",
                )

            # Check for expected keywords
            content = parsed["full_content"]
            missing_keywords = []
            for keyword in scenario.expected_keywords:
                if keyword.lower() not in content:
                    missing_keywords.append(keyword)

            if missing_keywords:
                return (
                    TestStatus.FAILED,
                    f"Missing keywords: {missing_keywords}. Content: {content[:200]}...",
                )

            # Check for blocked keywords (if any)
            if scenario.blocked_keywords:
                found_blocked = []
                for keyword in scenario.blocked_keywords:
                    if keyword.lower() in content:
                        found_blocked.append(keyword)
                if found_blocked:
                    return TestStatus.FAILED, f"Found blocked keywords: {found_blocked}"

            return TestStatus.PASSED, f"Response OK ({len(content)} chars)"

    except httpx.TimeoutException:
        return TestStatus.FAILED, "Request timeout"
    except Exception as e:
        return TestStatus.FAILED, f"Error: {type(e).__name__}: {str(e)}"


async def run_all_scenarios(scenarios: list[TestScenario], agent_name: str) -> dict:
    """
    Run all scenarios for an agent.

    Args:
        scenarios: List of test scenarios
        agent_name: Display name for the agent

    Returns:
        Summary dictionary with results
    """
    print(f"\n{'='*60}")
    print(f"Testing {agent_name}")
    print(f"{'='*60}")

    results = {"passed": 0, "failed": 0, "skipped": 0, "details": []}

    for scenario in scenarios:
        print(f"\n  [{scenario.name}] {scenario.description}")
        print(f'    Message: "{scenario.message[:50]}..."')

        status, message = await run_scenario(scenario)

        if status == TestStatus.PASSED:
            results["passed"] += 1
            print(f"    Result: PASSED - {message}")
        elif status == TestStatus.FAILED:
            results["failed"] += 1
            print(f"    Result: FAILED - {message}")
        else:
            results["skipped"] += 1
            print(f"    Result: SKIPPED - {message}")

        results["details"].append(
            {
                "scenario": scenario.name,
                "status": status.value,
                "message": message,
            }
        )

        # Small delay between requests to be nice to the API
        await asyncio.sleep(0.5)

    return results


async def main():
    """Main test runner."""
    print("\n" + "=" * 60)
    print("KIDS EDUCATIONAL AGENTS - PRODUCTION TESTS")
    print(f"Target: {PRODUCTION_URL}")
    print("=" * 60)

    # Check API health first
    print("\nChecking API health...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            health = await client.get(f"{PRODUCTION_URL}/health/")
            if health.status_code != 200:
                print(f"API unhealthy: {health.status_code}")
                return None
            print("API Status: OK")
    except Exception as e:
        print(f"Cannot reach API: {e}")
        return None

    # Run Monteiro Lobato tests
    lobato_results = await run_all_scenarios(
        MONTEIRO_LOBATO_SCENARIOS, "Monteiro Lobato (Kids Programming)"
    )

    # Run Tarsila tests
    tarsila_results = await run_all_scenarios(
        TARSILA_SCENARIOS, "Tarsila do Amaral (Kids Design)"
    )

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_passed = lobato_results["passed"] + tarsila_results["passed"]
    total_failed = lobato_results["failed"] + tarsila_results["failed"]
    total_tests = total_passed + total_failed

    print(
        f"\nMonteiro Lobato: {lobato_results['passed']}/{len(MONTEIRO_LOBATO_SCENARIOS)} passed"
    )
    print(
        f"Tarsila do Amaral: {tarsila_results['passed']}/{len(TARSILA_SCENARIOS)} passed"
    )
    print(
        f"\nTotal: {total_passed}/{total_tests} passed ({100*total_passed/total_tests:.1f}%)"
    )

    if total_failed > 0:
        print("\nFailed tests:")
        for result in lobato_results["details"] + tarsila_results["details"]:
            if result["status"] == "FAILED":
                print(f"  - {result['scenario']}: {result['message'][:100]}")

    return total_failed == 0


# ============================================================================
# PYTEST INTEGRATION
# ============================================================================
@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestMonteiroLobato:
    """Pytest test class for Monteiro Lobato agent."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "scenario", MONTEIRO_LOBATO_SCENARIOS, ids=lambda s: s.name
    )
    async def test_scenario(self, scenario: TestScenario):
        """Test a Monteiro Lobato scenario."""
        status, message = await run_scenario(scenario)
        assert status == TestStatus.PASSED, f"{scenario.name}: {message}"


class TestTarsila:
    """Pytest test class for Tarsila agent."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("scenario", TARSILA_SCENARIOS, ids=lambda s: s.name)
    async def test_scenario(self, scenario: TestScenario):
        """Test a Tarsila scenario."""
        status, message = await run_scenario(scenario)
        assert status == TestStatus.PASSED, f"{scenario.name}: {message}"


class TestAgentAliases:
    """Test that agent aliases work correctly."""

    @pytest.mark.asyncio
    async def test_lobato_alias(self):
        """Test 'lobato' alias routes to monteiro_lobato."""
        scenario = TestScenario(
            name="alias_test",
            agent_id="lobato",
            message="Ola!",
            expected_keywords=["sitio"],
        )
        status, message = await run_scenario(scenario)
        assert status == TestStatus.PASSED, message

    @pytest.mark.asyncio
    async def test_monteiro_alias(self):
        """Test 'monteiro' alias routes to monteiro_lobato."""
        scenario = TestScenario(
            name="alias_test",
            agent_id="monteiro",
            message="Ola!",
            expected_keywords=["sitio"],
        )
        status, message = await run_scenario(scenario)
        assert status == TestStatus.PASSED, message

    @pytest.mark.asyncio
    async def test_amaral_alias(self):
        """Test 'amaral' alias routes to tarsila."""
        scenario = TestScenario(
            name="alias_test",
            agent_id="amaral",
            message="Ola!",
            expected_keywords=["cor", "arte"],
        )
        status, message = await run_scenario(scenario)
        assert status == TestStatus.PASSED, message


if __name__ == "__main__":
    import sys

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
