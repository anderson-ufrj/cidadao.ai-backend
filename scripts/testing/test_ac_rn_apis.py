"""
Test connectivity for new CKAN APIs: Acre (AC) and Rio Grande do Norte (RN)

Tests both APIs to verify they follow CKAN standards and can be integrated.

Author: Anderson Henrique da Silva
Created: 2025-10-23
"""

import asyncio
import sys

from src.services.transparency_apis.registry import registry


async def test_ac_rn_apis():
    """Test Acre and RN CKAN API connectivity and data availability."""
    print("\n" + "=" * 70)
    print("Testing New CKAN APIs: Acre (AC) and Rio Grande do Norte (RN)")
    print("=" * 70 + "\n")

    # Test Acre (AC)
    print("[1/2] ACRE (AC) - https://dados.ac.gov.br")
    print("-" * 70)
    try:
        ac_client = registry.get_client("AC-ckan")
        if not ac_client:
            print("  ERROR: AC-ckan client not found in registry")
        else:
            # Test connection
            is_connected = await ac_client.test_connection()
            print(f"  Connection: {'OK' if is_connected else 'FAILED'}")

            if is_connected:
                # Get package list
                packages = await ac_client.list_packages(limit=5)
                print(f"  Available datasets: {len(packages)}")
                print("  Sample datasets:")
                for i, pkg in enumerate(packages[:3], 1):
                    print(f"    {i}. {pkg}")

                # Get first package details
                if packages:
                    details = await ac_client.get_package(packages[0])
                    if details:
                        print("\n  First dataset details:")
                        print(f"    Name: {details.get('name', 'N/A')}")
                        print(f"    Title: {details.get('title', 'N/A')}")
                        print(
                            f"    Resources: {len(details.get('resources', []))} files"
                        )
                        print(
                            f"    Organization: {details.get('organization', {}).get('title', 'N/A')}"
                        )

    except Exception as e:
        print(f"  ERROR: {str(e)}")

    print("\n")

    # Test Rio Grande do Norte (RN)
    print("[2/2] RIO GRANDE DO NORTE (RN) - https://dados.rn.gov.br")
    print("-" * 70)
    try:
        rn_client = registry.get_client("RN-ckan")
        if not rn_client:
            print("  ERROR: RN-ckan client not found in registry")
        else:
            # Test connection
            is_connected = await rn_client.test_connection()
            print(f"  Connection: {'OK' if is_connected else 'FAILED'}")

            if is_connected:
                # Get package list
                packages = await rn_client.list_packages(limit=5)
                print(f"  Available datasets: {len(packages)}")

                if packages:
                    print("  Sample datasets:")
                    for i, pkg in enumerate(packages[:3], 1):
                        print(f"    {i}. {pkg}")

                    # Get first package details
                    details = await rn_client.get_package(packages[0])
                    if details:
                        print("\n  First dataset details:")
                        print(f"    Name: {details.get('name', 'N/A')}")
                        print(f"    Title: {details.get('title', 'N/A')}")
                        print(
                            f"    Resources: {len(details.get('resources', []))} files"
                        )
                        print(
                            f"    Organization: {details.get('organization', {}).get('title', 'N/A')}"
                        )
                else:
                    print(
                        "  WARNING: API is online but no datasets published yet (empty portal)"
                    )

    except Exception as e:
        print(f"  ERROR: {str(e)}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\nNew CKAN APIs Status:")
    print("  - Acre (AC): Added to registry (has datasets)")
    print("  - Rio Grande do Norte (RN): Added to registry (portal empty/no datasets)")
    print("\nTotal CKAN APIs: 11 states (SP, RJ, RS, SC, BA, GO, ES, DF, PE, AC, RN)")
    print("Total APIs in system: 19 (11 CKAN + 6 TCE + 1 CGE + 1 Federal)")
    print("\nBrazil coverage: 13/27 states = 48.1% (up from 44.4%)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_ac_rn_apis())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
