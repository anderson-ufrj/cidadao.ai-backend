"""
Comprehensive API Integration Test
Tests all Federal, State, and TCE APIs
"""

import asyncio


async def test_all_apis():
    results = {"federal": {}, "state": {}, "tce": {}}

    print("=" * 80)
    print("COMPREHENSIVE API INTEGRATION TEST - ALL 15+ APIs")
    print("=" * 80)

    # ==================== FEDERAL APIS ====================
    print("\n📊 FEDERAL APIS\n")

    # 1. PNCP
    print("1. Testing PNCP...")
    try:
        from src.services.transparency_apis.federal_apis.pncp_client import PNCPClient

        async with PNCPClient() as client:
            contracts = await client.search_contracts(
                start_date="20241001", end_date="20241031", page_size=10
            )
            results["federal"]["PNCP"] = f"✅ {len(contracts)} contracts"
    except Exception as e:
        results["federal"]["PNCP"] = f"❌ {str(e)[:60]}"

    # 2. IBGE
    print("2. Testing IBGE...")
    try:
        from src.services.transparency_apis.federal_apis.ibge_client import IBGEClient

        async with IBGEClient() as client:
            states = await client.get_states()
            results["federal"]["IBGE"] = f"✅ {len(states)} states"
    except Exception as e:
        results["federal"]["IBGE"] = f"❌ {str(e)[:60]}"

    # 3. BCB
    print("3. Testing BCB...")
    try:
        from src.services.transparency_apis.federal_apis.bcb_client import (
            BancoCentralClient,
        )

        async with BancoCentralClient() as client:
            selic = await client.get_selic(last_n=5)
            results["federal"]["BCB"] = f"✅ {len(selic)} SELIC points"
    except Exception as e:
        results["federal"]["BCB"] = f"❌ {str(e)[:60]}"

    # 4. Compras.gov
    print("4. Testing Compras.gov...")
    try:
        from src.services.transparency_apis.federal_apis.compras_gov_client import (
            ComprasGovClient,
        )

        async with ComprasGovClient() as client:
            orgs = await client.search_organizations(limit=5)
            results["federal"]["Compras.gov"] = f"✅ {len(orgs)} orgs"
    except Exception as e:
        results["federal"]["Compras.gov"] = f"❌ {str(e)[:60]}"

    # 5. Minha Receita
    print("5. Testing Minha Receita...")
    try:
        from src.services.transparency_apis.federal_apis.minha_receita_client import (
            MinhaReceitaClient,
        )

        async with MinhaReceitaClient() as client:
            cnpj = await client.get_cnpj("00000000000191")
            results["federal"]["Minha Receita"] = f"✅ {cnpj.razao_social[:30]}"
    except Exception as e:
        results["federal"]["Minha Receita"] = f"❌ {str(e)[:60]}"

    # 6. DataSUS
    print("6. Testing DataSUS...")
    try:
        from src.services.transparency_apis.federal_apis.datasus_client import (
            DataSUSClient,
        )

        async with DataSUSClient() as client:
            datasets = await client.search_datasets(query="saúde", limit=3)
            results["federal"]["DataSUS"] = f"✅ {len(datasets)} datasets"
    except Exception as e:
        results["federal"]["DataSUS"] = f"❌ {str(e)[:60]}"

    # 7. INEP
    print("7. Testing INEP...")
    try:
        from src.services.transparency_apis.federal_apis.inep_client import INEPClient

        async with INEPClient() as client:
            institutions = await client.search_institutions(state="RJ", limit=5)
            results["federal"]["INEP"] = f"✅ {len(institutions)} institutions"
    except Exception as e:
        results["federal"]["INEP"] = f"❌ {str(e)[:60]}"

    # ==================== STATE APIS ====================
    print("\n🏛️  STATE APIS\n")

    # 8. CKAN
    print("8. Testing CKAN (generic state portals)...")
    try:
        from src.services.transparency_apis.state_apis.ckan_client import CKANClient

        async with CKANClient(base_url="https://dados.gov.br") as client:
            packages = await client.search_datasets(query="educação", limit=5)
            results["state"]["CKAN"] = f"✅ {len(packages)} datasets"
    except Exception as e:
        results["state"]["CKAN"] = f"❌ {str(e)[:60]}"

    # 9. Rondônia CGE
    print("9. Testing Rondônia CGE...")
    try:
        from src.services.transparency_apis.state_apis.rondonia_cge_client import (
            RondoniaCGEClient,
        )

        # Check if client can be instantiated
        client = RondoniaCGEClient()
        await client.close()
        results["state"]["Rondônia CGE"] = "⚠️  Client OK, needs endpoint test"
    except Exception as e:
        results["state"]["Rondônia CGE"] = f"❌ {str(e)[:60]}"

    # ==================== TCE APIS ====================
    print("\n⚖️  TCE APIS (Tribunais de Contas)\n")

    tce_configs = [
        ("BA", "TCEBahiaClient"),
        ("CE", "TCECearaClient"),
        ("MG", "TCEMinasGeraisClient"),
        ("PE", "TCEPernambucoClient"),
        ("RJ", "TCERioDeJaneiroClient"),
        ("SP", "TCESaoPauloClient"),
    ]

    for idx, (state, class_name) in enumerate(tce_configs, start=10):
        print(f"{idx}. Testing TCE-{state}...")
        try:
            # Import using new path
            from src.services.transparency_apis.tce_apis import (
                TCEBahiaClient,
                TCECearaClient,
                TCEMinasGeraisClient,
                TCEPernambucoClient,
                TCERioDeJaneiroClient,
                TCESaoPauloClient,
            )

            client_map = {
                "BA": TCEBahiaClient,
                "CE": TCECearaClient,
                "MG": TCEMinasGeraisClient,
                "PE": TCEPernambucoClient,
                "RJ": TCERioDeJaneiroClient,
                "SP": TCESaoPauloClient,
            }

            client_class = client_map.get(state)
            if client_class:
                async with client_class() as client:
                    # Try to test connection
                    connected = await client.test_connection()
                    if connected:
                        results["tce"][f"TCE-{state}"] = "✅ Connected successfully"
                    else:
                        results["tce"][
                            f"TCE-{state}"
                        ] = "⚠️  Client OK, connection test failed"
            else:
                results["tce"][f"TCE-{state}"] = "❌ Class not in map"
        except Exception as e:
            results["tce"][f"TCE-{state}"] = f"❌ {str(e)[:60]}"

    # ==================== SUMMARY ====================
    print("\n" + "=" * 80)
    print("SUMMARY - COMPREHENSIVE API STATUS")
    print("=" * 80)

    print("\n📊 FEDERAL APIS (7):")
    for api, status in results["federal"].items():
        print(f"   {api:20} {status}")

    print("\n🏛️  STATE APIS (2):")
    for api, status in results["state"].items():
        print(f"   {api:20} {status}")

    print("\n⚖️  TCE APIS (6):")
    for api, status in results["tce"].items():
        print(f"   {api:20} {status}")

    # Count totals
    total = len(results["federal"]) + len(results["state"]) + len(results["tce"])
    working = sum(
        1
        for category in results.values()
        for status in category.values()
        if "✅" in status
    )
    partial = sum(
        1
        for category in results.values()
        for status in category.values()
        if "⚠️" in status
    )
    broken = sum(
        1
        for category in results.values()
        for status in category.values()
        if "❌" in status
    )

    print("\n" + "=" * 80)
    print(f"📈 TOTAL APIS: {total}")
    print(f"   ✅ Working:  {working:2d} ({working/total*100:5.1f}%)")
    print(f"   ⚠️  Partial:  {partial:2d} ({partial/total*100:5.1f}%)")
    print(f"   ❌ Broken:   {broken:2d} ({broken/total*100:5.1f}%)")
    print("=" * 80)

    return results


if __name__ == "__main__":
    asyncio.run(test_all_apis())
