#!/usr/bin/env python3
"""
Test script for public investigation endpoint
Author: Anderson Henrique da Silva
Date: 2025-10-09
"""

from datetime import datetime

import requests

print("=" * 80)
print("🧪 TESTE DO ENDPOINT PÚBLICO - /api/investigations/public/create")
print("=" * 80)
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# API URL (local or Railway)
LOCAL_URL = "http://localhost:8000"
RAILWAY_URL = "https://cidadao-api-production.up.railway.app"

base_url = RAILWAY_URL  # Change to LOCAL_URL for local testing

print(f"🌐 Testing against: {base_url}")
print()

# Test 1: Health check
print("📊 [1/3] Testando health check público...")
try:
    response = requests.get(f"{base_url}/api/v1/investigations/public/health")
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {data.get('status')}")
        print(f"   ✅ System user configured: {data.get('system_user_configured')}")
        print(
            f"   ✅ Investigation service: {data.get('investigation_service_available')}"
        )
        print(f"   ✅ Active investigations: {data.get('active_investigations')}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print()

# Test 2: Create public investigation
print("🚀 [2/3] Criando investigação pública...")
try:
    payload = {
        "query": f"🧪 Teste Endpoint Público - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "data_source": "contracts",
        "filters": {
            "test": True,
            "public_endpoint_test": True,
            "timestamp": datetime.now().isoformat(),
        },
        "anomaly_types": ["price", "vendor", "temporal"],
        "system_name": "test_script",
    }

    response = requests.post(
        f"{base_url}/api/v1/investigations/public/create", json=payload
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        investigation_id = data.get("investigation_id")
        print(f"   ✅ Investigation created!")
        print(f"   🆔 ID: {investigation_id}")
        print(f"   👤 System User: {data.get('system_user_id')}")
        print(f"   📝 Status: {data.get('status')}")
        print(f"   💬 Message: {data.get('message')}")
    else:
        print(f"   ❌ Error: {response.text}")
        investigation_id = None
except Exception as e:
    print(f"   ❌ Exception: {e}")
    investigation_id = None

print()

# Test 3: Verify in Supabase (if investigation was created)
if investigation_id:
    print("🔍 [3/3] Verificação no Supabase...")
    print(
        f"   1. Acesse: https://supabase.com/dashboard/project/pbsiyuattnwgohvkkkks/editor"
    )
    print(f"   2. Abra a tabela 'investigations'")
    print(f"   3. Procure por ID: {investigation_id}")
    print(f"   4. Filtre por system_created: true")
    print()
    print("✅ Endpoint público funcionando!")
else:
    print("⏭️  [3/3] Verificação pulada (investigação não foi criada)")

print()
print("=" * 80)
print("📝 NOTAS DE SEGURANÇA:")
print("=" * 80)
print("⚠️  Este endpoint deve ser protegido em produção:")
print("   • Firewall/IP whitelist")
print("   • API Gateway com rate limiting")
print("   • Monitoramento de uso")
print()
