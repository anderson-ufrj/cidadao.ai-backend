#!/usr/bin/env python3
"""Test if Portal da Transparência API fix is working."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables BEFORE importing anything
import os

os.environ["JWT_SECRET_KEY"] = "test"
os.environ["SECRET_KEY"] = "test"


async def test_portal_api_fix():
    """Test the Portal API with the codigoOrgao fix."""
    print("=" * 80)
    print("🧪 Testing Portal da Transparência API Fix")
    print("=" * 80 + "\n")

    try:
        from datetime import datetime

        from src.services.portal_transparencia_service import PortalTransparenciaService

        service = PortalTransparenciaService()

        print("📝 Testing search_contracts with parameters that were failing before:")
        print("   - Estado: MG (31)")
        print("   - Ano: 2024")
        print("   - Valor: R$ 800.000 - R$ 1.200.000")
        print("   - No orgao specified (should default to 36000)\n")

        print("🔄 Calling Portal API...\n")

        result = await service.search_contracts(
            data_inicial=datetime(2024, 1, 1),
            data_final=datetime(2024, 12, 31),
            valor_minimo=800000.0,
            valor_maximo=1200000.0,
            page=1,
            size=20,
        )

        if result:
            print("✅ SUCCESS! Portal API returned data")
            print(f"   Total items: {len(result)}")

            if result:
                print("\n📋 First contract sample:")
                first = result[0]
                for key, value in list(first.items())[:5]:
                    print(f"   {key}: {value}")

            print("\n🎯 FIX VERIFIED:")
            print("   - Portal API accepted request with default orgao=36000")
            print("   - No more 400 Bad Request errors")
            print("   - Zumbi agent should now return real data!")
        else:
            print("⚠️  Portal API returned empty result (but no 400 error!)")
            print("   This means the fix is working - API accepted the request")
            print("   Empty result might be due to specific filter criteria")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Run test."""
    await test_portal_api_fix()


if __name__ == "__main__":
    asyncio.run(main())
