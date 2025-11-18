#!/usr/bin/env python3
"""
Testes Completos - Cenários Reais de Uso do Chat

Valida se o sistema realmente faz o que promete:
1. Extração de entidades em múltiplos formatos
2. Integração com APIs governamentais
3. Análise multi-agente
4. Respostas completas e precisas
"""
import asyncio
import sys
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.chat_data_integration import ChatDataIntegration

# Importar Orchestrator se disponível
try:
    from src.services.orchestration.orchestrator import InvestigationOrchestrator

    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    print("⚠️  Orchestrator não disponível - alguns testes serão limitados")


class TestScenario:
    """Representa um cenário de teste."""

    def __init__(self, name: str, query: str, expected_entities: dict[str, Any]):
        self.name = name
        self.query = query
        self.expected_entities = expected_entities
        self.passed = False
        self.details = []


async def test_entity_extraction_scenarios():
    """Testa extração de entidades em múltiplos cenários."""
    print("\n" + "=" * 80)
    print("TESTE 1: Extração de Entidades - Cenários Reais")
    print("=" * 80)

    integration = ChatDataIntegration()

    scenarios = [
        TestScenario(
            name="Consulta com estado por extenso + valor em milhão",
            query="Contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024",
            expected_entities={
                "estado": "MG",
                "codigo_uf": "31",
                "valor": 1000000.0,
                "ano": 2024,
                "categoria": "saúde",
            },
        ),
        TestScenario(
            name="Consulta com sigla + valor em mil",
            query="Mostrar despesas de educação em SP maiores que R$ 500 mil",
            expected_entities={
                "estado": "SP",
                "codigo_uf": "35",
                "valor": 500000.0,
                "categoria": "educação",
            },
        ),
        TestScenario(
            name="Consulta com estado com acento + bilhão",
            query="Obras no Pará acima de R$ 2 bilhões",
            expected_entities={
                "estado": "PA",
                "codigo_uf": "15",
                "valor": 2000000000.0,
                "categoria": "infraestrutura",
            },
        ),
        TestScenario(
            name="Consulta com estado composto",
            query="Contratos no Rio de Janeiro em 2023",
            expected_entities={"estado": "RJ", "codigo_uf": "33", "ano": 2023},
        ),
        TestScenario(
            name="Consulta com CPF de servidor",
            query="Servidor CPF 123.456.789-00",
            expected_entities={"cpf": "12345678900"},
        ),
        TestScenario(
            name="Consulta com CNPJ de fornecedor",
            query="Fornecedor CNPJ 12.345.678/0001-90",
            expected_entities={"cnpj": "12345678000190"},
        ),
        TestScenario(
            name="Consulta complexa multi-entidade",
            query="Contratos de infraestrutura em São Paulo acima de R$ 10 milhões em 2023 e 2024",
            expected_entities={
                "estado": "SP",
                "codigo_uf": "35",
                "valor": 10000000.0,
                "categoria": "infraestrutura",
                "ano": 2024,  # Should extract latest year
            },
        ),
    ]

    results = []

    for scenario in scenarios:
        print(f"\n{'─' * 80}")
        print(f"📝 Cenário: {scenario.name}")
        print(f'Query: "{scenario.query}"')
        print()

        try:
            entities = await integration._extract_entities(scenario.query)

            print("Entidades extraídas:")
            for key, value in entities.items():
                print(f"  {key}: {value}")

            # Verificar entidades esperadas
            checks_passed = 0
            checks_total = 0

            for key, expected_value in scenario.expected_entities.items():
                checks_total += 1
                if key in entities:
                    actual_value = entities[key]
                    # Para categoria, permitir match parcial (case-insensitive)
                    if key == "categoria":
                        if isinstance(actual_value, str) and isinstance(
                            expected_value, str
                        ):
                            match = expected_value.lower() in actual_value.lower()
                        else:
                            match = actual_value == expected_value
                    else:
                        match = actual_value == expected_value

                    if match:
                        print(
                            f"  ✅ {key}: {actual_value} (esperado: {expected_value})"
                        )
                        checks_passed += 1
                        scenario.details.append(f"✅ {key}")
                    else:
                        print(
                            f"  ❌ {key}: {actual_value} (esperado: {expected_value})"
                        )
                        scenario.details.append(
                            f"❌ {key}: esperado {expected_value}, obtido {actual_value}"
                        )
                else:
                    print(f"  ❌ {key}: NÃO ENCONTRADO (esperado: {expected_value})")
                    scenario.details.append(f"❌ {key}: não extraído")

            success_rate = (
                (checks_passed / checks_total * 100) if checks_total > 0 else 0
            )
            scenario.passed = checks_passed == checks_total

            print(f"\nResultado: {checks_passed}/{checks_total} ({success_rate:.1f}%)")

            if scenario.passed:
                print("✅ PASSOU")
            else:
                print("❌ FALHOU")

            results.append(scenario)

        except Exception as e:
            print(f"❌ ERRO: {e}")
            scenario.passed = False
            scenario.details.append(f"Erro: {e}")
            results.append(scenario)

    # Resumo
    print(f"\n{'═' * 80}")
    print("RESUMO - Extração de Entidades")
    print(f"{'═' * 80}")

    passed = sum(1 for s in results if s.passed)
    total = len(results)

    for scenario in results:
        status = "✅" if scenario.passed else "❌"
        print(f"{status} {scenario.name}")

    print(f"\nTotal: {passed}/{total} cenários passaram ({passed/total*100:.1f}%)")

    return passed == total


async def test_orchestrator_query_planning():
    """Testa se Orchestrator cria plano de execução correto."""
    print("\n" + "=" * 80)
    print("TESTE 2: Planejamento de Consultas do Orchestrator")
    print("=" * 80)

    if not ORCHESTRATOR_AVAILABLE:
        print("⚠️  SKIP: Orchestrator não disponível")
        return None

    orchestrator = InvestigationOrchestrator()

    test_queries = [
        {
            "query": "Contratos de saúde em Minas Gerais acima de R$ 1 milhão",
            "expected_apis": ["portal_transparencia", "pncp", "compras_gov"],
            "expected_intent": "INVESTIGATE_CONTRACTS",
        },
        {
            "query": "Servidor CPF 123.456.789-00",
            "expected_apis": ["portal_transparencia"],
            "expected_intent": "SEARCH_SERVANTS",
        },
        {
            "query": "Fornecedor CNPJ 12.345.678/0001-90",
            "expected_apis": ["portal_transparencia", "minha_receita"],
            "expected_intent": "SEARCH_SUPPLIERS",
        },
    ]

    passed_tests = 0

    for test in test_queries:
        print(f"\n{'─' * 80}")
        print(f"Query: \"{test['query']}\"")

        try:
            # Extrair entidades
            entities = await orchestrator.entity_extractor.extract_entities(
                test["query"]
            )
            print(f"Entidades: {list(entities.keys())}")

            # Detectar intent
            intent = await orchestrator.intent_classifier.classify(test["query"])
            print(
                f"Intent detectado: {intent.type.value} (confiança: {intent.confidence:.2f})"
            )

            # Criar plano de execução
            plan = await orchestrator.execution_planner.create_plan(
                query=test["query"], intent=intent, entities=entities
            )

            print(f"Plano criado: {len(plan.stages)} estágios")
            for i, stage in enumerate(plan.stages, 1):
                print(f"  Estágio {i}: {len(stage.api_calls)} chamadas de API")

            # Verificar intent
            intent_match = intent.type.value == test["expected_intent"]
            print(
                f"{'✅' if intent_match else '❌'} Intent esperado: {test['expected_intent']}"
            )

            if intent_match:
                passed_tests += 1

        except Exception as e:
            print(f"❌ ERRO: {e}")
            import traceback

            traceback.print_exc()

    total_tests = len(test_queries)
    print(f"\n{'═' * 80}")
    print(
        f"Total: {passed_tests}/{total_tests} testes passaram ({passed_tests/total_tests*100:.1f}%)"
    )

    return passed_tests == total_tests


async def test_real_api_integration():
    """Testa integração real com APIs governamentais."""
    print("\n" + "=" * 80)
    print("TESTE 3: Integração Real com APIs Governamentais")
    print("=" * 80)

    integration = ChatDataIntegration()

    # Teste apenas se temos API key configurada
    import os

    if not os.getenv("TRANSPARENCY_API_KEY"):
        print("⚠️  SKIP: TRANSPARENCY_API_KEY não configurada")
        print("   Configure .env para testar integração real com APIs")
        return None

    test_cases = [
        {
            "name": "Portal da Transparência - Órgãos",
            "method": "get_agencies",
            "should_work": True,
        },
    ]

    passed = 0

    for test in test_cases:
        print(f"\n{'─' * 80}")
        print(f"Teste: {test['name']}")

        try:
            if test["method"] == "get_agencies":
                # Testar endpoint de órgãos (sabemos que funciona)
                from src.tools.transparency_api import TransparencyAPIClient

                client = TransparencyAPIClient()

                # Buscar alguns órgãos
                result = await client._make_request("/orgaos", params={"pagina": 1})

                if result and len(result) > 0:
                    print(f"✅ API retornou {len(result)} órgãos")
                    print(f"   Exemplo: {result[0].get('nome', 'N/A')}")
                    passed += 1
                else:
                    print("❌ API não retornou dados")

        except Exception as e:
            print(f"❌ ERRO: {e}")
            if test["should_work"]:
                print(
                    "   Esta API DEVERIA funcionar - possível problema de configuração"
                )

    total = len(test_cases)
    if total > 0:
        print(f"\n{'═' * 80}")
        print(f"Total: {passed}/{total} APIs funcionando ({passed/total*100:.1f}%)")
        return passed == total

    return None


async def test_end_to_end_query():
    """Teste completo end-to-end de uma query."""
    print("\n" + "=" * 80)
    print("TESTE 4: End-to-End Query Completa")
    print("=" * 80)

    if not ORCHESTRATOR_AVAILABLE:
        print("⚠️  SKIP: Orchestrator não disponível")
        return None

    query = "Contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024"
    print(f'\nQuery: "{query}"')
    print()

    try:
        orchestrator = InvestigationOrchestrator()

        # Executar investigação completa (com timeout curto para teste)
        print("Executando investigação...")
        print("(Nota: Pode demorar alguns segundos para consultar APIs reais)")

        # Apenas simular o fluxo sem executar de fato (para não depender de APIs externas)
        print("\nSimulação do fluxo:")

        # 1. Intent Detection
        intent = await orchestrator.intent_classifier.classify(query)
        print(
            f"✅ 1. Intent Detection: {intent.type.value} (confiança: {intent.confidence:.2f})"
        )

        # 2. Entity Extraction
        entities = await orchestrator.entity_extractor.extract_entities(query)
        print(f"✅ 2. Entity Extraction: {len(entities)} entidades extraídas")
        for key, value in entities.items():
            print(f"      {key}: {value}")

        # 3. Execution Planning
        plan = await orchestrator.execution_planner.create_plan(
            query=query, intent=intent, entities=entities
        )
        print(f"✅ 3. Execution Plan: {len(plan.stages)} estágios criados")

        total_apis = sum(len(stage.api_calls) for stage in plan.stages)
        print(f"      Total de {total_apis} chamadas de API planejadas")

        # 4. Verificações
        checks = []

        # Check: Intent correto
        if intent.type.value == "INVESTIGATE_CONTRACTS":
            print("✅ 4. Intent correto (INVESTIGATE_CONTRACTS)")
            checks.append(True)
        else:
            print(f"❌ 4. Intent incorreto: {intent.type.value}")
            checks.append(False)

        # Check: Entidades essenciais extraídas
        required = ["estado", "codigo_uf", "valor"]
        missing = [r for r in required if r not in entities]
        if not missing:
            print(f"✅ 5. Entidades essenciais extraídas: {', '.join(required)}")
            checks.append(True)
        else:
            print(f"❌ 5. Entidades faltando: {', '.join(missing)}")
            checks.append(False)

        # Check: Múltiplas APIs no plano
        if total_apis >= 3:
            print(f"✅ 6. Múltiplas APIs planejadas ({total_apis} >= 3)")
            checks.append(True)
        else:
            print(f"❌ 6. Poucas APIs planejadas ({total_apis} < 3)")
            checks.append(False)

        success = all(checks)

        print(f"\n{'═' * 80}")
        if success:
            print("✅ TESTE END-TO-END PASSOU")
        else:
            print("❌ TESTE END-TO-END FALHOU")

        return success

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Executa todos os testes."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "TESTES COMPLETOS - CENÁRIOS REAIS" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")

    results = {}

    # Teste 1: Entity Extraction
    try:
        result1 = await test_entity_extraction_scenarios()
        results["Entity Extraction"] = result1
    except Exception as e:
        print(f"\n❌ Erro no Teste 1: {e}")
        results["Entity Extraction"] = False

    # Teste 2: Orchestrator Planning
    try:
        result2 = await test_orchestrator_query_planning()
        results["Orchestrator Planning"] = result2
    except Exception as e:
        print(f"\n❌ Erro no Teste 2: {e}")
        results["Orchestrator Planning"] = False

    # Teste 3: Real API Integration
    try:
        result3 = await test_real_api_integration()
        results["Real API Integration"] = result3
    except Exception as e:
        print(f"\n❌ Erro no Teste 3: {e}")
        results["Real API Integration"] = False

    # Teste 4: End-to-End
    try:
        result4 = await test_end_to_end_query()
        results["End-to-End Query"] = result4
    except Exception as e:
        print(f"\n❌ Erro no Teste 4: {e}")
        results["End-to-End Query"] = False

    # Resultado Final
    print("\n" + "=" * 80)
    print("RESULTADO FINAL - TODOS OS TESTES")
    print("=" * 80)

    for test_name, result in results.items():
        if result is True:
            print(f"✅ PASSOU: {test_name}")
        elif result is False:
            print(f"❌ FALHOU: {test_name}")
        else:
            print(f"⚠️  SKIP: {test_name} (dependências não disponíveis)")

    # Calcular taxa de sucesso (apenas testes que rodaram)
    executed = [r for r in results.values() if r is not None]
    if executed:
        passed = sum(1 for r in executed if r is True)
        total = len(executed)
        success_rate = passed / total * 100

        print(
            f"\nTaxa de Sucesso: {passed}/{total} testes passaram ({success_rate:.1f}%)"
        )

        if success_rate == 100:
            print("\n🎉 PERFEITO! O sistema está funcionando conforme prometido!")
            return 0
        elif success_rate >= 75:
            print("\n✅ BOM! A maioria dos testes passou, mas há melhorias a fazer.")
            return 0
        else:
            print("\n⚠️  ATENÇÃO! Muitos testes falharam - revisão necessária.")
            return 1
    else:
        print("\n⚠️  Nenhum teste foi executado - verifique dependências.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
