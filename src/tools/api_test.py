"""
Module: tools.api_test
Description: Testing utilities for government transparency APIs
Author: Anderson H. Silva
Date: 2025-01-15
"""

import asyncio
from src.core import json_utils
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from .transparency_api import TransparencyAPIClient, TransparencyAPIFilter
from ..core.config import settings
from ..core.exceptions import TransparencyAPIError, DataNotFoundError

logger = logging.getLogger(__name__)


class APITester:
    """Test suite for government transparency APIs."""
    
    def __init__(self):
        self.client = TransparencyAPIClient()
        self.test_results = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()
    
    def _log_test_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Log test result."""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        if success:
            logger.info(f"✅ {test_name}: PASSED", extra=details)
        else:
            logger.error(f"❌ {test_name}: FAILED", extra=details)
    
    async def test_api_connection(self) -> bool:
        """Test basic API connectivity."""
        try:
            # Test with minimal filters
            filters = TransparencyAPIFilter(
                ano=2024,
                tamanho_pagina=1
            )
            
            response = await self.client.get_expenses(filters)
            
            success = len(response.data) > 0
            self._log_test_result(
                "API Connection",
                success,
                {
                    "total_records": response.total_records,
                    "response_size": len(response.data)
                }
            )
            return success
            
        except Exception as e:
            self._log_test_result(
                "API Connection",
                False,
                {"error": str(e)}
            )
            return False
    
    async def test_contracts_endpoint(self) -> bool:
        """Test contracts endpoint."""
        try:
            # Test recent contracts
            filters = TransparencyAPIFilter(
                ano=2024,
                tamanho_pagina=5
            )
            
            response = await self.client.get_contracts(filters)
            
            success = isinstance(response.data, list)
            self._log_test_result(
                "Contracts Endpoint",
                success,
                {
                    "total_records": response.total_records,
                    "data_count": len(response.data),
                    "sample_fields": list(response.data[0].keys()) if response.data else []
                }
            )
            return success
            
        except Exception as e:
            self._log_test_result(
                "Contracts Endpoint",
                False,
                {"error": str(e)}
            )
            return False
    
    async def test_expenses_endpoint(self) -> bool:
        """Test expenses endpoint."""
        try:
            # Test recent expenses
            filters = TransparencyAPIFilter(
                ano=2024,
                mes=1,
                tamanho_pagina=5
            )
            
            response = await self.client.get_expenses(filters)
            
            success = isinstance(response.data, list)
            self._log_test_result(
                "Expenses Endpoint",
                success,
                {
                    "total_records": response.total_records,
                    "data_count": len(response.data),
                    "sample_fields": list(response.data[0].keys()) if response.data else []
                }
            )
            return success
            
        except Exception as e:
            self._log_test_result(
                "Expenses Endpoint",
                False,
                {"error": str(e)}
            )
            return False
    
    async def test_biddings_endpoint(self) -> bool:
        """Test biddings endpoint."""
        try:
            # Test recent biddings
            filters = TransparencyAPIFilter(
                ano=2024,
                tamanho_pagina=3
            )
            
            response = await self.client.get_biddings(filters)
            
            success = isinstance(response.data, list)
            self._log_test_result(
                "Biddings Endpoint",
                success,
                {
                    "total_records": response.total_records,
                    "data_count": len(response.data),
                    "sample_fields": list(response.data[0].keys()) if response.data else []
                }
            )
            return success
            
        except Exception as e:
            self._log_test_result(
                "Biddings Endpoint",
                False,
                {"error": str(e)}
            )
            return False
    
    async def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality."""
        try:
            # Make multiple rapid requests
            filters = TransparencyAPIFilter(
                ano=2024,
                tamanho_pagina=1
            )
            
            start_time = datetime.now()
            
            # Make 5 requests rapidly
            for i in range(5):
                await self.client.get_expenses(filters)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Should take some time due to rate limiting
            success = duration > 2  # At least 2 seconds for 5 requests
            
            self._log_test_result(
                "Rate Limiting",
                success,
                {
                    "requests_made": 5,
                    "duration_seconds": duration,
                    "avg_per_request": duration / 5
                }
            )
            return success
            
        except Exception as e:
            self._log_test_result(
                "Rate Limiting",
                False,
                {"error": str(e)}
            )
            return False
    
    async def test_data_quality(self) -> bool:
        """Test data quality and structure."""
        try:
            filters = TransparencyAPIFilter(
                ano=2024,
                tamanho_pagina=10
            )
            
            response = await self.client.get_contracts(filters)
            
            if not response.data:
                self._log_test_result(
                    "Data Quality",
                    False,
                    {"error": "No data returned"}
                )
                return False
            
            # Check data structure
            sample = response.data[0]
            required_fields = ['id', 'numero', 'objeto']  # Common contract fields
            
            has_required_fields = any(field in sample for field in required_fields)
            has_numeric_values = any(isinstance(v, (int, float)) for v in sample.values())
            has_text_values = any(isinstance(v, str) for v in sample.values())
            
            success = has_required_fields and has_numeric_values and has_text_values
            
            self._log_test_result(
                "Data Quality",
                success,
                {
                    "sample_fields": list(sample.keys()),
                    "has_required_fields": has_required_fields,
                    "has_numeric_values": has_numeric_values,
                    "has_text_values": has_text_values
                }
            )
            return success
            
        except Exception as e:
            self._log_test_result(
                "Data Quality",
                False,
                {"error": str(e)}
            )
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling with invalid requests."""
        try:
            # Test with invalid filters
            filters = TransparencyAPIFilter(
                ano=1900,  # Invalid year
                tamanho_pagina=1
            )
            
            try:
                await self.client.get_contracts(filters)
                # If no error, test fails
                success = False
                error_msg = "Expected error but got success"
            except (TransparencyAPIError, DataNotFoundError) as e:
                # Expected error
                success = True
                error_msg = str(e)
            except Exception as e:
                # Unexpected error
                success = False
                error_msg = f"Unexpected error: {str(e)}"
            
            self._log_test_result(
                "Error Handling",
                success,
                {"error_message": error_msg}
            )
            return success
            
        except Exception as e:
            self._log_test_result(
                "Error Handling",
                False,
                {"error": str(e)}
            )
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results."""
        logger.info("🚀 Starting API test suite...")
        
        # List of all test methods
        tests = [
            self.test_api_connection,
            self.test_contracts_endpoint,
            self.test_expenses_endpoint,
            self.test_biddings_endpoint,
            self.test_rate_limiting,
            self.test_data_quality,
            self.test_error_handling
        ]
        
        # Run all tests
        results = {}
        passed = 0
        total = len(tests)
        
        for test in tests:
            test_name = test.__name__.replace('test_', '').replace('_', ' ').title()
            try:
                success = await test()
                results[test_name] = success
                if success:
                    passed += 1
            except Exception as e:
                logger.error(f"Test {test_name} crashed: {str(e)}")
                results[test_name] = False
        
        # Summary
        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total) * 100,
            "results": results,
            "detailed_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"📊 Test suite completed: {passed}/{total} tests passed ({summary['success_rate']:.1f}%)")
        
        return summary


async def run_api_tests() -> Dict[str, Any]:
    """
    Convenience function to run all API tests.
    
    Returns:
        Test results summary
    """
    async with APITester() as tester:
        return await tester.run_all_tests()


async def quick_api_test() -> bool:
    """
    Quick API connectivity test.
    
    Returns:
        True if API is working, False otherwise
    """
    try:
        async with APITester() as tester:
            return await tester.test_api_connection()
    except Exception as e:
        logger.error(f"Quick API test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Run tests when executed directly
    async def main():
        results = await run_api_tests()
        print(json_utils.dumps(results, indent=2))
    
    asyncio.run(main())