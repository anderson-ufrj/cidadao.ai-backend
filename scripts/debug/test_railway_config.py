#!/usr/bin/env python3
"""
Teste de configuração no Railway
"""

import json
from datetime import datetime

import httpx

API_URL = "https://cidadao-api-production.up.railway.app"

print("\n" + "=" * 60)
print("🔧 TESTE DE CONFIGURAÇÃO DO RAILWAY")
print(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
print("=" * 60)

with httpx.Client(timeout=30.0) as client:
    # 1. Teste básico de health
    print("\n1️⃣ Health Check:")
    response = client.get(f"{API_URL}/health/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        health_data = response.json()
        print(f"   Response: {json.dumps(health_data, indent=2)}")

    # 2. Criar investigação mínima
    print("\n2️⃣ Criando investigação mínima (sem filtros):")

    investigation_data = {
        "query": "Teste mínimo",
        "data_source": "contracts",
        "filters": {},
        "anomaly_types": ["price"],
    }

    response = client.post(
        f"{API_URL}/api/v1/investigations/start", json=investigation_data
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        inv_id = result.get("investigation_id")
        print(f"   ✅ ID: {inv_id}")

        # 3. Aguardar 10 segundos
        print("\n3️⃣ Aguardando 10 segundos...")
        import time

        time.sleep(10)

        # 4. Verificar status
        print("\n4️⃣ Verificando status:")
        status_response = client.get(f"{API_URL}/api/v1/investigations/{inv_id}/status")

        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"   Status: {status_data.get('status')}")
            print(f"   Progress: {status_data.get('progress', 0)*100:.0f}%")
            print(f"   Phase: {status_data.get('current_phase')}")

            if status_data.get("status") == "failed":
                print("\n   ❌ INVESTIGAÇÃO FALHOU!")
                print("\n   POSSÍVEIS PROBLEMAS:")
                print("   1. MARITACA_API_KEY inválida ou não configurada")
                print("   2. LLM_PROVIDER não está como 'maritaca'")
                print("   3. Problema de conexão com a API do Maritaca")
                print("   4. Rate limiting ou quota excedida")

    else:
        print(f"   ❌ Erro: {response.status_code}")
        print(f"   Response: {response.text}")

    # 5. Verificar se há algum endpoint de configuração/info
    print("\n5️⃣ Testando endpoint /docs:")
    docs_response = client.get(f"{API_URL}/docs")
    print(f"   Status: {docs_response.status_code}")

print("\n" + "=" * 60)
print("💡 RECOMENDAÇÕES:")
print("=" * 60)
print(
    """
Se a investigação está falhando:

1. VERIFICAR NO RAILWAY:
   - Vá em Settings → Variables
   - Confirme que existe:
     • LLM_PROVIDER=maritaca
     • MARITACA_API_KEY=sk-... (sua chave real)
     • LLM_MODEL_NAME=sabiazinho-4

2. VERIFICAR LOGS NO RAILWAY:
   - Vá em Logs
   - Procure por:
     • "maritaca"
     • "401 Unauthorized"
     • "timeout"
     • "error"

3. TESTAR LOCALMENTE:
   export MARITACA_API_KEY=sua-chave
   export LLM_PROVIDER=maritaca
   python test_maritaca_integration.py

4. REINICIAR SERVIÇO:
   - No Railway Dashboard
   - Clique em Restart
"""
)
