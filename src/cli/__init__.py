"""Command-line interface for Cidadão.AI.

This module provides a comprehensive CLI for interacting with the multi-agent
transparency platform. Built with Typer and Rich for beautiful, professional
command-line experience.

Available Commands:
- investigate: Execute anomaly investigations on government data
- analyze: Perform pattern analysis and correlations
- report: Generate detailed investigation reports
- watch: Monitor data in real-time for anomalies
- status: Check system health and status
- version: Display version information

Features:
- Rich formatting with colors and panels
- Tab completion support
- Comprehensive help system
- Professional error handling
- Verbose output modes

Usage:
    # Direct CLI usage
    cidadao --help
    cidadao investigate --help

    # Programmatic usage
    from src.cli.main import app
    from src.cli.commands import investigate_command

Entry Point:
    Configured in pyproject.toml as: cidadao = "src.cli.main:app"

Status: Professional implementation with comprehensive command structure.
"""

from src.cli.main import app, cli_main

# Export the main CLI app and entry point
__all__ = [
    "app",
    "cli_main",
]
