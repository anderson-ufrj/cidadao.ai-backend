"""
Advanced Usage Examples for Transparency APIs

Demonstrates advanced features including caching, validation, health monitoring,
and anomaly detection.

Author: Anderson Henrique da Silva
Created: 2025-10-09 15:30:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

import asyncio

from src.services.transparency_apis import registry
from src.services.transparency_apis.cache import get_cache
from src.services.transparency_apis.health_check import get_health_monitor
from src.services.transparency_apis.validators import AnomalyDetector, DataValidator


async def example_1_health_monitoring():
    """Example 1: Monitor API health."""
    print("=== Example 1: Health Monitoring ===\n")

    monitor = get_health_monitor()

    # Check specific API
    print("Checking TCE-PE health...")
    result = await monitor.check_api("PE-tce")

    print(f"Status: {result.status.value}")
    print(f"Response time: {result.response_time * 1000:.2f}ms")
    if result.error:
        print(f"Error: {result.error}")
    print()

    # Check all APIs
    print("Checking all APIs...")
    all_results = await monitor.check_all_apis()

    healthy_count = sum(1 for r in all_results.values() if r.status.value == "healthy")
    print(f"✅ Healthy: {healthy_count}/{len(all_results)}")
    print()

    # Generate comprehensive report
    print("Generating health report...")
    report = await monitor.generate_report()

    print(f"Overall health: {report['overall_health_percentage']:.1f}%")
    print(f"Status: {report['overall_status']}")
    print(f"Summary: {report['summary']}")
    print()


async def example_2_caching():
    """Example 2: Using caching layer."""
    print("=== Example 2: Caching Layer ===\n")

    cache = get_cache()
    pe_tce = registry.get_client("PE-tce")

    if pe_tce:
        # First call (cache miss)
        print("First call (fetching from API)...")
        import time

        start = time.time()
        contracts = await pe_tce.get_contracts(year=2024)
        duration1 = time.time() - start

        # Cache the result
        cache.set_contracts("PE-tce", contracts, year=2024)

        # Second call (cache hit)
        print("Second call (from cache)...")
        start = time.time()
        cached_contracts = cache.get_contracts("PE-tce", year=2024)
        duration2 = time.time() - start

        print(f"API call: {duration1 * 1000:.2f}ms")
        print(f"Cache call: {duration2 * 1000:.2f}ms")
        print(f"Speedup: {duration1 / duration2:.0f}x faster")
        print()

        # Cache stats
        stats = cache.get_stats()
        print(f"Cache stats: {stats}")
        print()


async def example_3_data_validation():
    """Example 3: Validate contract data."""
    print("=== Example 3: Data Validation ===\n")

    pe_tce = registry.get_client("PE-tce")

    if pe_tce:
        contracts = await pe_tce.get_contracts(year=2024)

        # Validate batch
        print(f"Validating {len(contracts)} contracts...")
        validation_result = DataValidator.validate_batch(
            contracts, data_type="contract"
        )

        print(f"Valid: {validation_result['valid']}")
        print(f"Invalid: {validation_result['invalid']}")
        print(f"Validation rate: {validation_result['validation_rate'] * 100:.1f}%")

        # Show common issues
        if validation_result["common_issues"]:
            print("\nMost common issues:")
            for issue, count in list(validation_result["common_issues"].items())[:3]:
                print(f"  - {issue}: {count} occurrences")

        print()


async def example_4_anomaly_detection():
    """Example 4: Detect anomalies in contract data."""
    print("=== Example 4: Anomaly Detection ===\n")

    pe_tce = registry.get_client("PE-tce")

    if pe_tce:
        contracts = await pe_tce.get_contracts(year=2024)

        # Detect value outliers
        print("Detecting value outliers...")
        outliers = AnomalyDetector.detect_value_outliers(contracts, std_threshold=2.5)

        print(f"Found {len(outliers)} outliers\n")

        # Display top 3 outliers
        for i, outlier in enumerate(outliers[:3], 1):
            print(f"Outlier {i}:")
            print(f"  Contract: {outlier.get('contract_id')}")
            print(f"  Supplier: {outlier.get('supplier_name')}")
            print(f"  Value: R$ {outlier.get('value', 0):,.2f}")
            print(f"  Anomaly score: {outlier.get('anomaly_score', 0):.2f}")
            print()

        # Detect supplier concentration
        print("Analyzing supplier concentration...")
        concentration = AnomalyDetector.detect_supplier_concentration(contracts)

        if concentration.get("concentrated"):
            print("⚠️  High concentration detected!")
            print(
                f"Top 3 suppliers: {concentration['concentration_ratio'] * 100:.1f}% of total value"
            )

            print("\nTop suppliers:")
            for supplier in concentration["top_suppliers"]:
                print(
                    f"  - {supplier['supplier_name']}: R$ {supplier['total_value']:,.2f} ({supplier['percentage'] * 100:.1f}%)"
                )
        else:
            print("✅ Healthy supplier distribution")

        print()

        # Detect potential duplicates
        print("Detecting potential duplicate contracts...")
        duplicates = AnomalyDetector.detect_duplicate_contracts(contracts)

        print(f"Found {len(duplicates)} potential duplicates\n")

        if duplicates:
            for i, dup in enumerate(duplicates[:2], 1):
                print(f"Duplicate pair {i}:")
                print(
                    f"  Contract 1: {dup['contract1'].get('contract_id')} - R$ {dup['contract1'].get('value', 0):,.2f}"
                )
                print(
                    f"  Contract 2: {dup['contract2'].get('contract_id')} - R$ {dup['contract2'].get('value', 0):,.2f}"
                )
                print(f"  Similarity: {dup['similarity'] * 100:.1f}%")
                print()


async def example_5_comprehensive_analysis():
    """Example 5: Comprehensive analysis pipeline."""
    print("=== Example 5: Comprehensive Analysis Pipeline ===\n")

    # 1. Check API health
    print("Step 1: Health check...")
    monitor = get_health_monitor()
    result = await monitor.check_api("PE-tce")

    if result.status.value != "healthy":
        print(f"❌ API unhealthy: {result.error}")
        return

    print("✅ API healthy")

    # 2. Fetch data (with caching)
    print("\nStep 2: Fetching data...")
    cache = get_cache()
    cached_data = cache.get_contracts("PE-tce", year=2024)

    if cached_data:
        print("✅ Using cached data")
        contracts = cached_data
    else:
        pe_tce = registry.get_client("PE-tce")
        contracts = await pe_tce.get_contracts(year=2024)
        cache.set_contracts("PE-tce", contracts, year=2024)
        print("✅ Data fetched and cached")

    # 3. Validate data
    print("\nStep 3: Validating data...")
    validation = DataValidator.validate_batch(contracts, data_type="contract")
    print(f"✅ Validation rate: {validation['validation_rate'] * 100:.1f}%")

    # 4. Detect anomalies
    print("\nStep 4: Detecting anomalies...")
    outliers = AnomalyDetector.detect_value_outliers(contracts)
    concentration = AnomalyDetector.detect_supplier_concentration(contracts)
    duplicates = AnomalyDetector.detect_duplicate_contracts(contracts)

    print(f"✅ Found {len(outliers)} outliers")
    print(
        f"✅ Supplier concentration: {concentration['concentration_ratio'] * 100:.1f}%"
    )
    print(f"✅ Found {len(duplicates)} potential duplicates")

    # 5. Generate summary
    print("\n" + "=" * 50)
    print("ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Total contracts analyzed: {len(contracts)}")
    print(f"Valid contracts: {validation['valid']}")
    print(f"Anomalies detected: {len(outliers)}")
    print(
        f"High-risk concentration: {'Yes' if concentration.get('concentrated') else 'No'}"
    )
    print(f"Potential duplicates: {len(duplicates)}")
    print()


async def main():
    """Run all advanced examples."""
    print("╔════════════════════════════════════════════╗")
    print("║  Transparency APIs - Advanced Examples    ║")
    print("╚════════════════════════════════════════════╝\n")

    await example_1_health_monitoring()
    await example_2_caching()
    await example_3_data_validation()
    await example_4_anomaly_detection()
    await example_5_comprehensive_analysis()

    print("✅ All advanced examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
