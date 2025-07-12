#!/usr/bin/env python3
"""
Test Portal da Transparência API with correct parameters
"""

import httpx
import asyncio

async def test_final_fix():
    """Test with correct parameter names"""
    
    api_key = "e24f842355f7211a2f4895e301aa5bca"
    base_url = "https://api.portaldatransparencia.gov.br"
    
    headers = {
        "chave-api-dados": api_key,
        "Content-Type": "application/json",
        "User-Agent": "CidadaoAI/1.0.0"
    }
    
    test_cases = [
        # Contratos - with codigoOrgao
        {
            "endpoint": "/api-de-dados/contratos",
            "params": {
                "codigoOrgao": "26000",  # Ministério da Saúde
                "ano": 2024,
                "mes": 1,
                "pagina": 1,
                "tamanhoPagina": 3
            }
        },
        
        # Licitações - with codigoOrgao  
        {
            "endpoint": "/api-de-dados/licitacoes",
            "params": {
                "codigoOrgao": "26000",
                "ano": 2024,
                "mes": 1,
                "pagina": 1,
                "tamanhoPagina": 3
            }
        },
        
        # Convênios - with specific date range (1 month)
        {
            "endpoint": "/api-de-dados/convenios",
            "params": {
                "dataInicio": "01/01/2024",
                "dataFim": "31/01/2024",
                "pagina": 1,
                "tamanhoPagina": 3
            }
        },
        
        # Try different organization codes
        {
            "endpoint": "/api-de-dados/contratos",
            "params": {
                "codigoOrgao": "20000",  # Presidência da República
                "ano": 2024,
                "mes": 1,
                "pagina": 1,
                "tamanhoPagina": 2
            }
        }
    ]
    
    async with httpx.AsyncClient(timeout=30) as client:
        for i, test_case in enumerate(test_cases):
            endpoint = test_case["endpoint"]
            params = test_case["params"]
            
            print(f"Test {i+1}: {endpoint}")
            print(f"  Params: {params}")
            
            try:
                response = await client.get(
                    f"{base_url}{endpoint}",
                    headers=headers,
                    params=params
                )
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ SUCCESS!")
                    try:
                        data = response.json()
                        print(f"  Response type: {type(data)}")
                        
                        if isinstance(data, list):
                            print(f"  Records: {len(data)}")
                            if data:
                                sample = data[0]
                                print(f"  Sample record keys: {list(sample.keys())[:10]}...")
                                print(f"  Sample values:")
                                for key, value in list(sample.items())[:5]:
                                    print(f"    {key}: {value}")
                        
                        elif isinstance(data, dict):
                            print(f"  Dict keys: {list(data.keys())}")
                            if 'data' in data:
                                records = data['data']
                                print(f"  Data records: {len(records)}")
                                if records:
                                    sample = records[0]
                                    print(f"  Sample record keys: {list(sample.keys())[:10]}...")
                        
                        print(f"  🎉 API IS WORKING!")
                        return True
                        
                    except Exception as e:
                        print(f"  JSON parse error: {e}")
                        print(f"  Raw response: {response.text[:300]}")
                
                else:
                    print(f"  ❌ Status {response.status_code}")
                    print(f"  Error: {response.text[:200]}")
                
            except Exception as e:
                print(f"  Exception: {str(e)}")
            
            print()
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_final_fix())
    if success:
        print("\n🎉 API CONNECTION SUCCESSFUL!")
        print("The Portal da Transparência API is now working correctly.")
    else:
        print("\n❌ Still having issues with API connection.")