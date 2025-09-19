"""
Factory for Drummond agent to avoid import-time instantiation issues.
"""

from typing import Optional
from src.agents.drummond import CommunicationAgent
from src.core import get_logger

logger = get_logger(__name__)

# Global instance cache
_drummond_instance: Optional[CommunicationAgent] = None
_initialized = False


async def get_drummond_agent() -> Optional[CommunicationAgent]:
    """
    Get or create Drummond agent instance.
    This function handles lazy initialization to avoid import-time issues.
    """
    global _drummond_instance, _initialized
    
    if not _initialized:
        try:
            logger.info("Creating Drummond agent instance...")
            _drummond_instance = CommunicationAgent()
            
            logger.info("Initializing Drummond agent...")
            await _drummond_instance.initialize()
            
            _initialized = True
            logger.info("Drummond agent ready")
            
        except Exception as e:
            logger.error(f"Failed to create/initialize Drummond: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            _drummond_instance = None
            _initialized = False
            
    return _drummond_instance