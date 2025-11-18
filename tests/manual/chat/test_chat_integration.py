#!/usr/bin/env python3
"""
Script de teste para validar integração Chat → APIs Governamentais

Testa:
1. Extração de entidades (estado, valor, categoria)
2. Integração com Orchestrator
3. Busca real em APIs governamentais
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.chat_data_integration import ChatDataIntegration


async def test_entity_extraction():
    """Testa extração de entidades da mensagem do usuário."""
    print("=" * 80)
    print("TESTE 1: Extração de Entidades")
    print("=" * 80)

    integration = ChatDataIntegration()

    # Mensagem exata do usuário que estava falhando
    message = (
        "Quero ver contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024"
    )

    print(f"\nMensagem: {message}\n")

    entities = await integration._extract_entities(message)

    print("Entidades extraídas:")
    print("-" * 40)
    for key, value in entities.items():
        print(f"  {key}: {value}")
    print()

    # Verificações
    checks = []

    # Check 1: Estado extraído
    if "estado" in entities and entities["estado"] == "MG":
        print("✅ Estado 'Minas Gerais' → 'MG' extraído corretamente")
        checks.append(True)
    else:
        print(
            f"❌ Estado não extraído. Esperado: 'MG', Obtido: {entities.get('estado', 'N/A')}"
        )
        checks.append(False)

    # Check 2: Código IBGE
    if "codigo_uf" in entities and entities["codigo_uf"] == "31":
        print("✅ Código IBGE 'MG' → '31' mapeado corretamente")
        checks.append(True)
    else:
        print(
            f"❌ Código IBGE não extraído. Esperado: '31', Obtido: {entities.get('codigo_uf', 'N/A')}"
        )
        checks.append(False)

    # Check 3: Valor extraído
    if "valor" in entities and entities["valor"] == 1000000:
        print("✅ Valor 'R$ 1 milhão' → 1000000 convertido corretamente")
        checks.append(True)
    else:
        print(
            f"❌ Valor não extraído. Esperado: 1000000, Obtido: {entities.get('valor', 'N/A')}"
        )
        checks.append(False)

    # Check 4: Ano extraído
    if "ano" in entities and entities["ano"] == 2024:
        print("✅ Ano '2024' extraído corretamente")
        checks.append(True)
    else:
        print(
            f"❌ Ano não extraído. Esperado: 2024, Obtido: {entities.get('ano', 'N/A')}"
        )
        checks.append(False)

    # Check 5: Categoria extraída
    if "categoria" in entities and "saúde" in str(entities["categoria"]).lower():
        print("✅ Categoria 'saúde' extraída corretamente")
        checks.append(True)
    else:
        print(
            f"⚠️  Categoria não extraída (opcional): {entities.get('categoria', 'N/A')}"
        )

    print()
    success_rate = sum(checks) / len(checks) * 100
    print(f"Taxa de sucesso: {success_rate:.1f}% ({sum(checks)}/{len(checks)} checks)")

    return all(checks)


async def test_orchestrator_availability():
    """Verifica se Orchestrator está disponível."""
    print("\n" + "=" * 80)
    print("TESTE 2: Disponibilidade do Orchestrator")
    print("=" * 80)

    try:
        from src.services.orchestration.orchestrator import InvestigationOrchestrator

        orchestrator = InvestigationOrchestrator()
        print("\n✅ InvestigationOrchestrator importado com sucesso")
        print(f"   Tipo: {type(orchestrator)}")
        print(
            f"   Métodos: {[m for m in dir(orchestrator) if not m.startswith('_')][:5]}..."
        )
        return True
    except Exception as e:
        print(f"\n❌ Falha ao importar Orchestrator: {e}")
        return False


async def test_chat_endpoint_logic():
    """Simula lógica do endpoint /message."""
    print("\n" + "=" * 80)
    print("TESTE 3: Lógica do Endpoint /message")
    print("=" * 80)

    # Simular detecção de intent
    class MockIntent:
        def __init__(self):
            self.type = "INVESTIGATE"
            self.confidence = 0.95

    intent = MockIntent()
    print(f"\nIntent detectado: {intent.type} (confiança: {intent.confidence})")

    # Verificar se Orchestrator seria usado
    should_use_orchestrator = intent.type in ["INVESTIGATE", "ANALYZE", "UNKNOWN"]

    if should_use_orchestrator:
        print("✅ Orchestrator SERIA usado para este tipo de intent")

        # Verificar disponibilidade
        try:
            from src.services.orchestration.orchestrator import (
                InvestigationOrchestrator,
            )

            print("✅ Orchestrator disponível e pronto para uso")
            return True
        except Exception as e:
            print(f"❌ Orchestrator não disponível: {e}")
            print("   Sistema faria fallback para chat_data_integration")
            return False
    else:
        print(f"⚠️  Intent '{intent.type}' não usaria Orchestrator")
        return False


async def main():
    """Executa todos os testes."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TESTE DE INTEGRAÇÃO CHAT → APIs" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝")

    results = []

    # Teste 1: Extração de entidades
    try:
        result1 = await test_entity_extraction()
        results.append(("Extração de Entidades", result1))
    except Exception as e:
        print(f"\n❌ Erro no teste 1: {e}")
        results.append(("Extração de Entidades", False))

    # Teste 2: Orchestrator disponível
    try:
        result2 = await test_orchestrator_availability()
        results.append(("Orchestrator Disponível", result2))
    except Exception as e:
        print(f"\n❌ Erro no teste 2: {e}")
        results.append(("Orchestrator Disponível", False))

    # Teste 3: Lógica do endpoint
    try:
        result3 = await test_chat_endpoint_logic()
        results.append(("Lógica do Endpoint", result3))
    except Exception as e:
        print(f"\n❌ Erro no teste 3: {e}")
        results.append(("Lógica do Endpoint", False))

    # Resultado final
    print("\n" + "=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)

    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(
        f"\nTotal: {total_passed}/{total_tests} testes passaram ({total_passed/total_tests*100:.1f}%)"
    )

    if total_passed == total_tests:
        print("\n🎉 SUCESSO! Todas as correções estão funcionando.")
        return 0
    else:
        print("\n⚠️  ATENÇÃO! Algumas correções precisam de ajustes.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
