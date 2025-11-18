#!/usr/bin/env python3
"""
Test script for Grafana Cloud integration.

Tests:
1. Configuration validation
2. Metrics push
3. Authentication

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brasil
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_grafana_cloud():
    """Test Grafana Cloud integration."""
    print("🔍 Testing Grafana Cloud Integration\n")

    # Check environment variables
    print("1️⃣ Checking environment variables...")
    required_vars = [
        "GRAFANA_CLOUD_ENABLED",
        "GRAFANA_CLOUD_URL",
        "GRAFANA_CLOUD_USER",
        "GRAFANA_CLOUD_KEY",
    ]

    config_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "PASSWORD" in var:
                display_value = (
                    f"{value[:10]}...{value[-5:]}" if len(value) > 15 else "***"
                )
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: NOT SET")
            config_ok = False

    if not config_ok:
        print("\n❌ Configuration incomplete. Set missing variables in .env")
        print("\nExample:")
        print("   GRAFANA_CLOUD_ENABLED=true")
        print(
            "   GRAFANA_CLOUD_URL=https://prometheus-prod-XX.grafana.net/api/prom/push"
        )
        print("   GRAFANA_CLOUD_USER=123456")
        print("   GRAFANA_CLOUD_KEY=glc_xxx...")
        return False

    # Test pusher initialization
    print("\n2️⃣ Initializing Grafana Cloud pusher...")
    try:
        from src.infrastructure.observability.grafana_cloud_pusher import (
            GrafanaCloudPusher,
        )

        pusher = GrafanaCloudPusher()
        print("   ✅ Pusher initialized")
        print(f"   - Enabled: {pusher.enabled}")
        print(f"   - Push interval: {pusher.interval}s")
        print(f"   - Timeout: {pusher.timeout}s")
    except Exception as e:
        print(f"   ❌ Failed to initialize pusher: {e}")
        return False

    # Test configuration validation
    print("\n3️⃣ Validating configuration...")
    if pusher._validate_config():
        print("   ✅ Configuration valid")
    else:
        print("   ❌ Configuration invalid")
        return False

    # Generate sample metrics
    print("\n4️⃣ Generating sample metrics...")
    try:
        from src.infrastructure.observability.metrics import (
            agent_tasks_counter,
            http_requests_counter,
        )

        # Increment some test metrics
        agent_tasks_counter.labels(
            agent_name="test_agent", task_type="test", status="success"
        ).inc()

        http_requests_counter.labels(method="GET", endpoint="/test", status=200).inc()

        print("   ✅ Sample metrics generated")
    except Exception as e:
        print(f"   ⚠️  Could not generate metrics: {e}")

    # Test metrics push
    print("\n5️⃣ Testing metrics push to Grafana Cloud...")
    try:
        success = await pusher.push_metrics()
        if success:
            print("   ✅ Metrics pushed successfully!")
            print("\n📊 Next steps:")
            print("   1. Open Grafana Cloud: https://yourstack.grafana.net")
            print("   2. Go to Explore")
            print('   3. Query: up{job="cidadao-ai-backend"}')
            print("   4. You should see metrics from the last minute")
        else:
            print("   ❌ Failed to push metrics")
            return False
    except Exception as e:
        print(f"   ❌ Push failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n✅ All tests passed!")
    print("\n🎯 Grafana Cloud integration is working correctly")
    print("\n📚 Next steps:")
    print("   1. Deploy to Railway: git push origin main")
    print("   2. Set environment variables in Railway dashboard")
    print("   3. Import dashboards from monitoring/grafana/dashboards/")
    print("   4. Monitor metrics in Grafana Cloud")

    return True


if __name__ == "__main__":
    # Load .env if exists
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed. Make sure env vars are set.")

    # Run test
    result = asyncio.run(test_grafana_cloud())
    sys.exit(0 if result else 1)
