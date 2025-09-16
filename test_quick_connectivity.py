#!/usr/bin/env python3
"""
⚡ Teste Rápido de Conectividade
Verifica rapidamente se os serviços estão online
"""

import asyncio
import httpx

# URLs dos serviços
BACKEND_URL = "https://neural-thinker-cidadao-ai-backend.hf.space"
MODELS_URL = "https://neural-thinker-cidadao-ai-models.hf.space"

async def quick_test():
    """🚀 Teste rápido de conectividade"""
    print("⚡ TESTE RÁPIDO DE CONECTIVIDADE")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        
        # Test Backend
        print(f"🔍 Testando Backend: {BACKEND_URL}")
        try:
            response = await client.get(f"{BACKEND_URL}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Backend ONLINE - {data.get('status', 'N/A')}")
                print(f"   🤖 Agentes: {list(data.get('agents', {}).keys())}")
            else:
                print(f"   ❌ Backend retornou: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Backend OFFLINE: {str(e)}")
        
        # Test Models
        print(f"🤖 Testando Models: {MODELS_URL}")
        try:
            response = await client.get(f"{MODELS_URL}/")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Models ONLINE - {data.get('api', 'N/A')}")
            else:
                print(f"   ❌ Models retornou: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Models OFFLINE: {str(e)}")
        
        # Test Backend → Models integration (via backend status)
        print(f"🔄 Testando Integração via Backend Status:")
        try:
            response = await client.get(f"{BACKEND_URL}/api/status")
            if response.status_code == 200:
                data = response.json()
                cache_info = data.get('performance', {}).get('cache', {})
                print(f"   ✅ Backend Status OK")
                print(f"   📊 Cache: {cache_info.get('total_entries', 0)} entries")
                print(f"   🎯 API Version: {data.get('version', 'N/A')}")
            else:
                print(f"   ❌ Backend Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Backend Status Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(quick_test())