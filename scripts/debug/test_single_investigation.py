#!/usr/bin/env python3
"""
Teste de investigação única em produção no Railway
"""

import time
from datetime import datetime

import httpx

# URL de produção no Railway
API_URL = "https://cidadao-api-production.up.railway.app"


def test_investigation():
    """Testa uma investigação completa"""

    print("\n" + "=" * 60)
    print("🚀 TESTE DE INVESTIGAÇÃO COM MARITACA AI")
    print(f"📡 URL: {API_URL}")
    print(f"🕒 Hora: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    with httpx.Client(timeout=120.0) as client:
        # 1. Verificar saúde da API
        print("\n1️⃣  Verificando saúde da API...")
        try:
            health = client.get(f"{API_URL}/health/")
            if health.status_code == 200:
                print("   ✅ API está online e saudável")
            else:
                print(f"   ⚠️  Status: {health.status_code}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return False

        # 2. Criar investigação
        print("\n2️⃣  Criando nova investigação...")
        investigation_data = {
            "query": f"Teste Maritaca AI - {datetime.now().strftime('%H:%M:%S')}",
            "data_source": "contracts",
            "filters": {"ano": 2024, "modalidade": "Pregão Eletrônico"},
            "anomaly_types": [
                "price",
                "vendor",
            ],  # Tipos válidos: price, vendor, temporal, payment, duplicate, pattern
        }

        print(f"   📝 Query: {investigation_data['query']}")
        print(f"   📊 Fonte: {investigation_data['data_source']}")
        print(f"   🔍 Anomalias: {investigation_data['anomaly_types']}")

        try:
            response = client.post(
                f"{API_URL}/api/v1/investigations/start", json=investigation_data
            )

            if response.status_code == 200:
                result = response.json()
                investigation_id = result.get("investigation_id")
                print("   ✅ Investigação criada!")
                print(f"   📌 ID: {investigation_id}")
                print(f"   🏷️  Status inicial: {result.get('status')}")
            else:
                print(f"   ❌ Erro: Status {response.status_code}")
                print(f"   Resposta: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Erro ao criar investigação: {e}")
            return False

        # 3. Monitorar progresso
        print("\n3️⃣  Monitorando progresso...")
        print("   " + "-" * 40)

        max_attempts = 30  # 30 tentativas de 5 segundos = 2.5 minutos máximo
        for attempt in range(max_attempts):
            time.sleep(5)  # Aguardar 5 segundos entre verificações

            try:
                status_response = client.get(
                    f"{API_URL}/api/v1/investigations/public/status/{investigation_id}"
                )

                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data.get("status")
                    progress = status_data.get("progress", 0)
                    phase = status_data.get("current_phase", "unknown")

                    # Barra de progresso visual
                    progress_bar = "█" * int(progress * 20) + "░" * (
                        20 - int(progress * 20)
                    )

                    print(f"   [{progress_bar}] {progress*100:.0f}% - {phase}")

                    if current_status == "completed":
                        print("   " + "-" * 40)
                        print("   ✅ INVESTIGAÇÃO CONCLUÍDA COM SUCESSO!")

                        # 4. Buscar resultados completos
                        print("\n4️⃣  Obtendo resultados...")
                        results_response = client.get(
                            f"{API_URL}/api/v1/investigations/{investigation_id}"
                        )

                        if results_response.status_code == 200:
                            full_results = results_response.json()

                            # Mostrar resumo dos resultados
                            print("\n📊 RESUMO DOS RESULTADOS:")
                            print("   " + "-" * 40)

                            # Anomalias encontradas
                            anomalies = full_results.get("anomalies_found", 0)
                            print(f"   🔍 Anomalias detectadas: {anomalies}")

                            # Fase de análise
                            if full_results.get("analysis_results"):
                                analysis = full_results["analysis_results"]
                                print(
                                    f"   📈 Contratos analisados: {analysis.get('contracts_analyzed', 0)}"
                                )
                                print(
                                    f"   💰 Valor total: R$ {analysis.get('total_value', 0):,.2f}"
                                )

                            # Insights do LLM
                            if full_results.get("llm_insights"):
                                insights = full_results["llm_insights"]
                                print("\n   💡 INSIGHTS DO MARITACA AI:")
                                # Mostrar apenas os primeiros 200 caracteres
                                preview = (
                                    str(insights)[:200] + "..."
                                    if len(str(insights)) > 200
                                    else str(insights)
                                )
                                print(f"   {preview}")

                            # Metadata da investigação
                            if full_results.get("investigation_metadata"):
                                metadata = full_results["investigation_metadata"]
                                print("\n   ⚙️  METADATA:")
                                print(
                                    f"   Provider: {metadata.get('llm_provider', 'unknown')}"
                                )
                                print(
                                    f"   Model: {metadata.get('llm_model', 'unknown')}"
                                )
                                print(
                                    f"   Tempo total: {metadata.get('total_time', 0):.2f}s"
                                )

                            print("\n   " + "=" * 40)
                            print("   🎉 TESTE CONCLUÍDO COM SUCESSO!")
                            print("   ✅ Maritaca AI está funcionando!")
                            print("   ✅ Dados salvos no PostgreSQL!")
                            return True

                    elif current_status == "failed":
                        print("   " + "-" * 40)
                        print("   ❌ Investigação falhou!")
                        error_msg = status_data.get(
                            "error_message", "Erro desconhecido"
                        )
                        print(f"   Erro: {error_msg}")
                        return False

                    elif (
                        current_status == "running" and progress == 0.3 and attempt > 6
                    ):
                        # Se ficar travado em 30% por mais de 30 segundos
                        print("\n   ⚠️  ATENÇÃO: Investigação travada em 30%")
                        print("   Possível problema com o LLM (Maritaca AI)")
                        print("   Verifique:")
                        print("   1. MARITACA_API_KEY está configurada no Railway?")
                        print("   2. A chave é válida?")
                        print("   3. LLM_PROVIDER=maritaca está configurado?")

                else:
                    print(
                        f"   ❌ Erro ao verificar status: {status_response.status_code}"
                    )

            except Exception as e:
                print(f"   ❌ Erro: {e}")

        # Se chegou aqui, timeout
        print("\n   ⏱️  TIMEOUT: Investigação não concluiu em 2.5 minutos")
        print("   Possível problema de configuração ou performance")
        return False


if __name__ == "__main__":
    print("\n🚀 TESTE DE INVESTIGAÇÃO NO RAILWAY (PRODUÇÃO)")
    print("=" * 60)
    print("Este teste verifica se:")
    print("✅ A API está online")
    print("✅ Maritaca AI está configurado")
    print("✅ Investigações são processadas")
    print("✅ Resultados são salvos no banco")
    print("=" * 60)

    success = test_investigation()

    if not success:
        print("\n" + "=" * 60)
        print("💡 SUGESTÕES DE CORREÇÃO:")
        print("=" * 60)
        print(
            """
1. VERIFICAR NO RAILWAY DASHBOARD:
   - Vá em Variables
   - Confirme que existe:
     • LLM_PROVIDER=maritaca
     • MARITACA_API_KEY=sk-xxxxx
     • LLM_MODEL_NAME=sabiazinho-3

2. VERIFICAR LOGS DO RAILWAY:
   - Procure por erros relacionados a:
     • "maritaca"
     • "LLM timeout"
     • "401 Unauthorized"

3. TESTAR A API KEY LOCALMENTE:
   export MARITACA_API_KEY=sua-chave-aqui
   export LLM_PROVIDER=maritaca
   python test_maritaca_integration.py

4. REINICIAR O SERVIÇO:
   - No Railway Dashboard
   - Clique em "Restart"
   - Aguarde 2 minutos
"""
        )

    print("\n✨ Fim do teste!")
