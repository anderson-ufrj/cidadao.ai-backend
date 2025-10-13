#!/usr/bin/env python3
"""
Teste do endpoint simples de chat com Maritaca AI
"""

import time

import requests

# URL do backend no HuggingFace Spaces
BASE_URL = "https://neural-thinker-cidadao-ai-backend.hf.space"


def test_chat_simple():
    """Testa o novo endpoint simples de chat"""
    endpoint = f"{BASE_URL}/api/v1/chat/simple"

    print("🧪 Testando endpoint /api/v1/chat/simple")
    print("=" * 50)

    # Primeiro, verifica o status
    status_endpoint = f"{BASE_URL}/api/v1/chat/simple/status"
    try:
        response = requests.get(status_endpoint)
        if response.status_code == 200:
            status = response.json()
            print("📊 Status do Chat:")
            print(f"   Maritaca disponível: {status.get('maritaca_available', False)}")
            print(f"   API Key configurada: {status.get('api_key_configured', False)}")
            print()
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")

    # Mensagens de teste
    test_messages = [
        "Olá, como você está?",
        "O que é o Cidadão.AI?",
        "Como posso investigar contratos públicos?",
        "Me ajuda a entender o portal da transparência",
        "Quero analisar gastos com saúde em 2024",
    ]

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    session_id = f"test-session-{int(time.time())}"

    for i, message in enumerate(test_messages, 1):
        print(f"\n💬 Teste {i}: {message}")

        payload = {"message": message, "session_id": session_id}

        try:
            start_time = time.time()
            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=30
            )
            elapsed = time.time() - start_time

            print(f"   ⏱️ Tempo de resposta: {elapsed:.2f}s")
            print(f"   📡 Status HTTP: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("   ✅ Resposta recebida!")
                print(f"   🤖 Modelo usado: {data.get('model_used', 'N/A')}")
                print(f"   💬 Resposta: {data.get('message', '')[:150]}...")

                # Verifica se está usando Maritaca
                if data.get("model_used") != "fallback":
                    print(f"   🎉 Usando Maritaca AI! Modelo: {data.get('model_used')}")
            else:
                print(f"   ❌ Erro: {response.text[:200]}")

        except requests.exceptions.Timeout:
            print("   ⏱️ Timeout - demorou mais de 30 segundos")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

        # Pequena pausa entre requisições
        if i < len(test_messages):
            time.sleep(1)

    print("\n" + "=" * 50)
    print("✅ Teste concluído!")
    print("\n💡 Dica: Para usar no frontend, faça requisições POST para:")
    print(f"   {endpoint}")
    print('   Com body: {"message": "sua mensagem", "session_id": "opcional"}')


if __name__ == "__main__":
    test_chat_simple()
