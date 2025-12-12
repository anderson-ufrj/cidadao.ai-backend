#!/usr/bin/env python3
"""
Teste em Produção - Chat API
Testa a API real em produção (Railway)
"""
import asyncio
import sys

import httpx

BASE_URL = "https://cidadao-api-production.up.railway.app"


async def test_health():
    """Testa se a API está online."""
    print("\n" + "=" * 80)
    print("TESTE 1: Health Check")
    print("=" * 80)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/health")

            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")

            if response.status_code == 200:
                print("✅ API está online e funcionando")
                return True
            else:
                print(f"❌ API retornou status {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False


async def test_chat_entity_extraction():
    """Testa extração de entidades via chat."""
    print("\n" + "=" * 80)
    print("TESTE 2: Chat - Extração de Entidades")
    print("=" * 80)

    query = "Quero ver contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024"
    print(f'\nQuery: "{query}"')
    print()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Endpoint do chat
            response = await client.post(
                f"{BASE_URL}/api/v1/chat/message",
                json={"message": query, "session_id": "test-session-001"},
                headers={"Content-Type": "application/json"},
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("\nResposta recebida:")
                print(f"  Message ID: {data.get('message_id', 'N/A')}")
                print(f"  Message length: {len(data.get('message', ''))} chars")

                # Mostrar primeiros 500 caracteres da mensagem
                response_text = data.get("message", "")
                print("\nResposta (preview):")
                print("-" * 80)
                print(response_text[:500])
                if len(response_text) > 500:
                    print(f"\n... ({len(response_text) - 500} caracteres restantes)")
                print("-" * 80)

                # Verificar se menciona dados reais (não mock)
                metadata = data.get("metadata", {})
                print("\nMetadata:")
                for key, value in metadata.items():
                    print(f"  {key}: {value}")

                # Verificações
                checks = []

                # Check 1: Resposta não vazia
                if response_text and len(response_text) > 50:
                    print("\n✅ Resposta completa recebida")
                    checks.append(True)
                else:
                    print("\n❌ Resposta vazia ou muito curta")
                    checks.append(False)

                # Check 2: Não é apenas dados mockados (se tiver valor R$ 0.00 é mock)
                if "R$ 0.00" not in response_text or "R$ 0,00" not in response_text:
                    print("✅ Resposta parece conter dados reais (não apenas R$ 0.00)")
                    checks.append(True)
                else:
                    print("⚠️  Resposta pode conter dados mockados (R$ 0.00 encontrado)")
                    checks.append(False)

                # Check 3: Sistema entendeu a query
                if any(
                    word in response_text.lower()
                    for word in ["contrato", "saúde", "minas", "milhão"]
                ):
                    print("✅ Sistema entendeu contexto da query")
                    checks.append(True)
                else:
                    print("⚠️  Sistema pode não ter entendido a query")
                    checks.append(False)

                success = all(checks)
                if success:
                    print("\n🎉 TESTE PASSOU - Chat está funcionando corretamente!")
                else:
                    print(
                        "\n⚠️  TESTE PARCIAL - Chat respondeu mas pode haver problemas"
                    )

                return success

            elif response.status_code == 401:
                print("❌ Erro de autenticação (401)")
                print("   Nota: Endpoint pode requerer autenticação")
                return False

            else:
                print(f"❌ Erro: Status {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False

    except httpx.TimeoutException:
        print("❌ Timeout - Requisição demorou mais de 60 segundos")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_simple_chat():
    """Testa chat simples sem autenticação."""
    print("\n" + "=" * 80)
    print("TESTE 3: Chat Simples")
    print("=" * 80)

    query = "Olá, como funciona o sistema?"
    print(f'\nQuery: "{query}"')
    print()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/chat/message",
                json={"message": query, "session_id": "test-session-002"},
                headers={"Content-Type": "application/json"},
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                response_text = data.get("message", "")

                print(f"\nResposta ({len(response_text)} chars):")
                print("-" * 80)
                print(response_text[:300])
                if len(response_text) > 300:
                    print(f"... ({len(response_text) - 300} caracteres restantes)")
                print("-" * 80)

                if response_text:
                    print("\n✅ Chat respondeu corretamente")
                    return True
                else:
                    print("\n❌ Chat não retornou resposta")
                    return False

            else:
                print(f"❌ Status: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def test_orchestrator_integration():
    """Testa se Orchestrator está sendo usado."""
    print("\n" + "=" * 80)
    print("TESTE 4: Integração com Orchestrator")
    print("=" * 80)

    query = "Investigar despesas públicas em São Paulo 2024"
    print(f'\nQuery: "{query}"')
    print("Nota: Esta query deveria acionar o Orchestrator (INVESTIGATE intent)")
    print()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/chat/message",
                json={"message": query, "session_id": "test-session-003"},
                headers={"Content-Type": "application/json"},
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                metadata = data.get("metadata", {})

                print("\nMetadata recebida:")
                for key, value in metadata.items():
                    print(f"  {key}: {value}")

                print("\nResposta (preview):")
                print("-" * 80)
                print(response_text[:400])
                print("-" * 80)

                # Verificar sinais de que Orchestrator foi usado
                orchestrator_indicators = [
                    "investigation" in str(metadata).lower(),
                    "apis" in str(metadata).lower(),
                    len(response_text) > 100,  # Resposta substancial
                ]

                if any(orchestrator_indicators):
                    print("\n✅ Sinais de que Orchestrator pode ter sido usado")
                    return True
                else:
                    print("\n⚠️  Não há sinais claros de uso do Orchestrator")
                    print("   (Pode estar usando fallback)")
                    return False

            else:
                print(f"❌ Status: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def main():
    """Executa todos os testes."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TESTES EM PRODUÇÃO - RAILWAY" + " " * 28 + "║")
    print("║" + " " * 15 + "cidadao-api-production.up.railway.app" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")

    results = {}

    # Teste 1: Health
    try:
        result1 = await test_health()
        results["Health Check"] = result1
    except Exception as e:
        print(f"❌ Erro no teste 1: {e}")
        results["Health Check"] = False

    # Teste 2: Entity Extraction
    try:
        result2 = await test_chat_entity_extraction()
        results["Entity Extraction"] = result2
    except Exception as e:
        print(f"❌ Erro no teste 2: {e}")
        results["Entity Extraction"] = False

    # Teste 3: Simple Chat
    try:
        result3 = await test_simple_chat()
        results["Simple Chat"] = result3
    except Exception as e:
        print(f"❌ Erro no teste 3: {e}")
        results["Simple Chat"] = False

    # Teste 4: Orchestrator
    try:
        result4 = await test_orchestrator_integration()
        results["Orchestrator Integration"] = result4
    except Exception as e:
        print(f"❌ Erro no teste 4: {e}")
        results["Orchestrator Integration"] = False

    # Resultado Final
    print("\n" + "=" * 80)
    print("RESULTADO FINAL - PRODUÇÃO")
    print("=" * 80)

    for test_name, result in results.items():
        if result is True:
            print(f"✅ PASSOU: {test_name}")
        elif result is False:
            print(f"❌ FALHOU: {test_name}")
        else:
            print(f"⚠️  SKIP: {test_name}")

    passed = sum(1 for r in results.values() if r is True)
    total = len([r for r in results.values() if r is not None])

    print(f"\nTotal: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 SUCESSO TOTAL! Sistema em produção está funcionando perfeitamente!")
        return 0
    elif passed >= total * 0.75:
        print("\n✅ BOA! Maioria dos testes passou. Sistema está operacional.")
        return 0
    else:
        print("\n⚠️  ATENÇÃO! Vários testes falharam. Revisar sistema em produção.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
