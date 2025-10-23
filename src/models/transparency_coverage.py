"""
Transparency Coverage Snapshot Model

Stores periodic snapshots of transparency API coverage across Brazilian states.
Used by the Transparency Map feature to display API availability and health status.

Author: Anderson Henrique da Silva
Created: 2025-10-23
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSON

from src.models.base import Base


class TransparencyCoverageSnapshot(Base):
    """
    Snapshot of transparency API coverage for Brazil map visualization.

    Captures the health status of all transparency APIs across Brazilian states
    at a specific point in time. Updated every 6 hours by Celery Beat task.

    Attributes:
        id: Primary key
        snapshot_date: Timestamp when snapshot was taken
        coverage_data: Complete map data (JSON) with states, APIs, and summary
        summary_stats: Quick-access summary statistics (JSON)
        state_code: Two-letter state code (for per-state queries)
        state_status: Overall state status (healthy/degraded/no_api/unknown)
        coverage_percentage: Percentage of working APIs in this state (0-100)
    """

    __tablename__ = "transparency_coverage_snapshots"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Timestamp
    snapshot_date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="When this snapshot was taken",
    )

    # Complete coverage data (JSON)
    coverage_data = Column(
        JSON,
        nullable=False,
        comment="Complete map data with states, APIs, summary, and issues",
    )
    # Structure: {
    #   "last_update": "ISO timestamp",
    #   "states": { "SP": {...}, "MG": {...}, ... },
    #   "summary": { "total_states": 27, ... },
    #   "issues": [...],
    #   "call_to_action": {...}
    # }

    # Summary statistics (JSON) - for quick queries without parsing full data
    summary_stats = Column(
        JSON, nullable=False, comment="Summary statistics for quick access"
    )
    # Structure: {
    #   "total_states": 27,
    #   "states_with_apis": 5,
    #   "states_working": 5,
    #   "overall_coverage_percentage": 38.5,
    #   ...
    # }

    # Per-state data (for state-specific queries)
    # Note: Main snapshot has state_code=None, per-state entries have specific codes
    state_code = Column(
        String(2),
        nullable=True,
        index=True,
        comment="Two-letter state code (SP, MG, RJ, etc.) or None for main snapshot",
    )

    state_status = Column(
        String(20),
        nullable=True,
        comment="Overall state status: healthy, degraded, no_api, unknown",
    )

    coverage_percentage = Column(
        Float,
        nullable=True,
        comment="Percentage of working APIs in this state (0.0 to 100.0)",
    )

    # Indexes for performance
    __table_args__ = (
        # Index for finding latest snapshot quickly
        Index("idx_snapshot_date_desc", snapshot_date.desc()),
        # Index for state-specific queries with coverage filtering
        Index("idx_state_coverage", state_code, coverage_percentage),
        # Index for querying by state and date
        Index("idx_state_date", state_code, snapshot_date.desc()),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        if self.state_code:
            return (
                f"<TransparencyCoverageSnapshot("
                f"id={self.id}, "
                f"state={self.state_code}, "
                f"status={self.state_status}, "
                f"coverage={self.coverage_percentage:.1f}%, "
                f"date={self.snapshot_date.isoformat()}"
                f")>"
            )
        else:
            return (
                f"<TransparencyCoverageSnapshot("
                f"id={self.id}, "
                f"type=MAIN, "
                f"date={self.snapshot_date.isoformat()}"
                f")>"
            )

    def to_dict(self) -> dict:
        """Convert snapshot to dictionary for API responses."""
        return {
            "id": self.id,
            "snapshot_date": self.snapshot_date.isoformat(),
            "state_code": self.state_code,
            "state_status": self.state_status,
            "coverage_percentage": self.coverage_percentage,
            "summary_stats": self.summary_stats,
        }
