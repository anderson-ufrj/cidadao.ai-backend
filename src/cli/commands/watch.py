"""
Module: cli.commands.watch
Description: Real-time monitoring command for CLI
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio
import signal
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import httpx
import typer
from pydantic import BaseModel, Field
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# CLI app
app = typer.Typer(help="Monitor government data in real-time for anomalies")
console = Console()

# Global flag for graceful shutdown
shutdown_requested = False


class MonitoringMode(str, Enum):
    """Monitoring mode options."""

    CONTRACTS = "contracts"
    ORGANIZATIONS = "organizations"
    SUPPLIERS = "suppliers"
    ANOMALIES = "anomalies"
    ALL = "all"


class AlertLevel(str, Enum):
    """Alert level options."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MonitoringConfig(BaseModel):
    """Monitoring configuration."""

    mode: MonitoringMode
    organizations: list[str] = Field(default_factory=list)
    suppliers: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    min_value: Optional[float] = None
    anomaly_threshold: float = 0.7
    alert_level: AlertLevel = AlertLevel.MEDIUM
    check_interval: int = 60  # seconds


class MonitoringStats(BaseModel):
    """Monitoring statistics."""

    start_time: datetime
    checks_performed: int = 0
    anomalies_detected: int = 0
    alerts_triggered: int = 0
    last_check: Optional[datetime] = None
    active_alerts: list[dict[str, Any]] = Field(default_factory=list)


async def call_api(
    endpoint: str,
    method: str = "GET",
    data: Optional[dict[str, Any]] = None,
    params: Optional[dict[str, Any]] = None,
    auth_token: Optional[str] = None,
) -> dict[str, Any]:
    """Make API call to backend."""
    api_url = "http://localhost:8000"

    headers = {"Content-Type": "application/json", "User-Agent": "Cidadao.AI-CLI/1.0"}

    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=method,
            url=f"{api_url}{endpoint}",
            headers=headers,
            json=data,
            params=params,
            timeout=30.0,
        )

        if response.status_code >= 400:
            error_detail = response.json().get("detail", "Unknown error")
            raise Exception(f"API Error: {error_detail}")

        return response.json()


def create_dashboard_layout() -> Layout:
    """Create dashboard layout."""
    layout = Layout()

    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=4),
    )

    layout["main"].split_row(
        Layout(name="stats", ratio=1), Layout(name="alerts", ratio=2)
    )

    return layout


def render_header(config: MonitoringConfig) -> Panel:
    """Render header panel."""
    header_text = Text()
    header_text.append("👀 Cidadão.AI Watch Mode", style="bold blue")
    header_text.append("\n")
    header_text.append(f"Mode: {config.mode.value} | ", style="dim")
    header_text.append(f"Threshold: {config.anomaly_threshold} | ", style="dim")
    header_text.append(f"Interval: {config.check_interval}s", style="dim")

    return Panel(header_text, border_style="blue")


def render_stats(stats: MonitoringStats) -> Panel:
    """Render statistics panel."""
    elapsed = datetime.now() - stats.start_time
    hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    stats_table = Table(show_header=False, box=None)
    stats_table.add_column("Label", style="dim")
    stats_table.add_column("Value", justify="right")

    stats_table.add_row("Running for", f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    stats_table.add_row("Checks", str(stats.checks_performed))
    stats_table.add_row("Anomalies", str(stats.anomalies_detected))
    stats_table.add_row("Alerts", str(stats.alerts_triggered))

    if stats.last_check:
        time_since = (datetime.now() - stats.last_check).total_seconds()
        stats_table.add_row("Last check", f"{int(time_since)}s ago")

    return Panel(stats_table, title="📊 Statistics", border_style="green")


def render_alerts(stats: MonitoringStats) -> Panel:
    """Render alerts panel."""
    if not stats.active_alerts:
        content = Text("No active alerts", style="dim italic")
    else:
        alerts_table = Table(show_header=True, header_style="bold")
        alerts_table.add_column("Time", width=8)
        alerts_table.add_column("Level", width=8)
        alerts_table.add_column("Type", width=15)
        alerts_table.add_column("Description", width=40)

        # Show last 10 alerts
        for alert in stats.active_alerts[-10:]:
            level = alert.get("level", "unknown")
            level_color = {
                "low": "green",
                "medium": "yellow",
                "high": "red",
                "critical": "bold red",
            }.get(level, "white")

            time_str = datetime.fromisoformat(alert["timestamp"]).strftime("%H:%M:%S")

            alerts_table.add_row(
                time_str,
                f"[{level_color}]{level.upper()}[/{level_color}]",
                alert.get("type", "Unknown"),
                alert.get("description", "N/A")[:40],
            )

        content = alerts_table

    return Panel(content, title="🚨 Active Alerts", border_style="yellow")


def render_footer() -> Panel:
    """Render footer panel."""
    footer_text = Text()
    footer_text.append("Press ", style="dim")
    footer_text.append("Ctrl+C", style="bold yellow")
    footer_text.append(" to stop monitoring", style="dim")

    return Panel(footer_text, border_style="dim")


async def check_for_anomalies(
    config: MonitoringConfig, stats: MonitoringStats, auth_token: Optional[str] = None
) -> list[dict[str, Any]]:
    """Check for anomalies based on monitoring mode."""
    new_alerts = []

    try:
        # Build query based on mode
        query_params = {"threshold": config.anomaly_threshold, "limit": 50}

        if config.organizations:
            query_params["organizations"] = ",".join(config.organizations)
        if config.suppliers:
            query_params["suppliers"] = ",".join(config.suppliers)
        if config.categories:
            query_params["categories"] = ",".join(config.categories)
        if config.min_value:
            query_params["min_value"] = config.min_value

        # Get latest data based on mode
        if config.mode == MonitoringMode.CONTRACTS:
            # Check recent contracts
            contracts = await call_api(
                "/api/v1/data/contracts/recent",
                params=query_params,
                auth_token=auth_token,
            )

            # Simple anomaly detection on contract values
            for contract in contracts:
                value = contract.get("value", 0)
                if config.min_value and value >= config.min_value:
                    new_alerts.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "level": (
                                "high" if value > config.min_value * 2 else "medium"
                            ),
                            "type": "high_value",
                            "description": f"Contract {contract['id']} with value R$ {value:,.2f}",
                            "data": contract,
                        }
                    )

        elif config.mode == MonitoringMode.ANOMALIES:
            # Direct anomaly monitoring
            anomalies = await call_api(
                "/api/v1/investigations/anomalies/recent",
                params=query_params,
                auth_token=auth_token,
            )

            for anomaly in anomalies:
                severity = anomaly.get("severity", 0)
                if severity >= config.anomaly_threshold:
                    level = (
                        "critical"
                        if severity >= 0.9
                        else (
                            "high"
                            if severity >= 0.8
                            else "medium" if severity >= 0.7 else "low"
                        )
                    )

                    new_alerts.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "level": level,
                            "type": anomaly.get("type", "unknown"),
                            "description": anomaly.get(
                                "description", "Anomaly detected"
                            ),
                            "data": anomaly,
                        }
                    )

        # Update stats
        stats.checks_performed += 1
        stats.last_check = datetime.now()

        if new_alerts:
            stats.anomalies_detected += len(new_alerts)
            stats.alerts_triggered += len(
                [a for a in new_alerts if a["level"] in ["high", "critical"]]
            )
            stats.active_alerts.extend(new_alerts)

            # Keep only last 100 alerts
            if len(stats.active_alerts) > 100:
                stats.active_alerts = stats.active_alerts[-100:]

        return new_alerts

    except Exception as e:
        # Add error as alert
        error_alert = {
            "timestamp": datetime.now().isoformat(),
            "level": "medium",
            "type": "error",
            "description": f"Check failed: {str(e)}",
            "data": {},
        }
        stats.active_alerts.append(error_alert)
        return [error_alert]


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    global shutdown_requested

    def signal_handler(sig, frame):
        global shutdown_requested
        shutdown_requested = True
        console.print(
            "\n[yellow]Shutdown requested... finishing current check[/yellow]"
        )

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


@app.command()
def watch(
    mode: MonitoringMode = typer.Argument(help="What to monitor"),
    organizations: Optional[list[str]] = typer.Option(
        None, "--org", "-o", help="Organization codes to monitor"
    ),
    suppliers: Optional[list[str]] = typer.Option(
        None, "--supplier", "-s", help="Supplier names to monitor"
    ),
    categories: Optional[list[str]] = typer.Option(
        None, "--category", "-c", help="Contract categories to monitor"
    ),
    min_value: Optional[float] = typer.Option(
        None, "--min-value", help="Minimum value threshold for alerts"
    ),
    threshold: float = typer.Option(
        0.7, "--threshold", "-t", min=0.0, max=1.0, help="Anomaly detection threshold"
    ),
    alert_level: AlertLevel = typer.Option(
        AlertLevel.MEDIUM, "--alert-level", "-a", help="Minimum alert level to display"
    ),
    interval: int = typer.Option(
        60, "--interval", "-i", min=10, help="Check interval in seconds"
    ),
    export_alerts: Optional[Path] = typer.Option(
        None, "--export", "-e", help="Export alerts to file"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", envvar="CIDADAO_API_KEY", help="API key"
    ),
):
    """
    👀 Monitor government data in real-time for anomalies.

    This command runs continuous monitoring of government contracts and
    spending, alerting you when anomalies or suspicious patterns are detected.

    Monitoring Modes:
    - contracts: Monitor new contracts as they appear
    - organizations: Focus on specific organizations
    - suppliers: Track specific supplier activities
    - anomalies: Direct anomaly detection monitoring
    - all: Comprehensive monitoring of everything

    Examples:
        cidadao watch contracts --min-value 1000000
        cidadao watch anomalies --threshold 0.8 --interval 30
        cidadao watch organizations --org MIN_SAUDE MIN_EDUCACAO
    """
    global shutdown_requested

    # Setup signal handlers
    setup_signal_handlers()

    # Display start message
    console.print(f"\n[bold blue]👀 Starting {mode.value} monitoring[/bold blue]")
    console.print(f"Alert threshold: [yellow]{threshold}[/yellow]")
    console.print(f"Check interval: [yellow]{interval}s[/yellow]")

    if organizations:
        console.print(f"Organizations: [cyan]{', '.join(organizations)}[/cyan]")
    if suppliers:
        console.print(f"Suppliers: [cyan]{', '.join(suppliers)}[/cyan]")

    console.print("\n[dim]Press Ctrl+C to stop monitoring[/dim]\n")

    # Create monitoring config
    config = MonitoringConfig(
        mode=mode,
        organizations=organizations or [],
        suppliers=suppliers or [],
        categories=categories or [],
        min_value=min_value,
        anomaly_threshold=threshold,
        alert_level=alert_level,
        check_interval=interval,
    )

    # Initialize stats
    stats = MonitoringStats(start_time=datetime.now())

    # Create layout
    layout = create_dashboard_layout()

    # Export file handle
    export_file = None
    if export_alerts:
        export_path = export_alerts.expanduser().resolve()
        export_file = open(export_path, "a", encoding="utf-8")
        export_file.write(
            f"# Cidadão.AI Watch Mode - Started at {stats.start_time.isoformat()}\n"
        )
        export_file.write(f"# Mode: {mode.value}, Threshold: {threshold}\n\n")

    try:
        # Start monitoring loop
        with Live(layout, refresh_per_second=1, console=console) as live:
            while not shutdown_requested:
                # Update layout
                layout["header"].update(render_header(config))
                layout["stats"].update(render_stats(stats))
                layout["alerts"].update(render_alerts(stats))
                layout["footer"].update(render_footer())

                # Check for anomalies
                new_alerts = asyncio.run(
                    check_for_anomalies(config, stats, auth_token=api_key)
                )

                # Export alerts if configured
                if export_file and new_alerts:
                    for alert in new_alerts:
                        export_file.write(
                            f"{alert['timestamp']} | {alert['level'].upper()} | "
                            f"{alert['type']} | {alert['description']}\n"
                        )
                    export_file.flush()

                # Show notification for high alerts
                for alert in new_alerts:
                    if alert["level"] in ["high", "critical"]:
                        console.bell()  # System bell for attention

                # Wait for next check
                for _ in range(config.check_interval):
                    if shutdown_requested:
                        break
                    asyncio.run(asyncio_sleep(1))

                    # Update elapsed time
                    layout["stats"].update(render_stats(stats))

        # Shutdown message
        console.print("\n[green]✅ Monitoring stopped gracefully[/green]")

        # Final summary
        console.print(
            Panel(
                f"[bold]Monitoring Summary[/bold]\n\n"
                f"Duration: {datetime.now() - stats.start_time}\n"
                f"Total checks: {stats.checks_performed}\n"
                f"Anomalies detected: {stats.anomalies_detected}\n"
                f"Alerts triggered: {stats.alerts_triggered}",
                title="📊 Final Statistics",
                border_style="blue",
            )
        )

        if export_file:
            export_file.write(f"\n# Monitoring ended at {datetime.now().isoformat()}\n")
            export_file.write(f"# Total anomalies: {stats.anomalies_detected}\n")
            console.print(f"\n[green]Alerts exported to: {export_alerts}[/green]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)
    finally:
        if export_file:
            export_file.close()


@app.command()
def test_connection(
    api_key: Optional[str] = typer.Option(
        None, "--api-key", envvar="CIDADAO_API_KEY", help="API key"
    ),
):
    """
    🔌 Test connection to the API.

    Verify that the CLI can connect to the backend API.
    """
    console.print("[yellow]Testing API connection...[/yellow]")

    try:
        # Test health endpoint
        result = asyncio.run(call_api("/health", auth_token=api_key))

        console.print("[green]✅ API connection successful![/green]")
        console.print(f"Status: {result.get('status', 'unknown')}")

        # Test authenticated endpoint if API key provided
        if api_key:
            console.print("\n[yellow]Testing authenticated access...[/yellow]")
            user_info = asyncio.run(call_api("/api/v1/auth/me", auth_token=api_key))
            console.print("[green]✅ Authentication successful![/green]")
            console.print(f"User: {user_info.get('email', 'unknown')}")

    except Exception as e:
        console.print(f"[red]❌ Connection failed: {e}[/red]")
        console.print(
            "\n[dim]Make sure the API is running at http://localhost:8000[/dim]"
        )
        raise typer.Exit(1)


# Fix for asyncio.sleep in synchronous context
async def asyncio_sleep(seconds: float):
    """Async sleep helper."""
    await asyncio.sleep(seconds)


if __name__ == "__main__":
    app()
