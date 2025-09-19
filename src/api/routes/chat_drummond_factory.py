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
            # Lazy import to avoid module-level import errors
            logger.info("Attempting to import CommunicationAgent...")
            from src.agents.drummond import CommunicationAgent
            
            logger.info("Creating Drummond agent instance...")
            _drummond_instance = CommunicationAgent()
            
            logger.info("Initializing Drummond agent...")
            await _drummond_instance.initialize()
            
            _initialized = True
            logger.info("Drummond agent ready")
            
        except ImportError as e:
            logger.error(f"Import error for Drummond agent: {e}")
            import traceback
            logger.error(f"Import traceback: {traceback.format_exc()}")
            _drummond_instance = None
            _initialized = False
            _import_error = str(e)
            
        except Exception as e:
            logger.error(f"Failed to create/initialize Drummond: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            _drummond_instance = None
            _initialized = False
            _import_error = str(e)
            
    return _drummond_instance