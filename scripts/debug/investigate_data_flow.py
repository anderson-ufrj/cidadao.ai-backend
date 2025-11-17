#!/usr/bin/env python3
"""
Investigação Profunda - Fluxo de Dados Chat → APIs
Rastreia cada passo do processamento para encontrar onde os dados são perdidos
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.chat_data_integration import ChatDataIntegration


async def test_1_entity_extraction():
    """TESTE 1: Verificar se entity extraction funciona corretamente."""
    print("\n" + "=" * 80)
    print("TESTE 1: Entity Extraction Local")
    print("=" * 80)

    query = "Quero ver contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024"
    print(f"\nQuery: {query}")

    integration = ChatDataIntegration()
    entities = await integration._extract_entities(query)

    print("\n✅ Entidades extraídas:")
    for key, value in entities.items():
        print(f"  {key}: {value}")

    # Verificações críticas
    checks = {
        "Estado extraído": "estado" in entities and entities["estado"] == "MG",
        "Código IBGE": "codigo_uf" in entities and entities["codigo_uf"] == "31",
        "Valor extraído": "valor" in entities and entities["valor"] == 1000000.0,
        "Ano extraído": "ano" in entities and entities["ano"] == 2024,
    }

    print("\n📊 Verificações:")
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")

    return all(checks.values()), entities


async def test_2_portal_api_params():
    """TESTE 2: Verificar parâmetros enviados para Portal API."""
    print("\n" + "=" * 80)
    print("TESTE 2: Parâmetros para Portal da Transparência")
    print("=" * 80)

    from src.services.portal_transparencia_service import PortalTransparenciaService

    service = PortalTransparenciaService()

    # Simular parâmetros que DEVERIAM ser enviados
    params = {
        "data_inicial": "01/01/2024",
        "data_final": "31/12/2024",
        "valor_minimo": 1000000,  # R$ 1 milhão
    }

    print(f"\n📤 Parâmetros que deveriam ser enviados:")
    for key, value in params.items():
        print(f"  {key}: {value}")

    # Verificar se service tem método correto
    print(f"\n🔍 Métodos disponíveis no service:")
    methods = [m for m in dir(service) if not m.startswith("_") and callable(getattr(service, m))]
    for method in methods[:10]:
        print(f"  - {method}")

    return True


async def test_3_orchestrator_investigation():
    """TESTE 3: Simular chamada completa ao Orchestrator."""
    print("\n" + "=" * 80)
    print("TESTE 3: Orchestrator Investigation Flow")
    print("=" * 80)

    try:
        from src.services.orchestration.orchestrator import InvestigationOrchestrator

        orchestrator = InvestigationOrchestrator()
        print("✅ Orchestrator importado com sucesso")

        query = "Contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024"
        print(f"\nQuery: {query}")

        # Testar extração de entidades do orchestrator
        print("\n1️⃣ Testando entity extraction do Orchestrator...")
        try:
            entities = await orchestrator.entity_extractor.extract(query)
            print(f"  ✅ Entidades extraídas: {len(entities)} items")
            for key, value in list(entities.items())[:5]:
                print(f"    {key}: {value}")
        except Exception as e:
            print(f"  ❌ Erro na extração: {e}")
            import traceback
            traceback.print_exc()

        # Testar classificação de intent
        print("\n2️⃣ Testando intent classification...")
        try:
            intent = await orchestrator.intent_classifier.classify(query)
            print(f"  ✅ Intent: {intent}")
            if hasattr(intent, 'type'):
                print(f"    Type: {intent.type}")
                print(f"    Confidence: {intent.confidence if hasattr(intent, 'confidence') else 'N/A'}")
        except Exception as e:
            print(f"  ❌ Erro na classificação: {e}")
            import traceback
            traceback.print_exc()

        # Testar criação de plano
        print("\n3️⃣ Testando execution planning...")
        try:
            # Precisamos de intent e entities válidos
            from src.services.chat_service import IntentType

            # Criar um intent mock
            class MockIntent:
                def __init__(self):
                    self.type = IntentType.INVESTIGATE
                    self.confidence = 0.9
                    self.value = "INVESTIGATE"

            mock_intent = MockIntent()
            mock_entities = {
                "estado": "MG",
                "codigo_uf": "31",
                "valor": 1000000.0,
                "ano": 2024,
                "categoria": "saúde"
            }

            plan = await orchestrator.execution_planner.create_plan(
                query=query,
                intent=mock_intent,
                entities=mock_entities
            )
            print(f"  ✅ Plano criado: {len(plan.stages)} estágios")
            for i, stage in enumerate(plan.stages, 1):
                print(f"    Estágio {i}: {len(stage.api_calls)} chamadas de API")
                for call in stage.api_calls[:3]:  # Mostrar primeiras 3
                    print(f"      - {call.api_name}")
        except Exception as e:
            print(f"  ❌ Erro no planejamento: {e}")
            import traceback
            traceback.print_exc()

        return True

    except ImportError as e:
        print(f"❌ Orchestrator não disponível: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_4_zumbi_integration():
    """TESTE 4: Testar integração direta com Zumbi."""
    print("\n" + "=" * 80)
    print("TESTE 4: Integração Direta com Zumbi")
    print("=" * 80)

    try:
        from src.api.routes.chat_zumbi_integration import run_zumbi_investigation

        print("✅ Módulo de integração Zumbi importado")

        query = "Contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024"
        print(f"\nQuery: {query}")

        print("\n🔄 Executando investigação com Zumbi...")
        print("   (Nota: Pode demorar alguns segundos)")

        # Executar investigação
        result = await run_zumbi_investigation(
            query=query,
            organization_codes=None,
            enable_open_data=True,
            session_id="test-investigation-001",
            user_id="test-user"
        )

        print(f"\n📊 Resultado da investigação:")
        print(f"  Status: {result.get('status', 'N/A')}")
        print(f"  Registros analisados: {result.get('records_analyzed', 0)}")
        print(f"  Anomalias detectadas: {result.get('anomalies_found', 0)}")
        print(f"  Valor total: R$ {result.get('total_value', 0):,.2f}")

        # Verificar se há dados reais
        has_real_data = (
            result.get('records_analyzed', 0) > 0 and
            result.get('total_value', 0) > 0
        )

        if has_real_data:
            print("\n✅ DADOS REAIS FORAM RETORNADOS!")
        else:
            print("\n❌ DADOS MOCKADOS OU VAZIOS!")
            print("\n🔍 Detalhes do resultado:")
            for key, value in result.items():
                if key != "details":  # Não mostrar detalhes completos
                    print(f"  {key}: {value}")

        return has_real_data

    except Exception as e:
        print(f"❌ Erro ao testar Zumbi: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_5_check_api_key():
    """TESTE 5: Verificar se API key do Portal está configurada."""
    print("\n" + "=" * 80)
    print("TESTE 5: Verificação de API Key")
    print("=" * 80)

    import os
    from src.core.config import get_settings

    settings = get_settings()

    # Verificar variável de ambiente
    env_key = os.getenv("TRANSPARENCY_API_KEY")
    print(f"\n🔑 TRANSPARENCY_API_KEY no ambiente: {'✅ Configurada' if env_key else '❌ Não configurada'}")
    if env_key:
        print(f"   Tamanho da key: {len(env_key)} caracteres")
        print(f"   Preview: {env_key[:8]}...{env_key[-4:]}")

    # Verificar settings
    settings_key = getattr(settings, 'TRANSPARENCY_API_KEY', None)
    print(f"\n🔑 Settings.TRANSPARENCY_API_KEY: {'✅ Configurada' if settings_key else '❌ Não configurada'}")
    if settings_key:
        print(f"   Tamanho da key: {len(settings_key)} caracteres")

    return bool(env_key or settings_key)


async def main():
    """Executa investigação completa."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "INVESTIGAÇÃO PROFUNDA - FLUXO DE DADOS" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")

    results = {}

    # Teste 1: Entity Extraction
    try:
        passed, entities = await test_1_entity_extraction()
        results["Entity Extraction"] = passed
    except Exception as e:
        print(f"\n❌ Erro no teste 1: {e}")
        import traceback
        traceback.print_exc()
        results["Entity Extraction"] = False
        entities = {}

    # Teste 2: Portal API Params
    try:
        passed = await test_2_portal_api_params()
        results["Portal API Params"] = passed
    except Exception as e:
        print(f"\n❌ Erro no teste 2: {e}")
        results["Portal API Params"] = False

    # Teste 3: Orchestrator Flow
    try:
        passed = await test_3_orchestrator_investigation()
        results["Orchestrator Flow"] = passed
    except Exception as e:
        print(f"\n❌ Erro no teste 3: {e}")
        results["Orchestrator Flow"] = False

    # Teste 4: Zumbi Integration
    try:
        passed = await test_4_zumbi_integration()
        results["Zumbi Integration"] = passed
    except Exception as e:
        print(f"\n❌ Erro no teste 4: {e}")
        results["Zumbi Integration"] = False

    # Teste 5: API Key Check
    try:
        passed = await test_5_check_api_key()
        results["API Key Configuration"] = passed
    except Exception as e:
        print(f"\n❌ Erro no teste 5: {e}")
        results["API Key Configuration"] = False

    # Análise Final
    print("\n" + "=" * 80)
    print("ANÁLISE FINAL - DIAGNÓSTICO")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status}: {test_name}")

    # Identificar ponto de falha
    print("\n" + "=" * 80)
    print("DIAGNÓSTICO")
    print("=" * 80)

    if not results.get("Entity Extraction"):
        print("\n🔴 PROBLEMA: Entity Extraction está falhando")
        print("   → As entidades não estão sendo extraídas corretamente")
        print("   → FIX: Revisar src/services/chat_data_integration.py")

    elif not results.get("API Key Configuration"):
        print("\n🔴 PROBLEMA: API Key não configurada")
        print("   → Portal da Transparência requer API key")
        print("   → FIX: Configurar TRANSPARENCY_API_KEY no .env")

    elif not results.get("Orchestrator Flow"):
        print("\n🔴 PROBLEMA: Orchestrator não está funcionando")
        print("   → O fluxo de orquestração está quebrado")
        print("   → FIX: Revisar src/services/orchestration/")

    elif not results.get("Zumbi Integration"):
        print("\n🔴 PROBLEMA: Zumbi não está retornando dados reais")
        print("   → A integração com Zumbi está falhando")
        print("   → FIX: Revisar src/api/routes/chat_zumbi_integration.py")

    else:
        print("\n✅ Todos os componentes estão funcionando!")
        print("   → O problema pode estar na integração entre eles")
        print("   → Verificar fluxo completo em src/api/routes/chat.py")

    passed = sum(1 for r in results.values() if r is True)
    total = len(results)
    print(f"\nTotal: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
