"""
Agent Memory Integration Service

Integrates all agents with the Nanã memory system for persistent
knowledge sharing and context preservation.
"""

import hashlib
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from src.agents.deodoro import AgentContext, AgentMessage, BaseAgent
from src.agents.nana import (
    ContextMemoryAgent,
    EpisodicMemory,
    MemoryImportance,
    SemanticMemory,
)
from src.core import get_logger

logger = get_logger(__name__)


class MemoryIntegrationType(Enum):
    """Types of memory integration for agents."""

    READ_ONLY = "read_only"  # Agent can only read memories
    WRITE_ONLY = "write_only"  # Agent can only write memories
    READ_WRITE = "read_write"  # Agent can read and write memories
    SELECTIVE = "selective"  # Agent has selective access based on tags


class AgentMemoryIntegration:
    """
    Service to integrate agents with the Nanã memory system.

    This service acts as a bridge between agents and the memory system,
    providing:
    - Automatic memory storage for agent results
    - Context retrieval for informed decision making
    - Cross-agent knowledge sharing
    - Memory-based learning and improvement
    """

    def __init__(
        self,
        memory_agent: ContextMemoryAgent,
        auto_store: bool = True,
        auto_retrieve: bool = True,
    ):
        """
        Initialize memory integration service.

        Args:
            memory_agent: The Nanã memory agent instance
            auto_store: Automatically store agent results
            auto_retrieve: Automatically retrieve relevant context
        """
        self.memory_agent = memory_agent
        self.auto_store = auto_store
        self.auto_retrieve = auto_retrieve

        # Agent memory configurations
        self.agent_configs: dict[str, dict[str, Any]] = self._initialize_agent_configs()

        # Memory access tracking
        self.access_log: list[dict[str, Any]] = []

        # Cache for frequently accessed memories
        self.memory_cache: dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes

    def _initialize_agent_configs(self) -> dict[str, dict[str, Any]]:
        """Initialize memory configurations for each agent."""
        return {
            # Master agent has full access
            "abaporu": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["investigation", "coordination", "results"],
                "importance_threshold": MemoryImportance.LOW,
                "auto_store_results": True,
            },
            # Investigative agents store findings
            "zumbi": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["anomaly", "fraud", "investigation"],
                "importance_threshold": MemoryImportance.MEDIUM,
                "auto_store_results": True,
            },
            "anita": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["pattern", "analysis", "trend"],
                "importance_threshold": MemoryImportance.MEDIUM,
                "auto_store_results": True,
            },
            "oxossi": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["fraud", "evidence", "high_risk"],
                "importance_threshold": MemoryImportance.HIGH,
                "auto_store_results": True,
            },
            # Reporting agents read memories
            "tiradentes": {
                "integration_type": MemoryIntegrationType.READ_ONLY,
                "tags": ["report", "summary"],
                "importance_threshold": MemoryImportance.LOW,
                "auto_store_results": False,
            },
            "machado": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["document", "text_analysis", "compliance"],
                "importance_threshold": MemoryImportance.MEDIUM,
                "auto_store_results": True,
            },
            # Analysis agents
            "bonifacio": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["policy", "effectiveness", "impact"],
                "importance_threshold": MemoryImportance.MEDIUM,
                "auto_store_results": True,
            },
            "dandara": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["equity", "social_justice", "inclusion"],
                "importance_threshold": MemoryImportance.MEDIUM,
                "auto_store_results": True,
            },
            "lampiao": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["regional", "geographic", "inequality"],
                "importance_threshold": MemoryImportance.MEDIUM,
                "auto_store_results": True,
            },
            # Support agents
            "ayrton_senna": {
                "integration_type": MemoryIntegrationType.READ_ONLY,
                "tags": ["routing", "performance"],
                "importance_threshold": MemoryImportance.LOW,
                "auto_store_results": False,
            },
            "oscar_niemeyer": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["visualization", "aggregation", "metrics"],
                "importance_threshold": MemoryImportance.LOW,
                "auto_store_results": True,
            },
            "ceuci": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["prediction", "forecast", "analysis"],
                "importance_threshold": MemoryImportance.MEDIUM,
                "auto_store_results": True,
            },
            "maria_quiteria": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["security", "audit", "compliance"],
                "importance_threshold": MemoryImportance.HIGH,
                "auto_store_results": True,
            },
            "obaluaie": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["corruption", "systemic", "alert"],
                "importance_threshold": MemoryImportance.HIGH,
                "auto_store_results": True,
            },
            "drummond": {
                "integration_type": MemoryIntegrationType.READ_WRITE,
                "tags": ["communication", "message", "notification"],
                "importance_threshold": MemoryImportance.LOW,
                "auto_store_results": False,
            },
        }

    async def integrate_agent(self, agent: BaseAgent) -> None:
        """
        Integrate an agent with the memory system.

        This wraps the agent's process method to automatically handle
        memory operations.
        """
        agent_id = agent.agent_id.lower()
        if agent_id not in self.agent_configs:
            logger.warning(f"No memory configuration for agent {agent_id}")
            return

        # Store original process method
        original_process = agent.process

        # Create memory-aware process method
        async def memory_aware_process(
            message: AgentMessage, context: AgentContext
        ) -> Any:
            config = self.agent_configs[agent_id]

            # Retrieve relevant memories before processing
            if self.auto_retrieve and config["integration_type"] in [
                MemoryIntegrationType.READ_ONLY,
                MemoryIntegrationType.READ_WRITE,
                MemoryIntegrationType.SELECTIVE,
            ]:
                memories = await self.retrieve_relevant_memories(
                    agent_id=agent_id,
                    query=str(message.payload) if message.payload else "",
                    context=context,
                    tags=config["tags"],
                )

                # Inject memories into context
                if memories:
                    context.metadata["retrieved_memories"] = memories
                    logger.info(f"Retrieved {len(memories)} memories for {agent_id}")

            # Process with original method
            result = await original_process(message, context)

            # Store result in memory if configured
            if (
                self.auto_store
                and config["auto_store_results"]
                and config["integration_type"]
                in [MemoryIntegrationType.WRITE_ONLY, MemoryIntegrationType.READ_WRITE]
                and result.success
            ):

                # Determine importance based on result
                importance = self._determine_importance(agent_id, result)

                if importance.value >= config["importance_threshold"].value:
                    await self.store_agent_result(
                        agent_id=agent_id,
                        message=message,
                        context=context,
                        result=result,
                        importance=importance,
                        tags=config["tags"],
                    )

            return result

        # Replace process method
        agent.process = memory_aware_process
        logger.info(f"Successfully integrated {agent_id} with memory system")

    async def retrieve_relevant_memories(
        self,
        agent_id: str,
        query: str,
        context: AgentContext,
        tags: list[str],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant memories for an agent."""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(agent_id, query, tags)
            if cache_key in self.memory_cache:
                cached = self.memory_cache[cache_key]
                if datetime.utcnow() - cached["timestamp"] < timedelta(
                    seconds=self.cache_ttl
                ):
                    return cached["memories"]

            # Retrieve from memory agent
            memories = []

            # Get episodic memories
            episodic = await self.memory_agent.retrieve_episodic(
                investigation_id=context.investigation_id, limit=limit // 2
            )
            memories.extend(episodic)

            # Get semantic memories by tags
            for tag in tags:
                semantic = await self.memory_agent.retrieve_by_tag(
                    tag=tag, limit=limit // len(tags)
                )
                memories.extend(semantic)

            # Get similar memories by query
            similar = await self.memory_agent.retrieve_similar(
                query=query, limit=limit // 2
            )
            memories.extend(similar)

            # Deduplicate and sort by relevance
            unique_memories = self._deduplicate_memories(memories)
            sorted_memories = sorted(
                unique_memories, key=lambda m: m.get("relevance", 0), reverse=True
            )[:limit]

            # Cache results
            self.memory_cache[cache_key] = {
                "memories": sorted_memories,
                "timestamp": datetime.utcnow(),
            }

            # Log access
            self.access_log.append(
                {
                    "agent_id": agent_id,
                    "timestamp": datetime.utcnow(),
                    "query": query,
                    "memories_retrieved": len(sorted_memories),
                    "tags": tags,
                }
            )

            return sorted_memories

        except Exception as e:
            logger.error(f"Error retrieving memories for {agent_id}: {str(e)}")
            return []

    async def store_agent_result(
        self,
        agent_id: str,
        message: AgentMessage,
        context: AgentContext,
        result: Any,
        importance: MemoryImportance,
        tags: list[str],
    ) -> bool:
        """Store agent result in memory."""
        try:
            # Create episodic memory
            memory_id = (
                f"{agent_id}_{context.investigation_id}_{datetime.utcnow().timestamp()}"
            )

            episodic_memory = EpisodicMemory(
                id=memory_id,
                content={
                    "agent": agent_id,
                    "message": str(message.payload) if message.payload else "",
                    "result": result.data if hasattr(result, "data") else str(result),
                },
                importance=importance,
                tags=tags + [agent_id],
                investigation_id=context.investigation_id,
                user_id=context.user_id,
                session_id=context.session_id,
                query=str(message.payload) if message.payload else "",
                result=(
                    result.data if hasattr(result, "data") else {"result": str(result)}
                ),
                context=context.metadata,
            )

            # Store in memory agent
            await self.memory_agent.store_episodic(
                memory=episodic_memory, context=context
            )

            # Extract and store semantic knowledge
            if agent_id in ["zumbi", "anita", "oxossi", "bonifacio"]:
                await self._extract_semantic_knowledge(
                    agent_id=agent_id, result=result, tags=tags, context=context
                )

            logger.info(
                f"Stored result from {agent_id} with importance {importance.value}"
            )
            return True

        except Exception as e:
            logger.error(f"Error storing result from {agent_id}: {str(e)}")
            return False

    async def _extract_semantic_knowledge(
        self, agent_id: str, result: Any, tags: list[str], context: AgentContext
    ) -> None:
        """Extract semantic knowledge from agent results."""
        try:
            knowledge_items = []

            # Extract patterns from Anita
            if agent_id == "anita" and hasattr(result, "data"):
                patterns = result.data.get("patterns", [])
                for pattern in patterns:
                    knowledge_items.append(
                        {
                            "concept": f"pattern_{pattern.get('type', 'unknown')}",
                            "description": pattern.get("description", ""),
                            "confidence": pattern.get("confidence", 0.5),
                            "evidence": [pattern.get("evidence", "")],
                        }
                    )

            # Extract fraud indicators from Oxossi
            elif agent_id == "oxossi" and hasattr(result, "data"):
                fraud_analysis = result.data.get("fraud_analysis", {})
                patterns = fraud_analysis.get("patterns", [])
                for pattern in patterns:
                    knowledge_items.append(
                        {
                            "concept": f"fraud_{pattern.get('fraud_type', 'unknown')}",
                            "description": f"{pattern.get('fraud_type', 'Unknown')} fraud pattern detected",
                            "confidence": pattern.get("confidence", 0.5),
                            "evidence": [
                                str(ind) for ind in pattern.get("indicators", [])
                            ],
                        }
                    )

            # Extract anomalies from Zumbi
            elif agent_id == "zumbi" and hasattr(result, "data"):
                anomalies = result.data.get("anomalies", [])
                for anomaly in anomalies:
                    knowledge_items.append(
                        {
                            "concept": f"anomaly_{anomaly.get('type', 'unknown')}",
                            "description": anomaly.get("description", ""),
                            "confidence": anomaly.get("confidence", 0.5),
                            "evidence": [anomaly.get("evidence", "")],
                        }
                    )

            # Store semantic memories
            for item in knowledge_items:
                semantic_memory = SemanticMemory(
                    id=f"semantic_{agent_id}_{item['concept']}_{datetime.utcnow().timestamp()}",
                    content=item,
                    concept=item["concept"],
                    relationships=[agent_id] + tags,
                    evidence=item["evidence"],
                    confidence=item["confidence"],
                    importance=MemoryImportance.MEDIUM,
                    tags=tags + [agent_id, "knowledge"],
                )

                await self.memory_agent.store_semantic(
                    memory=semantic_memory, context=context
                )

            if knowledge_items:
                logger.info(
                    f"Extracted {len(knowledge_items)} semantic knowledge items from {agent_id}"
                )

        except Exception as e:
            logger.error(
                f"Error extracting semantic knowledge from {agent_id}: {str(e)}"
            )

    def _determine_importance(self, agent_id: str, result: Any) -> MemoryImportance:
        """Determine the importance of a result for memory storage."""
        # High importance for critical findings
        if agent_id in ["oxossi", "maria_quiteria", "obaluaie"]:
            if hasattr(result, "data"):
                # Check for high-severity findings
                if "risk_level" in result.data and result.data["risk_level"] in [
                    "HIGH",
                    "CRITICAL",
                ]:
                    return MemoryImportance.HIGH
                if "severity" in result.data and result.data["severity"] in [
                    "high",
                    "critical",
                ]:
                    return MemoryImportance.HIGH

        # Medium importance for analytical findings
        if agent_id in ["zumbi", "anita", "bonifacio", "dandara"]:
            if hasattr(result, "data"):
                # Check for significant findings
                if result.data.get("anomalies", []) or result.data.get("patterns", []):
                    return MemoryImportance.MEDIUM

        # Default to low importance
        return MemoryImportance.LOW

    def _generate_cache_key(self, agent_id: str, query: str, tags: list[str]) -> str:
        """Generate cache key for memory retrieval."""
        components = [agent_id, query] + sorted(tags)
        return hashlib.md5(":".join(components).encode()).hexdigest()

    def _deduplicate_memories(
        self, memories: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Remove duplicate memories based on content hash."""
        seen = set()
        unique = []

        for memory in memories:
            # Create content hash
            content_str = json.dumps(memory.get("content", {}), sort_keys=True)
            content_hash = hashlib.md5(content_str.encode()).hexdigest()

            if content_hash not in seen:
                seen.add(content_hash)
                unique.append(memory)

        return unique

    async def share_knowledge_between_agents(
        self,
        source_agent: str,
        target_agent: str,
        knowledge_type: str,
        filters: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Share specific knowledge from one agent to another.

        This enables cross-agent learning and collaboration.
        """
        try:
            source_config = self.agent_configs.get(source_agent)
            target_config = self.agent_configs.get(target_agent)

            if not source_config or not target_config:
                logger.error(f"Invalid agent IDs: {source_agent} or {target_agent}")
                return False

            # Check permissions
            if source_config["integration_type"] not in [
                MemoryIntegrationType.READ_WRITE,
                MemoryIntegrationType.READ_ONLY,
            ]:
                logger.error(f"{source_agent} cannot share knowledge (write-only)")
                return False

            # Retrieve knowledge from source agent
            source_memories = await self.memory_agent.retrieve_by_tag(
                tag=source_agent, limit=100
            )

            # Filter by knowledge type
            filtered_memories = [
                m for m in source_memories if knowledge_type in m.get("tags", [])
            ]

            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    filtered_memories = [
                        m for m in filtered_memories if m.get(key) == value
                    ]

            # Tag memories for target agent
            for memory in filtered_memories:
                memory["tags"] = list(
                    set(memory.get("tags", []) + [target_agent, "shared"])
                )

            logger.info(
                f"Shared {len(filtered_memories)} {knowledge_type} memories "
                f"from {source_agent} to {target_agent}"
            )

            return True

        except Exception as e:
            logger.error(f"Error sharing knowledge: {str(e)}")
            return False

    async def get_memory_statistics(self) -> dict[str, Any]:
        """Get statistics about memory usage by agents."""
        stats = {
            "total_accesses": len(self.access_log),
            "cache_size": len(self.memory_cache),
            "by_agent": {},
        }

        # Calculate per-agent statistics
        for log_entry in self.access_log:
            agent_id = log_entry["agent_id"]
            if agent_id not in stats["by_agent"]:
                stats["by_agent"][agent_id] = {
                    "accesses": 0,
                    "memories_retrieved": 0,
                    "last_access": None,
                }

            stats["by_agent"][agent_id]["accesses"] += 1
            stats["by_agent"][agent_id]["memories_retrieved"] += log_entry[
                "memories_retrieved"
            ]
            stats["by_agent"][agent_id]["last_access"] = log_entry["timestamp"]

        return stats

    async def optimize_memory_for_agent(self, agent_id: str) -> None:
        """
        Optimize memory storage for a specific agent.

        This consolidates related memories and removes outdated ones.
        """
        try:
            config = self.agent_configs.get(agent_id)
            if not config:
                return

            # Retrieve all memories for this agent
            agent_memories = await self.memory_agent.retrieve_by_tag(
                tag=agent_id, limit=1000
            )

            # Group by concept/pattern
            memory_groups = {}
            for memory in agent_memories:
                key = memory.get("concept", memory.get("id", "unknown"))
                if key not in memory_groups:
                    memory_groups[key] = []
                memory_groups[key].append(memory)

            # Consolidate groups with multiple entries
            for key, memories in memory_groups.items():
                if len(memories) > 5:  # Threshold for consolidation
                    # Create consolidated memory
                    consolidated = await self._consolidate_memories(memories)

                    # Store consolidated version
                    await self.memory_agent.store_semantic(
                        memory=consolidated,
                        context=AgentContext(
                            investigation_id=f"consolidation_{agent_id}",
                            user_id="system",
                            session_id="optimization",
                        ),
                    )

                    # Mark old memories for cleanup
                    for memory in memories[:-1]:  # Keep the most recent
                        memory["tags"].append("consolidated")

            logger.info(
                f"Optimized memory for {agent_id}: {len(memory_groups)} concepts"
            )

        except Exception as e:
            logger.error(f"Error optimizing memory for {agent_id}: {str(e)}")

    async def _consolidate_memories(
        self, memories: list[dict[str, Any]]
    ) -> SemanticMemory:
        """Consolidate multiple memories into a single semantic memory."""
        # Extract common concept
        concepts = [m.get("concept", "") for m in memories if m.get("concept")]
        concept = max(set(concepts), key=concepts.count) if concepts else "consolidated"

        # Merge evidence
        all_evidence = []
        for memory in memories:
            evidence = memory.get("evidence", [])
            if isinstance(evidence, list):
                all_evidence.extend(evidence)

        # Calculate average confidence
        confidences = [m.get("confidence", 0.5) for m in memories if "confidence" in m]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        # Merge tags
        all_tags = []
        for memory in memories:
            tags = memory.get("tags", [])
            if isinstance(tags, list):
                all_tags.extend(tags)

        return SemanticMemory(
            id=f"consolidated_{concept}_{datetime.utcnow().timestamp()}",
            content={
                "consolidated_from": len(memories),
                "original_ids": [m.get("id") for m in memories],
                "concept": concept,
            },
            concept=concept,
            relationships=list(set(all_tags)),
            evidence=list(set(all_evidence))[:10],  # Keep top 10 unique evidence
            confidence=avg_confidence,
            importance=MemoryImportance.MEDIUM,
            tags=list(set(all_tags)) + ["consolidated"],
        )


# Global instance for easy access
memory_integration = None


async def initialize_memory_integration(
    memory_agent: ContextMemoryAgent,
) -> AgentMemoryIntegration:
    """Initialize the global memory integration service."""
    global memory_integration
    memory_integration = AgentMemoryIntegration(memory_agent)
    logger.info("Memory integration service initialized")
    return memory_integration


def get_memory_integration() -> Optional[AgentMemoryIntegration]:
    """Get the global memory integration instance."""
    return memory_integration
