"""Episodic memory for specific events and investigations."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import BaseMemory


class EpisodicMemory(BaseMemory):
    """Memory for specific investigation episodes and events."""
    
    def __init__(self):
        super().__init__()
        self._episodes: List[Dict] = []
    
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Store an episodic memory."""
        episode = {
            "key": key,
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "episode_id": len(self._episodes)
        }
        self._episodes.append(episode)
        self._storage[key] = episode
        return True
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve an episode by key."""
        episode = self._storage.get(key)
        return episode["value"] if episode else None
    
    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search episodes by query (stub implementation)."""
        # TODO: Implement semantic search when vector DB is integrated
        matching_episodes = []
        query_lower = query.lower()
        
        for episode in self._episodes[-limit:]:  # Return recent episodes for now
            episode_text = str(episode.get("value", "")).lower()
            if query_lower in episode_text:
                matching_episodes.append(episode)
        
        return matching_episodes
    
    async def clear(self) -> bool:
        """Clear all episodic memories."""
        self._episodes.clear()
        self._storage.clear()
        return True
    
    def get_recent_episodes(self, limit: int = 5) -> List[Dict]:
        """Get recent episodes."""
        return self._episodes[-limit:] if self._episodes else []