"""Semantic memory for knowledge and patterns."""

from typing import Any, Dict, List, Optional
from .base import BaseMemory


class SemanticMemory(BaseMemory):
    """Memory for semantic knowledge and patterns."""
    
    def __init__(self):
        super().__init__()
        self._knowledge_base: Dict[str, Dict] = {}
        self._patterns: List[Dict] = []
    
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Store semantic knowledge."""
        knowledge_item = {
            "key": key,
            "value": value,
            "metadata": metadata or {},
            "type": metadata.get("type", "knowledge") if metadata else "knowledge"
        }
        
        self._knowledge_base[key] = knowledge_item
        self._storage[key] = knowledge_item
        
        # Store patterns separately
        if knowledge_item["type"] == "pattern":
            self._patterns.append(knowledge_item)
        
        return True
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve knowledge by key."""
        knowledge = self._storage.get(key)
        return knowledge["value"] if knowledge else None
    
    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search knowledge base by query (stub implementation)."""
        # TODO: Implement vector-based semantic search
        matching_items = []
        query_lower = query.lower()
        
        for item in list(self._knowledge_base.values())[:limit]:
            item_text = str(item.get("value", "")).lower()
            if query_lower in item_text:
                matching_items.append(item)
        
        return matching_items
    
    async def clear(self) -> bool:
        """Clear all semantic memories."""
        self._knowledge_base.clear()
        self._patterns.clear()
        self._storage.clear()
        return True
    
    def get_patterns(self) -> List[Dict]:
        """Get stored patterns."""
        return self._patterns
    
    async def store_pattern(self, pattern_name: str, pattern_data: Dict) -> bool:
        """Store a detected pattern."""
        return await self.store(
            f"pattern:{pattern_name}",
            pattern_data,
            {"type": "pattern"}
        )