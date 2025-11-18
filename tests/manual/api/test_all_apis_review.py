"""
Comprehensive API Review and Testing Script
Tests all implemented transparency APIs to identify issues.

Author: Anderson Henrique da Silva
Created: 2025-11-14
License: Proprietary - All rights reserved
"""

import asyncio
import sys
from typing import Any

sys.path.insert(0, "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend")


def print_header(title: str) -> None:
    """Print formatted section header."""
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)
    print()


def print_test(number: int, description: str) -> None:
    """Print test description."""
    print(f"TEST {number}: {description}")
    print("-" * 80)


async def test_federal_apis() -> dict[str, Any]:
    """Test all federal APIs."""
    print_header("FEDERAL APIS REVIEW")
    results = {}

    # Test 1: SICONFI
    print_test(1, "SICONFI - Tesouro Nacional")
    try:
        from src.services.transparency_apis.federal_apis import SICONFIClient

        async with SICONFIClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                entities = await client.get_entities(year=2024, sphere="M", limit=5)
                print(f"  ✅ Connection: OK")
                print(f"  ✅ Entities: {len(entities)} municipalities found")
                results["SICONFI"] = {"status": "OK", "entities": len(entities)}
            else:
                print("  ❌ Connection: FAILED")
                results["SICONFI"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["SICONFI"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    # Test 2: IBGE
    print_test(2, "IBGE - Geographic and Demographic Data")
    try:
        from src.services.transparency_apis.federal_apis import IBGEClient

        async with IBGEClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                print(f"  ✅ Connection: OK")
                # Test get states
                states = await client.get_states()
                print(f"  ✅ States: {len(states)} found")
                results["IBGE"] = {"status": "OK", "states": len(states)}
            else:
                print("  ❌ Connection: FAILED")
                results["IBGE"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["IBGE"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    # Test 3: DataSUS
    print_test(3, "DataSUS - Health Ministry Data")
    try:
        from src.services.transparency_apis.federal_apis import DataSUSClient

        async with DataSUSClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                print(f"  ✅ Connection: OK")
                results["DataSUS"] = {"status": "OK"}
            else:
                print("  ❌ Connection: FAILED")
                results["DataSUS"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["DataSUS"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    # Test 4: INEP
    print_test(4, "INEP - Education Ministry Data")
    try:
        from src.services.transparency_apis.federal_apis import INEPClient

        async with INEPClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                print(f"  ✅ Connection: OK")
                results["INEP"] = {"status": "OK"}
            else:
                print("  ❌ Connection: FAILED")
                results["INEP"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["INEP"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    # Test 5: PNCP
    print_test(5, "PNCP - Public Procurement Portal")
    try:
        from src.services.transparency_apis.federal_apis import PNCPClient

        async with PNCPClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                print(f"  ✅ Connection: OK")
                results["PNCP"] = {"status": "OK"}
            else:
                print("  ❌ Connection: FAILED")
                results["PNCP"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["PNCP"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    # Test 6: BCB
    print_test(6, "BCB - Central Bank Economic Data")
    try:
        from src.services.transparency_apis.federal_apis import BCBClient

        async with BCBClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                print(f"  ✅ Connection: OK")
                results["BCB"] = {"status": "OK"}
            else:
                print("  ❌ Connection: FAILED")
                results["BCB"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["BCB"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    # Test 7: Compras.gov
    print_test(7, "Compras.gov - Government Procurement")
    try:
        from src.services.transparency_apis.federal_apis import ComprasGovClient

        async with ComprasGovClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                print(f"  ✅ Connection: OK")
                results["ComprasGov"] = {"status": "OK"}
            else:
                print("  ❌ Connection: FAILED")
                results["ComprasGov"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["ComprasGov"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    # Test 8: Minha Receita
    print_test(8, "Minha Receita - Federal Revenue Data")
    try:
        from src.services.transparency_apis.federal_apis import MinhaReceitaClient

        async with MinhaReceitaClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                print(f"  ✅ Connection: OK")
                results["MinhaReceita"] = {"status": "OK"}
            else:
                print("  ❌ Connection: FAILED")
                results["MinhaReceita"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["MinhaReceita"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    return results


async def test_state_apis() -> dict[str, Any]:
    """Test state CKAN portals."""
    print_header("STATE CKAN APIS REVIEW")
    results = {}

    print_test(1, "CKAN Client - 12 State Portals")
    try:
        from src.services.transparency_apis.state_apis import CKANClient

        # Test a few states
        test_states = [
            ("SP", "https://dados.sp.gov.br"),
            ("MG", "https://dados.mg.gov.br"),
            ("RJ", "https://dados.rj.gov.br"),
        ]

        for state, url in test_states:
            try:
                async with CKANClient(base_url=url, state_code=state) as client:
                    print(f"  Testing {state}: {url}")
                    connected = await client.test_connection()
                    if connected:
                        datasets = await client.search_datasets(query="saúde", limit=3)
                        print(f"    ✅ {state}: OK ({len(datasets)} datasets)")
                        results[f"CKAN_{state}"] = {
                            "status": "OK",
                            "datasets": len(datasets),
                        }
                    else:
                        print(f"    ❌ {state}: Connection failed")
                        results[f"CKAN_{state}"] = {"status": "FAILED"}
            except Exception as e:
                print(f"    ❌ {state}: {type(e).__name__}: {str(e)[:80]}")
                results[f"CKAN_{state}"] = {"status": "ERROR", "error": str(e)[:80]}

    except Exception as e:
        print(f"  ❌ Error loading CKAN: {type(e).__name__}: {str(e)[:100]}")
        results["CKAN"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    return results


async def test_tce_apis() -> dict[str, Any]:
    """Test TCE state audit court APIs."""
    print_header("TCE APIS REVIEW")
    results = {}

    # Test 1: TCE-SP
    print_test(1, "TCE-SP - São Paulo Audit Court")
    try:
        from src.services.transparency_apis.tce_apis import TCESaoPauloClient

        async with TCESaoPauloClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                municipalities = await client.get_municipalities()
                print(f"  ✅ Connection: OK")
                print(f"  ✅ Municipalities: {len(municipalities)} found")
                results["TCE-SP"] = {
                    "status": "OK",
                    "municipalities": len(municipalities),
                }
            else:
                print("  ❌ Connection: FAILED")
                results["TCE-SP"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["TCE-SP"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    # Test 2: TCE-CE
    print_test(2, "TCE-CE - Ceará Audit Court")
    try:
        from src.services.transparency_apis.tce_apis import TCECearaClient

        async with TCECearaClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                municipalities = await client.get_municipalities()
                print(f"  ✅ Connection: OK")
                print(f"  ✅ Municipalities: {len(municipalities)} found")
                results["TCE-CE"] = {
                    "status": "OK",
                    "municipalities": len(municipalities),
                }
            else:
                print("  ❌ Connection: FAILED")
                results["TCE-CE"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["TCE-CE"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    # Test 3: TCE-MG (expected to fail - SSL issues)
    print_test(3, "TCE-MG - Minas Gerais Audit Court (SSL Issues)")
    try:
        from src.services.transparency_apis.tce_apis import TCEMinasGeraisClient

        async with TCEMinasGeraisClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                print("  ✅ Connection: OK (unexpected!)")
                results["TCE-MG"] = {"status": "OK"}
            else:
                print("  ❌ Connection: FAILED (expected - SSL issues)")
                results["TCE-MG"] = {"status": "FAILED_EXPECTED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["TCE-MG"] = {"status": "ERROR_EXPECTED", "error": str(e)[:100]}
    print()

    # Test 4: TCE-BA (expected to fail - 403)
    print_test(4, "TCE-BA - Bahia Audit Court (403 Expected)")
    try:
        from src.services.transparency_apis.tce_apis import TCEBahiaClient

        async with TCEBahiaClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                print("  ✅ Connection: OK (unexpected!)")
                results["TCE-BA"] = {"status": "OK"}
            else:
                print("  ❌ Connection: FAILED (expected - 403 Forbidden)")
                results["TCE-BA"] = {"status": "FAILED_EXPECTED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["TCE-BA"] = {"status": "ERROR_EXPECTED", "error": str(e)[:100]}
    print()

    # Test 5: TCE-PE
    print_test(5, "TCE-PE - Pernambuco Audit Court")
    try:
        from src.services.transparency_apis.tce_apis import TCEPernambucoClient

        async with TCEPernambucoClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                print("  ✅ Connection: OK")
                results["TCE-PE"] = {"status": "OK"}
            else:
                print("  ❌ Connection: FAILED")
                results["TCE-PE"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["TCE-PE"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    # Test 6: TCE-RJ
    print_test(6, "TCE-RJ - Rio de Janeiro Audit Court")
    try:
        from src.services.transparency_apis.tce_apis import TCERioClient

        async with TCERioClient() as client:
            print(f"  Base URL: {client.base_url}")
            connected = await client.test_connection()
            if connected:
                print("  ✅ Connection: OK")
                results["TCE-RJ"] = {"status": "OK"}
            else:
                print("  ❌ Connection: FAILED")
                results["TCE-RJ"] = {"status": "FAILED"}
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")
        results["TCE-RJ"] = {"status": "ERROR", "error": str(e)[:100]}
    print()

    return results


async def main() -> None:
    """Run all API tests."""
    print_header("COMPREHENSIVE API REVIEW - 2025-11-14")
    print("Testing all implemented transparency APIs...")
    print()

    # Test all API categories
    federal_results = await test_federal_apis()
    state_results = await test_state_apis()
    tce_results = await test_tce_apis()

    # Generate summary
    print_header("SUMMARY")

    all_results = {**federal_results, **state_results, **tce_results}

    ok_count = sum(1 for r in all_results.values() if r.get("status") == "OK")
    failed_count = sum(
        1
        for r in all_results.values()
        if r.get("status") in ["FAILED", "FAILED_EXPECTED"]
    )
    error_count = sum(
        1
        for r in all_results.values()
        if r.get("status") in ["ERROR", "ERROR_EXPECTED"]
    )

    total = len(all_results)

    print(f"Total APIs Tested: {total}")
    print(f"✅ Working: {ok_count} ({ok_count/total*100:.1f}%)")
    print(f"❌ Failed: {failed_count} ({failed_count/total*100:.1f}%)")
    print(f"⚠️  Errors: {error_count} ({error_count/total*100:.1f}%)")
    print()

    print("Issues to Fix:")
    for api_name, result in all_results.items():
        if result.get("status") in ["FAILED", "ERROR"]:
            print(
                f"  - {api_name}: {result.get('status')} - {result.get('error', 'Connection failed')}"
            )
    print()

    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
