"""Base memory interface for Cidadão.AI agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime


class BaseMemory(ABC):
    """Abstract base class for memory systems."""
    
    def __init__(self):
        self._storage: Dict[str, Any] = {}
        self._created_at = datetime.now()
    
    @abstractmethod
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Store a memory item."""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a memory item by key."""
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search memory items by query."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all memory items."""
        pass