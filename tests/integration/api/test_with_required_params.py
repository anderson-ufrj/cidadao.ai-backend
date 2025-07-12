#!/usr/bin/env python3
"""
Test Portal da Transparência API with required parameters
"""

import httpx
import asyncio
from datetime import datetime, timedelta

async def test_working_endpoints():
    """Test endpoints with proper required parameters"""
    
    api_key = "e24f842355f7211a2f4895e301aa5bca"
    base_url = "https://api.portaldatransparencia.gov.br"
    
    headers = {
        "chave-api-dados": api_key,
        "Content-Type": "application/json",
        "User-Agent": "CidadaoAI/1.0.0"
    }
    
    # Working endpoints that returned 400 (need parameters)
    working_endpoints = [
        "/api-de-dados/contratos",
        "/api-de-dados/convenios",
        "/api-de-dados/licitacoes"
    ]
    
    async with httpx.AsyncClient(timeout=30) as client:
        for endpoint in working_endpoints:
            print(f"Testing endpoint: {endpoint}")
            
            # Try different parameter combinations
            param_sets = [
                # Basic year/month
                {"ano": 2024, "mes": 1, "pagina": 1},
                
                # With date range
                {"dataInicio": "01/01/2024", "dataFim": "31/01/2024", "pagina": 1},
                
                # With organization
                {"ano": 2024, "mes": 1, "orgao": "26000", "pagina": 1},
                
                # Minimal with page size
                {"ano": 2024, "pagina": 1, "tamanhoPagina": 5},
                
                # Just year
                {"ano": 2024, "pagina": 1},
                
                # Different year
                {"ano": 2023, "mes": 12, "pagina": 1, "tamanhoPagina": 3}
            ]
            
            for i, params in enumerate(param_sets):
                try:
                    print(f"  Test {i+1}: {params}")
                    
                    response = await client.get(
                        f"{base_url}{endpoint}",
                        headers=headers,
                        params=params
                    )
                    
                    print(f"    Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"    ✅ SUCCESS!")
                        try:
                            data = response.json()
                            print(f"    Response type: {type(data)}")
                            if isinstance(data, list):
                                print(f"    Records: {len(data)}")
                                if data:
                                    print(f"    Sample keys: {list(data[0].keys()) if data[0] else 'Empty'}")
                            elif isinstance(data, dict):
                                print(f"    Dict keys: {list(data.keys())}")
                                if 'data' in data:
                                    print(f"    Data records: {len(data['data'])}")
                        except Exception as e:
                            print(f"    JSON parse error: {e}")
                            print(f"    Raw response: {response.text[:200]}")
                        
                        print("    🎉 FOUND WORKING CONFIGURATION!")
                        return endpoint, params, data
                    
                    elif response.status_code == 400:
                        print(f"    ❌ Bad Request: {response.text[:100]}")
                    elif response.status_code == 404:
                        print(f"    ❌ Not Found")
                    elif response.status_code == 403:
                        print(f"    ❌ Forbidden")
                    else:
                        print(f"    ❌ Status {response.status_code}: {response.text[:100]}")
                    
                except Exception as e:
                    print(f"    Exception: {str(e)}")
            
            print()
    
    print("❌ No working configuration found")
    return None, None, None

if __name__ == "__main__":
    asyncio.run(test_working_endpoints())