"""
Investigation models for database persistence.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, Index, JSON
from sqlalchemy.sql import func
from src.models.base import BaseModel


class Investigation(BaseModel):
    """
    Investigation database model.

    Stores complete investigation data for frontend consumption.
    """

    __tablename__ = "investigations"

    # User identification
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=True, index=True)

    # Investigation details
    query = Column(Text, nullable=False)
    data_source = Column(String(100), nullable=False, index=True)

    # Status tracking
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )
    current_phase = Column(String(100), nullable=True)
    progress = Column(Float, default=0.0)

    # Results summary
    anomalies_found = Column(Integer, default=0)
    total_records_analyzed = Column(Integer, default=0)
    confidence_score = Column(Float, nullable=True)

    # JSON data (stored as TEXT in SQLite, JSONB in PostgreSQL)
    filters = Column(JSON, default={})
    anomaly_types = Column(JSON, default=[])
    results = Column(JSON, default=[])
    investigation_metadata = Column(JSON, default={})

    # Text fields
    summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    # Indexes for performance
    __table_args__ = (
        Index('idx_investigations_user_status', 'user_id', 'status'),
        Index('idx_investigations_created_at', 'created_at'),
    )

    def to_dict(self, include_results: bool = True) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "query": self.query,
            "data_source": self.data_source,
            "status": self.status,
            "current_phase": self.current_phase,
            "progress": self.progress,
            "anomalies_found": self.anomalies_found,
            "total_records_analyzed": self.total_records_analyzed,
            "confidence_score": self.confidence_score,
            "filters": self.filters or {},
            "anomaly_types": self.anomaly_types or [],
            "summary": self.summary,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.investigation_metadata or {},
        }

        if include_results:
            data["results"] = self.results or []
        else:
            data["results_count"] = len(self.results) if self.results else 0

        return data

    def to_status_dict(self) -> Dict[str, Any]:
        """Lightweight status response."""
        return {
            "investigation_id": self.id,
            "status": self.status,
            "progress": self.progress,
            "current_phase": self.current_phase,
            "records_processed": self.total_records_analyzed,
            "anomalies_detected": self.anomalies_found,
            "estimated_completion": None,
        }
