"""
Module: core.audit
Description: Comprehensive audit logging system for security and compliance
Author: Anderson H. Silva
Date: 2025-01-15
License: Proprietary - All rights reserved
"""

import json
import hashlib
import asyncio
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from uuid import uuid4

from pydantic import BaseModel, Field
import structlog

from src.core import get_logger, settings


class AuditEventType(str, Enum):
    """Types of audit events."""
    
    # Authentication events
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    TOKEN_REFRESH = "auth.token.refresh"
    PASSWORD_CHANGE = "auth.password.change"
    ACCOUNT_LOCKED = "auth.account.locked"
    
    # OAuth events
    OAUTH_LOGIN_SUCCESS = "oauth.login.success"
    OAUTH_LOGIN_FAILURE = "oauth.login.failure"
    OAUTH_USER_CREATED = "oauth.user.created"
    OAUTH_USER_APPROVED = "oauth.user.approved"
    OAUTH_USER_REJECTED = "oauth.user.rejected"
    
    # User management
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_ACTIVATED = "user.activated"
    USER_DEACTIVATED = "user.deactivated"
    ROLE_CHANGED = "user.role.changed"
    
    # Data access
    DATA_QUERY = "data.query"
    DATA_EXPORT = "data.export"
    DATA_IMPORT = "data.import"
    TRANSPARENCY_API_CALL = "transparency.api.call"
    
    # Investigation events
    INVESTIGATION_CREATED = "investigation.created"
    INVESTIGATION_UPDATED = "investigation.updated"
    INVESTIGATION_DELETED = "investigation.deleted"
    INVESTIGATION_SHARED = "investigation.shared"
    REPORT_GENERATED = "report.generated"
    REPORT_DOWNLOADED = "report.downloaded"
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    CONFIG_CHANGED = "system.config.changed"
    BACKUP_CREATED = "system.backup.created"
    BACKUP_RESTORED = "system.backup.restored"
    
    # Security events
    UNAUTHORIZED_ACCESS = "security.unauthorized.access"
    SUSPICIOUS_ACTIVITY = "security.suspicious.activity"
    RATE_LIMIT_EXCEEDED = "security.rate_limit.exceeded"
    INVALID_TOKEN = "security.invalid.token"
    BRUTE_FORCE_DETECTED = "security.brute_force.detected"
    
    # API events
    API_CALL = "api.call"
    API_ERROR = "api.error"
    API_RATE_LIMITED = "api.rate_limited"
    
    # Admin events
    ADMIN_ACTION = "admin.action"
    PERMISSION_GRANTED = "admin.permission.granted"
    PERMISSION_REVOKED = "admin.permission.revoked"


class AuditSeverity(str, Enum):
    """Audit event severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditContext:
    """Audit event context information."""
    
    # Request context
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    # Network context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    host: Optional[str] = None
    referer: Optional[str] = None
    
    # Geographic context
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    
    # Device context
    device_type: Optional[str] = None
    os: Optional[str] = None
    browser: Optional[str] = None


class AuditEvent(BaseModel):
    """Structured audit event."""
    
    # Core identification
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: AuditEventType
    severity: AuditSeverity = AuditSeverity.MEDIUM
    
    # Event details
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    
    # Actor information
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    impersonated_by: Optional[str] = None
    
    # Resource information
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    
    # Result information
    success: bool = True
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    # Context
    context: Optional[AuditContext] = None
    
    # Data integrity
    checksum: Optional[str] = None
    
    def calculate_checksum(self) -> str:
        """Calculate checksum for data integrity."""
        # Create a deterministic string representation
        data_dict = self.model_dump(exclude={"checksum"})
        data_str = json.dumps(data_dict, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def validate_integrity(self) -> bool:
        """Validate event integrity using checksum."""
        if not self.checksum:
            return False
        return self.calculate_checksum() == self.checksum


class AuditFilter(BaseModel):
    """Audit log filtering options."""
    
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
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


class AuditStatistics(BaseModel):
    """Audit statistics."""
    
    total_events: int
    events_by_type: Dict[str, int]
    events_by_severity: Dict[str, int]
    events_by_user: Dict[str, int]
    events_by_hour: Dict[str, int]
    success_rate: float
    most_active_users: List[Dict[str, Any]]
    most_common_errors: List[Dict[str, Any]]


class AuditLogger:
    """Comprehensive audit logging system."""
    
    def __init__(self):
        """Initialize audit logger."""
        self.logger = get_logger(__name__)
        self.audit_logger = structlog.get_logger("audit")
        self.audit_path = settings.audit_log_path
        self.events: List[AuditEvent] = []  # In-memory storage for demo
        
        # Ensure audit directory exists
        self.audit_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize audit file
        self.audit_file = self.audit_path / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    async def log_event(
        self,
        event_type: AuditEventType,
        message: str,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        success: bool = True,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[AuditContext] = None,
        **kwargs
    ) -> AuditEvent:
        """Log an audit event."""
        
        # Create audit event
        event = AuditEvent(
            event_type=event_type,
            message=message,
            severity=severity,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            success=success,
            error_code=error_code,
            error_message=error_message,
            details=details or {},
            context=context,
            **kwargs
        )
        
        # Calculate and set checksum for integrity
        event.checksum = event.calculate_checksum()
        
        # Store event (in production, use database)
        self.events.append(event)
        
        # Write to file for persistence
        await self._write_to_file(event)
        
        # Log to structured logger
        self.audit_logger.info(
            "audit_event",
            event_id=event.id,
            event_type=event.event_type.value,
            severity=event.severity.value,
            user_id=user_id,
            user_email=user_email,
            message=message,
            success=success,
            **event.details
        )
        
        # Check for security alerts
        await self._check_security_alerts(event)
        
        return event
    
    async def _write_to_file(self, event: AuditEvent):
        """Write audit event to file."""
        try:
            with open(self.audit_file, "a", encoding="utf-8") as f:
                event_json = event.model_dump_json()
                f.write(f"{event_json}\n")
        except Exception as e:
            self.logger.error(
                "audit_file_write_error",
                error=str(e),
                event_id=event.id
            )
    
    async def _check_security_alerts(self, event: AuditEvent):
        """Check for security alerts based on audit events."""
        
        # Check for brute force attacks
        if event.event_type == AuditEventType.LOGIN_FAILURE:
            await self._check_brute_force(event)
        
        # Check for suspicious activity patterns
        if event.severity == AuditSeverity.HIGH:
            await self._alert_high_severity_event(event)
        
        # Check for unauthorized access attempts
        if event.event_type == AuditEventType.UNAUTHORIZED_ACCESS:
            await self._alert_unauthorized_access(event)
    
    async def _check_brute_force(self, event: AuditEvent):
        """Check for brute force login attempts."""
        if not event.context or not event.context.ip_address:
            return
        
        # Count recent login failures from same IP
        recent_failures = [
            e for e in self.events[-100:]  # Last 100 events
            if e.event_type == AuditEventType.LOGIN_FAILURE
            and e.context
            and e.context.ip_address == event.context.ip_address
            and (datetime.now(timezone.utc) - e.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        if len(recent_failures) >= 5:  # 5 failures in 1 hour
            await self.log_event(
                event_type=AuditEventType.BRUTE_FORCE_DETECTED,
                message=f"Brute force attack detected from IP {event.context.ip_address}",
                severity=AuditSeverity.CRITICAL,
                details={
                    "ip_address": event.context.ip_address,
                    "failure_count": len(recent_failures),
                    "time_window_hours": 1
                },
                context=event.context
            )
    
    async def _alert_high_severity_event(self, event: AuditEvent):
        """Alert on high severity events."""
        self.logger.warning(
            "high_severity_audit_event",
            event_id=event.id,
            event_type=event.event_type.value,
            message=event.message,
            user_id=event.user_id
        )
    
    async def _alert_unauthorized_access(self, event: AuditEvent):
        """Alert on unauthorized access attempts."""
        self.logger.warning(
            "unauthorized_access_attempt",
            event_id=event.id,
            ip_address=event.context.ip_address if event.context else None,
            user_agent=event.context.user_agent if event.context else None,
            details=event.details
        )
    
    async def query_events(self, filter_options: AuditFilter) -> List[AuditEvent]:
        """Query audit events with filtering."""
        
        filtered_events = self.events.copy()
        
        # Apply filters
        if filter_options.start_date:
            filtered_events = [
                e for e in filtered_events
                if e.timestamp >= filter_options.start_date
            ]
        
        if filter_options.end_date:
            filtered_events = [
                e for e in filtered_events
                if e.timestamp <= filter_options.end_date
            ]
        
        if filter_options.event_types:
            filtered_events = [
                e for e in filtered_events
                if e.event_type in filter_options.event_types
            ]
        
        if filter_options.severity_levels:
            filtered_events = [
                e for e in filtered_events
                if e.severity in filter_options.severity_levels
            ]
        
        if filter_options.user_id:
            filtered_events = [
                e for e in filtered_events
                if e.user_id == filter_options.user_id
            ]
        
        if filter_options.user_email:
            filtered_events = [
                e for e in filtered_events
                if e.user_email == filter_options.user_email
            ]
        
        if filter_options.resource_type:
            filtered_events = [
                e for e in filtered_events
                if e.resource_type == filter_options.resource_type
            ]
        
        if filter_options.resource_id:
            filtered_events = [
                e for e in filtered_events
                if e.resource_id == filter_options.resource_id
            ]
        
        if filter_options.success_only is not None:
            filtered_events = [
                e for e in filtered_events
                if e.success == filter_options.success_only
            ]
        
        if filter_options.ip_address:
            filtered_events = [
                e for e in filtered_events
                if e.context and e.context.ip_address == filter_options.ip_address
            ]
        
        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        start = filter_options.offset
        end = start + filter_options.limit
        
        return filtered_events[start:end]
    
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> AuditStatistics:
        """Get audit statistics."""
        
        events = self.events
        
        if start_date:
            events = [e for e in events if e.timestamp >= start_date]
        
        if end_date:
            events = [e for e in events if e.timestamp <= end_date]
        
        total_events = len(events)
        
        # Events by type
        events_by_type = {}
        for event in events:
            event_type = event.event_type.value
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
        
        # Events by severity
        events_by_severity = {}
        for event in events:
            severity = event.severity.value
            events_by_severity[severity] = events_by_severity.get(severity, 0) + 1
        
        # Events by user
        events_by_user = {}
        for event in events:
            if event.user_email:
                events_by_user[event.user_email] = events_by_user.get(event.user_email, 0) + 1
        
        # Events by hour
        events_by_hour = {}
        for event in events:
            hour = event.timestamp.strftime("%Y-%m-%d %H:00")
            events_by_hour[hour] = events_by_hour.get(hour, 0) + 1
        
        # Success rate
        successful_events = sum(1 for e in events if e.success)
        success_rate = (successful_events / total_events * 100) if total_events > 0 else 0
        
        # Most active users
        most_active_users = [
            {"user": user, "count": count}
            for user, count in sorted(events_by_user.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Most common errors
        error_counts = {}
        for event in events:
            if not event.success and event.error_code:
                error_counts[event.error_code] = error_counts.get(event.error_code, 0) + 1
        
        most_common_errors = [
            {"error_code": error, "count": count}
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        return AuditStatistics(
            total_events=total_events,
            events_by_type=events_by_type,
            events_by_severity=events_by_severity,
            events_by_user=events_by_user,
            events_by_hour=events_by_hour,
            success_rate=success_rate,
            most_active_users=most_active_users,
            most_common_errors=most_common_errors
        )
    
    async def export_events(
        self,
        filter_options: AuditFilter,
        format: str = "json"
    ) -> str:
        """Export audit events in specified format."""
        
        events = await self.query_events(filter_options)
        
        if format.lower() == "json":
            return json.dumps([event.model_dump() for event in events], indent=2, default=str)
        
        elif format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "id", "timestamp", "event_type", "severity", "message",
                "user_id", "user_email", "success", "error_code",
                "resource_type", "resource_id", "ip_address"
            ])
            
            # Write events
            for event in events:
                writer.writerow([
                    event.id,
                    event.timestamp.isoformat(),
                    event.event_type.value,
                    event.severity.value,
                    event.message,
                    event.user_id or "",
                    event.user_email or "",
                    event.success,
                    event.error_code or "",
                    event.resource_type or "",
                    event.resource_id or "",
                    event.context.ip_address if event.context else ""
                ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def verify_integrity(self) -> Dict[str, Any]:
        """Verify integrity of all audit events."""
        
        total_events = len(self.events)
        valid_events = 0
        invalid_events = []
        
        for event in self.events:
            if event.validate_integrity():
                valid_events += 1
            else:
                invalid_events.append({
                    "id": event.id,
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type.value
                })
        
        integrity_percentage = (valid_events / total_events * 100) if total_events > 0 else 100
        
        return {
            "total_events": total_events,
            "valid_events": valid_events,
            "invalid_events": len(invalid_events),
            "integrity_percentage": integrity_percentage,
            "invalid_event_details": invalid_events
        }


# Global audit logger instance
audit_logger = AuditLogger()


# Convenience functions for common audit events
async def audit_login_success(user_id: str, user_email: str, context: Optional[AuditContext] = None):
    """Audit successful login."""
    await audit_logger.log_event(
        event_type=AuditEventType.LOGIN_SUCCESS,
        message=f"User {user_email} logged in successfully",
        user_id=user_id,
        user_email=user_email,
        context=context
    )


async def audit_login_failure(email: str, reason: str, context: Optional[AuditContext] = None):
    """Audit failed login attempt."""
    await audit_logger.log_event(
        event_type=AuditEventType.LOGIN_FAILURE,
        message=f"Failed login attempt for {email}: {reason}",
        severity=AuditSeverity.MEDIUM,
        user_email=email,
        success=False,
        error_message=reason,
        context=context
    )


async def audit_data_access(
    user_id: str,
    user_email: str,
    resource_type: str,
    resource_id: str,
    action: str,
    context: Optional[AuditContext] = None
):
    """Audit data access."""
    await audit_logger.log_event(
        event_type=AuditEventType.DATA_QUERY,
        message=f"User {user_email} accessed {resource_type} {resource_id} ({action})",
        user_id=user_id,
        user_email=user_email,
        resource_type=resource_type,
        resource_id=resource_id,
        details={"action": action},
        context=context
    )


async def audit_unauthorized_access(
    resource: str,
    reason: str,
    context: Optional[AuditContext] = None
):
    """Audit unauthorized access attempt."""
    await audit_logger.log_event(
        event_type=AuditEventType.UNAUTHORIZED_ACCESS,
        message=f"Unauthorized access attempt to {resource}: {reason}",
        severity=AuditSeverity.HIGH,
        success=False,
        error_message=reason,
        resource_name=resource,
        context=context
    )