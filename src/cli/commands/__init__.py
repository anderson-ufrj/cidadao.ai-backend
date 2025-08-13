"""CLI commands for Cidadão.AI.

This module provides command-line interface commands for:
- Investigation operations
- Data analysis
- Report generation
- System monitoring

Status: Stub implementation - Full CLI planned for production phase.
"""

from .investigate import investigate_command
from .analyze import analyze_command
from .report import report_command
from .watch import watch_command

__all__ = [
    "investigate_command",
    "analyze_command", 
    "report_command",
    "watch_command"
]