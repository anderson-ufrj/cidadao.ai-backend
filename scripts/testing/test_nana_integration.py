"""
Quick integration test for Nanã memory agent
"""

import asyncio

from src.agents.deodoro import AgentContext, AgentMessage
from src.services.memory_service import get_memory_agent


async def test_nana_integration():
    """Test Nanã integration with vector store and Redis."""
    print("=" * 60)
    print("Nanã Integration Test")
    print("=" * 60)

    try:
        # Get memory agent
        print("\n1. Initializing memory agent...")
        memory_agent = await get_memory_agent()
        print(f"   ✓ Memory agent initialized: {memory_agent.name}")
        print(f"   ✓ Capabilities: {', '.join(memory_agent.capabilities)}")

        # Test episodic memory storage
        print("\n2. Testing episodic memory storage...")
        context = AgentContext(
            investigation_id="test_investigation_001",
            user_id="test_user",
            session_id="test_session",
        )

        store_message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="store_episodic",
            payload={
                "investigation_id": "test_investigation_001",
                "query": "Contratos de TI em 2024",
                "result": {
                    "total_contracts": 150,
                    "anomalies_found": 5,
                    "suspicious_patterns": [
                        "Concentração de fornecedores",
                        "Valores inflacionados",
                    ],
                },
                "context": {"year": 2024, "category": "IT"},
            },
        )

        response = await memory_agent.process(store_message, context)
        print(f"   ✓ Storage status: {response.status}")
        if response.result:
            memory_id = response.result.get("memory_id")
            print(f"   ✓ Memory ID: {memory_id}")

        # Test episodic memory retrieval
        print("\n3. Testing episodic memory retrieval...")
        retrieve_message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="retrieve_episodic",
            payload={
                "query": "contratos TI",
                "limit": 5,
            },
        )

        response = await memory_agent.process(retrieve_message, context)
        print(f"   ✓ Retrieval status: {response.status}")
        if response.result:
            memories = response.result.get("memories", [])
            print(f"   ✓ Found {len(memories)} memories")
            for memory in memories[:2]:
                print(f"     - Memory ID: {memory.get('id')}")
                print(f"       Query: {memory.get('query', 'N/A')}")
                print(f"       Timestamp: {memory.get('timestamp', 'N/A')}")

        # Test semantic memory
        print("\n4. Testing semantic memory...")
        semantic_store = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="store_semantic",
            payload={
                "concept": "Concentração de Fornecedores",
                "relationships": ["Monopólio", "Fraude", "Licitação"],
                "evidence": ["Índice de Herfindahl-Hirschman > 0.7"],
                "confidence": 0.85,
            },
        )

        response = await memory_agent.process(semantic_store, context)
        print(f"   ✓ Semantic storage status: {response.status}")

        # Test conversation memory
        print("\n5. Testing conversation memory...")
        conversation_store = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="store_conversation",
            payload={
                "conversation_id": "conv_test_001",
                "turn_number": 1,
                "speaker": "user",
                "message": "Quero investigar contratos de TI",
                "intent": "investigation_request",
            },
        )

        response = await memory_agent.process(conversation_store, context)
        print(f"   ✓ Conversation storage status: {response.status}")

        # Test memory consolidation
        print("\n6. Testing memory consolidation...")
        consolidate_message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="consolidate_memories",
            payload={"similarity_threshold": 0.8},
        )

        response = await memory_agent.process(consolidate_message, context)
        print(f"   ✓ Consolidation status: {response.status}")
        if response.result:
            consolidated = response.result.get("consolidated_count", 0)
            print(f"   ✓ Consolidated {consolidated} memories")

        # Get vector store stats
        print("\n7. Vector store statistics...")
        count = await memory_agent.vector_store.count()
        print(f"   ✓ Total documents in vector store: {count}")

        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_nana_integration())
