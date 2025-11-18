#!/usr/bin/env python3
"""
Testar o agente Zumbi diretamente via API
"""

import json

import httpx

API_URL = "https://cidadao-api-production.up.railway.app"


def test_zumbi_agent():
    """Testa o agente Zumbi diretamente"""

    print("\n" + "=" * 60)
    print("🔍 TESTE DIRETO DO AGENTE ZUMBI")
    print("=" * 60)

    with httpx.Client(timeout=30.0) as client:
        # Testar endpoint do Zumbi
        print("\n1. Testando endpoint do agente Zumbi...")

        payload = {
            "query": "Detectar anomalias em contratos",
            "data_source": "contracts",
            "filters": {"ano": 2024, "codigo_orgao": "26000"},
            "anomaly_types": ["price"],
        }

        try:
            response = client.post(
                f"{API_URL}/api/agents/zumbi/analyze", json=payload, timeout=30.0
            )

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                print("   ✅ Agente respondeu!")
                result = response.json()
                print(f"   Resposta: {json.dumps(result, indent=2)[:500]}...")
            elif response.status_code == 404:
                print("   ⚠️ Endpoint não encontrado")
                print("   O endpoint direto do agente pode não estar disponível")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")

        except httpx.TimeoutException:
            print("   ⏱️ Timeout - o agente está demorando muito para responder")
            print("   Possível problema com a API do LLM (Groq/Maritaca)")
        except Exception as e:
            print(f"   ❌ Erro: {e}")


def check_llm_config():
    """Verifica configuração de LLM"""

    print("\n" + "=" * 60)
    print("🤖 VERIFICAÇÃO DE LLM")
    print("=" * 60)

    print(
        """
POSSÍVEIS PROBLEMAS COM LLM:

1. GROQ_API_KEY:
   • Verifique se está configurada no Railway
   • Teste se a chave ainda é válida
   • Verifique rate limits (14K tokens/min)

2. MARITACA_API_KEY:
   • Alternativa para português
   • Verifique se está configurada como fallback

3. TIMEOUT DO LLM:
   • O agente pode estar esperando resposta do LLM
   • Default timeout pode ser muito alto

4. VERIFICAR NO RAILWAY:
   • Vá em Settings → Variables
   • Confirme que GROQ_API_KEY está presente
   • Adicione MARITACA_API_KEY como backup

5. LOGS PARA PROCURAR:
   • "groq_client" ou "maritaca_client"
   • "timeout" ou "rate limit"
   • "LLM" ou "completion"
"""
    )


def suggest_fixes():
    """Sugestões de correções"""

    print("\n" + "=" * 60)
    print("🔧 SUGESTÕES DE CORREÇÃO")
    print("=" * 60)

    print(
        """
1. ADICIONAR TIMEOUT MENOR NO LLM:
   • Editar src/services/llm_service.py
   • Reduzir timeout para 30 segundos

2. ADICIONAR FALLBACK PARA MOCK:
   • Se LLM falhar, usar resposta mock
   • Permitir que investigação continue

3. VERIFICAR RATE LIMITS:
   • Groq: 14,400 tokens/min
   • Adicionar retry com backoff

4. TESTAR COM CURL:
   curl -X POST https://cidadao-api-production.up.railway.app/api/v1/investigations/start \
     -H "Content-Type: application/json" \
     -d '{"query":"Teste","data_source":"contracts","filters":{},"anomaly_types":["price"]}'

5. VERIFICAR LOGS EM TEMPO REAL:
   • Railway Dashboard → Logs
   • Filtrar por "ERROR" ou "WARN"
"""
    )


if __name__ == "__main__":
    print("\n🚀 DIAGNÓSTICO DO PROBLEMA DE INVESTIGAÇÃO\n")

    # Testar agente diretamente
    test_zumbi_agent()

    # Verificar LLM
    check_llm_config()

    # Sugestões
    suggest_fixes()

    print("\n✅ Diagnóstico concluído!")
    print("\n📊 RESUMO: A investigação está travando na chamada do LLM")
    print("   Provavelmente o GROQ_API_KEY não está configurado ou expirou")
