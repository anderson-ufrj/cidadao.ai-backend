"""
Investigation service using Supabase REST API (HuggingFace Spaces compatible).

This version uses HTTP/HTTPS REST API instead of direct PostgreSQL connections,
making it work on HuggingFace Spaces and other restricted environments.
"""

from typing import List, Optional, Dict, Any

from src.core import get_logger
from src.services.supabase_service_rest import get_supabase_service_rest
from src.agents import get_agent_pool
from src.agents.deodoro import AgentContext

logger = get_logger(__name__)


class InvestigationServiceSupabaseRest:
    """
    Service for managing investigations with Supabase via REST API.

    Compatible with HuggingFace Spaces and other environments that block
    direct database connections but allow HTTP/HTTPS.
    """

    def __init__(self):
        """Initialize investigation service."""
        self._supabase = None

    async def _get_supabase(self):
        """Lazy load Supabase service."""
        if self._supabase is None:
            self._supabase = await get_supabase_service_rest()
        return self._supabase

    async def create(
        self,
        user_id: str,
        query: str,
        data_source: str = "contracts",
        filters: Optional[Dict[str, Any]] = None,
        anomaly_types: Optional[List[str]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new investigation in Supabase.

        Args:
            user_id: User ID
            query: Investigation query
            data_source: Data source to investigate
            filters: Query filters
            anomaly_types: Types of anomalies to detect
            session_id: Optional session ID

        Returns:
            Created investigation dict
        """
        supabase = await self._get_supabase()

        investigation = await supabase.create_investigation(
            user_id=user_id,
            query=query,
            data_source=data_source,
            filters=filters or {},
            anomaly_types=anomaly_types or [],
            session_id=session_id,
        )

        logger.info(
            "investigation_created",
            investigation_id=investigation["id"],
            user_id=user_id,
            data_source=data_source,
        )

        return investigation

    async def start_investigation(
        self,
        investigation_id: str,
    ) -> None:
        """
        Start processing an investigation in the background.

        Args:
            investigation_id: Investigation UUID
        """
        supabase = await self._get_supabase()

        # Get investigation details
        investigation = await supabase.get_investigation(investigation_id)

        if not investigation:
            raise ValueError(f"Investigation {investigation_id} not found")

        # Update to processing status
        from datetime import datetime
        await supabase.update_investigation(
            investigation_id,
            status="processing",
            started_at=datetime.utcnow().isoformat(),
            progress=0.1,
            current_phase="initializing",
        )

        try:
            # Execute investigation with agents
            await self._execute_investigation(investigation)

        except Exception as e:
            logger.error(
                "investigation_execution_failed",
                investigation_id=investigation_id,
                error=str(e),
                exc_info=True,
            )

            # Mark as failed in Supabase
            await supabase.fail_investigation(
                investigation_id,
                error_message=str(e),
            )
            raise

    async def _execute_investigation(self, investigation: Dict[str, Any]):
        """
        Execute investigation using the agent system.

        Args:
            investigation: Investigation dict from database
        """
        investigation_id = investigation["id"]
        supabase = await self._get_supabase()

        # Update progress: data retrieval
        await supabase.update_progress(
            investigation_id,
            progress=0.2,
            current_phase="data_retrieval",
        )

        # Get agent pool
        pool = await get_agent_pool()

        # Create agent context
        context = AgentContext(
            investigation_id=investigation_id,
            user_id=investigation["user_id"],
            session_id=investigation.get("session_id"),
            metadata={
                "data_source": investigation["data_source"],
                "filters": investigation.get("filters", {}),
                "anomaly_types": investigation.get("anomaly_types", []),
            }
        )

        # Update progress: anomaly detection
        await supabase.update_progress(
            investigation_id,
            progress=0.4,
            current_phase="anomaly_detection",
        )

        # Execute with investigator agent
        from src.agents import InvestigatorAgent
        investigator = InvestigatorAgent()

        # Prepare investigation parameters
        from src.tools import TransparencyAPIFilter
        filters = TransparencyAPIFilter(**investigation.get("filters", {}))

        # Execute investigation
        results = await investigator.investigate_anomalies(
            query=investigation["query"],
            data_source=investigation["data_source"],
            filters=filters,
            anomaly_types=investigation.get("anomaly_types", []),
            context=context,
        )

        # Update progress: analysis
        await supabase.update_progress(
            investigation_id,
            progress=0.7,
            current_phase="analysis",
            records_processed=sum(len(r.affected_data) for r in results),
            anomalies_found=len(results),
        )

        # Generate summary
        summary = await investigator.generate_summary(results, context)

        # Calculate confidence
        confidence_score = (
            sum(r.confidence for r in results) / len(results)
            if results else 0.0
        )

        # Format results for storage
        import uuid
        formatted_results = [
            {
                "anomaly_id": str(uuid.uuid4()),
                "type": result.anomaly_type,
                "severity": result.severity,
                "confidence": result.confidence,
                "description": result.description,
                "explanation": result.explanation,
                "affected_records": result.affected_data,
                "suggested_actions": result.recommendations,
                "metadata": result.metadata,
            }
            for result in results
        ]

        # Complete investigation in Supabase
        await supabase.complete_investigation(
            investigation_id=investigation_id,
            results=formatted_results,
            summary=summary,
            confidence_score=confidence_score,
            total_records=sum(len(r.affected_data) for r in results),
            anomalies_found=len(results),
        )

        logger.info(
            "investigation_completed",
            investigation_id=investigation_id,
            anomalies_found=len(results),
            confidence_score=confidence_score,
        )

    async def update_progress(
        self,
        investigation_id: str,
        progress: float,
        current_phase: str,
        records_processed: Optional[int] = None,
        anomalies_found: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Update investigation progress.

        Args:
            investigation_id: Investigation UUID
            progress: Progress percentage (0.0 to 1.0)
            current_phase: Current processing phase
            records_processed: Number of records processed
            anomalies_found: Number of anomalies detected

        Returns:
            Updated investigation dict
        """
        supabase = await self._get_supabase()
        return await supabase.update_progress(
            investigation_id=investigation_id,
            progress=progress,
            current_phase=current_phase,
            records_processed=records_processed,
            anomalies_found=anomalies_found,
        )

    async def complete_investigation(
        self,
        investigation_id: str,
        results: List[Dict[str, Any]],
        summary: str,
        confidence_score: float,
        total_records: int = 0,
        anomalies_found: int = 0,
    ) -> Dict[str, Any]:
        """
        Mark investigation as completed with results.

        Args:
            investigation_id: Investigation UUID
            results: List of anomaly results
            summary: Investigation summary
            confidence_score: Overall confidence
            total_records: Total records analyzed
            anomalies_found: Total anomalies found

        Returns:
            Updated investigation dict
        """
        supabase = await self._get_supabase()
        return await supabase.complete_investigation(
            investigation_id=investigation_id,
            results=results,
            summary=summary,
            confidence_score=confidence_score,
            total_records=total_records,
            anomalies_found=anomalies_found,
        )

    async def get(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get investigation by ID (alias for get_by_id).

        Args:
            investigation_id: Investigation UUID

        Returns:
            Investigation dict or None
        """
        return await self.get_by_id(investigation_id)

    async def get_by_id(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get investigation by ID.

        Args:
            investigation_id: Investigation UUID

        Returns:
            Investigation dict or None
        """
        supabase = await self._get_supabase()
        return await supabase.get_investigation(investigation_id)

    async def update_status(
        self,
        investigation_id: str,
        status: str,
        progress: Optional[float] = None,
        current_phase: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update investigation status and progress.

        Args:
            investigation_id: Investigation UUID
            status: New status
            progress: Progress percentage
            current_phase: Current phase
            **kwargs: Additional fields to update

        Returns:
            Updated investigation dict
        """
        supabase = await self._get_supabase()

        updates = {"status": status}

        if progress is not None:
            updates["progress"] = progress

        if current_phase is not None:
            updates["current_phase"] = current_phase

        updates.update(kwargs)

        return await supabase.update_investigation(investigation_id, **updates)

    async def search(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Search investigations with filters.

        Args:
            user_id: Filter by user ID
            status: Filter by status
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of investigation dicts
        """
        if not user_id:
            raise ValueError("user_id is required for investigation search")

        supabase = await self._get_supabase()
        return await supabase.list_user_investigations(
            user_id=user_id,
            limit=limit,
            offset=offset,
            status=status,
        )

    async def cancel(self, investigation_id: str, user_id: str) -> Dict[str, Any]:
        """
        Cancel a running investigation.

        Args:
            investigation_id: Investigation UUID
            user_id: User ID (for authorization)

        Returns:
            Updated investigation dict
        """
        supabase = await self._get_supabase()

        # Get investigation to check ownership
        investigation = await supabase.get_investigation(investigation_id)

        if not investigation:
            raise ValueError(f"Investigation {investigation_id} not found")

        if investigation["user_id"] != user_id:
            raise ValueError("Unauthorized: investigation belongs to another user")

        if investigation["status"] in ["completed", "failed", "cancelled"]:
            raise ValueError(
                f"Cannot cancel investigation in {investigation['status']} status"
            )

        # Mark as cancelled
        deleted = await supabase.delete_investigation(investigation_id, user_id)

        if not deleted:
            raise ValueError(f"Failed to cancel investigation {investigation_id}")

        logger.info(
            "investigation_cancelled",
            investigation_id=investigation_id,
            user_id=user_id,
        )

        # Return updated investigation
        return await supabase.get_investigation(investigation_id)

    async def get_user_investigations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get investigations for a user.

        Args:
            user_id: User ID
            limit: Maximum results

        Returns:
            List of investigation dicts
        """
        return await self.search(user_id=user_id, limit=limit)


# Global service instance
investigation_service_supabase_rest = InvestigationServiceSupabaseRest()
