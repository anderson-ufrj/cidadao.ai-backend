import pytest

#!/usr/bin/env python3
"""
🧪 Teste de Comunicação Backend ↔ Models
Verifica se os repositórios estão conversando via API
"""

import asyncio
import os
import sys
from datetime import datetime

import httpx

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.tools.models_client import ModelsClient

# Test configuration
MODELS_API_URL = "https://neural-thinker-cidadao-ai-models.hf.space"
BACKEND_API_URL = "https://neural-thinker-cidadao-ai-backend.hf.space"


@pytest.mark.asyncio
async def test_models_api_direct():
    """🔍 TESTE 1: Acesso direto à API de Modelos"""
    print("=" * 60)
    print("🔍 TESTE 1: MODELS API - ACESSO DIRETO")
    print("=" * 60)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test root endpoint
            print(f"📡 Testando: {MODELS_API_URL}")
            response = await client.get(f"{MODELS_API_URL}/")

            if response.status_code == 200:
                data = response.json()
                print("✅ Models API está ONLINE!")
                print(f"   📊 API: {data.get('api', 'N/A')}")
                print(f"   🔢 Versão: {data.get('version', 'N/A')}")
                print(f"   📋 Status: {data.get('status', 'N/A')}")
                print(f"   🔗 Endpoints: {list(data.get('endpoints', {}).keys())}")
                return True
            else:
                print(f"❌ Models API retornou status: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Erro ao conectar Models API: {str(e)}")
        return False


@pytest.mark.asyncio
async def test_models_health():
    """🏥 TESTE 2: Health check da API de Modelos"""
    print("\n" + "=" * 60)
    print("🏥 TESTE 2: MODELS API - HEALTH CHECK")
    print("=" * 60)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{MODELS_API_URL}/health")

            if response.status_code == 200:
                data = response.json()
                print("✅ Health check OK!")
                print(f"   📊 Status: {data.get('status', 'N/A')}")
                print(f"   🤖 Modelos carregados: {data.get('models_loaded', 'N/A')}")
                return True
            else:
                print(f"❌ Health check falhou: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Erro no health check: {str(e)}")
        return False


@pytest.mark.asyncio
async def test_backend_to_models():
    """🔄 TESTE 3: Backend chamando Models via Client"""
    print("\n" + "=" * 60)
    print("🔄 TESTE 3: BACKEND → MODELS VIA CLIENT")
    print("=" * 60)

    try:
        # Initialize client with explicit URL
        async with ModelsClient(base_url=MODELS_API_URL) as client:

            # Test anomaly detection
            print("🧠 Testando detecção de anomalias...")

            # Sample data for testing
            test_data = {
                "transaction_amount": 150000.00,
                "vendor_name": "Tech Solutions LTDA",
                "contract_type": "informática",
                "transaction_date": "2024-08-18",
            }

            result = await client.detect_anomaly(test_data)

            if result:
                print("✅ Comunicação Backend → Models OK!")
                print(f"   🎯 Resultado: {result}")
                return True
            else:
                print("❌ Nenhum resultado retornado")
                return False

    except Exception as e:
        print(f"❌ Erro na comunicação: {str(e)}")
        return False


@pytest.mark.asyncio
async def test_models_specific_endpoints():
    """🎯 TESTE 4: Endpoints específicos de modelos"""
    print("\n" + "=" * 60)
    print("🎯 TESTE 4: ENDPOINTS ESPECÍFICOS DE MODELOS")
    print("=" * 60)

    endpoints_to_test = [
        "/models/anomaly/detect",
        "/models/pattern/analyze",
        "/models/spectral/analyze",
    ]

    results = {}

    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints_to_test:
            try:
                url = f"{MODELS_API_URL}{endpoint}"
                print(f"📡 Testando: {endpoint}")

                # Sample request data
                test_payload = {"data": [1, 2, 3, 4, 5], "params": {"threshold": 0.8}}

                response = await client.post(url, json=test_payload)

                if response.status_code == 200:
                    print(f"   ✅ {endpoint} - OK")
                    results[endpoint] = "OK"
                elif response.status_code == 422:
                    print(f"   ⚠️ {endpoint} - Schema validation (normal)")
                    results[endpoint] = "Schema OK"
                else:
                    print(f"   ❌ {endpoint} - Status: {response.status_code}")
                    results[endpoint] = f"Error: {response.status_code}"

            except Exception as e:
                print(f"   ❌ {endpoint} - Erro: {str(e)}")
                results[endpoint] = f"Exception: {str(e)}"

    return results


@pytest.mark.asyncio
async def test_backend_api_integration():
    """🏛️ TESTE 5: Backend API usando Models internamente"""
    print("\n" + "=" * 60)
    print("🏛️ TESTE 5: BACKEND API - INTEGRAÇÃO COM MODELS")
    print("=" * 60)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test investigation endpoint (should use models internally)
            print("🔍 Testando investigação (usa models internamente)...")

            payload = {
                "query": "Analisar contratos de informática com valores suspeitos",
                "data_source": "contracts",
                "max_results": 10,
            }

            response = await client.post(
                f"{BACKEND_API_URL}/api/agents/zumbi/investigate", json=payload
            )

            if response.status_code == 200:
                data = response.json()
                print("✅ Backend API funcionando!")
                print(f"   🔍 Status: {data.get('status', 'N/A')}")
                print(f"   📊 Anomalias: {data.get('anomalies_found', 'N/A')}")
                print(f"   ⏱️ Tempo: {data.get('processing_time_ms', 'N/A')}ms")
                return True
            else:
                print(f"❌ Backend API erro: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Erro no Backend API: {str(e)}")
        return False


async def run_communication_tests():
    """🚀 Executar todos os testes de comunicação"""
    print("🧪 TESTE DE COMUNICAÇÃO CIDADÃO.AI BACKEND ↔ MODELS")
    print("🕐 Iniciado em:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()

    results = {
        "models_api_direct": await test_models_api_direct(),
        "models_health": await test_models_health(),
        "backend_to_models": await test_backend_to_models(),
        "models_endpoints": await test_models_specific_endpoints(),
        "backend_integration": await test_backend_api_integration(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(
        1
        for v in results.values()
        if v is True
        or (isinstance(v, dict) and any("OK" in str(val) for val in v.values()))
    )

    for test_name, result in results.items():
        status = (
            "✅ PASSOU"
            if result is True
            else "📊 DETALHES" if isinstance(result, dict) else "❌ FALHOU"
        )
        print(f"   {test_name}: {status}")

        if isinstance(result, dict):
            for endpoint, endpoint_result in result.items():
                emoji = "✅" if "OK" in str(endpoint_result) else "❌"
                print(f"     {emoji} {endpoint}: {endpoint_result}")

    print(f"\n🎯 RESULTADO GERAL: {passed_tests}/{total_tests} testes funcionais")

    if passed_tests == total_tests:
        print("🎉 COMUNICAÇÃO BACKEND ↔ MODELS TOTALMENTE FUNCIONAL!")
    elif passed_tests > 0:
        print("⚠️ COMUNICAÇÃO PARCIALMENTE FUNCIONAL - Verificar issues")
    else:
        print("❌ COMUNICAÇÃO NÃO FUNCIONAL - Verificar deployment")

    return results


if __name__ == "__main__":
    asyncio.run(run_communication_tests())
