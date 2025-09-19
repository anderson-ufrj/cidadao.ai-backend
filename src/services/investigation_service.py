"""
Investigation service for managing investigations.

This module provides a service layer for investigation operations,
abstracting the database and agent interactions.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from dataclasses import dataclass

from src.core import get_logger
from src.agents import MasterAgent, get_agent_pool
from src.agents.deodoro import AgentContext

logger = get_logger(__name__)


@dataclass
class InvestigationModel:
    """Investigation data model."""
    id: str
    user_id: str
    query: str
    status: str
    confidence_score: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class InvestigationService:
    """
    Service for managing investigations.
    
    This is a simplified implementation. In production,
    this would interact with the database.
    """
    
    def __init__(self):
        """Initialize investigation service."""
        self._investigations: Dict[str, InvestigationModel] = {}
    
    async def create(
        self,
        user_id: str,
        query: str,
        data_sources: Optional[List[str]] = None,
        priority: str = "medium",
        context: Optional[Dict[str, Any]] = None
    ) -> InvestigationModel:
        """
        Create a new investigation.
        
        Args:
            user_id: User ID
            query: Investigation query
            data_sources: Data sources to use
            priority: Investigation priority
            context: Additional context
            
        Returns:
            Created investigation
        """
        investigation_id = str(uuid.uuid4())
        
        investigation = InvestigationModel(
            id=investigation_id,
            user_id=user_id,
            query=query,
            status="pending",
            confidence_score=0.0,
            created_at=datetime.utcnow(),
            metadata={
                "data_sources": data_sources or [],
                "priority": priority,
                "context": context or {}
            }
        )
        
        self._investigations[investigation_id] = investigation
        
        # Start investigation asynchronously
        import asyncio
        asyncio.create_task(self._execute_investigation(investigation))
        
        logger.info(f"Created investigation {investigation_id} for user {user_id}")
        return investigation
    
    async def _execute_investigation(self, investigation: InvestigationModel):
        """Execute investigation using agents."""
        try:
            start_time = datetime.utcnow()
            investigation.status = "processing"
            
            # Get agent pool
            pool = await get_agent_pool()
            
            # Create agent context
            context = AgentContext(
                investigation_id=investigation.id,
                user_id=investigation.user_id,
                data_sources=investigation.metadata.get("data_sources", [])
            )
            
            # Execute with master agent
            async with pool.acquire(MasterAgent, context) as master:
                result = await master._investigate(
                    {"query": investigation.query},
                    context
                )
            
            # Update investigation
            investigation.status = "completed"
            investigation.confidence_score = result.confidence_score
            investigation.completed_at = datetime.utcnow()
            investigation.processing_time_ms = (
                investigation.completed_at - start_time
            ).total_seconds() * 1000
            
            logger.info(f"Investigation {investigation.id} completed")
            
        except Exception as e:
            logger.error(f"Investigation {investigation.id} failed: {e}")
            investigation.status = "failed"
            investigation.completed_at = datetime.utcnow()
    
    async def get_by_id(self, investigation_id: str) -> Optional[InvestigationModel]:
        """Get investigation by ID."""
        return self._investigations.get(investigation_id)
    
    async def search(
        self,
        filters: Optional[List[Any]] = None,
        limit: int = 20,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_dir: str = "desc"
    ) -> List[InvestigationModel]:
        """
        Search investigations with filters.
        
        This is a simplified implementation.
        In production, this would query the database.
        """
        # Get all investigations
        investigations = list(self._investigations.values())
        
        # Sort by created_at desc by default
        investigations.sort(
            key=lambda x: x.created_at,
            reverse=(order_dir == "desc")
        )
        
        # Apply pagination
        start = offset
        end = offset + limit
        
        return investigations[start:end]
    
    async def cancel(self, investigation_id: str, user_id: str) -> InvestigationModel:
        """
        Cancel an investigation.
        
        Args:
            investigation_id: Investigation ID
            user_id: User ID (for authorization)
            
        Returns:
            Updated investigation
        """
        investigation = self._investigations.get(investigation_id)
        
        if not investigation:
            raise ValueError(f"Investigation {investigation_id} not found")
        
        if investigation.user_id != user_id:
            raise ValueError("Unauthorized")
        
        if investigation.status in ["completed", "failed", "cancelled"]:
            raise ValueError(f"Cannot cancel investigation in {investigation.status} status")
        
        investigation.status = "cancelled"
        investigation.completed_at = datetime.utcnow()
        
        logger.info(f"Investigation {investigation_id} cancelled by user {user_id}")
        return investigation
    
    async def get_user_investigations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[InvestigationModel]:
        """Get investigations for a user."""
        user_investigations = [
            inv for inv in self._investigations.values()
            if inv.user_id == user_id
        ]
        
        # Sort by created_at desc
        user_investigations.sort(
            key=lambda x: x.created_at,
            reverse=True
        )
        
        return user_investigations[:limit]


# Global service instance
investigation_service = InvestigationService()