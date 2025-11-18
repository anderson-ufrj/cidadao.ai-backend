#!/usr/bin/env python3
"""
Teste direto de coleta de dados
"""

from datetime import datetime

import httpx

API_URL = "https://cidadao-api-production.up.railway.app"

print("\n" + "=" * 60)
print("🔍 TESTE DE COLETA DE DADOS")
print(f"📡 URL: {API_URL}")
print(f"🕒 Hora: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 60)

with httpx.Client(timeout=60.0) as client:
    # Testar busca de contratos via PNCP (Portal Nacional de Contratações Públicas)
    print("\n1️⃣  Testando PNCP - Portal Nacional de Contratações...")
    try:
        response = client.get(
            f"{API_URL}/api/v1/federal/pncp/contracts",
            params={"ano": 2024, "pagina": 1, "tamanhoPagina": 5},
        )

        if response.status_code == 200:
            data = response.json()
            print("   ✅ PNCP funcionando!")
            print(f"   📊 Contratos retornados: {data.get('total', 0)}")
            if data.get("data"):
                print(f"   📝 Exemplo: {data['data'][0].get('objeto', 'N/A')[:100]}")
        else:
            print(f"   ❌ Erro: Status {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n" + "=" * 60)
