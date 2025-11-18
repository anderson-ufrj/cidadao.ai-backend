"""Test CKAN portals for multiple Brazilian states"""

import asyncio

from src.services.transparency_apis.state_apis.ckan_client import CKANClient

CKAN_PORTALS = {
    "SP": "https://dadosabertos.sp.gov.br",
    "RJ": "https://dados.rj.gov.br",
    "MG": "https://dados.mg.gov.br",
    "RS": "https://dados.rs.gov.br",
    "SC": "https://dados.sc.gov.br",
    "BA": "https://dados.ba.gov.br",
    "GO": "https://dadosabertos.go.gov.br",
    "ES": "https://dados.es.gov.br",
    "DF": "https://dados.df.gov.br",
    "PE": "http://web.transparencia.pe.gov.br/ckan",
    "AC": "https://dados.ac.gov.br",
    "RN": "https://dados.rn.gov.br",
}


async def test_state(state_code, url):
    try:
        async with CKANClient(base_url=url, state_code=state_code) as client:
            # Try to search for a common term
            datasets = await client.search_datasets(query="saúde", limit=3)
            return f"✅ {len(datasets):3d} datasets"
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            return "❌ 404 Not Found"
        elif "timeout" in error_msg.lower():
            return "❌ Timeout"
        elif "connection" in error_msg.lower():
            return "❌ Connection failed"
        elif "ssl" in error_msg.lower():
            return "❌ SSL error"
        else:
            return f"❌ {error_msg[:30]}"


async def main():
    print("=" * 80)
    print("Testing CKAN Portals Across Brazilian States")
    print("=" * 80)
    print()

    results = {}

    for state_code, url in CKAN_PORTALS.items():
        print(f"Testing {state_code:2s} - {url:50s} ... ", end="", flush=True)
        result = await test_state(state_code, url)
        results[state_code] = result
        print(result)

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    working = sum(1 for r in results.values() if "✅" in r)
    broken = sum(1 for r in results.values() if "❌" in r)

    print(f"\nTotal States Tested: {len(CKAN_PORTALS)}")
    print(f"✅ Working: {working} ({working/len(CKAN_PORTALS)*100:.1f}%)")
    print(f"❌ Broken:  {broken} ({broken/len(CKAN_PORTALS)*100:.1f}%)")
    print()

    if working > 0:
        print("Working States:")
        for state, result in results.items():
            if "✅" in result:
                print(f"  {state}: {result}")

    if broken > 0:
        print("\nBroken States:")
        for state, result in results.items():
            if "❌" in result:
                print(f"  {state}: {result}")


if __name__ == "__main__":
    asyncio.run(main())
