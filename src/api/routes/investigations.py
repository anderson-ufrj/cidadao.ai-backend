"""
Module: api.routes.investigations
Description: Investigation endpoints for anomaly detection and irregularity analysis
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field as PydanticField, validator
import json

from src.core import get_logger
from src.agents import InvestigatorAgent, AgentContext
from src.api.middleware.authentication import get_current_user
from src.tools import TransparencyAPIFilter


logger = get_logger(__name__)

router = APIRouter()


class InvestigationRequest(BaseModel):
    """Request model for starting an investigation."""
    
    query: str = PydanticField(description="Investigation query or focus area")
    data_source: str = PydanticField(default="contracts", description="Data source to investigate")
    filters: Dict[str, Any] = PydanticField(default_factory=dict, description="Additional filters")
    anomaly_types: List[str] = PydanticField(
        default=["price", "vendor", "temporal", "payment"],
        description="Types of anomalies to detect"
    )
    include_explanations: bool = PydanticField(default=True, description="Include AI explanations")
    stream_results: bool = PydanticField(default=False, description="Stream results as they're found")
    
    @validator('data_source')
    def validate_data_source(cls, v):
        """Validate data source."""
        allowed_sources = ['contracts', 'expenses', 'agreements', 'biddings', 'servants']
        if v not in allowed_sources:
            raise ValueError(f'Data source must be one of: {allowed_sources}')
        return v
    
    @validator('anomaly_types')
    def validate_anomaly_types(cls, v):
        """Validate anomaly types."""
        allowed_types = ['price', 'vendor', 'temporal', 'payment', 'duplicate', 'pattern']
        invalid_types = [t for t in v if t not in allowed_types]
        if invalid_types:
            raise ValueError(f'Invalid anomaly types: {invalid_types}. Allowed: {allowed_types}')
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
    results: List[Dict[str, Any]]
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
    affected_records: List[Dict[str, Any]]
    suggested_actions: List[str]
    metadata: Dict[str, Any]


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
_active_investigations: Dict[str, Dict[str, Any]] = {}


@router.post("/start", response_model=Dict[str, str])
async def start_investigation(
    request: InvestigationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start a new investigation for anomaly detection.
    
    Creates and queues an investigation task that will analyze government data
    for irregularities and suspicious patterns.
    """
    investigation_id = str(uuid4())
    
    # Store investigation metadata
    _active_investigations[investigation_id] = {
        "id": investigation_id,
        "status": "started",
        "query": request.query,
        "data_source": request.data_source,
        "filters": request.filters,
        "anomaly_types": request.anomaly_types,
        "user_id": current_user.get("user_id"),
        "started_at": datetime.utcnow(),
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
        request
    )
    
    logger.info(
        "investigation_started",
        investigation_id=investigation_id,
        query=request.query,
        data_source=request.data_source,
        user_id=current_user.get("user_id"),
    )
    
    return {
        "investigation_id": investigation_id,
        "status": "started",
        "message": "Investigation queued for processing"
    }


@router.get("/stream/{investigation_id}")
async def stream_investigation_results(
    investigation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
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
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(update_data)}\n\n"
                last_update = current_investigation["progress"]
            
            # Send anomaly results as they're found
            new_results = current_investigation["results"][len(current_investigation.get("sent_results", [])):]
            for result in new_results:
                result_data = {
                    "type": "anomaly",
                    "investigation_id": investigation_id,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(result_data)}\n\n"
            
            # Mark results as sent
            current_investigation["sent_results"] = current_investigation["results"].copy()
            
            # Check if investigation is complete
            if current_investigation["status"] in ["completed", "failed"]:
                completion_data = {
                    "type": "completion",
                    "investigation_id": investigation_id,
                    "status": current_investigation["status"],
                    "total_anomalies": len(current_investigation["results"]),
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                break
            
            await asyncio.sleep(1)  # Poll every second
    
    return StreamingResponse(
        generate_updates(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@router.get("/{investigation_id}/status", response_model=InvestigationStatus)
async def get_investigation_status(
    investigation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
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
    investigation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
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
        processing_time = (investigation["completed_at"] - investigation["started_at"]).total_seconds()
    
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
        processing_time=processing_time
    )


@router.get("/", response_model=List[InvestigationStatus])
async def list_investigations(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Number of investigations to return"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List user's investigations.
    
    Returns a list of investigations owned by the current user.
    """
    user_id = current_user.get("user_id")
    
    # Filter investigations by user
    user_investigations = [
        inv for inv in _active_investigations.values()
        if inv["user_id"] == user_id
    ]
    
    # Filter by status if provided
    if status:
        user_investigations = [inv for inv in user_investigations if inv["status"] == status]
    
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
    investigation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
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
    investigation["completed_at"] = datetime.utcnow()
    
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
    
    try:
        # Update status
        investigation["status"] = "running"
        investigation["current_phase"] = "data_retrieval"
        investigation["progress"] = 0.1
        
        # Create agent context
        context = AgentContext(
            conversation_id=investigation_id,
            user_id=investigation["user_id"],
            session_data={"investigation_query": request.query}
        )
        
        # Initialize InvestigatorAgent
        investigator = InvestigatorAgent()
        
        # Prepare filters for data retrieval
        filters = TransparencyAPIFilter(**request.filters)
        
        investigation["current_phase"] = "anomaly_detection"
        investigation["progress"] = 0.3
        
        # Execute investigation
        results = await investigator.investigate_anomalies(
            query=request.query,
            data_source=request.data_source,
            filters=filters,
            anomaly_types=request.anomaly_types,
            context=context
        )
        
        investigation["current_phase"] = "analysis"
        investigation["progress"] = 0.7
        
        # Process results
        investigation["results"] = [
            {
                "anomaly_id": str(uuid4()),
                "type": result.anomaly_type,
                "severity": result.severity,
                "confidence": result.confidence,
                "description": result.description,
                "explanation": result.explanation if request.include_explanations else "",
                "affected_records": result.affected_data,
                "suggested_actions": result.recommendations,
                "metadata": result.metadata,
            }
            for result in results
        ]
        
        investigation["anomalies_detected"] = len(results)
        investigation["records_processed"] = sum(len(r.affected_data) for r in results)
        
        # Generate summary
        investigation["current_phase"] = "summary_generation"
        investigation["progress"] = 0.9
        
        summary = await investigator.generate_summary(results, context)
        investigation["summary"] = summary
        investigation["confidence_score"] = sum(r.confidence for r in results) / len(results) if results else 0.0
        
        # Mark as completed
        investigation["status"] = "completed"
        investigation["completed_at"] = datetime.utcnow()
        investigation["progress"] = 1.0
        investigation["current_phase"] = "completed"
        
        logger.info(
            "investigation_completed",
            investigation_id=investigation_id,
            anomalies_found=len(results),
            records_analyzed=investigation["records_processed"],
        )
        
    except Exception as e:
        logger.error(
            "investigation_failed",
            investigation_id=investigation_id,
            error=str(e),
        )
        
        investigation["status"] = "failed"
        investigation["completed_at"] = datetime.utcnow()
        investigation["current_phase"] = "failed"
        investigation["error"] = str(e)