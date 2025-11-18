"""
Test all 6 TCE APIs to identify working endpoints

Author: Anderson Henrique da Silva
Created: 2025-11-14
License: Proprietary - All rights reserved
"""

import asyncio


async def test_tce_sp():
    """Test TCE São Paulo - Known to work"""
    from src.services.transparency_apis.tce_apis.tce_sp import TCESaoPauloClient

    print("\n" + "=" * 80)
    print("Testing TCE-SP (São Paulo)")
    print("=" * 80)

    try:
        async with TCESaoPauloClient() as client:
            # Test connection
            connected = await client.test_connection()
            print(f"Connection test: {'✅ PASSED' if connected else '❌ FAILED'}")

            if connected:
                # Test municipalities
                munic = await client.get_municipalities()
                print(f"Municipalities: ✅ {len(munic)} found")

        return "✅ WORKING"
    except Exception as e:
        print(f"Error: ❌ {str(e)[:100]}")
        return f"❌ {str(e)[:60]}"


async def test_tce_ce():
    """Test TCE Ceará - New API discovered"""
    print("\n" + "=" * 80)
    print("Testing TCE-CE (Ceará) - New API")
    print("=" * 80)
    print("Base URL: https://api-dados-abertos.tce.ce.gov.br")

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            # Test municipalities endpoint
            response = await client.get(
                "https://api-dados-abertos.tce.ce.gov.br/municipios", timeout=10
            )
            data = response.json()

            if "data" in data:
                print(f"Municipalities: ✅ {len(data['data'])} found")
                print(
                    f"Sample: {data['data'][1]['nome_municipio']} (IBGE: {data['data'][1].get('geoibgeId')})"
                )
                return "✅ WORKING - Needs client update"
            else:
                print(f"Response: {data}")
                return "⚠️ PARTIAL"

    except Exception as e:
        print(f"Error: ❌ {str(e)[:100]}")
        return f"❌ {str(e)[:60]}"


async def test_tce_ba():
    """Test TCE Bahia"""
    print("\n" + "=" * 80)
    print("Testing TCE-BA (Bahia)")
    print("=" * 80)

    try:
        import httpx

        # Test current URL in client
        urls_to_test = [
            "https://sistemas.tce.ba.gov.br/egestaoapi/v1/municipios",
            "https://www.tce.ba.gov.br/dados-abertos",  # Data portal
        ]

        async with httpx.AsyncClient() as client:
            for url in urls_to_test:
                try:
                    response = await client.get(url, timeout=10)
                    print(f"  {url}")
                    print(f"    Status: {response.status_code}")
                    if response.status_code == 200:
                        return "✅ WORKING"
                except Exception as e:
                    print(f"    Error: {str(e)[:50]}")

        return "❌ No public API found - only data downloads"

    except Exception as e:
        print(f"Error: ❌ {str(e)[:100]}")
        return f"❌ {str(e)[:60]}"


async def test_tce_mg():
    """Test TCE Minas Gerais"""
    print("\n" + "=" * 80)
    print("Testing TCE-MG (Minas Gerais)")
    print("=" * 80)

    try:
        import httpx

        urls_to_test = [
            "https://www.tce.mg.gov.br/api",
            "https://dadosabertos.tce.mg.gov.br",
            "https://www.tce.mg.gov.br/dados-abertos",
        ]

        async with httpx.AsyncClient() as client:
            for url in urls_to_test:
                try:
                    response = await client.get(url, timeout=10)
                    print(f"  {url}")
                    print(f"    Status: {response.status_code}")
                    if response.status_code == 200:
                        content = response.text[:200]
                        print(f"    Preview: {content[:100]}")
                except Exception as e:
                    print(f"    Error: {str(e)[:50]}")

        return "⚠️ Needs investigation"

    except Exception as e:
        print(f"Error: ❌ {str(e)[:100]}")
        return f"❌ {str(e)[:60]}"


async def test_tce_pe():
    """Test TCE Pernambuco"""
    print("\n" + "=" * 80)
    print("Testing TCE-PE (Pernambuco)")
    print("=" * 80)
    print("Documentation: https://sistemas.tce.pe.gov.br/DadosAbertos/Exemplo!listar")

    try:
        import httpx

        urls_to_test = [
            "https://sistemas.tce.pe.gov.br/DadosAbertos/api/Municipios",
            "https://sistemas.tce.pe.gov.br/DadosAbertos/api/Receitas",
        ]

        async with httpx.AsyncClient() as client:
            for url in urls_to_test:
                try:
                    response = await client.get(url, timeout=10)
                    print(f"  {url}")
                    print(f"    Status: {response.status_code}")
                    print(f"    Response: {response.text[:100]}")
                except Exception as e:
                    print(f"    Error: {str(e)[:50]}")

        return "❌ Requires authentication/parameters"

    except Exception as e:
        print(f"Error: ❌ {str(e)[:100]}")
        return f"❌ {str(e)[:60]}"


async def test_tce_rj():
    """Test TCE Rio de Janeiro"""
    print("\n" + "=" * 80)
    print("Testing TCE-RJ (Rio de Janeiro)")
    print("=" * 80)

    try:
        import httpx

        urls_to_test = [
            "https://www.tce.rj.gov.br/dados-abertos",
            "https://api.tce.rj.gov.br",
        ]

        async with httpx.AsyncClient() as client:
            for url in urls_to_test:
                try:
                    response = await client.get(url, timeout=10)
                    print(f"  {url}")
                    print(f"    Status: {response.status_code}")
                except Exception as e:
                    print(f"    Error: {str(e)[:50]}")

        return "⚠️ Needs investigation"

    except Exception as e:
        print(f"Error: ❌ {str(e)[:100]}")
        return f"❌ {str(e)[:60]}"


async def main():
    print("=" * 80)
    print("TCE APIs Comprehensive Test")
    print("=" * 80)
    print()

    results = {}

    # Test all TCEs
    results["TCE-SP"] = await test_tce_sp()
    results["TCE-CE"] = await test_tce_ce()
    results["TCE-BA"] = await test_tce_ba()
    results["TCE-MG"] = await test_tce_mg()
    results["TCE-PE"] = await test_tce_pe()
    results["TCE-RJ"] = await test_tce_rj()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY - TCE APIs Status")
    print("=" * 80)
    print()

    for tce, status in results.items():
        print(f"{tce:15} {status}")

    print()

    working = sum(1 for r in results.values() if "✅" in r)
    partial = sum(1 for r in results.values() if "⚠️" in r)
    broken = sum(1 for r in results.values() if "❌" in r)

    print(f"✅ Working: {working}/6")
    print(f"⚠️  Partial: {partial}/6")
    print(f"❌ Broken:  {broken}/6")
    print()


if __name__ == "__main__":
    asyncio.run(main())
