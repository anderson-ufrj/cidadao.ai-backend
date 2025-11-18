#!/usr/bin/env python3
"""
Teste simplificado para investigação
"""

from datetime import datetime

import httpx

# URLs para teste
PRODUCTION_URL = "https://cidadao-api-production.up.railway.app"
LOCAL_URL = "http://localhost:8000"


def test_investigation(api_url, environment="Production"):
    """Teste simples de investigação"""

    print(f"\n{'='*60}")
    print(f"🔍 TESTANDO {environment.upper()}")
    print(f"📡 URL: {api_url}")
    print(f"{'='*60}")

    with httpx.Client(timeout=30.0) as client:
        # 1. Verificar saúde
        print("\n1. Verificando saúde...")
        try:
            health = client.get(f"{api_url}/health/")
            print(f"   Status: {health.status_code}")
            if health.status_code == 200:
                print("   ✅ API saudável")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return

        # 2. Criar investigação mínima
        print("\n2. Criando investigação simples...")
        investigation_data = {
            "query": f"Teste simples {datetime.now().strftime('%H:%M:%S')}",
            "data_source": "contracts",
            "filters": {},
            "anomaly_types": ["price"],
        }

        try:
            response = client.post(
                f"{api_url}/api/v1/investigations/start", json=investigation_data
            )
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                investigation_id = data.get("investigation_id")
                print("   ✅ Investigação criada")
                print(f"   ID: {investigation_id}")
                print(f"   Status inicial: {data.get('status')}")

                # 3. Verificar status após 5 segundos
                print("\n3. Aguardando 5 segundos...")
                import time

                time.sleep(5)

                print("\n4. Verificando status...")
                status_response = client.get(
                    f"{api_url}/api/v1/investigations/{investigation_id}/status"
                )

                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"   Status: {status.get('status')}")
                    print(f"   Progresso: {status.get('progress', 0)*100:.0f}%")
                    print(f"   Fase: {status.get('current_phase')}")

                    # Se ainda está rodando, esperar mais
                    if status.get("status") == "running":
                        print("\n5. Aguardando mais 10 segundos...")
                        time.sleep(10)

                        status_response = client.get(
                            f"{api_url}/api/v1/investigations/{investigation_id}/status"
                        )
                        if status_response.status_code == 200:
                            status = status_response.json()
                            print(f"   Status atualizado: {status.get('status')}")
                            print(f"   Progresso: {status.get('progress', 0)*100:.0f}%")
                            print(f"   Fase: {status.get('current_phase')}")
                else:
                    print(
                        f"   ❌ Erro ao verificar status: {status_response.status_code}"
                    )

            else:
                print(f"   ❌ Erro: {response.status_code}")
                print(f"   Resposta: {response.text}")

        except Exception as e:
            print(f"   ❌ Erro: {e}")


def check_logs():
    """Sugestões para verificar os logs"""

    print(f"\n{'='*60}")
    print("📋 PRÓXIMOS PASSOS PARA DIAGNÓSTICO")
    print(f"{'='*60}")

    print(
        """
1. VERIFICAR LOGS DO RAILWAY:
   • Acesse o dashboard do Railway
   • Vá para o serviço cidadao-api-production
   • Clique em "Logs" para ver os logs em tempo real
   • Procure por erros relacionados à investigação

2. POSSÍVEIS CAUSAS DO TRAVAMENTO:
   • LLM API (Groq/Maritaca) sem resposta
   • Rate limiting das APIs externas
   • Loop infinito no processamento
   • Erro de conexão com APIs externas
   • Timeout no processamento

3. VERIFICAR VARIÁVEIS DE AMBIENTE NO RAILWAY:
   • GROQ_API_KEY está configurada?
   • MARITACA_API_KEY está configurada?
   • DATABASE_URL está correta?

4. TESTAR LOCALMENTE COM DATABASE_URL DO RAILWAY:
   • Copie a DATABASE_URL do Railway
   • Adicione ao .env local
   • Execute: make run-dev
   • Teste novamente localmente
"""
    )


if __name__ == "__main__":
    print("\n🚀 TESTE SIMPLIFICADO DE INVESTIGAÇÕES\n")

    # Testar produção
    test_investigation(PRODUCTION_URL, "Production Railway")

    # Testar local
    print("\n" + "=" * 60)
    resp = input("\n🔷 Testar também localmente? (s/n): ")
    if resp.lower() == "s":
        test_investigation(LOCAL_URL, "Local")

    # Sugestões
    check_logs()

    print("\n✅ Teste concluído!")
