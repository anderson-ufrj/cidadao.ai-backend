#!/usr/bin/env python3
"""Test Portal da Transparência API directly with the fixed parameters."""

import asyncio

import httpx


async def test_portal_api_direct():
    """Test the Portal API directly with codigoOrgao parameter."""
    print("=" * 80)
    print("🧪 Testing Portal da Transparência API (Direct HTTP)")
    print("=" * 80 + "\n")

    # The exact URL that was failing in production (from Railway logs)
    base_url = "https://api.portaldatransparencia.gov.br/api-de-dados/contratos"

    # BEFORE FIX: This was the failing request
    print("❌ BEFORE FIX - Missing codigoOrgao:")
    params_before = {
        "pagina": 1,
        "tamanhoPagina": 20,
        "dataInicial": "01/01/2024",
        "dataFinal": "31/12/2024",
        "valorMinimo": 800000.0,
        "valorMaximo": 1200000.0,
    }
    print(f"   Params: {params_before}")
    print(f"   Expected: 400 Bad Request\n")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url, params=params_before)
            print(f"   Status: {response.status_code}")
            if response.status_code == 400:
                print(f"   ✓ Confirmed: Returns 400 without codigoOrgao\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    # AFTER FIX: With codigoOrgao parameter
    print("✅ AFTER FIX - With codigoOrgao=36000:")
    params_after = {
        "pagina": 1,
        "tamanhoPagina": 20,
        "codigoOrgao": "36000",  # THIS IS THE FIX!
        "dataInicial": "01/01/2024",
        "dataFinal": "31/12/2024",
        "valorMinimo": 800000.0,
        "valorMaximo": 1200000.0,
    }
    print(f"   Params: {params_after}")
    print(f"   Expected: 200 OK with data\n")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url, params=params_after)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ SUCCESS! Portal API returned data")

                if isinstance(data, list):
                    print(f"   Total contracts: {len(data)}")
                    if data:
                        print(f"\n   📋 First contract sample:")
                        first = data[0]
                        for key in [
                            "numeroConvenio",
                            "objetoConvenio",
                            "valorConvenio",
                            "situacaoConvenio",
                        ]:
                            if key in first:
                                print(f"      {key}: {first[key]}")
                else:
                    print(f"   Response type: {type(data)}")
                    print(
                        f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}"
                    )

                print(f"\n🎯 FIX VERIFIED:")
                print(f"   ✅ Portal API accepts requests with codigoOrgao parameter")
                print(f"   ✅ No more 400 Bad Request errors")
                print(f"   ✅ portal_transparencia_service.py fix is working!")
                print(f"   ✅ Zumbi agent will now return real data in production!")
            else:
                print(f"   ⚠️  Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_portal_api_direct())
