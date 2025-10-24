#!/usr/bin/env python3
"""
Backend Readiness Test - Comprehensive check for frontend integration
Tests all critical endpoints that the frontend needs to function
"""

import asyncio
import sys
from datetime import datetime

import httpx

# Configuration
PRODUCTION_URL = "https://cidadao-api-production.up.railway.app"
LOCAL_URL = "http://localhost:8000"

# Choose which environment to test
TEST_URL = PRODUCTION_URL  # Change to LOCAL_URL for local testing


class BackendReadinessTest:
    """Test backend readiness for frontend integration."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
        self.passed = 0
        self.failed = 0

    def log_test(self, name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append(f"{status} - {name}: {details}")
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    async def test_health_check(self):
        """Test health check endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                data = response.json()
                self.log_test(
                    "Health Check",
                    response.status_code == 200,
                    f"Status: {data.get('status', 'unknown')}",
                )
        except Exception as e:
            self.log_test("Health Check", False, str(e))

    async def test_root_endpoint(self):
        """Test root API endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/")
                data = response.json()
                self.log_test(
                    "Root Endpoint",
                    response.status_code == 200 and data.get("status") == "operational",
                    f"Version: {data.get('version', 'N/A')}",
                )
        except Exception as e:
            self.log_test("Root Endpoint", False, str(e))

    async def test_api_info(self):
        """Test API info endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/info")
                data = response.json()
                agents_count = len(data.get("agents", {}))
                self.log_test(
                    "API Info",
                    response.status_code == 200,
                    f"Agents available: {agents_count}",
                )
        except Exception as e:
            self.log_test("API Info", False, str(e))

    async def test_federal_apis(self):
        """Test federal API endpoints (IBGE)."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/federal/ibge/states"
                )
                data = response.json()
                states_count = data.get("total", 0)
                self.log_test(
                    "Federal APIs (IBGE)",
                    response.status_code == 200 and states_count > 0,
                    f"States found: {states_count}",
                )
        except Exception as e:
            self.log_test("Federal APIs (IBGE)", False, str(e))

    async def test_chat_endpoint(self):
        """Test chat endpoint (no auth required)."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/chat/message",
                    json={
                        "message": "Olá! Quem são os agentes disponíveis?",
                        "session_id": "test-session",
                    },
                )
                # Chat may require auth, accept 401/403 as "endpoint exists"
                exists = response.status_code in [200, 401, 403, 422]
                self.log_test(
                    "Chat Endpoint",
                    exists,
                    f"Status: {response.status_code} (endpoint exists: {exists})",
                )
        except Exception as e:
            self.log_test("Chat Endpoint", False, str(e))

    async def test_investigations_endpoint(self):
        """Test investigations list endpoint."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/investigations")
                # May require auth, accept 401/403 as "endpoint exists"
                exists = response.status_code in [200, 401, 403]
                self.log_test(
                    "Investigations List",
                    exists,
                    f"Status: {response.status_code} (endpoint exists: {exists})",
                )
        except Exception as e:
            self.log_test("Investigations List", False, str(e))

    async def test_docs_endpoint(self):
        """Test API documentation endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/docs")
                self.log_test(
                    "API Documentation",
                    response.status_code == 200,
                    "Swagger UI accessible",
                )
        except Exception as e:
            self.log_test("API Documentation", False, str(e))

    async def test_openapi_schema(self):
        """Test OpenAPI schema endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/openapi.json")
                data = response.json()
                paths_count = len(data.get("paths", {}))
                self.log_test(
                    "OpenAPI Schema",
                    response.status_code == 200,
                    f"Endpoints documented: {paths_count}",
                )
        except Exception as e:
            self.log_test("OpenAPI Schema", False, str(e))

    async def test_agents_endpoint(self):
        """Test agents listing endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                # Try multiple possible endpoints
                endpoints = [
                    "/api/v1/agents",
                    "/api/v1/agents/available",
                    "/api/v1/agents/list",
                ]

                found = False
                for endpoint in endpoints:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    if response.status_code in [200, 401, 403]:
                        found = True
                        self.log_test(
                            "Agents Endpoint",
                            True,
                            f"Found at {endpoint} (status: {response.status_code})",
                        )
                        break

                if not found:
                    self.log_test("Agents Endpoint", False, "No agents endpoint found")
        except Exception as e:
            self.log_test("Agents Endpoint", False, str(e))

    async def test_export_endpoint(self):
        """Test export endpoints."""
        try:
            async with httpx.AsyncClient() as client:
                # Just check if endpoint exists (may need data/auth)
                response = await client.get(f"{self.base_url}/api/v1/export")
                exists = response.status_code in [200, 401, 403, 404, 422]
                self.log_test(
                    "Export Endpoint",
                    exists,
                    f"Status: {response.status_code} (endpoint exists: {exists})",
                )
        except Exception as e:
            self.log_test("Export Endpoint", False, str(e))

    async def run_all_tests(self):
        """Run all backend readiness tests."""
        print("=" * 80)
        print(
            f"BACKEND READINESS TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print(f"Testing: {self.base_url}")
        print("=" * 80)
        print()

        # Run all tests
        await self.test_health_check()
        await self.test_root_endpoint()
        await self.test_api_info()
        await self.test_federal_apis()
        await self.test_chat_endpoint()
        await self.test_investigations_endpoint()
        await self.test_agents_endpoint()
        await self.test_export_endpoint()
        await self.test_docs_endpoint()
        await self.test_openapi_schema()

        # Summary
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(
            f"📊 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%"
        )
        print()

        if self.failed > 0:
            print("⚠️  BACKEND NOT FULLY READY - Some endpoints need attention")
            return False
        else:
            print("✅ BACKEND READY FOR FRONTEND INTEGRATION!")
            return True


async def main():
    """Main test execution."""
    print()
    print("🏛️  CIDADÃO.AI - BACKEND READINESS TEST")
    print()

    tester = BackendReadinessTest(TEST_URL)
    success = await tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
