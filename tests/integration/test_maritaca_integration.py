#!/usr/bin/env python3
"""
Script para testar a integração Maritaca AI no Cidadão.AI
"""

from datetime import datetime

import requests

# URL do backend no HuggingFace Spaces
BASE_URL = "https://neural-thinker-cidadao-ai-backend.hf.space"


def test_health():
    """Testa se a API está online"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False


def test_chat_endpoint():
    """Testa o endpoint de chat com a Maritaca AI"""
    endpoint = f"{BASE_URL}/api/v1/chat/message"

    # Mensagens de teste
    test_messages = [
        {"message": "Olá, tudo bem?", "expected_agent": "drummond"},
        {
            "message": "Quero investigar contratos de saúde em São Paulo",
            "expected_agent": "abaporu",
        },
        {
            "message": "Me explique como funciona o portal da transparência",
            "expected_agent": "drummond",
        },
    ]

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    for test in test_messages:
        print(f"\n📤 Testando: '{test['message']}'")
        print(f"   Agente esperado: {test['expected_agent']}")

        payload = {
            "message": test["message"],
            "session_id": f"test-{datetime.now().timestamp()}",
        }

        try:
            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=30
            )

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("   ✅ Resposta recebida!")
                print(f"   Agente: {data.get('agent_name', 'N/A')}")
                print(f"   Mensagem: {data.get('message', 'N/A')[:100]}...")
                print(f"   Confiança: {data.get('confidence', 'N/A')}")

                # Verifica se está usando Maritaca
                if "drummond" in data.get("agent_id", "").lower():
                    print("   🤖 Drummond ativado (deve estar usando Maritaca AI)")

            elif response.status_code == 422:
                print(f"   ❌ Erro de validação: {response.json()}")
            else:
                print(f"   ❌ Erro: {response.text[:200]}")

        except requests.exceptions.Timeout:
            print("   ⏱️ Timeout - a requisição demorou mais de 30 segundos")
        except Exception as e:
            print(f"   ❌ Erro na requisição: {e}")


def test_api_docs():
    """Verifica se a documentação da API está acessível"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"\n📚 API Docs: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Documentação disponível em: {BASE_URL}/docs")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Docs Error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testando integração Maritaca AI no Cidadão.AI")
    print(f"🌐 Backend URL: {BASE_URL}")
    print("=" * 50)

    # Testa health check
    if test_health():
        # Testa documentação
        test_api_docs()

        # Testa endpoint de chat
        test_chat_endpoint()
    else:
        print(
            "\n❌ API não está respondendo. Verifique se o HuggingFace Spaces está online."
        )

    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")
