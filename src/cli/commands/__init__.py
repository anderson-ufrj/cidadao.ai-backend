"""CLI commands for Cidad�o.AI.

This module provides command-line interface commands for:
- Investigation operations
- Data analysis
- Report generation
- System monitoring

Status: Stub implementation - Full CLI planned for production phase.
"""

from .analyze import analyze
from .investigate import investigate
from .report import report
from .watch import watch

__all__ = ["investigate", "analyze", "report", "watch"]
