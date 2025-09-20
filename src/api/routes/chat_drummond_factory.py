"""
Factory for Drummond agent to avoid import-time instantiation issues.
"""

from typing import Optional, TYPE_CHECKING
from src.core import get_logger

# Use TYPE_CHECKING to avoid import at runtime
if TYPE_CHECKING:
    from src.agents.drummond import CommunicationAgent

logger = get_logger(__name__)

# Global instance cache
_drummond_instance: Optional['CommunicationAgent'] = None
_initialized = False
_import_error = None


async def get_drummond_agent() -> Optional['CommunicationAgent']:
    """
    Get or create Drummond agent instance.
    This function handles lazy initialization to avoid import-time issues.
    """
    global _drummond_instance, _initialized, _import_error
    
    if not _initialized:
        try:
            # Try to import the full Drummond first
            logger.info("Attempting to import CommunicationAgent...")
            from src.agents.drummond import CommunicationAgent
            
            logger.info("Creating Drummond agent instance...")
            _drummond_instance = CommunicationAgent()
            
            logger.info("Initializing Drummond agent...")
            await _drummond_instance.initialize()
            
            _initialized = True
            logger.info("Full Drummond agent ready with Maritaca AI")
            
        except Exception as e:
            logger.warning(f"Failed to load full Drummond, falling back to simple version: {e}")
            
            try:
                # Fallback to simplified version
                from src.agents.drummond_simple import SimpleDrummondAgent
                
                logger.info("Creating SimpleDrummondAgent instance...")
                _drummond_instance = SimpleDrummondAgent()
                
                logger.info("Initializing SimpleDrummondAgent...")
                await _drummond_instance.initialize()
                
                _initialized = True
                logger.info("Simple Drummond agent ready")
                
            except Exception as e2:
                logger.error(f"Failed to create even simple Drummond: {e2}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                _drummond_instance = None
                _initialized = False
                _import_error = str(e2)
            
    return _drummond_instance