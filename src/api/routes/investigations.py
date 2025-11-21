"""
Module: api.routes.investigations
Description: Investigation endpoints for anomaly detection and irregularity analysis
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic import field_validator

from src.agents import AgentContext, InvestigatorAgent
from src.agents.zumbi_wrapper import patch_investigator_agent
from src.api.middleware.authentication import get_current_user
from src.config.system_users import SYSTEM_AUTO_MONITOR_USER_ID
from src.core import get_logger, json_utils
from src.infrastructure.observability.metrics import (
    BusinessMetrics,
    count_calls,
    track_time,
)
from src.services.forensic_enrichment_service import forensic_enrichment_service
from src.services.investigation_service_selector import investigation_service
from src.tools import TransparencyAPIFilter

logger = get_logger(__name__)

router = APIRouter()

# Apply the wrapper to InvestigatorAgent to add investigate_anomalies method
patch_investigator_agent()


class InvestigationRequest(BaseModel):
    """Request model for starting an investigation."""

    query: str = PydanticField(description="Investigation query or focus area")
    data_source: str = PydanticField(
        default="contracts", description="Data source to investigate"
    )
    filters: dict[str, Any] = PydanticField(
        default_factory=dict, description="Additional filters"
    )
    anomaly_types: list[str] = PydanticField(
        default=["price", "vendor", "temporal", "payment"],
        description="Types of anomalies to detect",
    )
    include_explanations: bool = PydanticField(
        default=True, description="Include AI explanations"
    )
    stream_results: bool = PydanticField(
        default=False, description="Stream results as they're found"
    )

    @field_validator("data_source")
    @classmethod
    def validate_data_source(cls, v):
        """Validate data source."""
        allowed_sources = [
            "contracts",
            "expenses",
            "agreements",
            "biddings",
            "servants",
        ]
        if v not in allowed_sources:
            raise ValueError(f"Data source must be one of: {allowed_sources}")
        return v

    @field_validator("anomaly_types")
    @classmethod
    def validate_anomaly_types(cls, v):
        """Validate anomaly types."""
        allowed_types = [
            "price",
            "vendor",
            "temporal",
            "payment",
            "duplicate",
            "pattern",
        ]
        invalid_types = [t for t in v if t not in allowed_types]
        if invalid_types:
            raise ValueError(
                f"Invalid anomaly types: {invalid_types}. Allowed: {allowed_types}"
            )
        return v


class InvestigationResponse(BaseModel):
    """Response model for investigation results."""

    investigation_id: str
    status: str
    query: str
    data_source: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    anomalies_found: int
    total_records_analyzed: int
    results: list[dict[str, Any]]
    summary: str
    confidence_score: float
    processing_time: float


class AnomalyResult(BaseModel):
    """Individual anomaly result."""

    anomaly_id: str
    type: str
    severity: str
    confidence: float
    description: str
    explanation: str
    affected_records: list[dict[str, Any]]
    suggested_actions: list[str]
    metadata: dict[str, Any]


class InvestigationStatus(BaseModel):
    """Investigation status response."""

    investigation_id: str
    status: str
    progress: float
    current_phase: str
    records_processed: int
    anomalies_detected: int
    estimated_completion: Optional[datetime] = None


# In-memory storage for investigation tracking (replace with database later)
_active_investigations: dict[str, dict[str, Any]] = {}


@router.post("/start", response_model=dict[str, str])
@count_calls("cidadao_ai_investigation_requests_total", labels={"operation": "start"})
@track_time("cidadao_ai_investigation_start_duration_seconds")
async def start_investigation(
    request: InvestigationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Start a new investigation for anomaly detection.

    Creates and queues an investigation task that will analyze government data
    for irregularities and suspicious patterns.
    """
    try:
        # Get user_id or use system default for unauthenticated requests
        user_id = current_user.get("user_id") or SYSTEM_AUTO_MONITOR_USER_ID

        # Create investigation in database (Supabase via REST API on HuggingFace)
        db_investigation = await investigation_service.create(
            user_id=user_id,
            query=request.query,
            data_source=request.data_source,
            filters=request.filters,
            anomaly_types=request.anomaly_types,
        )

        investigation_id = (
            db_investigation.id
            if hasattr(db_investigation, "id")
            else db_investigation["id"]
        )

        logger.info(
            "investigation_created_in_database",
            investigation_id=investigation_id,
            query=request.query,
            data_source=request.data_source,
            user_id=current_user.get("user_id"),
        )

    except Exception as e:
        # Fallback to in-memory if database fails
        logger.warning(
            "Failed to save investigation to database, using in-memory fallback",
            error=str(e),
        )
        investigation_id = str(uuid4())

    # Keep in-memory copy for backward compatibility and fast access
    _active_investigations[investigation_id] = {
        "id": investigation_id,
        "status": "started",
        "query": request.query,
        "data_source": request.data_source,
        "filters": request.filters,
        "anomaly_types": request.anomaly_types,
        "user_id": user_id,  # Use the same user_id as database
        "started_at": datetime.now(UTC),
        "progress": 0.0,
        "current_phase": "initializing",
        "records_processed": 0,
        "anomalies_detected": 0,
        "results": [],
    }

    # Start investigation in background
    background_tasks.add_task(_run_investigation, investigation_id, request)

    logger.info(
        "investigation_started",
        investigation_id=investigation_id,
        query=request.query,
        data_source=request.data_source,
        user_id=current_user.get("user_id"),
    )

    # Track business metrics
    BusinessMetrics.record_investigation_created(
        priority="medium", user_type="authenticated"
    )
    BusinessMetrics.update_active_investigations(len(_active_investigations))

    return {
        "investigation_id": investigation_id,
        "status": "started",
        "message": "Investigation queued for processing",
    }


@router.get("/stream/{investigation_id}")
async def stream_investigation_results(
    investigation_id: str, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Stream investigation results in real-time.

    Returns a streaming response with investigation progress and results
    as they are discovered.
    """
    if investigation_id not in _active_investigations:
        raise HTTPException(status_code=404, detail="Investigation not found")

    investigation = _active_investigations[investigation_id]

    # Check user authorization
    if investigation["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    async def generate_updates():
        """Generate real-time updates for the investigation."""
        last_update = 0

        while True:
            current_investigation = _active_investigations.get(investigation_id)
            if not current_investigation:
                break

            # Send progress updates
            if current_investigation["progress"] > last_update:
                update_data = {
                    "type": "progress",
                    "investigation_id": investigation_id,
                    "progress": current_investigation["progress"],
                    "current_phase": current_investigation["current_phase"],
                    "records_processed": current_investigation["records_processed"],
                    "anomalies_detected": current_investigation["anomalies_detected"],
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                yield f"data: {json_utils.dumps(update_data)}\n\n"
                last_update = current_investigation["progress"]

            # Send anomaly results as they're found
            new_results = current_investigation["results"][
                len(current_investigation.get("sent_results", [])) :
            ]
            for result in new_results:
                result_data = {
                    "type": "anomaly",
                    "investigation_id": investigation_id,
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                yield f"data: {json_utils.dumps(result_data)}\n\n"

            # Mark results as sent
            current_investigation["sent_results"] = current_investigation[
                "results"
            ].copy()

            # Check if investigation is complete
            if current_investigation["status"] in ["completed", "failed"]:
                completion_data = {
                    "type": "completion",
                    "investigation_id": investigation_id,
                    "status": current_investigation["status"],
                    "total_anomalies": len(current_investigation["results"]),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                yield f"data: {json_utils.dumps(completion_data)}\n\n"
                break

            await asyncio.sleep(1)  # Poll every second

    return StreamingResponse(
        generate_updates(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )


@router.get("/{investigation_id}/status", response_model=InvestigationStatus)
async def get_investigation_status(
    investigation_id: str, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Get the current status of an investigation.

    Returns progress information and current phase of the investigation.
    """
    if investigation_id not in _active_investigations:
        raise HTTPException(status_code=404, detail="Investigation not found")

    investigation = _active_investigations[investigation_id]

    # Check user authorization
    if investigation["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    return InvestigationStatus(
        investigation_id=investigation_id,
        status=investigation["status"],
        progress=investigation["progress"],
        current_phase=investigation["current_phase"],
        records_processed=investigation["records_processed"],
        anomalies_detected=investigation["anomalies_detected"],
    )


@router.get("/{investigation_id}/results", response_model=InvestigationResponse)
async def get_investigation_results(
    investigation_id: str, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Get complete investigation results.

    Returns all anomalies found and analysis summary.
    """
    if investigation_id not in _active_investigations:
        raise HTTPException(status_code=404, detail="Investigation not found")

    investigation = _active_investigations[investigation_id]

    # Check user authorization
    if investigation["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    if investigation["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=409, detail="Investigation not yet completed")

    processing_time = 0.0
    if investigation.get("completed_at") and investigation.get("started_at"):
        processing_time = (
            investigation["completed_at"] - investigation["started_at"]
        ).total_seconds()

    return InvestigationResponse(
        investigation_id=investigation_id,
        status=investigation["status"],
        query=investigation["query"],
        data_source=investigation["data_source"],
        started_at=investigation["started_at"],
        completed_at=investigation.get("completed_at"),
        anomalies_found=len(investigation["results"]),
        total_records_analyzed=investigation["records_processed"],
        results=investigation["results"],
        summary=investigation.get("summary", "Investigation completed"),
        confidence_score=investigation.get("confidence_score", 0.0),
        processing_time=processing_time,
    )


@router.get("/", response_model=list[InvestigationStatus])
async def list_investigations(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(
        10, ge=1, le=100, description="Number of investigations to return"
    ),
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    List user's investigations.

    Returns a list of investigations owned by the current user.
    """
    user_id = current_user.get("user_id")

    # Filter investigations by user
    user_investigations = [
        inv for inv in _active_investigations.values() if inv["user_id"] == user_id
    ]

    # Filter by status if provided
    if status:
        user_investigations = [
            inv for inv in user_investigations if inv["status"] == status
        ]

    # Sort by start time (newest first)
    user_investigations.sort(key=lambda x: x["started_at"], reverse=True)

    # Apply limit
    user_investigations = user_investigations[:limit]

    return [
        InvestigationStatus(
            investigation_id=inv["id"],
            status=inv["status"],
            progress=inv["progress"],
            current_phase=inv["current_phase"],
            records_processed=inv["records_processed"],
            anomalies_detected=inv["anomalies_detected"],
        )
        for inv in user_investigations
    ]


@router.delete("/{investigation_id}")
async def cancel_investigation(
    investigation_id: str, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Cancel a running investigation.

    Stops the investigation and removes it from the queue.
    """
    if investigation_id not in _active_investigations:
        raise HTTPException(status_code=404, detail="Investigation not found")

    investigation = _active_investigations[investigation_id]

    # Check user authorization
    if investigation["user_id"] != current_user.get("user_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    if investigation["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=409, detail="Investigation already finished")

    # Mark as cancelled
    investigation["status"] = "cancelled"
    investigation["completed_at"] = datetime.now(UTC)

    logger.info(
        "investigation_cancelled",
        investigation_id=investigation_id,
        user_id=current_user.get("user_id"),
    )

    return {"message": "Investigation cancelled successfully"}


async def _run_investigation(investigation_id: str, request: InvestigationRequest):
    """
    Execute the investigation in the background.

    This function runs the actual anomaly detection using InvestigatorAgent.
    """
    investigation = _active_investigations[investigation_id]
    start_time = datetime.now(UTC)

    try:
        # Update status
        investigation["status"] = "running"
        investigation["current_phase"] = "data_retrieval"
        investigation["progress"] = 0.1

        # Update in database
        try:
            await investigation_service.update_status(
                investigation_id=investigation_id,
                status="running",
                progress=0.1,
                current_phase="data_retrieval",
                started_at=start_time,
            )
        except Exception as e:
            logger.warning(f"Failed to update investigation status in database: {e}")

        # Create agent context
        context = AgentContext(
            investigation_id=investigation_id,
            user_id=investigation["user_id"],
            metadata={"investigation_query": request.query},
        )

        # Initialize InvestigatorAgent
        investigator = InvestigatorAgent()

        # Prepare filters for data retrieval
        filters = TransparencyAPIFilter(**request.filters)

        investigation["current_phase"] = "anomaly_detection"
        investigation["progress"] = 0.3

        # Update progress in database
        try:
            await investigation_service.update_status(
                investigation_id=investigation_id,
                status="running",
                progress=0.3,
                current_phase="anomaly_detection",
            )
        except Exception as e:
            logger.warning(f"Failed to update investigation progress in database: {e}")

        # Execute investigation and track contracts analyzed
        results = await investigator.investigate_anomalies(
            query=request.query,
            data_source=request.data_source,
            filters=filters,
            anomaly_types=request.anomaly_types,
            context=context,
        )

        # Get total contracts analyzed from context metadata
        total_contracts_analyzed = context.metadata.get("total_contracts_analyzed", 0)

        investigation["current_phase"] = "forensic_enrichment"
        investigation["progress"] = 0.7

        # Process results with forensic enrichment
        enriched_results = []
        for result in results:
            try:
                # Extract contract data from affected entities
                contract_data = (
                    result.affected_entities[0] if result.affected_entities else {}
                )

                # Get comparative data from remaining affected entities or metadata
                comparative_data = (
                    result.affected_entities[1:]
                    if len(result.affected_entities) > 1
                    else None
                )

                # Build basic anomaly structure
                basic_anomaly = {
                    "type": result.anomaly_type,
                    "severity": result.severity,
                    "confidence": result.confidence,
                    "description": result.description,
                    "explanation": (
                        result.explanation if request.include_explanations else ""
                    ),
                    "recommendations": result.recommendations,
                    "metadata": result.metadata,
                }

                # Enrich with forensic details
                forensic_result = await forensic_enrichment_service.enrich_anomaly(
                    basic_anomaly=basic_anomaly,
                    contract_data=contract_data,
                    comparative_data=comparative_data,
                )

                enriched_results.append(forensic_result.to_dict())

            except Exception as e:
                logger.warning(
                    "Failed to enrich anomaly with forensic details, using basic result",
                    error=str(e),
                    anomaly_type=result.anomaly_type,
                )
                # Fallback to basic result if enrichment fails
                enriched_results.append(
                    {
                        "anomaly_id": str(uuid4()),
                        "type": result.anomaly_type,
                        "severity": result.severity,
                        "confidence": result.confidence,
                        "description": result.description,
                        "explanation": (
                            result.explanation if request.include_explanations else ""
                        ),
                        "affected_records": result.affected_entities,
                        "suggested_actions": result.recommendations,
                        "metadata": result.metadata,
                    }
                )

        investigation["results"] = enriched_results

        investigation["anomalies_detected"] = len(results)
        investigation["records_processed"] = (
            total_contracts_analyzed
            if total_contracts_analyzed > 0
            else sum(len(r.affected_entities) for r in results)
        )

        # Generate summary
        investigation["current_phase"] = "summary_generation"
        investigation["progress"] = 0.9

        summary = await investigator.generate_summary(results, context)
        investigation["summary"] = summary
        investigation["confidence_score"] = (
            sum(r.confidence for r in results) / len(results) if results else 0.0
        )

        # Mark as completed
        investigation["status"] = "completed"
        investigation["completed_at"] = datetime.now(UTC)
        investigation["progress"] = 1.0
        investigation["current_phase"] = "completed"

        # Save final results to database
        try:
            await investigation_service.update_status(
                investigation_id=investigation_id,
                status="completed",
                progress=1.0,
                current_phase="completed",
                total_records_analyzed=investigation["records_processed"],
                anomalies_found=investigation["anomalies_detected"],
                summary=summary,
                confidence_score=investigation["confidence_score"],
                results=investigation["results"],
                completed_at=investigation["completed_at"],
            )
            logger.info(
                "investigation_saved_to_database",
                investigation_id=investigation_id,
                records=investigation["records_processed"],
                anomalies=investigation["anomalies_detected"],
            )
        except Exception as e:
            logger.error(
                "Failed to save investigation results to database",
                investigation_id=investigation_id,
                error=str(e),
                exc_info=True,
            )

        # Calculate duration
        duration = (datetime.now(UTC) - start_time).total_seconds()

        logger.info(
            "investigation_completed",
            investigation_id=investigation_id,
            anomalies_found=len(results),
            records_analyzed=investigation["records_processed"],
        )

        # Track business metrics
        BusinessMetrics.record_investigation_completed(
            investigation_type=request.data_source,
            duration_seconds=duration,
            priority="medium",
        )
        BusinessMetrics.update_active_investigations(len(_active_investigations) - 1)

        # Track anomalies found
        for result in results:
            BusinessMetrics.record_anomaly_detected(
                anomaly_type=result.anomaly_type,
                severity=result.severity,
                data_source=request.data_source,
                confidence_score=result.confidence,
            )

    except Exception as e:
        logger.error(
            "investigation_failed",
            investigation_id=investigation_id,
            error=str(e),
        )

        investigation["status"] = "failed"
        investigation["completed_at"] = datetime.now(UTC)
        investigation["current_phase"] = "failed"
        investigation["error"] = str(e)

        # Save failure to database
        try:
            await investigation_service.update_status(
                investigation_id=investigation_id,
                status="failed",
                progress=investigation.get("progress", 0.0),
                current_phase="failed",
                error=str(e),
            )
        except Exception as db_error:
            logger.error(
                "Failed to save investigation failure to database",
                investigation_id=investigation_id,
                error=str(db_error),
            )


# ============================================================================
# PUBLIC ENDPOINTS (No Authentication Required)
# ============================================================================
# These endpoints are used by system processes like Celery Beat for
# automatic investigations and other automated workflows.
# ============================================================================


class PublicInvestigationRequest(BaseModel):
    """Public request model for system-created investigations."""

    query: str = PydanticField(description="Investigation query")
    data_source: str = PydanticField(default="contracts", description="Data source")
    filters: dict[str, Any] = PydanticField(default_factory=dict, description="Filters")
    anomaly_types: list[str] = PydanticField(
        default=["price", "vendor", "temporal", "payment"], description="Anomaly types"
    )
    # System identification (for audit)
    system_name: str = PydanticField(
        default="auto_investigation_service",
        description="System creating investigation",
    )

    @field_validator("data_source")
    @classmethod
    def validate_data_source(cls, v):
        """Validate data source."""
        allowed_sources = [
            "contracts",
            "expenses",
            "agreements",
            "biddings",
            "servants",
        ]
        if v not in allowed_sources:
            raise ValueError(f"Data source must be one of: {allowed_sources}")
        return v


@router.post("/public/create", response_model=dict[str, str])
@count_calls(
    "cidadao_ai_public_investigation_requests_total",
    labels={"operation": "public_create"},
)
@track_time("cidadao_ai_public_investigation_create_duration_seconds")
async def create_public_investigation(
    request: PublicInvestigationRequest, background_tasks: BackgroundTasks
):
    """
    Create investigation without authentication (for system processes).

    This endpoint is used by automated processes like Celery Beat auto-investigations.
    Investigations are created with the system user ID.

    **Security Note**: This endpoint should be protected at the infrastructure level
    (firewall, API gateway) to prevent abuse.
    """
    try:
        # Create investigation with system user
        db_investigation = await investigation_service.create(
            user_id=SYSTEM_AUTO_MONITOR_USER_ID,
            query=request.query,
            data_source=request.data_source,
            filters={
                **request.filters,
                "system_created": True,
                "system_name": request.system_name,
            },
            anomaly_types=request.anomaly_types,
        )

        investigation_id = (
            db_investigation.id
            if hasattr(db_investigation, "id")
            else db_investigation["id"]
        )

        logger.info(
            "public_investigation_created",
            investigation_id=investigation_id,
            query=request.query[:100],
            data_source=request.data_source,
            system_name=request.system_name,
            user_id=SYSTEM_AUTO_MONITOR_USER_ID,
        )

        # Keep in-memory copy for backward compatibility
        _active_investigations[investigation_id] = {
            "id": investigation_id,
            "status": "started",
            "query": request.query,
            "data_source": request.data_source,
            "filters": request.filters,
            "anomaly_types": request.anomaly_types,
            "user_id": SYSTEM_AUTO_MONITOR_USER_ID,
            "system_created": True,
            "system_name": request.system_name,
            "started_at": datetime.now(UTC),
            "progress": 0.0,
            "current_phase": "initializing",
            "records_processed": 0,
            "anomalies_detected": 0,
            "results": [],
        }

        # Start investigation in background
        background_tasks.add_task(
            _run_investigation,
            investigation_id,
            InvestigationRequest(
                query=request.query,
                data_source=request.data_source,
                filters=request.filters,
                anomaly_types=request.anomaly_types,
            ),
        )

        # Track business metrics
        BusinessMetrics.record_investigation_created(
            priority="medium", user_type="system"
        )
        BusinessMetrics.update_active_investigations(len(_active_investigations))

        return {
            "investigation_id": investigation_id,
            "status": "started",
            "message": "System investigation queued for processing",
            "system_user_id": SYSTEM_AUTO_MONITOR_USER_ID,
        }

    except Exception as e:
        logger.error(
            "public_investigation_creation_failed",
            error=str(e),
            system_name=request.system_name,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to create investigation: {str(e)}"
        )


@router.get("/public/status/{investigation_id}", response_model=InvestigationStatus)
async def get_public_investigation_status(investigation_id: str):
    """
    Get investigation status without authentication (for system processes).

    This endpoint allows monitoring investigations created by automated processes
    without requiring authentication.
    """
    if investigation_id not in _active_investigations:
        # Try to fetch from database if not in memory
        try:
            db_investigation = await investigation_service.get_by_id(investigation_id)
            if db_investigation:
                return InvestigationStatus(
                    investigation_id=investigation_id,
                    status=db_investigation.status,
                    progress=getattr(db_investigation, "progress", 0.0),
                    current_phase=getattr(db_investigation, "current_phase", "unknown"),
                    records_processed=getattr(db_investigation, "records_processed", 0),
                    anomalies_detected=getattr(db_investigation, "anomalies_found", 0),
                )
        except Exception as e:
            logger.warning(
                "Investigation not found in memory or database",
                investigation_id=investigation_id,
                error=str(e),
            )

        raise HTTPException(status_code=404, detail="Investigation not found")

    investigation = _active_investigations[investigation_id]

    return InvestigationStatus(
        investigation_id=investigation_id,
        status=investigation["status"],
        progress=investigation["progress"],
        current_phase=investigation["current_phase"],
        records_processed=investigation["records_processed"],
        anomalies_detected=investigation["anomalies_detected"],
    )


@router.get("/public/results/{investigation_id}", response_model=InvestigationResponse)
async def get_public_investigation_results(investigation_id: str):
    """
    Get complete investigation results without authentication (for public access).

    This endpoint allows retrieving investigation results without authentication,
    making it suitable for public dashboards, sharing, and system monitoring.

    Returns all anomalies found, analysis summary, and processing metrics.
    """
    # Check in-memory first
    if investigation_id in _active_investigations:
        investigation = _active_investigations[investigation_id]

        if investigation["status"] not in ["completed", "failed"]:
            raise HTTPException(
                status_code=409, detail="Investigation not yet completed"
            )

        processing_time = 0.0
        if investigation.get("completed_at") and investigation.get("started_at"):
            processing_time = (
                investigation["completed_at"] - investigation["started_at"]
            ).total_seconds()

        return InvestigationResponse(
            investigation_id=investigation_id,
            status=investigation["status"],
            query=investigation["query"],
            data_source=investigation["data_source"],
            started_at=investigation["started_at"],
            completed_at=investigation.get("completed_at"),
            anomalies_found=len(investigation["results"]),
            total_records_analyzed=investigation["records_processed"],
            results=investigation["results"],
            summary=investigation.get("summary", "Investigation completed"),
            confidence_score=investigation.get("confidence_score", 0.0),
            processing_time=processing_time,
        )

    # Try to fetch from database if not in memory
    try:
        db_investigation = await investigation_service.get_by_id(investigation_id)
        if not db_investigation:
            raise HTTPException(status_code=404, detail="Investigation not found")

        # Check if completed
        if db_investigation.status not in ["completed", "failed"]:
            raise HTTPException(
                status_code=409, detail="Investigation not yet completed"
            )

        processing_time = 0.0
        if (
            hasattr(db_investigation, "completed_at")
            and hasattr(db_investigation, "started_at")
            and db_investigation.completed_at
            and db_investigation.started_at
        ):
            processing_time = (
                db_investigation.completed_at - db_investigation.started_at
            ).total_seconds()

        return InvestigationResponse(
            investigation_id=investigation_id,
            status=db_investigation.status,
            query=db_investigation.query,
            data_source=getattr(db_investigation, "data_source", "contracts"),
            started_at=db_investigation.started_at,
            completed_at=getattr(db_investigation, "completed_at", None),
            anomalies_found=getattr(db_investigation, "anomalies_found", 0),
            total_records_analyzed=getattr(
                db_investigation, "total_records_analyzed", 0
            ),
            results=getattr(db_investigation, "results", []) or [],
            summary=getattr(
                db_investigation, "summary", "Investigation completed from database"
            ),
            confidence_score=getattr(db_investigation, "confidence_score", 0.0),
            processing_time=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to fetch investigation results from database",
            investigation_id=investigation_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve results: {str(e)}"
        )


@router.get("/public/health", response_model=dict[str, Any])
async def public_health_check():
    """
    Health check for public investigation endpoints.

    Returns system status and basic metrics.
    """
    try:
        # Quick check of investigation service
        test_success = True
        try:
            # Just verify the service is accessible
            _ = investigation_service
        except Exception as e:
            test_success = False
            logger.error("Investigation service health check failed", error=str(e))

        return {
            "status": "healthy" if test_success else "degraded",
            "timestamp": datetime.now(UTC).isoformat(),
            "system_user_configured": bool(SYSTEM_AUTO_MONITOR_USER_ID),
            "investigation_service_available": test_success,
            "active_investigations": len(_active_investigations),
        }
    except Exception as e:
        logger.error("Public health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }
