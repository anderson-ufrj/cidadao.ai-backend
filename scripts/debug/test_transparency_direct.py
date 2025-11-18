#!/usr/bin/env python3
"""
Teste direto da API de transparência
"""

from datetime import datetime

import httpx

API_URL = "https://cidadao-api-production.up.railway.app"

print("\n" + "=" * 60)
print("🔍 TESTE DIRETO DA API DE TRANSPARÊNCIA")
print(f"📡 URL: {API_URL}")
print(f"🕒 Hora: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 60)

with httpx.Client(timeout=60.0) as client:
    # Testar endpoint de contratos
    print("\n1️⃣  Testando /api/v1/transparency/contracts...")
    try:
        response = client.get(
            f"{API_URL}/api/v1/transparency/contracts",
            params={
                "ano": 2024,
                "codigoOrgao": "36000",  # Ministério da Saúde
                "pagina": 1,
            },
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("   ✅ API funcionando!")
            print(f"   📊 Estrutura: {list(data.keys())}")
            if isinstance(data, dict):
                if "data" in data:
                    print(f"   📝 Contratos: {len(data.get('data', []))}")
                if "total" in data:
                    print(f"   📈 Total: {data.get('total')}")
        elif response.status_code == 403:
            print("   ⚠️  403 Forbidden - API key pode ser inválida")
        else:
            print(f"   ❌ Erro: {response.text[:300]}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

    # Testar health check das APIs
    print("\n2️⃣  Testando /api/v1/transparency/health...")
    try:
        response = client.get(f"{API_URL}/api/v1/transparency/health")

        if response.status_code == 200:
            data = response.json()
            print("   ✅ Health check funcionando!")
            print(f"   APIs disponíveis: {list(data.keys())[:5]}")
        else:
            print(f"   ❌ Erro: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

print("\n" + "=" * 60)
