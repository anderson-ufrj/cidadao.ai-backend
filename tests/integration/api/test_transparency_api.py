#!/usr/bin/env python3
"""
Script to test Portal da Transparência API integration.

Author: Anderson H. Silva
Date: 2025-01-24

TODO: Mock Portal da Transparência API responses for integration tests
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logging import setup_logging
from src.tools.transparency_api import TransparencyAPIClient, TransparencyAPIFilter
from src.tools.transparency_models import parse_api_data


@pytest.mark.asyncio
async def test_api_connection():
    """Test basic API connection."""
    print("🔄 Testing API connection...")

    async with TransparencyAPIClient() as client:
        try:
            # Test with a simple contract search (requires codigoOrgao)
            filters = TransparencyAPIFilter(
                codigo_orgao="26000",  # Ministério da Saúde
                ano=2024,
                mes=1,
                pagina=1,
                tamanho_pagina=5,  # Small test
            )

            response = await client.get_contracts(filters)

            print("✅ API connection successful!")
            print(f"📊 Retrieved {len(response.data)} contracts")
            print(f"📄 Total pages: {response.total_pages}")
            print(f"📋 Total records: {response.total_records}")

            if response.data:
                print("\n📝 Sample contract:")
                sample = response.data[0]
                print(f"   ID: {sample.get('id', 'N/A')}")
                print(f"   Objeto: {sample.get('objeto', 'N/A')[:100]}...")
                print(f"   Valor: R$ {sample.get('valor', 'N/A')}")
                print(
                    f"   Fornecedor: {sample.get('fornecedor', {}).get('nome', 'N/A')}"
                )

            return True

        except Exception as e:
            print(f"❌ API connection failed: {str(e)}")
            return False


@pytest.mark.asyncio
async def test_different_endpoints():
    """Test different API endpoints."""
    print("\n🔄 Testing different endpoints...")

    async with TransparencyAPIClient() as client:
        endpoints = [
            ("contracts", "get_contracts"),
            ("expenses", "get_expenses"),
            ("agreements", "get_agreements"),
            ("biddings", "get_biddings"),
        ]

        results = {}

        for endpoint_name, method_name in endpoints:
            try:
                print(f"   Testing {endpoint_name}...")

                # Different endpoints need different required params
                if endpoint_name in ["contracts", "biddings"]:
                    filters = TransparencyAPIFilter(
                        codigo_orgao="26000",  # Required for contratos/licitacoes
                        ano=2024,
                        mes=1,
                        pagina=1,
                        tamanho_pagina=3,
                    )
                elif endpoint_name == "agreements":
                    filters = TransparencyAPIFilter(
                        data_inicio="01/01/2024",
                        data_fim="31/01/2024",
                        pagina=1,
                        tamanho_pagina=3,
                    )
                else:
                    filters = TransparencyAPIFilter(
                        ano=2024, mes=1, pagina=1, tamanho_pagina=3
                    )

                method = getattr(client, method_name)
                response = await method(filters)

                results[endpoint_name] = {
                    "success": True,
                    "records": len(response.data),
                    "total": response.total_records,
                }

                print(f"   ✅ {endpoint_name}: {len(response.data)} records")

            except Exception as e:
                results[endpoint_name] = {"success": False, "error": str(e)}
                print(f"   ⚠️ {endpoint_name}: {str(e)}")

        return results


@pytest.mark.asyncio
async def test_data_parsing():
    """Test data parsing with models."""
    print("\n🔄 Testing data parsing...")

    async with TransparencyAPIClient() as client:
        try:
            filters = TransparencyAPIFilter(
                codigo_orgao="26000",  # Required for contracts
                ano=2024,
                mes=1,
                pagina=1,
                tamanho_pagina=3,
            )

            response = await client.get_contracts(filters)

            # Parse data using our models
            parsed_contracts = parse_api_data(response.data, "contracts")

            print(f"✅ Successfully parsed {len(parsed_contracts)} contracts")

            if parsed_contracts:
                sample = parsed_contracts[0]
                print("\n📝 Parsed contract sample:")
                print(f"   Objeto: {sample.objeto}")
                print(f"   Valor: {sample.valor_inicial or sample.valor_global}")
                print(f"   Data Assinatura: {sample.data_assinatura}")
                print(
                    f"   Fornecedor: {sample.fornecedor.nome if sample.fornecedor else 'N/A'}"
                )
                print(f"   Órgão: {sample.orgao.nome if sample.orgao else 'N/A'}")

            return True

        except Exception as e:
            print(f"❌ Data parsing failed: {str(e)}")
            return False


@pytest.mark.asyncio
async def test_filters():
    """Test different filter combinations."""
    print("\n🔄 Testing filters...")

    async with TransparencyAPIClient() as client:
        filter_tests = [
            {
                "name": "By year and month",
                "filters": TransparencyAPIFilter(ano=2024, mes=1, tamanho_pagina=3),
            },
            {
                "name": "By value range",
                "filters": TransparencyAPIFilter(
                    ano=2024, valor_inicial=1000000, tamanho_pagina=3  # > 1M
                ),
            },
            {
                "name": "By organization",
                "filters": TransparencyAPIFilter(
                    ano=2024, orgao="26000", tamanho_pagina=3  # Ministério da Saúde
                ),
            },
        ]

        for test in filter_tests:
            try:
                print(f"   Testing {test['name']}...")

                response = await client.get_contracts(test["filters"])

                print(f"   ✅ {test['name']}: {len(response.data)} records")

            except Exception as e:
                print(f"   ⚠️ {test['name']}: {str(e)}")


@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting behavior."""
    print("\n🔄 Testing rate limiting...")

    async with TransparencyAPIClient(rate_limit_per_minute=5) as client:
        try:
            print("   Making 6 rapid requests to test rate limiting...")

            filters = TransparencyAPIFilter(ano=2024, pagina=1, tamanho_pagina=1)

            start_time = asyncio.get_event_loop().time()

            for i in range(6):
                print(f"   Request {i+1}...")
                await client.get_contracts(filters)

            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time

            print(f"   ✅ Completed 6 requests in {duration:.2f} seconds")
            print(
                f"   Rate limiting {'active' if duration > 10 else 'may not be active'}"
            )

        except Exception as e:
            print(f"   ⚠️ Rate limiting test failed: {str(e)}")


async def main():
    """Run all tests."""
    setup_logging()

    print("🚀 Starting Portal da Transparência API Tests")
    print("=" * 50)

    # Test 1: Basic connection
    connection_ok = await test_api_connection()

    if not connection_ok:
        print(
            "\n❌ Basic connection failed. Check your API key and internet connection."
        )
        return

    # Test 2: Different endpoints
    await test_different_endpoints()

    # Test 3: Data parsing
    await test_data_parsing()

    # Test 4: Filters
    await test_filters()

    # Test 5: Rate limiting
    await test_rate_limiting()

    print("\n" + "=" * 50)
    print("🎉 API tests completed!")
    print("\n💡 Tips:")
    print("   - Rate limiting is active (90 req/min during normal hours)")
    print("   - Use filters to get specific data")
    print("   - Parse data with our models for better structure")
    print("   - Check logs for detailed request information")


if __name__ == "__main__":
    asyncio.run(main())
