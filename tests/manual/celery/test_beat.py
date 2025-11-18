#!/usr/bin/env python3
"""
Test script for Celery Beat auto-investigations
Author: Anderson Henrique da Silva
Date: 2025-10-09

This script tests the auto-investigation Celery tasks locally.
"""

import asyncio
import os
from datetime import datetime

# IMPORTANT: Load .env BEFORE any project imports
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("🧪 TESTE CELERY BEAT - AUTO INVESTIGATIONS")
print("=" * 80)
print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test 1: Import and verify environment
print("📦 [1/4] Verificando imports e configuração...")
print(f"   ℹ️  SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(
    f"   ℹ️  SUPABASE_SERVICE_ROLE_KEY: {'***' + os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')[-10:] if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'NOT SET'}"
)
try:
    from src.config.system_users import SYSTEM_AUTO_MONITOR_USER_ID
    from src.services.auto_investigation_service import auto_investigation_service

    print(f"   ✅ Imports OK")
    print(f"   ✅ System User ID: {SYSTEM_AUTO_MONITOR_USER_ID}")
except Exception as e:
    print(f"   ❌ Erro nos imports: {e}")
    exit(1)

print()

# Test 2: Test investigation service
print("🗄️  [2/4] Testando Investigation Service...")
try:
    from src.services.investigation_service_selector import investigation_service

    print(f"   ✅ Investigation service carregado")
except Exception as e:
    print(f"   ❌ Erro ao carregar investigation service: {e}")
    exit(1)

print()

# Test 3: Test transparency API (quick check)
print("🌐 [3/4] Testando Portal da Transparência...")
try:
    from datetime import timedelta

    from src.tools.transparency_api import TransparencyAPIClient, TransparencyAPIFilter

    api = TransparencyAPIClient()

    # Quick test with 1 day lookback
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)

    filters = TransparencyAPIFilter(
        dataInicial=start_date.strftime("%d/%m/%Y"),
        dataFinal=end_date.strftime("%d/%m/%Y"),
    )

    print(f"   🔍 Buscando contratos de {start_date.date()} a {end_date.date()}...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        contracts = loop.run_until_complete(api.get_contracts(filters=filters, limit=5))
        print(
            f"   ✅ Portal da Transparência OK - {len(contracts)} contratos encontrados"
        )
    finally:
        loop.close()

except Exception as e:
    print(f"   ⚠️  Portal da Transparência com problemas: {e}")
    print(f"   ℹ️  Isso é esperado - 78% dos endpoints retornam 403")

print()

# Test 4: Execute auto-investigation monitoring
print("🚀 [4/4] Executando auto-investigation (lookback 24h)...")
print()

try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(
            auto_investigation_service.monitor_new_contracts(
                lookback_hours=24, organization_codes=None
            )
        )

        print("=" * 80)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
        print()
        print("📊 RESULTADOS:")
        print(f"   • Tipo: {result.get('monitoring_type')}")
        print(f"   • Lookback: {result.get('lookback_hours')}h")
        print(f"   • Contratos analisados: {result.get('contracts_analyzed')}")
        print(f"   • Suspeitos encontrados: {result.get('suspicious_found')}")
        print(f"   • Investigações criadas: {result.get('investigations_created')}")
        print(f"   • Anomalias detectadas: {result.get('anomalies_detected')}")
        print(f"   • Duração: {result.get('duration_seconds'):.2f}s")
        print()

        if result.get("investigations_created", 0) > 0:
            print("🎉 SUCESSO! Investigações foram criadas no Supabase!")
            print()
            print("🔍 Verifique no Supabase Dashboard:")
            print(
                "   https://supabase.com/dashboard/project/pbsiyuattnwgohvkkkks/editor"
            )
            print()
            print(
                f"   👉 Procure por investigações com user_id: {SYSTEM_AUTO_MONITOR_USER_ID}"
            )
            print(f"   👉 Timestamp: {result.get('timestamp')}")
        else:
            print(
                "ℹ️  Nenhuma investigação criada (nenhum contrato suspeito encontrado)"
            )
            print("   Isso é normal se não houver contratos suspeitos no período.")

        print()
        print("=" * 80)

    finally:
        loop.close()

except Exception as e:
    print("=" * 80)
    print("❌ ERRO NO TESTE!")
    print("=" * 80)
    print(f"Erro: {e}")
    import traceback

    traceback.print_exc()
    exit(1)
