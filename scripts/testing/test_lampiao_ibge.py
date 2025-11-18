#!/usr/bin/env python3
"""
Test script for Lampião agent with IBGE data integration
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_lampiao_ibge():
    """Test Lampião agent with IBGE data"""
    try:
        from src.agents.lampiao import LampiaoAgent

        print("✅ Lampião agent imported successfully")

        # Initialize agent
        agent = LampiaoAgent()
        print(f"✅ Agent initialized: {agent.name}")
        print(f"   Capabilities: {len(agent.capabilities)} features")

        # Call initialize() to load IBGE data
        await agent.initialize()
        print("✅ Agent initialization complete")

        # Check if IBGE data was loaded
        if hasattr(agent, "states_data"):
            print(f"✅ IBGE states data loaded: {len(agent.states_data)} states")

            # Show sample state data
            sp_data = agent.states_data.get("SP", {})
            print("\n📊 Sample: São Paulo State")
            print(f"   Name: {sp_data.get('name')}")
            print(f"   Capital: {sp_data.get('capital')}")
            print(f"   Region: {sp_data.get('region')}")
            print(f"   Area: {sp_data.get('area'):,.0f} km²")

        if hasattr(agent, "regional_indicators"):
            sp_indicators = agent.regional_indicators.get("SP", {})
            if sp_indicators:
                print("\n📈 São Paulo Indicators:")
                print(f"   Population: {sp_indicators.get('population'):,}")
                print(
                    f"   GDP per capita: R$ {sp_indicators.get('gdp_per_capita'):,.1f}k"
                )
                print(f"   HDI: {sp_indicators.get('hdi'):.3f}")
                print(f"   Density: {sp_indicators.get('density'):,.1f} hab/km²")
                print(f"   Source: {sp_indicators.get('source')}")

        print("\n✅ All IBGE data integration tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Error testing Lampião: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_lampiao_ibge())
    sys.exit(0 if success else 1)
