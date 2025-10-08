"""
Example: Using Zumbi agent with dados.gov.br integration

This example demonstrates how the Zumbi agent can use the dados.gov.br
integration to enrich investigation data with open government datasets.
"""

import asyncio
import json
from datetime import datetime

from src.agents.zumbi import InvestigatorAgent, InvestigationRequest
from src.agents.deodoro import AgentContext


async def example_investigation_with_open_data():
    """
    Example of running an investigation with open data enrichment.
    """
    # Initialize the Zumbi agent
    agent = InvestigatorAgent()
    await agent.initialize()
    
    # Create investigation request with open data enrichment enabled
    request = InvestigationRequest(
        query="Investigate health ministry contracts for anomalies",
        organization_codes=["26000"],  # Ministry of Health
        anomaly_types=["price_anomaly", "vendor_concentration"],
        max_records=50,
        enable_open_data_enrichment=True  # Enable dados.gov.br integration
    )
    
    # Create agent context
    context = AgentContext(
        investigation_id=f"inv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        user_id="example_user",
        correlation_id="example_001"
    )
    
    # Create agent message
    message = {
        "action": "investigate",
        "payload": request.model_dump()
    }
    
    print("Starting investigation with open data enrichment...")
    print(f"Investigation ID: {context.investigation_id}")
    print(f"Query: {request.query}")
    print(f"Organization: {request.organization_codes}")
    print("-" * 50)
    
    # Process the investigation
    response = await agent.process(message, context)
    
    # Display results
    if response.status == "completed":
        result = response.result
        
        print(f"\n✅ Investigation Status: {result['status']}")
        print(f"📊 Records Analyzed: {result['metadata']['records_analyzed']}")
        print(f"⚠️  Anomalies Found: {result['metadata']['anomalies_detected']}")
        
        # Show anomalies
        if result['anomalies']:
            print("\n🔍 Detected Anomalies:")
            for i, anomaly in enumerate(result['anomalies'], 1):
                print(f"\n{i}. {anomaly['anomaly_type'].upper()}")
                print(f"   Severity: {anomaly['severity']:.2f}")
                print(f"   Confidence: {anomaly['confidence']:.2f}")
                print(f"   Description: {anomaly['description']}")
                
                # Check if open data was found
                if anomaly.get('evidence', {}).get('open_data_available'):
                    datasets = anomaly['evidence'].get('related_datasets', [])
                    if datasets:
                        print(f"   📂 Related Open Datasets Found: {len(datasets)}")
                        for ds in datasets[:2]:  # Show first 2 datasets
                            print(f"      - {ds.get('title', 'Unknown dataset')}")
        
        # Show summary
        print(f"\n📋 Investigation Summary:")
        print(f"   Total Contracts: {result['summary']['total_records']}")
        print(f"   Anomalies Found: {result['summary']['anomalies_found']}")
        
        # Check for open data enrichment
        if 'open_data_stats' in result['summary']:
            stats = result['summary']['open_data_stats']
            print(f"\n📊 Open Data Enrichment:")
            print(f"   Organizations with Open Data: {stats['organizations_with_data']}")
            print(f"   Total Datasets Referenced: {stats['total_datasets']}")
            
    else:
        print(f"\n❌ Investigation Failed: {response.error}")
    
    # Cleanup
    await agent.shutdown()


async def example_compare_with_without_open_data():
    """
    Compare investigation results with and without open data enrichment.
    """
    agent = InvestigatorAgent()
    await agent.initialize()
    
    # Base request parameters
    base_params = {
        "query": "Find suspicious contracts in education sector",
        "organization_codes": ["25000"],  # Ministry of Education
        "anomaly_types": ["price_anomaly"],
        "max_records": 30
    }
    
    # Context
    context = AgentContext(
        investigation_id="comparison_test",
        user_id="example_user",
        correlation_id="compare_001"
    )
    
    print("🔬 Comparing investigations with and without open data enrichment\n")
    
    # Run without open data
    print("1️⃣ Investigation WITHOUT open data enrichment:")
    request1 = InvestigationRequest(**base_params, enable_open_data_enrichment=False)
    message1 = {"action": "investigate", "payload": request1.model_dump()}
    
    start_time = asyncio.get_event_loop().time()
    response1 = await agent.process(message1, context)
    time1 = asyncio.get_event_loop().time() - start_time
    
    anomalies1 = len(response1.result.get('anomalies', []))
    print(f"   ⏱️  Time: {time1:.2f}s")
    print(f"   ⚠️  Anomalies found: {anomalies1}")
    
    # Run with open data
    print("\n2️⃣ Investigation WITH open data enrichment:")
    request2 = InvestigationRequest(**base_params, enable_open_data_enrichment=True)
    message2 = {"action": "investigate", "payload": request2.model_dump()}
    
    start_time = asyncio.get_event_loop().time()
    response2 = await agent.process(message2, context)
    time2 = asyncio.get_event_loop().time() - start_time
    
    anomalies2 = len(response2.result.get('anomalies', []))
    datasets_found = 0
    
    # Count datasets found
    for anomaly in response2.result.get('anomalies', []):
        if anomaly.get('evidence', {}).get('related_datasets'):
            datasets_found += len(anomaly['evidence']['related_datasets'])
    
    print(f"   ⏱️  Time: {time2:.2f}s")
    print(f"   ⚠️  Anomalies found: {anomalies2}")
    print(f"   📂 Open datasets referenced: {datasets_found}")
    
    print("\n📊 Comparison Summary:")
    print(f"   Time difference: +{time2-time1:.2f}s ({((time2-time1)/time1)*100:.1f}% slower)")
    print(f"   Additional context gained: {datasets_found} datasets")
    print(f"   Enhanced investigation: {'Yes' if datasets_found > 0 else 'No'}")
    
    await agent.shutdown()


async def example_analyze_topic_availability():
    """
    Example of using dados.gov.br to analyze data availability before investigation.
    """
    from src.tools.dados_gov_tool import DadosGovTool
    
    tool = DadosGovTool()
    
    print("🔍 Analyzing open data availability for different government topics\n")
    
    topics = ["saúde", "educação", "segurança pública", "transportes"]
    
    for topic in topics:
        print(f"\n📋 Topic: {topic.upper()}")
        
        result = await tool._execute(
            action="analyze",
            topic=topic
        )
        
        if result.success:
            data = result.data
            print(f"   Total datasets: {data['total_datasets']}")
            print(f"   Coverage: Federal({data['coverage']['federal']}), "
                  f"State({data['coverage']['state']}), "
                  f"Municipal({data['coverage']['municipal']})")
            print(f"   Formats: {', '.join(data['available_formats'][:5])}")
            
            if data['top_organizations']:
                print(f"   Top publishers:")
                for org, count in list(data['top_organizations'].items())[:3]:
                    print(f"      - {org}: {count} datasets")
        else:
            print(f"   ❌ Error: {result.error}")
    
    await tool.service.close()


if __name__ == "__main__":
    # Run examples
    print("=" * 70)
    print("CIDADÃO.AI - Zumbi Agent with dados.gov.br Integration Examples")
    print("=" * 70)
    
    # Choose which example to run
    examples = {
        "1": ("Basic investigation with open data", example_investigation_with_open_data),
        "2": ("Compare with/without enrichment", example_compare_with_without_open_data),
        "3": ("Analyze topic data availability", example_analyze_topic_availability),
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")
    
    choice = input("\nSelect example (1-3): ").strip()
    
    if choice in examples:
        _, example_func = examples[choice]
        asyncio.run(example_func())
    else:
        print("Invalid choice. Running default example...")
        asyncio.run(example_investigation_with_open_data())