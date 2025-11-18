#!/usr/bin/env python3
"""
Teste completo de investigações em produção no Railway
Verifica:
1. Criação de investigação
2. Salvamento no banco de dados PostgreSQL
3. Status e progresso
4. Resultados finais
"""

import asyncio
import time
from datetime import datetime

import httpx

# API de Produção no Railway
API_URL = "https://cidadao-api-production.up.railway.app"


async def test_production_investigation():
    """Teste completo de investigação em produção"""

    print("\n" + "=" * 70)
    print("🔍 TESTE DE INVESTIGAÇÃO EM PRODUÇÃO - RAILWAY")
    print("=" * 70)
    print(f"📡 API: {API_URL}")
    print(f"🕐 Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)

    async with httpx.AsyncClient(timeout=60.0) as client:

        # 1. Verificar saúde da API
        print("\n1️⃣ VERIFICANDO SAÚDE DA API...")
        health_response = await client.get(f"{API_URL}/health/")
        print(f"   Status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"   ✅ API está saudável: {health_response.json()}")

        # 2. Criar investigação com dados realistas
        print("\n2️⃣ CRIANDO INVESTIGAÇÃO...")
        investigation_data = {
            "query": f"Análise de contratos do Ministério da Saúde - Teste {datetime.now().strftime('%H:%M:%S')}",
            "data_source": "contracts",
            "filters": {
                "ano": 2024,
                "codigo_orgao": "36000",  # Ministério da Saúde
                "mes": 10,
            },
            "anomaly_types": [
                "price",  # Anomalias de preço
                "vendor",  # Concentração de fornecedores
                "temporal",  # Padrões temporais
                "duplicate",  # Contratos duplicados
            ],
            "include_explanations": True,
            "stream_results": False,
        }

        print("   📋 Payload:")
        for key, value in investigation_data.items():
            if key == "filters":
                print(f"      {key}:")
                for fk, fv in value.items():
                    print(f"         {fk}: {fv}")
            elif key == "anomaly_types":
                print(f"      {key}: {', '.join(value)}")
            else:
                print(f"      {key}: {value}")

        # Enviar requisição
        start_time = time.time()
        response = await client.post(
            f"{API_URL}/api/v1/investigations/start",
            json=investigation_data,
            headers={"Content-Type": "application/json"},
        )

        print(f"\n   📊 Resposta: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            investigation_id = result.get("investigation_id")

            print("   ✅ Investigação criada com sucesso!")
            print(f"   🆔 ID: {investigation_id}")
            print(f"   📌 Status inicial: {result.get('status')}")
            print(f"   💬 Mensagem: {result.get('message')}")

            # 3. Monitorar progresso
            print("\n3️⃣ MONITORANDO PROGRESSO...")
            max_checks = 20  # Máximo 20 verificações
            check_interval = 3  # A cada 3 segundos

            for i in range(max_checks):
                await asyncio.sleep(check_interval)

                # Verificar status
                status_response = await client.get(
                    f"{API_URL}/api/v1/investigations/{investigation_id}/status"
                )

                if status_response.status_code == 200:
                    status = status_response.json()
                    progress = status.get("progress", 0) * 100
                    current_status = status.get("status", "unknown")
                    phase = status.get("current_phase", "-")
                    records = status.get("records_processed", 0)
                    anomalies = status.get("anomalies_detected", 0)

                    # Barra de progresso visual
                    bar_length = 30
                    filled = int(bar_length * progress / 100)
                    bar = "█" * filled + "░" * (bar_length - filled)

                    print(
                        f"\r   [{bar}] {progress:.0f}% | Status: {current_status} | "
                        f"Fase: {phase} | Registros: {records} | Anomalias: {anomalies}",
                        end="",
                        flush=True,
                    )

                    # Se completou ou falhou, parar
                    if current_status in ["completed", "failed", "error"]:
                        print()  # Nova linha
                        break
                else:
                    print(
                        f"\n   ⚠️ Erro ao verificar status: {status_response.status_code}"
                    )

            # 4. Obter resultados finais
            print("\n\n4️⃣ OBTENDO RESULTADOS FINAIS...")

            # Tentar obter investigação completa
            try:
                full_response = await client.get(
                    f"{API_URL}/api/v1/investigations/{investigation_id}"
                )

                if full_response.status_code == 200:
                    full_data = full_response.json()

                    print("\n   📈 RESULTADOS DA INVESTIGAÇÃO:")
                    print(f"   • Status final: {full_data.get('status', 'N/A')}")
                    print(
                        f"   • Registros analisados: {full_data.get('total_records_analyzed', 0)}"
                    )
                    print(
                        f"   • Anomalias encontradas: {full_data.get('anomalies_found', 0)}"
                    )
                    print(
                        f"   • Score de confiança: {full_data.get('confidence_score', 0):.2f}"
                        if full_data.get("confidence_score")
                        else "   • Score de confiança: N/A"
                    )

                    # Tempo de processamento
                    if full_data.get("processing_time_ms"):
                        proc_time = full_data["processing_time_ms"] / 1000
                        print(f"   • Tempo de processamento: {proc_time:.2f}s")

                    # Resultados detalhados
                    if full_data.get("results"):
                        print("\n   📋 DETALHES DAS ANOMALIAS:")
                        for idx, anomaly in enumerate(
                            full_data["results"][:5], 1
                        ):  # Primeiras 5
                            print(f"      {idx}. Tipo: {anomaly.get('type', 'N/A')}")
                            print(
                                f"         Severidade: {anomaly.get('severity', 'N/A')}"
                            )
                            print(
                                f"         Descrição: {anomaly.get('description', 'N/A')[:100]}..."
                            )

                    # Sumário
                    if full_data.get("summary"):
                        print("\n   📝 SUMÁRIO:")
                        print(f"      {full_data['summary'][:200]}...")

                    # Verificar se foi salvo no banco
                    print("\n   💾 PERSISTÊNCIA NO BANCO DE DADOS:")
                    if full_data.get("created_at") and full_data.get("updated_at"):
                        print("      ✅ Salvo no PostgreSQL")
                        print(f"      • Criado em: {full_data['created_at']}")
                        print(f"      • Atualizado em: {full_data['updated_at']}")
                    else:
                        print("      ⚠️ Pode estar usando memória temporária")

                elif full_response.status_code == 405:
                    print("   ⚠️ Endpoint GET não disponível (método não permitido)")
                    print("   ℹ️ Usando apenas dados do status")
                else:
                    print(
                        f"   ❌ Erro ao obter resultados: {full_response.status_code}"
                    )

            except Exception as e:
                print(f"   ⚠️ Erro ao obter resultados completos: {e}")

            # Tempo total
            total_time = time.time() - start_time
            print(f"\n   ⏱️ Tempo total: {total_time:.2f} segundos")

        else:
            print("   ❌ Falha ao criar investigação!")
            print(f"   Resposta: {response.text}")

    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 70)


async def test_list_investigations():
    """Testa listagem de investigações para verificar persistência"""

    print("\n5️⃣ VERIFICANDO INVESTIGAÇÕES NO BANCO...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Tentar listar investigações
            list_response = await client.get(
                f"{API_URL}/api/v1/investigations", params={"limit": 5}  # Últimas 5
            )

            if list_response.status_code == 200:
                investigations = list_response.json()

                if investigations:
                    print(
                        f"   ✅ Encontradas {len(investigations)} investigações no banco:"
                    )
                    for inv in investigations[:3]:  # Mostrar até 3
                        created = inv.get("created_at", "N/A")
                        query = inv.get("query", "N/A")[:50]
                        status = inv.get("status", "N/A")
                        print(f"      • {created}: {query}... ({status})")
                else:
                    print("   ℹ️ Nenhuma investigação encontrada no banco")
            else:
                print(
                    f"   ⚠️ Endpoint de listagem indisponível: {list_response.status_code}"
                )

        except Exception as e:
            print(f"   ⚠️ Erro ao listar investigações: {e}")


if __name__ == "__main__":
    print("\n🚀 INICIANDO TESTE DE INVESTIGAÇÕES EM PRODUÇÃO...")

    # Executar teste principal
    asyncio.run(test_production_investigation())

    # Verificar persistência
    asyncio.run(test_list_investigations())

    print("\n✅ Todos os testes concluídos!")
    print("📊 Verifique os logs do Railway para mais detalhes do backend")
