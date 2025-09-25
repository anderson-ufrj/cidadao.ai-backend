"""
Module: utils.cors_validator
Description: CORS configuration validator and tester
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import httpx
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from src.core import get_logger
from src.core.config import settings

logger = get_logger(__name__)


class CORSValidator:
    """Validate and test CORS configuration."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize CORS validator."""
        self.base_url = base_url
        self.test_endpoints = [
            "/",
            "/health",
            "/api/v1/chat/message",
            "/api/v1/investigations/analyze",
            "/api/v1/auth/login"
        ]
    
    async def validate_origin(
        self,
        origin: str,
        endpoint: str = "/health",
        method: str = "GET"
    ) -> Tuple[bool, Dict[str, str]]:
        """
        Validate if origin is allowed by CORS policy.
        
        Returns:
            Tuple of (is_allowed, cors_headers)
        """
        headers = {
            "Origin": origin,
            "User-Agent": "CORS-Validator/1.0"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Send preflight request
                preflight_response = await client.options(
                    f"{self.base_url}{endpoint}",
                    headers={
                        **headers,
                        "Access-Control-Request-Method": method,
                        "Access-Control-Request-Headers": "Content-Type, Authorization"
                    }
                )
                
                # Extract CORS headers
                cors_headers = {}
                for header in preflight_response.headers:
                    if header.lower().startswith("access-control-"):
                        cors_headers[header] = preflight_response.headers[header]
                
                # Check if origin is allowed
                allowed_origin = cors_headers.get("Access-Control-Allow-Origin", "")
                is_allowed = allowed_origin == origin or allowed_origin == "*"
                
                logger.info(
                    "cors_validation_result",
                    origin=origin,
                    endpoint=endpoint,
                    is_allowed=is_allowed,
                    cors_headers=cors_headers
                )
                
                return is_allowed, cors_headers
                
            except Exception as e:
                logger.error(
                    "cors_validation_error",
                    origin=origin,
                    endpoint=endpoint,
                    error=str(e)
                )
                return False, {}
    
    async def test_all_origins(self) -> Dict[str, Dict[str, any]]:
        """Test all configured origins."""
        results = {}
        
        # Test configured origins
        for origin in settings.cors_origins:
            if origin == "*" or origin.startswith("https://*."):
                # Skip wildcards
                continue
                
            is_allowed, headers = await self.validate_origin(origin)
            results[origin] = {
                "allowed": is_allowed,
                "headers": headers
            }
        
        # Test common Vercel preview URLs
        vercel_test_origins = [
            "https://cidadao-ai-frontend-abc123-neural-thinker.vercel.app",
            "https://cidadao-ai-preview-xyz789-neural-thinker.vercel.app"
        ]
        
        for origin in vercel_test_origins:
            is_allowed, headers = await self.validate_origin(origin)
            results[origin] = {
                "allowed": is_allowed,
                "headers": headers,
                "note": "Vercel preview URL test"
            }
        
        return results
    
    def generate_nginx_config(self) -> str:
        """Generate nginx CORS configuration."""
        config = """# CORS configuration for Cidadão.AI
# Add this to your nginx server block

# Handle preflight requests
if ($request_method = 'OPTIONS') {
    add_header 'Access-Control-Allow-Origin' '$http_origin' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, PATCH, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With,X-API-Key' always;
    add_header 'Access-Control-Allow-Credentials' 'true' always;
    add_header 'Access-Control-Max-Age' 86400 always;
    add_header 'Content-Length' 0;
    add_header 'Content-Type' 'text/plain charset=UTF-8';
    return 204;
}

# Add CORS headers to responses
add_header 'Access-Control-Allow-Origin' '$http_origin' always;
add_header 'Access-Control-Allow-Credentials' 'true' always;
add_header 'Access-Control-Expose-Headers' 'X-RateLimit-Limit,X-RateLimit-Remaining,X-RateLimit-Reset,X-Request-ID,X-Total-Count' always;
"""
        return config
    
    def generate_cloudflare_headers(self) -> List[Dict[str, str]]:
        """Generate Cloudflare transform rules for CORS."""
        rules = []
        
        # Allow Vercel origins
        rules.append({
            "name": "CORS - Vercel Origins",
            "expression": 'http.request.headers["origin"][0] matches "^https://[a-zA-Z0-9-]+\\.vercel\\.app$"',
            "headers": {
                "Access-Control-Allow-Origin": '${http.request.headers["origin"][0]}',
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS"
            }
        })
        
        # Allow localhost for development
        rules.append({
            "name": "CORS - Localhost Development",
            "expression": 'http.request.headers["origin"][0] in {"http://localhost:3000", "http://127.0.0.1:3000"}',
            "headers": {
                "Access-Control-Allow-Origin": '${http.request.headers["origin"][0]}',
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS"
            }
        })
        
        return rules
    
    async def test_credentials_flow(
        self,
        origin: str = "https://cidadao-ai-frontend.vercel.app"
    ) -> Dict[str, any]:
        """Test CORS with credentials (cookies/auth)."""
        results = {
            "origin": origin,
            "tests": {}
        }
        
        async with httpx.AsyncClient() as client:
            # Test login endpoint
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/login",
                    headers={"Origin": origin},
                    json={"email": "test@example.com", "password": "test"},
                    follow_redirects=False
                )
                
                results["tests"]["login"] = {
                    "status": response.status_code,
                    "cors_origin": response.headers.get("Access-Control-Allow-Origin"),
                    "cors_credentials": response.headers.get("Access-Control-Allow-Credentials"),
                    "has_cookies": "Set-Cookie" in response.headers
                }
            except Exception as e:
                results["tests"]["login"] = {"error": str(e)}
            
            # Test authenticated endpoint
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/chat/history",
                    headers={
                        "Origin": origin,
                        "Authorization": "Bearer test-token"
                    }
                )
                
                results["tests"]["authenticated"] = {
                    "status": response.status_code,
                    "cors_origin": response.headers.get("Access-Control-Allow-Origin"),
                    "cors_credentials": response.headers.get("Access-Control-Allow-Credentials")
                }
            except Exception as e:
                results["tests"]["authenticated"] = {"error": str(e)}
        
        return results


# CLI utility
async def main():
    """Run CORS validation tests."""
    import asyncio
    import json
    
    validator = CORSValidator()
    
    print("🔍 Testing CORS configuration...\n")
    
    # Test all origins
    print("1. Testing configured origins:")
    results = await validator.test_all_origins()
    for origin, result in results.items():
        status = "✅" if result["allowed"] else "❌"
        print(f"  {status} {origin}")
    
    # Test credentials flow
    print("\n2. Testing credentials flow:")
    creds_results = await validator.test_credentials_flow()
    print(json.dumps(creds_results, indent=2))
    
    # Generate configs
    print("\n3. Generated nginx configuration:")
    print(validator.generate_nginx_config())
    
    print("\n4. Cloudflare transform rules:")
    cf_rules = validator.generate_cloudflare_headers()
    print(json.dumps(cf_rules, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())