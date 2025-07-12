#!/usr/bin/env python3
"""
Simple test to debug API connection issues
"""

import httpx
import asyncio

async def test_api_key():
    """Test API key with minimal request"""
    
    api_key = "e24f842355f7211a2f4895e301aa5bca"
    base_url = "https://api.portaldatransparencia.gov.br"
    
    headers = {
        "chave-api-dados": api_key,
        "Content-Type": "application/json",
        "User-Agent": "CidadaoAI/1.0.0"
    }
    
    test_endpoints = [
        "/contratos",
        "/despesas", 
        "/convenios",
        "/licitacoes"
    ]
    
    async with httpx.AsyncClient(timeout=30) as client:
        for endpoint in test_endpoints:
            try:
                print(f"Testing {endpoint}...")
                
                params = {
                    "ano": 2024,
                    "mes": 1,
                    "pagina": 1,
                    "tamanhoPagina": 1
                }
                
                response = await client.get(
                    f"{base_url}{endpoint}",
                    headers=headers,
                    params=params
                )
                
                print(f"  Status: {response.status_code}")
                print(f"  Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  Success! Data type: {type(data)}")
                    if isinstance(data, list):
                        print(f"  Records: {len(data)}")
                    elif isinstance(data, dict):
                        print(f"  Keys: {list(data.keys())}")
                else:
                    print(f"  Error: {response.text[:200]}")
                
                print()
                
            except Exception as e:
                print(f"  Exception: {str(e)}")
                print()

if __name__ == "__main__":
    asyncio.run(test_api_key())