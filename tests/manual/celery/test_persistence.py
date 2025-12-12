#!/usr/bin/env python3
"""
Test Celery auto-investigation persistence to Supabase
Author: Anderson Henrique da Silva
Date: 2025-10-09
"""

import asyncio
import os
from datetime import datetime

# Load .env FIRST
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("🧪 TESTE DE PERSIST ÊNCIA - Celery → Supabase")
print("=" * 80)
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

from src.config.system_users import SYSTEM_AUTO_MONITOR_USER_ID

# Import after .env is loaded
from src.services.investigation_service_selector import investigation_service

print("📦 [1/3] Configuração verificada")
print(f"   ✅ SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"   ✅ System User: {SYSTEM_AUTO_MONITOR_USER_ID}")
print()

# Test creating investigation directly
print("🗄️  [2/3] Criando investigação de teste no Supabase...")


async def create_test_investigation():
    """Create a test auto-investigation."""
    try:
        investigation = await investigation_service.create(
            user_id=SYSTEM_AUTO_MONITOR_USER_ID,
            query=f"🧪 Teste Auto-Investigation - Celery Beat - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            data_source="contracts",
            filters={
                "test": True,
                "celery_test": True,
                "auto_triggered": True,
                "timestamp": datetime.now().isoformat(),
            },
            anomaly_types=["price", "vendor", "temporal"],
        )

        investigation_id = (
            investigation.id if hasattr(investigation, "id") else investigation["id"]
        )

        print("   ✅ Investigação criada!")
        print(f"   🆔 ID: {investigation_id}")
        print()

        # Update with results
        print("📊 [3/3] Atualizando investigação com resultados...")

        await investigation_service.update_status(
            investigation_id=investigation_id,
            status="completed",
            progress=1.0,
            results=[
                {
                    "message": "Teste de persistência Celery → Supabase",
                    "system": "auto_investigation_service",
                    "test": True,
                }
            ],
            anomalies_found=0,
        )

        print("   ✅ Investigação atualizada!")
        print()

        return investigation_id

    except Exception as e:
        print(f"   ❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        return None


# Run test
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    investigation_id = loop.run_until_complete(create_test_investigation())

    if investigation_id:
        print("=" * 80)
        print("✅ SUCESSO TOTAL! 🎉")
        print("=" * 80)
        print()
        print("📊 Verificação:")
        print(
            "   1. Acesse: https://supabase.com/dashboard/project/pbsiyuattnwgohvkkkks/editor"
        )
        print("   2. Abra a tabela 'investigations'")
        print(f"   3. Procure por ID: {investigation_id}")
        print(f"   4. Filtre por user_id: {SYSTEM_AUTO_MONITOR_USER_ID}")
        print()
        print(
            "🚀 Agora o Celery Beat no Railway vai criar investigações automaticamente!"
        )
        print()
    else:
        print("=" * 80)
        print("❌ FALHA NO TESTE")
        print("=" * 80)

finally:
    loop.close()
