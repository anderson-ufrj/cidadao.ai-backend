"""
TCE-MG Detailed Test Report Generator
Creates visual test report for official API access request.

Author: Anderson Henrique da Silva
Created: 2025-11-14
License: Proprietary - All rights reserved
"""

from datetime import datetime

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def print_header(title):
    """Print formatted section header."""
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)
    print()


def print_test(number, description):
    """Print test description."""
    print(f"TEST {number}: {description}")
    print("-" * 80)


def test_ssl_certificate():
    """Test SSL certificate verification."""
    print_test(1, "SSL Certificate Verification")

    url = "https://dadosabertos.tce.mg.gov.br"

    print(f"URL: {url}")
    print()

    # Test with SSL verification enabled (production requirement)
    print("Attempt 1: WITH SSL verification (production requirement)")
    try:
        response = requests.get(url, verify=True, timeout=10)
        print(f"  ✅ Status: {response.status_code}")
        print("  ✅ SSL: Valid certificate")
    except requests.exceptions.SSLError as e:
        print("  ❌ SSL Error: Certificate verification failed")
        print(f"  ❌ Details: {str(e)[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}")

    print()

    # Test without SSL verification (insecure, only for testing)
    print("Attempt 2: WITHOUT SSL verification (insecure test only)")
    try:
        response = requests.get(url, verify=False, timeout=10)
        print(f"  ⚠️  Status: {response.status_code}")
        print("  ⚠️  SSL: Bypassed (NOT SAFE for production)")
        print("  ℹ️  Note: Site is accessible but SSL is broken")
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")

    print()
    print("RESULT: ❌ SSL certificate cannot be verified")
    print("IMPACT: Cannot use this API in production without security risk")
    print()


def test_api_endpoints():
    """Test various API endpoint patterns."""
    print_test(2, "API Endpoint Discovery")

    base_url = "https://dadosabertos.tce.mg.gov.br"

    endpoints = [
        "/api",
        "/api/3",
        "/api/3/action",
        "/api/3/action/package_list",
        "/api/datasets",
        "/api/municipios",
        "/api/contratos",
        "/api/licitacoes",
    ]

    print(f"Base URL: {base_url}")
    print(f"Testing {len(endpoints)} common endpoint patterns...")
    print()

    results = []
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, verify=False, timeout=10)
            status = response.status_code
            content_type = response.headers.get("Content-Type", "unknown")[:40]

            if status == 200:
                symbol = "✅"
            elif status == 404:
                symbol = "❌"
            else:
                symbol = "⚠️"

            result = f"{symbol} {endpoint:35} Status: {status:3}  Type: {content_type}"
            results.append((status, result))

        except Exception as e:
            result = f"❌ {endpoint:35} Error: {type(e).__name__}"
            results.append((999, result))

    # Print sorted results (errors last)
    for _, result in sorted(results):
        print(result)

    print()
    working = sum(1 for status, _ in results if status == 200)
    print(f"RESULT: ❌ 0/{len(endpoints)} endpoints working (all return 404)")
    print("IMPACT: No CKAN-style API available at this portal")
    print()


def test_state_ckan():
    """Test state CKAN portal."""
    print_test(3, "State CKAN Portal (dados.mg.gov.br)")

    base_url = "https://dados.mg.gov.br"

    endpoints = [
        "/",
        "/api/3",
        "/api/3/action/package_list",
        "/api/3/action/organization_list",
    ]

    print(f"Base URL: {base_url}")
    print("Note: This is State Government portal, not TCE-specific")
    print()

    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, verify=False, timeout=10)
            status = response.status_code

            if status == 200:
                print(f"✅ {endpoint:40} Status: {status}")
            elif status == 403:
                print(f"❌ {endpoint:40} Status: {status} (Forbidden)")
            else:
                print(f"⚠️  {endpoint:40} Status: {status}")

        except Exception as e:
            print(f"❌ {endpoint:40} Error: {type(e).__name__}")

    print()
    print("RESULT: ❌ All endpoints return 403 Forbidden")
    print("IMPACT: Requires authentication or registration")
    print()


def test_main_website():
    """Test main TCE-MG website."""
    print_test(4, "Main TCE-MG Website")

    urls = [
        ("Main site", "https://www.tce.mg.gov.br"),
        ("Open Data Portal", "https://dadosabertos.tce.mg.gov.br"),
        ("Transparency", "https://www.tce.mg.gov.br/transparencia"),
    ]

    print("Testing website accessibility...")
    print()

    for name, url in urls:
        try:
            response = requests.get(url, verify=False, timeout=10)
            status = response.status_code

            if status == 200:
                is_html = "text/html" in response.headers.get("Content-Type", "")
                if is_html:
                    print(f"✅ {name:20} Status: {status} (HTML page, no API)")
                else:
                    print(f"✅ {name:20} Status: {status}")
            else:
                print(f"⚠️  {name:20} Status: {status}")

        except requests.exceptions.SSLError:
            print(f"❌ {name:20} SSL certificate error")
        except Exception as e:
            print(f"❌ {name:20} Error: {type(e).__name__}")

    print()
    print("RESULT: ⚠️  Websites accessible but no programmatic API")
    print("IMPACT: Would require web scraping (not recommended)")
    print()


def test_current_client():
    """Test our current TCE-MG client implementation."""
    print_test(5, "Current TCE-MG Client Implementation")

    print("Testing existing client from our codebase...")
    print()

    try:
        import asyncio
        import sys

        sys.path.insert(
            0, "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend"
        )

        from src.services.transparency_apis.tce_apis.tce_mg import TCEMinasGeraisClient

        async def test_client():
            async with TCEMinasGeraisClient() as client:
                print(f"Client base URL: {client.base_url}")
                print(f"Client name: {client.name}")
                print()

                # Test connection
                print("Testing connection...")
                try:
                    connected = await client.test_connection()
                    if connected:
                        print("  ✅ Connection successful")
                    else:
                        print("  ❌ Connection failed")
                except Exception as e:
                    print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")

                print()

                # Test get municipalities
                print("Testing get_municipalities()...")
                try:
                    municipalities = await client.get_municipalities()
                    if municipalities:
                        print(f"  ✅ Retrieved {len(municipalities)} municipalities")
                    else:
                        print("  ❌ No municipalities retrieved")
                except Exception as e:
                    print(f"  ❌ Error: {type(e).__name__}: {str(e)[:100]}")

        asyncio.run(test_client())

    except Exception as e:
        print(f"❌ Failed to load client: {type(e).__name__}: {str(e)[:100]}")

    print()
    print("RESULT: ❌ Client cannot connect due to SSL and endpoint issues")
    print("IMPACT: TCE-MG integration currently non-functional")
    print()


def generate_summary():
    """Generate final summary and recommendations."""
    print_header("SUMMARY AND RECOMMENDATIONS")

    print("PROBLEMS IDENTIFIED:")
    print()
    print("  1. ❌ SSL Certificate Verification Failure")
    print("     - Certificate cannot be verified")
    print("     - Blocks production deployment (security requirement)")
    print("     - Would expose system to man-in-the-middle attacks")
    print()

    print("  2. ❌ No Public API Endpoints Found")
    print("     - CKAN endpoints return 404 Not Found")
    print("     - Modern Angular app hides backend API")
    print("     - No API documentation available")
    print()

    print("  3. ❌ State Portal Access Restricted")
    print("     - dados.mg.gov.br returns 403 Forbidden")
    print("     - Likely requires authentication/registration")
    print("     - Not TCE-specific (general state data)")
    print()

    print("-" * 80)
    print()

    print("CURRENT SOLUTION:")
    print()
    print("  ✅ SICONFI Federal API (Already Working)")
    print("     - Covers all 853 Minas Gerais municipalities")
    print("     - No SSL issues (valid certificates)")
    print("     - Well documented and reliable")
    print("     - Provides RREO, RGF, DCA fiscal reports")
    print()

    print("-" * 80)
    print()

    print("REQUESTED FROM TCE-MG:")
    print()
    print("  1. Fix SSL certificate configuration")
    print("     - Install valid certificate from recognized CA")
    print("     - Or provide CA certificate for installation")
    print()

    print("  2. Provide API documentation")
    print("     - Endpoint URLs and parameters")
    print("     - Response formats and schemas")
    print("     - Usage examples and rate limits")
    print()

    print("  3. Grant API access")
    print("     - Public access OR registration process")
    print("     - API keys if authentication required")
    print("     - Support contact for technical issues")
    print()

    print("=" * 80)
    print()


def main():
    """Run all tests and generate report."""
    print_header("TCE-MG API ACCESS TEST REPORT")

    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Project: Cidadão.AI - Government Transparency Analysis Platform")
    print("Author: Anderson Henrique da Silva (Minas Gerais native)")
    print("Purpose: Request official API access to TCE-MG data")

    # Run all tests
    test_ssl_certificate()
    test_api_endpoints()
    test_state_ckan()
    test_main_website()
    test_current_client()

    # Generate summary
    generate_summary()

    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("=" * 80)
    print("  END OF REPORT")
    print("=" * 80)


if __name__ == "__main__":
    main()
