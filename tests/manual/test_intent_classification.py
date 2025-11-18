#!/usr/bin/env python3
"""
Test Intent Classification Improvements
Validates that investigation queries are properly detected
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.orchestration.models.investigation import InvestigationIntent
from src.services.orchestration.query_planner.intent_classifier import IntentClassifier

# Test queries that MUST be classified as investigations
INVESTIGATION_QUERIES = [
    # Original problem query
    (
        "Quero ver contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024",
        InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
    ),
    (
        "Contratos de saúde em MG acima de 1 milhão em 2024",
        InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
    ),
    # Variations with different keywords
    (
        "Investigar contratos públicos em São Paulo 2024",
        InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
    ),
    (
        "Analisar licitações de educação acima de R$ 500 mil",
        InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
    ),
    (
        "Verificar despesas da prefeitura maiores que 1 milhão",
        InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
    ),
    # With explicit investigation verbs
    (
        "INVESTIGAR contratos suspeitos em Minas Gerais",
        InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
    ),
    (
        "ANALISAR gastos públicos em São Paulo",
        InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
    ),
    # CNPJ queries
    ("Investigar CNPJ 12.345.678/0001-90", InvestigationIntent.SUPPLIER_INVESTIGATION),
    ("Contratos da empresa 12345678000190", InvestigationIntent.SUPPLIER_INVESTIGATION),
]

# Test queries that should be general questions
GENERAL_QUERIES = [
    ("Como funciona o sistema?", InvestigationIntent.GENERAL_QUERY),
    ("O que é transparência pública?", InvestigationIntent.GENERAL_QUERY),
    ("Ajuda sobre o Portal da Transparência", InvestigationIntent.GENERAL_QUERY),
    ("Quais dados estão disponíveis?", InvestigationIntent.GENERAL_QUERY),
]


async def test_intent_classification():
    """Test intent classification with real queries."""
    print("\n" + "=" * 80)
    print("TESTE: Intent Classification Improvements")
    print("=" * 80)
    print()

    classifier = IntentClassifier()

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    # Test investigation queries
    print("🔍 Testando Queries de INVESTIGAÇÃO:")
    print("-" * 80)
    for query, expected_intent in INVESTIGATION_QUERIES:
        total_tests += 1
        result = await classifier.classify(query)

        actual_intent = result["intent"]
        confidence = result["confidence"]
        method = result.get("method", "unknown")
        reasoning = result.get("reasoning", "")

        if actual_intent == expected_intent:
            status = "✅"
            passed_tests += 1
        else:
            status = "❌"
            failed_tests.append(
                {
                    "query": query,
                    "expected": expected_intent,
                    "actual": actual_intent,
                    "confidence": confidence,
                    "method": method,
                    "reasoning": reasoning,
                }
            )

        print(
            f"{status} [{method:7}] {confidence:.2f} | {actual_intent.value[:25]:25} | {query[:50]}"
        )
        if reasoning and status == "❌":
            print(f"          Reasoning: {reasoning}")
    print()

    # Test general queries
    print("❓ Testando Queries GERAIS:")
    print("-" * 80)
    for query, expected_intent in GENERAL_QUERIES:
        total_tests += 1
        result = await classifier.classify(query)

        actual_intent = result["intent"]
        confidence = result["confidence"]
        method = result.get("method", "unknown")
        reasoning = result.get("reasoning", "")

        if actual_intent == expected_intent:
            status = "✅"
            passed_tests += 1
        else:
            status = "❌"
            failed_tests.append(
                {
                    "query": query,
                    "expected": expected_intent,
                    "actual": actual_intent,
                    "confidence": confidence,
                    "method": method,
                    "reasoning": reasoning,
                }
            )

        print(
            f"{status} [{method:7}] {confidence:.2f} | {actual_intent.value[:25]:25} | {query[:50]}"
        )
    print()

    # Results summary
    print("=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    print(f"Total de testes: {total_tests}")
    print(f"✅ Passou: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"❌ Falhou: {len(failed_tests)} ({len(failed_tests)/total_tests*100:.1f}%)")
    print()

    if failed_tests:
        print("⚠️  TESTES QUE FALHARAM:")
        print("-" * 80)
        for fail in failed_tests:
            print(f"\nQuery: {fail['query']}")
            print(f"  Esperado: {fail['expected'].value}")
            print(f"  Recebido: {fail['actual'].value}")
            print(f"  Confiança: {fail['confidence']:.2f}")
            print(f"  Método: {fail['method']}")
            print(f"  Reasoning: {fail['reasoning']}")
        print()

    # Success criteria
    success_rate = passed_tests / total_tests
    if success_rate >= 0.95:  # 95% success rate
        print("🎉 EXCELENTE! Taxa de sucesso >= 95%")
        return 0
    elif success_rate >= 0.80:  # 80% success rate
        print("✅ BOM! Taxa de sucesso >= 80%")
        return 0
    else:
        print("❌ PRECISA MELHORAR! Taxa de sucesso < 80%")
        return 1


async def test_specific_problem_query():
    """Test the specific problem query that was failing."""
    print("\n" + "=" * 80)
    print("TESTE ESPECÍFICO: Query Original do Problema")
    print("=" * 80)
    print()

    classifier = IntentClassifier()

    # The exact query that was failing
    query = "Quero ver contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024"

    print(f'Query: "{query}"')
    print()

    result = await classifier.classify(query)

    print("📊 Resultado da Classificação:")
    print(f"  Intent: {result['intent'].value}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Method: {result.get('method', 'unknown')}")
    print(f"  Reasoning: {result.get('reasoning', '')}")
    print()

    expected = InvestigationIntent.CONTRACT_ANOMALY_DETECTION
    if result["intent"] == expected:
        print(
            "✅ SUCESSO! Query classificada corretamente como CONTRACT_ANOMALY_DETECTION"
        )
        print()
        print("   Isso significa que:")
        print("   - Sistema vai chamar Zumbi ou Abaporu (investigadores)")
        print("   - Orchestrator vai buscar dados reais das APIs")
        print("   - Usuário vai receber análise com valores reais")
        print()
        return 0
    else:
        print(
            f"❌ FALHOU! Query classificada incorretamente como {result['intent'].value}"
        )
        print(f"   Esperado: {expected.value}")
        print()
        return 1


async def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TESTES DE INTENT CLASSIFICATION" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")

    # Test specific problem query first
    result1 = await test_specific_problem_query()

    # Test full test suite
    result2 = await test_intent_classification()

    # Overall result
    if result1 == 0 and result2 == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("   O sistema está pronto para retornar dados reais!")
        return 0
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
        print("   Revisar classificação antes de deploy")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
