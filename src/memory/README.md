# 🧠 Cidadão.AI Memory System

## 📋 Overview

The **Memory System** implements a sophisticated **multi-layer memory architecture** inspired by human cognitive memory models. This system enables agents to maintain **context**, **learn from experiences**, and **build knowledge** over time, crucial for effective transparency analysis and investigation continuity.

## 🏗️ Architecture

```
src/memory/
├── base.py             # Abstract memory interfaces
├── episodic.py         # Event-specific memory storage
├── semantic.py         # General knowledge and patterns
├── conversational.py   # Dialog context management
└── __init__.py        # Memory system initialization
```

## 🧩 Memory Architecture

### Multi-Layer Memory Model

The system implements **three distinct memory layers** based on cognitive science research:

```python
# Memory hierarchy (cognitive psychology inspired)
┌─────────────────────┐
│ Conversational      │ ← Short-term, session-based
│ Memory              │
├─────────────────────┤
│ Episodic Memory     │ ← Medium-term, event-based
├─────────────────────┤
│ Semantic Memory     │ ← Long-term, knowledge-based
└─────────────────────┘
```

### 1. **Base Memory Framework** (base.py)

#### Abstract Memory Interface
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

class MemoryType(Enum):
    """Memory classification types"""
    EPISODIC = "episodic"           # Specific events and experiences
    SEMANTIC = "semantic"           # General knowledge and facts
    PROCEDURAL = "procedural"       # Skills and procedures
    WORKING = "working"             # Temporary, active information

class MemoryImportance(Enum):
    """Memory importance levels for retention management"""
    TRIVIAL = 1      # Can be discarded easily
    LOW = 2          # Moderate retention
    MEDIUM = 3       # Standard retention
    HIGH = 4         # Long retention
    CRITICAL = 5     # Permanent retention

class BaseMemory(ABC):
    """
    Abstract base class for all memory implementations
    
    Core Principles:
    - Importance-based retention
    - Temporal decay with reinforcement
    - Associative retrieval
    - Context-aware storage
    - Efficient search and indexing
    """
    
    def __init__(self, memory_type: MemoryType, max_size: int = 10000):
        self.memory_type = memory_type
        self.max_size = max_size
        self.memories: Dict[str, MemoryEntry] = {}
        self.index = {}  # For fast retrieval
        
    @abstractmethod
    async def store(
        self, 
        key: str, 
        content: Any, 
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Store memory with importance weighting"""
        pass
        
    @abstractmethod
    async def retrieve(
        self, 
        key: str = None,
        query: str = None,
        similarity_threshold: float = 0.8,
        max_results: int = 10
    ) -> List[MemoryEntry]:
        """Retrieve memories by key or semantic query"""
        pass
        
    @abstractmethod
    async def forget(self, key: str) -> bool:
        """Explicitly remove memory"""
        pass
        
    @abstractmethod
    async def consolidate(self) -> Dict[str, int]:
        """Consolidate memories (move from short to long-term)"""
        pass

class MemoryEntry(BaseModel):
    """Individual memory entry with metadata"""
    
    id: str = Field(..., description="Unique memory identifier")
    content: Any = Field(..., description="Memory content")
    memory_type: MemoryType = Field(..., description="Type of memory")
    importance: MemoryImportance = Field(..., description="Importance level")
    
    # Temporal information
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(default=0, description="Number of times accessed")
    
    # Context and associations
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual metadata")
    associations: List[str] = Field(default_factory=list, description="Associated memory IDs")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    
    # Decay and reinforcement
    decay_rate: float = Field(default=0.1, description="Memory decay rate (0-1)")
    reinforcement_count: int = Field(default=0, description="Times reinforced")
    strength: float = Field(default=1.0, description="Memory strength (0-1)")
    
    def calculate_current_strength(self) -> float:
        """Calculate current memory strength with decay"""
        time_elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        decay_factor = math.exp(-self.decay_rate * time_elapsed / 86400)  # Per day
        reinforcement_boost = min(0.5, self.reinforcement_count * 0.1)
        
        return min(1.0, (self.strength * decay_factor) + reinforcement_boost)
    
    def reinforce(self) -> None:
        """Reinforce memory (strengthen and reset decay)"""
        self.reinforcement_count += 1
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
        self.strength = min(1.0, self.strength + 0.1)
```

### 2. **Episodic Memory** (episodic.py)

#### Event-Based Memory Storage
```python
class EpisodicMemory(BaseMemory):
    """
    Episodic memory for specific events and experiences
    
    Use Cases:
    - Investigation results and findings
    - Agent interactions and decisions
    - User queries and responses
    - System events and anomalies
    - Analysis outcomes and insights
    
    Features:
    - Temporal ordering and retrieval
    - Context-rich storage
    - Event clustering and patterns
    - Causal relationship tracking
    """
    
    def __init__(self, max_size: int = 5000):
        super().__init__(MemoryType.EPISODIC, max_size)
        self.temporal_index = {}  # Time-based indexing
        self.context_index = {}   # Context-based indexing
        self.event_chains = {}    # Causal event sequences
    
    async def store_investigation_result(
        self,
        investigation_id: str,
        results: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> bool:
        """Store investigation results as episodic memory"""
        
        memory_entry = MemoryEntry(
            id=f"investigation_{investigation_id}",
            content={
                "investigation_id": investigation_id,
                "results": results,
                "anomalies_found": results.get("anomalies_found", 0),
                "confidence_score": results.get("confidence_score", 0.0),
                "processing_time": results.get("processing_time_ms", 0)
            },
            memory_type=MemoryType.EPISODIC,
            importance=self._calculate_investigation_importance(results),
            context=context or {},
            tags=self._extract_investigation_tags(results)
        )
        
        # Store in main memory
        self.memories[memory_entry.id] = memory_entry
        
        # Update temporal index
        timestamp = memory_entry.created_at.isoformat()
        if timestamp not in self.temporal_index:
            self.temporal_index[timestamp] = []
        self.temporal_index[timestamp].append(memory_entry.id)
        
        # Update context index
        for key, value in memory_entry.context.items():
            context_key = f"{key}:{value}"
            if context_key not in self.context_index:
                self.context_index[context_key] = []
            self.context_index[context_key].append(memory_entry.id)
        
        return True
    
    async def store_agent_interaction(
        self,
        agent_name: str,
        action: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        success: bool
    ) -> bool:
        """Store agent interaction as episodic memory"""
        
        memory_entry = MemoryEntry(
            id=f"agent_{agent_name}_{datetime.utcnow().isoformat()}",
            content={
                "agent_name": agent_name,
                "action": action,
                "input_summary": self._summarize_data(input_data),
                "output_summary": self._summarize_data(output_data),
                "success": success,
                "execution_context": self._extract_execution_context()
            },
            memory_type=MemoryType.EPISODIC,
            importance=MemoryImportance.MEDIUM if success else MemoryImportance.HIGH,
            context={"agent": agent_name, "action": action},
            tags=[agent_name, action, "success" if success else "failure"]
        )
        
        await self.store(memory_entry.id, memory_entry.content, memory_entry.importance, memory_entry.context)
        return True
    
    async def retrieve_investigation_history(
        self,
        investigation_id: str = None,
        organization: str = None,
        time_range: Dict[str, datetime] = None,
        max_results: int = 50
    ) -> List[MemoryEntry]:
        """Retrieve investigation history with filtering"""
        
        relevant_memories = []
        
        for memory_id, memory in self.memories.items():
            # Filter by investigation ID
            if investigation_id and investigation_id not in memory.content.get("investigation_id", ""):
                continue
                
            # Filter by organization
            if organization and organization not in memory.context.get("organization", ""):
                continue
                
            # Filter by time range
            if time_range:
                if "start" in time_range and memory.created_at < time_range["start"]:
                    continue
                if "end" in time_range and memory.created_at > time_range["end"]:
                    continue
            
            relevant_memories.append(memory)
        
        # Sort by creation time (most recent first)
        relevant_memories.sort(key=lambda m: m.created_at, reverse=True)
        
        return relevant_memories[:max_results]
    
    async def detect_investigation_patterns(self) -> Dict[str, Any]:
        """Detect patterns in investigation history"""
        
        patterns = {
            "common_anomaly_types": {},
            "organization_patterns": {},
            "temporal_patterns": {},
            "success_patterns": {}
        }
        
        for memory in self.memories.values():
            if "investigation_" in memory.id:
                content = memory.content
                
                # Anomaly type patterns
                anomaly_types = content.get("results", {}).get("anomaly_types", [])
                for anomaly_type in anomaly_types:
                    patterns["common_anomaly_types"][anomaly_type] = patterns["common_anomaly_types"].get(anomaly_type, 0) + 1
                
                # Organization patterns
                org = memory.context.get("organization", "unknown")
                patterns["organization_patterns"][org] = patterns["organization_patterns"].get(org, 0) + 1
                
                # Temporal patterns (by hour of day)
                hour = memory.created_at.hour
                patterns["temporal_patterns"][hour] = patterns["temporal_patterns"].get(hour, 0) + 1
                
                # Success patterns
                confidence = content.get("confidence_score", 0.0)
                if confidence > 0.8:
                    patterns["success_patterns"]["high_confidence"] = patterns["success_patterns"].get("high_confidence", 0) + 1
                elif confidence > 0.6:
                    patterns["success_patterns"]["medium_confidence"] = patterns["success_patterns"].get("medium_confidence", 0) + 1
                else:
                    patterns["success_patterns"]["low_confidence"] = patterns["success_patterns"].get("low_confidence", 0) + 1
        
        return patterns
```

### 3. **Semantic Memory** (semantic.py)

#### Knowledge and Pattern Storage
```python
class SemanticMemory(BaseMemory):
    """
    Semantic memory for general knowledge and learned patterns
    
    Use Cases:
    - Government organization profiles
    - Vendor behavior patterns
    - Legal framework knowledge
    - Statistical benchmarks
    - Domain expertise
    
    Features:
    - Vector-based semantic search
    - Knowledge graph relationships
    - Pattern abstraction
    - Automated knowledge extraction
    """
    
    def __init__(self, max_size: int = 20000):
        super().__init__(MemoryType.SEMANTIC, max_size)
        self.vector_store = None  # ChromaDB or FAISS
        self.knowledge_graph = {}  # Entity relationships
        self.concept_hierarchy = {}  # Taxonomic organization
        
    async def store_organization_profile(
        self,
        organization_code: str,
        profile_data: Dict[str, Any]
    ) -> bool:
        """Store government organization profile"""
        
        memory_entry = MemoryEntry(
            id=f"org_profile_{organization_code}",
            content={
                "organization_code": organization_code,
                "name": profile_data.get("name", ""),
                "type": profile_data.get("type", ""),
                "budget_range": profile_data.get("budget_range", ""),
                "typical_contracts": profile_data.get("typical_contracts", []),
                "spending_patterns": profile_data.get("spending_patterns", {}),
                "risk_profile": profile_data.get("risk_profile", "medium"),
                "compliance_history": profile_data.get("compliance_history", [])
            },
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.HIGH,
            context={"type": "organization_profile", "code": organization_code},
            tags=["organization", organization_code, profile_data.get("type", "")]
        )
        
        # Store in main memory
        self.memories[memory_entry.id] = memory_entry
        
        # Update knowledge graph
        await self._update_knowledge_graph(memory_entry)
        
        # Store vector representation for semantic search
        if self.vector_store:
            await self._store_vector_representation(memory_entry)
        
        return True
    
    async def store_pattern_knowledge(
        self,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        evidence: List[str] = None
    ) -> bool:
        """Store learned patterns and knowledge"""
        
        memory_entry = MemoryEntry(
            id=f"pattern_{pattern_type}_{datetime.utcnow().timestamp()}",
            content={
                "pattern_type": pattern_type,
                "description": pattern_data.get("description", ""),
                "conditions": pattern_data.get("conditions", []),
                "indicators": pattern_data.get("indicators", []),
                "confidence": pattern_data.get("confidence", 0.0),
                "frequency": pattern_data.get("frequency", 0),
                "evidence": evidence or [],
                "applications": pattern_data.get("applications", [])
            },
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.HIGH,
            context={"type": "pattern", "pattern_type": pattern_type},
            tags=["pattern", pattern_type] + pattern_data.get("tags", [])
        )
        
        await self.store(memory_entry.id, memory_entry.content, memory_entry.importance, memory_entry.context)
        return True
    
    async def query_similar_patterns(
        self,
        query_pattern: Dict[str, Any],
        similarity_threshold: float = 0.8,
        max_results: int = 10
    ) -> List[MemoryEntry]:
        """Find patterns similar to the query pattern"""
        
        if not self.vector_store:
            # Fallback to keyword-based search
            return await self._keyword_based_pattern_search(query_pattern, max_results)
        
        # Vector-based semantic search
        query_vector = await self._generate_pattern_embedding(query_pattern)
        similar_memories = await self.vector_store.similarity_search(
            query_vector,
            threshold=similarity_threshold,
            max_results=max_results
        )
        
        return similar_memories
    
    async def extract_knowledge_from_investigations(
        self,
        investigation_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract semantic knowledge from investigation results"""
        
        extracted_knowledge = {
            "organization_insights": {},
            "vendor_patterns": {},
            "anomaly_patterns": {},
            "seasonal_patterns": {},
            "compliance_insights": {}
        }
        
        for result in investigation_results:
            # Extract organization insights
            org_code = result.get("organization_code")
            if org_code:
                if org_code not in extracted_knowledge["organization_insights"]:
                    extracted_knowledge["organization_insights"][org_code] = {
                        "anomaly_frequency": 0,
                        "avg_confidence": 0.0,
                        "common_issues": []
                    }
                
                org_insight = extracted_knowledge["organization_insights"][org_code]
                org_insight["anomaly_frequency"] += result.get("anomalies_found", 0)
                org_insight["avg_confidence"] += result.get("confidence_score", 0.0)
            
            # Extract vendor patterns
            vendors = result.get("vendors", [])
            for vendor in vendors:
                vendor_id = vendor.get("id")
                if vendor_id and vendor.get("anomaly_score", 0) > 0.7:
                    if vendor_id not in extracted_knowledge["vendor_patterns"]:
                        extracted_knowledge["vendor_patterns"][vendor_id] = {
                            "risk_score": 0.0,
                            "issue_types": [],
                            "frequency": 0
                        }
                    
                    pattern = extracted_knowledge["vendor_patterns"][vendor_id]
                    pattern["risk_score"] = max(pattern["risk_score"], vendor.get("anomaly_score", 0))
                    pattern["frequency"] += 1
        
        # Store extracted knowledge
        for category, knowledge in extracted_knowledge.items():
            if knowledge:  # Only store non-empty knowledge
                await self.store_pattern_knowledge(
                    pattern_type=category,
                    pattern_data={"description": f"Extracted {category}", "data": knowledge}
                )
        
        return extracted_knowledge
```

### 4. **Conversational Memory** (conversational.py)

#### Dialog Context Management
```python
class ConversationalMemory(BaseMemory):
    """
    Conversational memory for dialog context and user interactions
    
    Use Cases:
    - User query context and history
    - Multi-turn conversation tracking
    - User preferences and patterns
    - Session state management
    - Personalization data
    
    Features:
    - Session-based organization
    - Context window management
    - Intent tracking
    - Preference learning
    """
    
    def __init__(self, max_size: int = 2000, context_window: int = 20):
        super().__init__(MemoryType.WORKING, max_size)
        self.context_window = context_window
        self.active_sessions = {}
        self.user_profiles = {}
        
    async def store_user_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        intent: str = None,
        entities: Dict[str, Any] = None
    ) -> bool:
        """Store user message with context"""
        
        message_entry = MemoryEntry(
            id=f"user_msg_{session_id}_{datetime.utcnow().timestamp()}",
            content={
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
                "intent": intent,
                "entities": entities or {},
                "message_type": "user"
            },
            memory_type=MemoryType.WORKING,
            importance=MemoryImportance.MEDIUM,
            context={"user_id": user_id, "session_id": session_id},
            tags=["user_message", intent or "unknown_intent"]
        )
        
        # Store message
        await self.store(message_entry.id, message_entry.content, message_entry.importance, message_entry.context)
        
        # Update session tracking
        await self._update_session_context(session_id, message_entry)
        
        # Update user profile
        await self._update_user_profile(user_id, message_entry)
        
        return True
    
    async def store_agent_response(
        self,
        session_id: str,
        agent_name: str,
        response: str,
        confidence: float = 1.0,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Store agent response with context"""
        
        response_entry = MemoryEntry(
            id=f"agent_resp_{session_id}_{datetime.utcnow().timestamp()}",
            content={
                "session_id": session_id,
                "agent_name": agent_name,
                "response": response,
                "confidence": confidence,
                "metadata": metadata or {},
                "message_type": "agent"
            },
            memory_type=MemoryType.WORKING,
            importance=MemoryImportance.MEDIUM,
            context={"session_id": session_id, "agent": agent_name},
            tags=["agent_response", agent_name]
        )
        
        await self.store(response_entry.id, response_entry.content, response_entry.importance, response_entry.context)
        await self._update_session_context(session_id, response_entry)
        
        return True
    
    async def get_conversation_context(
        self,
        session_id: str,
        max_messages: int = None
    ) -> List[MemoryEntry]:
        """Get conversation context for a session"""
        
        max_messages = max_messages or self.context_window
        
        session_memories = []
        for memory in self.memories.values():
            if memory.context.get("session_id") == session_id:
                session_memories.append(memory)
        
        # Sort by creation time and limit to context window
        session_memories.sort(key=lambda m: m.created_at)
        return session_memories[-max_messages:]
    
    async def learn_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Learn user preferences from conversation history"""
        
        user_memories = [
            memory for memory in self.memories.values()
            if memory.context.get("user_id") == user_id
        ]
        
        preferences = {
            "preferred_analysis_types": {},
            "common_organizations": {},
            "typical_queries": [],
            "response_preferences": {
                "detail_level": "medium",
                "format_preference": "natural_language"
            }
        }
        
        for memory in user_memories:
            content = memory.content
            
            # Learn from intents
            if content.get("intent"):
                intent = content["intent"]
                preferences["preferred_analysis_types"][intent] = preferences["preferred_analysis_types"].get(intent, 0) + 1
            
            # Learn from entities
            entities = content.get("entities", {})
            if "organization" in entities:
                org = entities["organization"]
                preferences["common_organizations"][org] = preferences["common_organizations"].get(org, 0) + 1
        
        # Update user profile
        self.user_profiles[user_id] = preferences
        
        return preferences
```

## 🔄 Memory Consolidation & Management

### Automated Memory Management
```python
class MemoryManager:
    """
    Central memory management system
    
    Features:
    - Automatic memory consolidation
    - Importance-based retention
    - Cross-memory association
    - Garbage collection
    - Performance optimization
    """
    
    def __init__(self):
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.conversational_memory = ConversationalMemory()
        
    async def consolidate_memories(self) -> Dict[str, int]:
        """Consolidate memories across layers"""
        
        consolidation_stats = {
            "episodic_to_semantic": 0,
            "conversational_to_episodic": 0,
            "forgotten_memories": 0
        }
        
        # Promote important episodic memories to semantic
        important_episodes = [
            memory for memory in self.episodic_memory.memories.values()
            if memory.importance.value >= MemoryImportance.HIGH.value
            and memory.reinforcement_count > 3
        ]
        
        for episode in important_episodes:
            # Extract semantic patterns
            semantic_knowledge = await self._extract_semantic_knowledge(episode)
            if semantic_knowledge:
                await self.semantic_memory.store_pattern_knowledge(
                    pattern_type="learned_from_episode",
                    pattern_data=semantic_knowledge,
                    evidence=[episode.id]
                )
                consolidation_stats["episodic_to_semantic"] += 1
        
        # Promote important conversations to episodic
        important_conversations = [
            memory for memory in self.conversational_memory.memories.values()
            if memory.importance.value >= MemoryImportance.HIGH.value
        ]
        
        for conversation in important_conversations:
            await self.episodic_memory.store_agent_interaction(
                agent_name="conversational_agent",
                action="important_conversation",
                input_data={"conversation_id": conversation.id},
                output_data=conversation.content,
                success=True
            )
            consolidation_stats["conversational_to_episodic"] += 1
        
        # Forget low-importance, old memories
        forgotten_count = await self._forget_old_memories()
        consolidation_stats["forgotten_memories"] = forgotten_count
        
        return consolidation_stats
    
    async def _forget_old_memories(self) -> int:
        """Remove low-importance memories based on age and strength"""
        
        forgotten_count = 0
        current_time = datetime.utcnow()
        
        for memory_layer in [self.episodic_memory, self.semantic_memory, self.conversational_memory]:
            memories_to_forget = []
            
            for memory_id, memory in memory_layer.memories.items():
                # Calculate memory strength with decay
                current_strength = memory.calculate_current_strength()
                age_days = (current_time - memory.created_at).days
                
                # Forget if strength is very low and memory is old
                if (current_strength < 0.1 and age_days > 30) or \
                   (memory.importance == MemoryImportance.TRIVIAL and age_days > 7):
                    memories_to_forget.append(memory_id)
            
            # Remove forgotten memories
            for memory_id in memories_to_forget:
                await memory_layer.forget(memory_id)
                forgotten_count += 1
        
        return forgotten_count
```

## 🧪 Usage Examples

### Basic Memory Operations
```python
from src.memory import EpisodicMemory, SemanticMemory, ConversationalMemory

# Initialize memory systems
episodic = EpisodicMemory()
semantic = SemanticMemory()
conversational = ConversationalMemory()

# Store investigation result
investigation_result = {
    "anomalies_found": 5,
    "confidence_score": 0.92,
    "processing_time_ms": 1500
}

await episodic.store_investigation_result(
    investigation_id="inv_001",
    results=investigation_result,
    context={"organization": "20000", "year": "2024"}
)

# Store organization knowledge  
org_profile = {
    "name": "Ministério da Saúde",
    "type": "federal_ministry",
    "budget_range": "50B+",
    "risk_profile": "medium"
}

await semantic.store_organization_profile("20000", org_profile)

# Store conversation
await conversational.store_user_message(
    user_id="user123",
    session_id="session_001", 
    message="Analyze health ministry contracts from 2024",
    intent="analyze_contracts",
    entities={"organization": "20000", "year": "2024"}
)
```

### Advanced Memory Retrieval
```python
# Retrieve investigation history
investigation_history = await episodic.retrieve_investigation_history(
    organization="20000",
    time_range={
        "start": datetime(2024, 1, 1),
        "end": datetime(2024, 12, 31)
    },  
    max_results=20
)

# Find similar patterns
similar_patterns = await semantic.query_similar_patterns(
    query_pattern={
        "pattern_type": "vendor_concentration",
        "conditions": ["high_market_share", "few_competitors"],
        "confidence": 0.8
    },
    similarity_threshold=0.7
)

# Get conversation context
context = await conversational.get_conversation_context(
    session_id="session_001",
    max_messages=10
)
```

### Memory Consolidation
```python
from src.memory import MemoryManager

# Initialize memory manager
memory_manager = MemoryManager()

# Perform memory consolidation  
consolidation_stats = await memory_manager.consolidate_memories()

print(f"Promoted {consolidation_stats['episodic_to_semantic']} episodes to semantic memory")
print(f"Forgot {consolidation_stats['forgotten_memories']} old memories")
```

---

This sophisticated memory system enables the Cidadão.AI agents to **learn from experience**, **maintain context**, and **build knowledge** over time, crucial for effective long-term transparency analysis and investigation continuity.