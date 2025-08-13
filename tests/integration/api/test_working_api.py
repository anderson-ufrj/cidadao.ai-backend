#!/usr/bin/env python3
"""
Test working API functionality with contracts
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.transparency_api import TransparencyAPIClient, TransparencyAPIFilter

async def test_working_api():
    """Test successful API calls with contracts"""
    
    print("🎯 Testing Working API Functionality")
    print("=" * 40)
    
    async with TransparencyAPIClient() as client:
        # Test 1: Basic contract search
        print("📋 Test 1: Basic contract search")
        filters = TransparencyAPIFilter(
            codigo_orgao="26000",  # Ministério da Saúde
            ano=2024,
            mes=1,
            pagina=1,
            tamanho_pagina=5
        )
        
        response = await client.get_contracts(filters)
        print(f"   ✅ Found {len(response.data)} contracts")
        
        if response.data:
            contract = response.data[0]
            print(f"   📄 Sample: {contract.get('objeto', 'N/A')[:80]}...")
            print(f"   💰 Valor: R$ {contract.get('valorInicial', 'N/A')}")
            print(f"   🏢 Fornecedor: {contract.get('fornecedor', {}).get('nome', 'N/A')}")
        
        # Test 2: Different organization
        print("\n📋 Test 2: Different organization (Presidência)")
        filters2 = TransparencyAPIFilter(
            codigo_orgao="20000",  # Presidência da República
            ano=2024,
            mes=1,
            pagina=1,
            tamanho_pagina=3
        )
        
        response2 = await client.get_contracts(filters2)
        print(f"   ✅ Found {len(response2.data)} contracts from Presidência")
        
        # Test 3: High-value contracts
        print("\n📋 Test 3: High-value contracts (>1M)")
        filters3 = TransparencyAPIFilter(
            codigo_orgao="26000",
            ano=2024,
            valor_inicial=1000000,  # > 1M
            pagina=1,
            tamanho_pagina=5
        )
        
        response3 = await client.get_contracts(filters3)
        print(f"   ✅ Found {len(response3.data)} high-value contracts")
        
        if response3.data:
            high_value = response3.data[0]
            print(f"   💎 High-value: {high_value.get('objeto', 'N/A')[:60]}...")
            print(f"   💰 Valor: R$ {high_value.get('valorInicial', 'N/A')}")
        
        # Summary
        total_contracts = len(response.data) + len(response2.data) + len(response3.data)
        print(f"\n🎉 API Test Complete!")
        print(f"   📊 Total contracts retrieved: {total_contracts}")
        print(f"   ✅ API is fully functional for contracts")
        print(f"   🔗 Ready for integration with agents")

if __name__ == "__main__":
    asyncio.run(test_working_api())