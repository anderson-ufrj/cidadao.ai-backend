"""
Basic Usage Examples for Transparency APIs

Demonstrates simple usage patterns for Brazilian transparency APIs.

Author: Anderson Henrique da Silva
Created: 2025-10-09 15:25:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

import asyncio
from src.services.transparency_apis import registry


async def example_1_list_apis():
    """Example 1: List all available APIs."""
    print("=== Example 1: List Available APIs ===\n")

    apis = registry.list_available_apis()
    print(f"Total APIs available: {len(apis)}\n")

    for api_key in apis:
        print(f"  - {api_key}")

    print()


async def example_2_get_contracts():
    """Example 2: Get contracts from TCE Pernambuco."""
    print("=== Example 2: Get Contracts from TCE-PE ===\n")

    # Get TCE-PE client
    pe_tce = registry.get_client('PE-tce')

    if pe_tce:
        # Test connection
        is_connected = await pe_tce.test_connection()
        print(f"Connection status: {'✅ Connected' if is_connected else '❌ Failed'}\n")

        if is_connected:
            # Fetch contracts from 2024
            print("Fetching contracts from 2024...")
            contracts = await pe_tce.get_contracts(year=2024)

            print(f"Found {len(contracts)} contracts\n")

            # Display first 3 contracts
            for i, contract in enumerate(contracts[:3], 1):
                print(f"Contract {i}:")
                print(f"  ID: {contract.get('contract_id')}")
                print(f"  Supplier: {contract.get('supplier_name')}")
                print(f"  Value: R$ {contract.get('value', 0):,.2f}")
                print(f"  Municipality: {contract.get('municipality')}")
                print()


async def example_3_get_municipalities():
    """Example 3: Get municipality list from TCE Ceará."""
    print("=== Example 3: Get Municipalities from TCE-CE ===\n")

    # Get TCE-CE client
    ce_tce = registry.get_client('CE-tce')

    if ce_tce:
        # Fetch municipalities
        municipalities = await ce_tce.get_municipalities()

        print(f"Total municipalities in Ceará: {len(municipalities)}\n")

        # Display first 5
        for i, mun in enumerate(municipalities[:5], 1):
            print(f"{i}. {mun.get('municipality_name')} (IBGE: {mun.get('municipality_code')})")

        print()


async def example_4_multi_state_data():
    """Example 4: Get contracts from multiple states."""
    print("=== Example 4: Multi-State Contract Analysis ===\n")

    states = ['PE', 'CE', 'RJ']
    all_contracts = {}

    for state_code in states:
        tce_key = f"{state_code}-tce"
        client = registry.get_client(tce_key)

        if client:
            print(f"Fetching {state_code} contracts...")
            contracts = await client.get_contracts(year=2024)
            all_contracts[state_code] = contracts
            print(f"  {state_code}: {len(contracts)} contracts")

    print(f"\nTotal contracts across states: {sum(len(c) for c in all_contracts.values())}")
    print()


async def example_5_ckan_search():
    """Example 5: Search datasets in CKAN portal."""
    print("=== Example 5: Search CKAN Datasets (São Paulo) ===\n")

    # Get SP CKAN client
    sp_ckan = registry.get_client('SP-ckan')

    if sp_ckan:
        # Search for contract-related datasets
        print("Searching for 'contratos' datasets...")
        datasets = await sp_ckan.search_datasets(query="contratos", limit=5)

        print(f"Found {len(datasets)} datasets\n")

        for i, dataset in enumerate(datasets, 1):
            print(f"Dataset {i}:")
            print(f"  Title: {dataset.get('title', 'N/A')}")
            print(f"  Resources: {len(dataset.get('resources', []))}")
            print()


async def main():
    """Run all examples."""
    print("╔════════════════════════════════════════╗")
    print("║  Transparency APIs - Usage Examples   ║")
    print("╚════════════════════════════════════════╝\n")

    await example_1_list_apis()
    await example_2_get_contracts()
    await example_3_get_municipalities()
    await example_4_multi_state_data()
    await example_5_ckan_search()

    print("✅ All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
