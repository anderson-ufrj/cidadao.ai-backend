#!/usr/bin/env python3
"""
Test Portal da Transparência API with correct endpoints
"""

import httpx
import asyncio

async def test_api_endpoints():
    """Test API with various endpoint formats"""
    
    api_key = "e24f842355f7211a2f4895e301aa5bca"
    base_url = "https://api.portaldatransparencia.gov.br"
    
    headers = {
        "chave-api-dados": api_key,
        "Content-Type": "application/json",
        "User-Agent": "CidadaoAI/1.0.0"
    }
    
    # Try different endpoint patterns from documentation
    test_endpoints = [
        # Basic endpoints
        "/api-de-dados/contratos",
        "/api-de-dados/despesas",
        "/api-de-dados/convenios", 
        "/api-de-dados/licitacoes",
        
        # Alternative formats
        "/contratos",
        "/despesas",
        "/convenios",
        "/licitacoes",
        
        # V1 endpoints
        "/v1/contratos",
        "/v1/despesas",
        
        # Specific documented endpoints
        "/api-de-dados/contratos/doc/swagger-ui.html",
        
        # Simple test without params
        "/api-de-dados/despesas/consulta"
    ]
    
    async with httpx.AsyncClient(timeout=30) as client:
        for endpoint in test_endpoints:
            try:
                print(f"Testing: {base_url}{endpoint}")
                
                # Test without parameters first
                response = await client.get(
                    f"{base_url}{endpoint}",
                    headers=headers
                )
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ SUCCESS! Working endpoint found")
                    try:
                        data = response.json()
                        print(f"  Response type: {type(data)}")
                        if isinstance(data, list):
                            print(f"  Records: {len(data)}")
                        elif isinstance(data, dict):
                            print(f"  Keys: {list(data.keys())}")
                    except:
                        print(f"  Response text: {response.text[:200]}")
                    print()
                    break
                
                elif response.status_code == 400:
                    print(f"  ⚠️ Bad Request - may need parameters")
                    # Try with basic parameters
                    params = {"ano": 2024, "mes": 1, "pagina": 1}
                    response2 = await client.get(
                        f"{base_url}{endpoint}",
                        headers=headers,
                        params=params
                    )
                    print(f"  With params status: {response2.status_code}")
                    if response2.status_code == 200:
                        print(f"  ✅ SUCCESS with parameters!")
                        print()
                        break
                
                elif response.status_code == 404:
                    print(f"  ❌ Not Found")
                elif response.status_code == 403:
                    print(f"  ❌ Forbidden")
                else:
                    print(f"  Status: {response.status_code}")
                    print(f"  Text: {response.text[:100]}")
                
                print()
                
            except Exception as e:
                print(f"  Exception: {str(e)}")
                print()

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())