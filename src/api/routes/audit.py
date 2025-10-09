"""
Audit routes for Cidadão.AI API
Security audit logging and monitoring endpoints
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from src.core.audit import (
    audit_logger,
    AuditFilter,
    AuditEvent,
    AuditEventType,
    AuditSeverity,
    AuditStatistics
)
from src.api.auth import get_current_user, require_admin, User

router = APIRouter(prefix="/api/v1/audit")


class AuditEventResponse(BaseModel):
    """Audit event response model."""
    
    id: str
    timestamp: datetime
    event_type: str
    severity: str
    message: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    details: dict = {}
    context: Optional[dict] = None


class AuditQueryRequest(BaseModel):
    """Audit query request model."""
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_types: Optional[List[AuditEventType]] = None
    severity_levels: Optional[List[AuditSeverity]] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    success_only: Optional[bool] = None
    ip_address: Optional[str] = None
    limit: int = 100
    offset: int = 0


@router.get("/events", response_model=List[AuditEventResponse])
async def get_audit_events(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    event_type: Optional[AuditEventType] = Query(None, description="Event type filter"),
    severity: Optional[AuditSeverity] = Query(None, description="Severity filter"),
    user_email: Optional[str] = Query(None, description="User email filter"),
    resource_type: Optional[str] = Query(None, description="Resource type filter"),
    success_only: Optional[bool] = Query(None, description="Success only filter"),
    limit: int = Query(100, le=1000, description="Result limit"),
    offset: int = Query(0, ge=0, description="Result offset"),
    current_user: User = Depends(get_current_user)
):
    """Get audit events (admin only)."""
    
    require_admin(current_user)
    
    # Build filter
    filter_options = AuditFilter(
        start_date=start_date,
        end_date=end_date,
        event_types=[event_type] if event_type else None,
        severity_levels=[severity] if severity else None,
        user_email=user_email,
        resource_type=resource_type,
        success_only=success_only,
        limit=limit,
        offset=offset
    )
    
    # Query events
    events = await audit_logger.query_events(filter_options)
    
    # Convert to response format
    response_events = []
    for event in events:
        response_events.append(AuditEventResponse(
            id=event.id,
            timestamp=event.timestamp,
            event_type=event.event_type.value,
            severity=event.severity.value,
            message=event.message,
            user_id=event.user_id,
            user_email=event.user_email,
            user_role=event.user_role,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            resource_name=event.resource_name,
            success=event.success,
            error_code=event.error_code,
            error_message=event.error_message,
            details=event.details,
            context=event.context.model_dump() if event.context else None
        ))
    
    return response_events


@router.post("/events/query", response_model=List[AuditEventResponse])
async def query_audit_events(
    query_request: AuditQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Query audit events with advanced filters (admin only)."""
    
    require_admin(current_user)
    
    # Convert to filter options
    filter_options = AuditFilter(**query_request.model_dump())
    
    # Query events
    events = await audit_logger.query_events(filter_options)
    
    # Convert to response format
    response_events = []
    for event in events:
        response_events.append(AuditEventResponse(
            id=event.id,
            timestamp=event.timestamp,
            event_type=event.event_type.value,
            severity=event.severity.value,
            message=event.message,
            user_id=event.user_id,
            user_email=event.user_email,
            user_role=event.user_role,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            resource_name=event.resource_name,
            success=event.success,
            error_code=event.error_code,
            error_message=event.error_message,
            details=event.details,
            context=event.context.model_dump() if event.context else None
        ))
    
    return response_events


@router.get("/statistics", response_model=AuditStatistics)
async def get_audit_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    current_user: User = Depends(get_current_user)
):
    """Get audit statistics (admin only)."""
    
    require_admin(current_user)
    
    statistics = await audit_logger.get_statistics(
        start_date=start_date,
        end_date=end_date
    )
    
    return statistics


@router.get("/export")
async def export_audit_events(
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    event_type: Optional[AuditEventType] = Query(None, description="Event type filter"),
    severity: Optional[AuditSeverity] = Query(None, description="Severity filter"),
    user_email: Optional[str] = Query(None, description="User email filter"),
    current_user: User = Depends(get_current_user)
):
    """Export audit events (admin only)."""
    
    require_admin(current_user)
    
    # Build filter
    filter_options = AuditFilter(
        start_date=start_date,
        end_date=end_date,
        event_types=[event_type] if event_type else None,
        severity_levels=[severity] if severity else None,
        user_email=user_email,
        limit=10000  # Allow larger exports
    )
    
    # Export events
    exported_data = await audit_logger.export_events(filter_options, format)
    
    # Set appropriate content type and filename
    if format == "json":
        media_type = "application/json"
        filename = f"audit_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    else:  # csv
        media_type = "text/csv"
        filename = f"audit_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Create streaming response
    return StreamingResponse(
        io.StringIO(exported_data),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/events/{event_id}", response_model=AuditEventResponse)
async def get_audit_event(
    event_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific audit event (admin only)."""
    
    require_admin(current_user)
    
    # Find event by ID
    event = None
    for e in audit_logger.events:
        if e.id == event_id:
            event = e
            break
    
    if not event:
        raise HTTPException(status_code=404, detail="Audit event not found")
    
    return AuditEventResponse(
        id=event.id,
        timestamp=event.timestamp,
        event_type=event.event_type.value,
        severity=event.severity.value,
        message=event.message,
        user_id=event.user_id,
        user_email=event.user_email,
        user_role=event.user_role,
        resource_type=event.resource_type,
        resource_id=event.resource_id,
        resource_name=event.resource_name,
        success=event.success,
        error_code=event.error_code,
        error_message=event.error_message,
        details=event.details,
        context=event.context.model_dump() if event.context else None
    )


@router.get("/integrity")
async def verify_audit_integrity(
    current_user: User = Depends(get_current_user)
):
    """Verify audit log integrity (admin only)."""
    
    require_admin(current_user)
    
    integrity_report = await audit_logger.verify_integrity()
    
    return integrity_report


@router.get("/event-types")
async def get_audit_event_types(
    current_user: User = Depends(get_current_user)
):
    """Get available audit event types (admin only)."""
    
    require_admin(current_user)
    
    event_types = [
        {
            "value": event_type.value,
            "name": event_type.name,
            "description": event_type.value.replace(".", " ").replace("_", " ").title()
        }
        for event_type in AuditEventType
    ]
    
    return {"event_types": event_types}


@router.get("/severity-levels")
async def get_audit_severity_levels(
    current_user: User = Depends(get_current_user)
):
    """Get available audit severity levels (admin only)."""
    
    require_admin(current_user)
    
    severity_levels = [
        {
            "value": severity.value,
            "name": severity.name,
            "description": severity.value.title()
        }
        for severity in AuditSeverity
    ]
    
    return {"severity_levels": severity_levels}


@router.get("/dashboard")
async def get_audit_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Get audit dashboard data (admin only)."""
    
    require_admin(current_user)
    
    # Get recent statistics
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)
    
    stats_24h = await audit_logger.get_statistics(start_date=last_24h)
    stats_7d = await audit_logger.get_statistics(start_date=last_7d)
    stats_30d = await audit_logger.get_statistics(start_date=last_30d)
    
    # Get recent high severity events
    high_severity_filter = AuditFilter(
        severity_levels=[AuditSeverity.HIGH, AuditSeverity.CRITICAL],
        start_date=last_24h,
        limit=10
    )
    recent_alerts = await audit_logger.query_events(high_severity_filter)
    
    # Get recent failed events
    failed_events_filter = AuditFilter(
        success_only=False,
        start_date=last_24h,
        limit=10
    )
    recent_failures = await audit_logger.query_events(failed_events_filter)
    
    return {
        "statistics": {
            "last_24h": stats_24h,
            "last_7d": stats_7d,
            "last_30d": stats_30d
        },
        "recent_alerts": [
            {
                "id": event.id,
                "timestamp": event.timestamp,
                "event_type": event.event_type.value,
                "severity": event.severity.value,
                "message": event.message,
                "user_email": event.user_email
            }
            for event in recent_alerts
        ],
        "recent_failures": [
            {
                "id": event.id,
                "timestamp": event.timestamp,
                "event_type": event.event_type.value,
                "message": event.message,
                "error_message": event.error_message,
                "user_email": event.user_email
            }
            for event in recent_failures
        ]
    }


@router.post("/test-event")
async def create_test_audit_event(
    current_user: User = Depends(get_current_user)
):
    """Create a test audit event (admin only, for testing purposes)."""
    
    require_admin(current_user)
    
    from src.core.audit import AuditContext
    
    # Create test context
    test_context = AuditContext(
        ip_address="127.0.0.1",
        user_agent="Test Agent",
        host="localhost"
    )
    
    # Create test event
    event = await audit_logger.log_event(
        event_type=AuditEventType.ADMIN_ACTION,
        message="Test audit event created by administrator",
        severity=AuditSeverity.LOW,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        resource_type="audit",
        resource_id="test",
        details={"test": True, "created_by": current_user.email},
        context=test_context
    )
    
    return {
        "message": "Test audit event created successfully",
        "event_id": event.id
    }