#!/usr/bin/env python3
"""
Test script for Models API integration

Test communication between backend and models API.
"""

import asyncio
import logging
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.core import settings
from src.tools.models_client import ModelsClient, get_models_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_models_integration():
    """Test complete models integration."""

    print("🧪 TESTING CIDADÃO.AI MODELS INTEGRATION")
    print("=" * 50)

    # Display configuration
    print(f"📡 Models API URL: {settings.models_api_url}")
    print(f"⏱️ Timeout: {settings.models_api_timeout}s")
    print(f"🔄 Fallback enabled: {settings.models_fallback_local}")
    print(f"⚡ Circuit breaker: {settings.models_circuit_breaker_failures} failures")
    print()

    # Test 1: Health check
    print("1️⃣ TESTING HEALTH CHECK")
    print("-" * 30)

    async with ModelsClient() as client:
        health = await client.health_check()
        print(f"Health status: {health.get('status', 'unknown')}")

        if health.get("status") == "healthy":
            print("✅ Models API is healthy")
        else:
            print(f"⚠️ Models API unhealthy: {health.get('error', 'Unknown error')}")
        print()

        # Test 2: Anomaly detection
        print("2️⃣ TESTING ANOMALY DETECTION")
        print("-" * 30)

        sample_contracts = [
            {
                "id": "CT001",
                "description": "Aquisição de computadores",
                "value": 50000.0,
                "supplier": "Tech Company A",
                "date": "2024-01-15",
                "organ": "Ministry of Education",
            },
            {
                "id": "CT002",
                "description": "Aquisição de computadores",
                "value": 500000.0,  # Potential anomaly - 10x higher
                "supplier": "Tech Company B",
                "date": "2024-01-20",
                "organ": "Ministry of Education",
            },
        ]

        try:
            result = await client.detect_anomalies(sample_contracts, threshold=0.7)
            print(f"Total contracts analyzed: {result['total_analyzed']}")
            print(f"Anomalies found: {result['anomalies_found']}")
            print(f"Confidence score: {result['confidence_score']:.2f}")

            source = result.get("source", "api")
            if source == "api":
                print("✅ Used Models API successfully")
            else:
                print("🔄 Used local fallback")

            if result["anomalies_found"] > 0:
                print("🔍 Anomalies detected:")
                for anomaly in result["anomalies"][:3]:  # Show first 3
                    print(
                        f"  - {anomaly.get('contract_id', 'Unknown')}: {anomaly.get('anomaly_type', 'Unknown type')}"
                    )

        except Exception as e:
            print(f"❌ Anomaly detection failed: {e}")

        print()

        # Test 3: Pattern analysis
        print("3️⃣ TESTING PATTERN ANALYSIS")
        print("-" * 30)

        try:
            result = await client.analyze_patterns(
                data={"contracts": sample_contracts}, analysis_type="temporal"
            )
            print(f"Patterns found: {result['pattern_count']}")
            print(f"Analysis confidence: {result['confidence']:.2f}")

            if result["insights"]:
                print("💡 Insights:")
                for insight in result["insights"]:
                    print(f"  - {insight}")

        except Exception as e:
            print(f"❌ Pattern analysis failed: {e}")

        print()

        # Test 4: Spectral analysis
        print("4️⃣ TESTING SPECTRAL ANALYSIS")
        print("-" * 30)

        try:
            time_series = [100000, 150000, 120000, 200000, 180000, 300000, 250000]
            result = await client.analyze_spectral(time_series, sampling_rate=1.0)

            print(f"Dominant frequency: {result['dominant_frequency']:.3f}")
            print(f"Periodic patterns found: {len(result['periodic_patterns'])}")

            if result["periodic_patterns"]:
                print("📈 Periodic patterns:")
                for pattern in result["periodic_patterns"]:
                    print(
                        f"  - Frequency: {pattern['frequency']:.3f}, Period: {pattern.get('period', 'unknown')}"
                    )

        except Exception as e:
            print(f"❌ Spectral analysis failed: {e}")

    print()
    print("🏁 INTEGRATION TEST COMPLETE")
    print("=" * 50)


def test_singleton_client():
    """Test singleton client pattern."""
    print("5️⃣ TESTING SINGLETON PATTERN")
    print("-" * 30)

    client1 = get_models_client()
    client2 = get_models_client()

    if client1 is client2:
        print("✅ Singleton pattern working correctly")
    else:
        print("❌ Singleton pattern failed")

    print(f"Client base URL: {client1.base_url}")
    print(f"Fallback enabled: {client1.enable_fallback}")
    print()


if __name__ == "__main__":
    print("🤖 CIDADÃO.AI MODELS INTEGRATION TEST")
    print()

    # Test singleton first
    test_singleton_client()

    # Test async integration
    try:
        asyncio.run(test_models_integration())
        print("✅ All tests completed successfully!")
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
