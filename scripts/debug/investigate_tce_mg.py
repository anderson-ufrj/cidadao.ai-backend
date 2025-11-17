"""
Investigate TCE-MG API endpoints by analyzing the portal.

Author: Anderson Henrique da Silva
Created: 2025-11-14
License: Proprietary - All rights reserved
"""

import re

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def find_api_endpoints():
    """Find API endpoints by analyzing the portal HTML and JS files."""
    print("=" * 80)
    print("TCE-MG API Investigation")
    print("=" * 80)
    print()

    # Get main page
    print("1. Fetching main page...")
    response = requests.get(
        "https://dadosabertos.tce.mg.gov.br/", verify=False, timeout=10
    )
    html = response.text
    print(f"   Status: {response.status_code}")
    print(f"   Size: {len(html)} bytes")
    print()

    # Find JavaScript files
    print("2. Finding JavaScript files...")
    js_files = re.findall(r'src="(/[^"]+\.js)"', html)
    print(f"   Found: {len(js_files)} JS files")
    print()

    # Analyze first few JS files
    print("3. Analyzing JavaScript for API endpoints...")
    all_apis = set()

    for js_file in js_files[:10]:
        if js_file.startswith("/"):
            js_url = f"https://dadosabertos.tce.mg.gov.br{js_file}"
            try:
                js_response = requests.get(js_url, verify=False, timeout=10)
                js_content = js_response.text

                # Look for API URLs
                patterns = [
                    r'(https?://[a-zA-Z0-9.-]*tce\.mg\.gov\.br[^\s"\'`,;)}\]]+)',
                    r'baseUrl["\']?\s*[:=]\s*["\']([^"\']+)',
                    r'apiUrl["\']?\s*[:=]\s*["\']([^"\']+)',
                    r"/api/[a-zA-Z0-9/_-]+",
                    r"/ws/[a-zA-Z0-9/_-]+",
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, js_content)
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        if "/api" in match.lower() or "/ws" in match.lower():
                            all_apis.add(match)
            except Exception:
                pass

    if all_apis:
        print(f"   Found {len(all_apis)} potential API endpoints:")
        for api in sorted(all_apis):
            print(f"      {api}")
    else:
        print("   No API endpoints found in JS files")

    print()

    # Try common API patterns
    print("4. Testing common API patterns...")
    common_endpoints = [
        "/api/datasets",
        "/api/municipios",
        "/api/contratos",
        "/api/v1/datasets",
        "/api/v1/municipios",
        "/ws/datasets",
        "/ws/municipios",
    ]

    for endpoint in common_endpoints:
        url = f"https://dadosabertos.tce.mg.gov.br{endpoint}"
        try:
            test_response = requests.get(url, verify=False, timeout=5)
            if test_response.status_code != 404:
                print(f"   ✅ {endpoint} - Status: {test_response.status_code}")
        except Exception:
            pass

    print()

    # Check subdomain APIs
    print("5. Checking known TCE-MG subdomains...")
    subdomains = [
        "grafite.tce.mg.gov.br",
        "arabiasaudita.tce.mg.gov.br:8443",
        "argentina.tce.mg.gov.br:8443",
        "bronze.tce.mg.gov.br",
    ]

    for subdomain in subdomains:
        url = f"https://{subdomain}"
        try:
            sub_response = requests.get(url, verify=False, timeout=5)
            print(f"   {subdomain} - Status: {sub_response.status_code}")
        except Exception as e:
            print(f"   {subdomain} - Error: {str(e)[:50]}")

    print()
    print("=" * 80)
    print("Investigation complete")
    print("=" * 80)


if __name__ == "__main__":
    find_api_endpoints()
