#!/usr/bin/env python3
"""
Simple test to check HuggingFace Space deployment
"""

import asyncio
import httpx

async def test_hf_space():
    """Test HuggingFace Space is running."""
    
    print("🧪 TESTING HUGGINGFACE SPACE DEPLOYMENT")
    print("=" * 50)
    
    base_url = "https://neural-thinker-cidadao-ai-models.hf.space"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test health endpoint
            print("1️⃣ TESTING HEALTH ENDPOINT")
            print("-" * 30)
            
            response = await client.get(f"{base_url}/health")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ HuggingFace Space is healthy")
                print(f"Service: {health_data.get('service', 'unknown')}")
                print(f"Status: {health_data.get('status', 'unknown')}")
                print(f"Version: {health_data.get('version', 'unknown')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                print(f"Response: {response.text}")
            
            print()
            
            # Test root endpoint
            print("2️⃣ TESTING ROOT ENDPOINT")
            print("-" * 30)
            
            response = await client.get(f"{base_url}/")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Root endpoint accessible")
                # Don't print full HTML response
                if "html" in response.headers.get("content-type", ""):
                    print("📄 HTML interface available")
                else:
                    print(f"Response: {response.text[:200]}...")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
            
            print()
            
            # Test docs endpoint
            print("3️⃣ TESTING DOCS ENDPOINT")
            print("-" * 30)
            
            response = await client.get(f"{base_url}/docs")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ API docs accessible")
            else:
                print(f"⚠️ Docs not available: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("💡 HuggingFace Space may still be building...")
            return False
    
    print()
    print("🏁 HUGGINGFACE SPACE TEST COMPLETE")
    print("=" * 50)
    return True

if __name__ == "__main__":
    print("🤖 CIDADÃO.AI MODELS DEPLOYMENT TEST")
    print()
    
    try:
        success = asyncio.run(test_hf_space())
        if success:
            print("✅ Test completed successfully!")
        else:
            print("❌ Test failed!")
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")