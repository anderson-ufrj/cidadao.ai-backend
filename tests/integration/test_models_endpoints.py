#!/usr/bin/env python3
"""
🧪 Teste dos Endpoints da Models API
Verifica quando os endpoints ML estão disponíveis
"""

import asyncio
from datetime import datetime

import httpx

# Models API URL
MODELS_URL = "https://neural-thinker-cidadao-ai-models.hf.space"


async def test_endpoints():
    """🔍 Testa todos os endpoints da Models API"""
    print("🧪 TESTE DOS ENDPOINTS DA MODELS API")
    print("=" * 50)
    print(f"🔗 Base URL: {MODELS_URL}")
    print(f"🕐 Teste iniciado: {datetime.now().strftime('%H:%M:%S')}")
    print()

    async with httpx.AsyncClient(timeout=30.0) as client:

        # 1. Health Check
        print("1️⃣ HEALTH CHECK")
        try:
            response = await client.get(f"{MODELS_URL}/health")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Models loaded: {data.get('models_loaded')}")
            print(f"   Message: {data.get('message')}")

            if data.get("models_loaded") == True:
                print("   ✅ Models API está COMPLETA!")
            else:
                print("   ⚠️ Models API em modo fallback")
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")

        # 2. Documentação
        print("\n2️⃣ DOCUMENTAÇÃO")
        print(f"   📚 Swagger UI: {MODELS_URL}/docs")
        print(f"   📋 OpenAPI JSON: {MODELS_URL}/openapi.json")

        # 3. Endpoints ML
        print("\n3️⃣ ENDPOINTS DE ML")

        # Anomaly Detection
        print("\n   🔍 DETECÇÃO DE ANOMALIAS")
        print(f"   POST {MODELS_URL}/v1/detect-anomalies")
        try:
            test_data = {
                "contracts": [
                    {
                        "id": "TEST-001",
                        "vendor": "Empresa Teste LTDA",
                        "amount": 50000.00,
                        "date": "2025-08-18",
                        "category": "Serviços de TI",
                    }
                ],
                "threshold": 0.7,
            }

            response = await client.post(
                f"{MODELS_URL}/v1/detect-anomalies", json=test_data
            )

            if response.status_code == 200:
                result = response.json()
                print("   ✅ Endpoint funcional!")
                print(
                    f"   📊 Anomalias encontradas: {result.get('anomalies_found', 0)}"
                )
            elif response.status_code == 404:
                print("   ❌ Endpoint não encontrado (Models em fallback)")
            else:
                print(f"   ⚠️ Status: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:50]}...")

        # Pattern Analysis
        print("\n   📊 ANÁLISE DE PADRÕES")
        print(f"   POST {MODELS_URL}/v1/analyze-patterns")
        try:
            test_data = {
                "data": {
                    "time_series": [100, 120, 90, 150, 200, 180],
                    "categories": ["A", "B", "A", "C", "B", "A"],
                },
                "analysis_type": "temporal",
            }

            response = await client.post(
                f"{MODELS_URL}/v1/analyze-patterns", json=test_data
            )

            if response.status_code == 200:
                result = response.json()
                print("   ✅ Endpoint funcional!")
                print(f"   📈 Padrões encontrados: {result.get('pattern_count', 0)}")
            elif response.status_code == 404:
                print("   ❌ Endpoint não encontrado (Models em fallback)")
            else:
                print(f"   ⚠️ Status: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:50]}...")

        # Spectral Analysis
        print("\n   🌊 ANÁLISE ESPECTRAL")
        print(f"   POST {MODELS_URL}/v1/analyze-spectral")
        try:
            test_data = {
                "time_series": [1, 2, 3, 2, 1, 2, 3, 2, 1],
                "sampling_rate": 1.0,
            }

            response = await client.post(
                f"{MODELS_URL}/v1/analyze-spectral", json=test_data
            )

            if response.status_code == 200:
                result = response.json()
                print("   ✅ Endpoint funcional!")
                print(
                    f"   🎵 Frequência dominante: {result.get('dominant_frequency', 'N/A')}"
                )
            elif response.status_code == 404:
                print("   ❌ Endpoint não encontrado (Models em fallback)")
            else:
                print(f"   ⚠️ Status: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:50]}...")

    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")


if __name__ == "__main__":
    asyncio.run(test_endpoints())
