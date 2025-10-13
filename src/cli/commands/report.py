"""
Module: cli.commands.report
Description: Report generation command for CLI
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import httpx
import typer
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

# CLI app
app = typer.Typer(
    help="Generate comprehensive reports from investigations and analyses"
)
console = Console()


class ReportType(str, Enum):
    """Report type options."""

    INVESTIGATION = "investigation"
    ANALYSIS = "analysis"
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    AUDIT = "audit"
    COMPLIANCE = "compliance"


class OutputFormat(str, Enum):
    """Output format options."""

    PDF = "pdf"
    MARKDOWN = "markdown"
    HTML = "html"
    EXCEL = "excel"
    JSON = "json"


class ReportRequest(BaseModel):
    """Report request model."""

    report_type: ReportType
    investigation_ids: list[str] = Field(default_factory=list)
    analysis_ids: list[str] = Field(default_factory=list)
    title: str
    target_audience: str = "general"
    include_visualizations: bool = True
    include_raw_data: bool = False
    time_range: Optional[dict[str, str]] = None
    language: str = "pt-BR"


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
            timeout=120.0,
        )

        if response.status_code >= 400:
            error_detail = response.json().get("detail", "Unknown error")
            raise Exception(f"API Error: {error_detail}")

        return response.json()


def display_report_preview(report_data: dict[str, Any]):
    """Display report preview."""
    console.print(
        Panel(
            f"[bold blue]📋 Report Generated[/bold blue]\n\n"
            f"[bold]ID:[/bold] {report_data.get('report_id', 'N/A')}\n"
            f"[bold]Type:[/bold] {report_data.get('report_type', 'N/A')}\n"
            f"[bold]Title:[/bold] {report_data.get('title', 'N/A')}\n"
            f"[bold]Status:[/bold] {report_data.get('status', 'N/A')}\n"
            f"[bold]Word Count:[/bold] {report_data.get('word_count', 0):,}",
            title="Report Summary",
            border_style="blue",
        )
    )

    # Show first few lines of content
    content = report_data.get("content", "")
    if content:
        lines = content.split("\n")
        preview = "\n".join(lines[:10])
        if len(lines) > 10:
            preview += "\n[dim]... (truncated)[/dim]"

        console.print("\n[bold]Preview:[/bold]")
        syntax = Syntax(preview, "markdown", theme="monokai", line_numbers=False)
        console.print(syntax)


async def download_report(
    report_id: str, format: str, save_path: Path, auth_token: Optional[str] = None
):
    """Download report in specified format."""
    # Get download URL
    download_url = f"/api/v1/reports/{report_id}/download?format={format}"

    # Download file
    api_url = "http://localhost:8000"
    headers = {"User-Agent": "Cidadao.AI-CLI/1.0"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{api_url}{download_url}", headers=headers, timeout=60.0
        )

        if response.status_code >= 400:
            raise Exception(f"Download failed: {response.text}")

        # Save file
        with open(save_path, "wb") as f:
            f.write(response.content)

        return len(response.content)


def get_file_extension(format: str) -> str:
    """Get file extension for format."""
    extensions = {
        "pdf": "pdf",
        "markdown": "md",
        "html": "html",
        "excel": "xlsx",
        "json": "json",
    }
    return extensions.get(format, "txt")


@app.command()
def report(
    report_type: ReportType = typer.Argument(help="Type of report to generate"),
    investigations: Optional[list[str]] = typer.Option(
        None, "--investigation", "-i", help="Investigation IDs to include"
    ),
    analyses: Optional[list[str]] = typer.Option(
        None, "--analysis", "-a", help="Analysis IDs to include"
    ),
    title: str = typer.Option(None, "--title", "-t", help="Report title"),
    audience: str = typer.Option(
        "general",
        "--audience",
        help="Target audience: general, technical, executive, journalist",
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.PDF, "--output", "-f", help="Output format"
    ),
    save_dir: Optional[Path] = typer.Option(
        None, "--save-dir", "-d", help="Directory to save report"
    ),
    filename: Optional[str] = typer.Option(
        None, "--filename", help="Custom filename (without extension)"
    ),
    include_data: bool = typer.Option(
        False, "--include-data", help="Include raw data appendix"
    ),
    no_visuals: bool = typer.Option(
        False, "--no-visuals", help="Exclude visualizations"
    ),
    language: str = typer.Option("pt-BR", "--language", "-l", help="Report language"),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", envvar="CIDADAO_API_KEY", help="API key"
    ),
):
    """
    📋 Generate comprehensive reports from investigations and analyses.

    This command creates professional reports combining investigation results,
    analysis findings, and AI-generated insights in various formats.

    Report Types:
    - investigation: Detailed investigation findings
    - analysis: Pattern and correlation analysis
    - executive: High-level executive summary
    - technical: In-depth technical report
    - audit: Formal audit report
    - compliance: Compliance verification report

    Examples:
        cidadao report investigation -i INV-001 INV-002 --output pdf
        cidadao report executive -i INV-001 -a ANAL-001 --audience executive
        cidadao report audit --investigation INV-001 --save-dir reports/
    """
    # Validate inputs
    if not investigations and not analyses:
        console.print(
            "[red]❌ Error: Must provide at least one investigation or analysis ID[/red]"
        )
        console.print("[dim]Use -i/--investigation or -a/--analysis options[/dim]")
        raise typer.Exit(1)

    # Generate title if not provided
    if not title:
        title = f"{report_type.value.title()} Report - {datetime.now().strftime('%Y-%m-%d')}"

    # Display start message
    console.print(f"\n[bold blue]📋 Generating {report_type.value} Report[/bold blue]")
    console.print(f"Title: [green]{title}[/green]")
    console.print(f"Format: [cyan]{output.value.upper()}[/cyan]")
    console.print(f"Audience: [cyan]{audience}[/cyan]")

    if investigations:
        console.print(f"Investigations: [yellow]{', '.join(investigations)}[/yellow]")
    if analyses:
        console.print(f"Analyses: [yellow]{', '.join(analyses)}[/yellow]")

    console.print()

    # Create report request
    request = ReportRequest(
        report_type=report_type,
        investigation_ids=investigations or [],
        analysis_ids=analyses or [],
        title=title,
        target_audience=audience,
        include_visualizations=not no_visuals,
        include_raw_data=include_data,
        language=language,
    )

    # Convert output format to API format
    api_format_map = {
        OutputFormat.PDF: "pdf",
        OutputFormat.MARKDOWN: "markdown",
        OutputFormat.HTML: "html",
        OutputFormat.EXCEL: "excel",
        OutputFormat.JSON: "json",
    }

    try:
        # Generate report
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing report generation...", total=None)

            # Start report generation
            progress.update(task, description="Creating report...")

            # Prepare request data
            request_data = {
                "report_type": request.report_type.value,
                "title": request.title,
                "target_audience": request.target_audience,
                "output_format": api_format_map[output],
                "investigation_ids": request.investigation_ids,
                "analysis_ids": request.analysis_ids,
                "data_sources": [],  # Will be populated from investigations
                "time_range": request.time_range or {},
                "include_visualizations": request.include_visualizations,
                "include_raw_data": request.include_raw_data,
            }

            result_data = asyncio.run(
                call_api(
                    "/api/v1/reports/generate",
                    method="POST",
                    data=request_data,
                    auth_token=api_key,
                )
            )

            report_id = result_data.get("report_id")
            progress.update(task, description=f"Report ID: {report_id}")

            # Poll for completion
            while True:
                progress.update(task, description="Generating report content...")

                status_data = asyncio.run(
                    call_api(f"/api/v1/reports/{report_id}/status", auth_token=api_key)
                )

                status = status_data.get("status", "unknown")
                progress_pct = status_data.get("progress", 0)
                current_phase = status_data.get("current_phase", "processing")

                progress.update(
                    task,
                    description=f"Status: {current_phase} ({int(progress_pct * 100)}%)",
                )

                if status in ["completed", "failed"]:
                    break

                asyncio.run(asyncio.sleep(2))

        if status == "failed":
            console.print(
                f"[red]❌ Report generation failed: {status_data.get('error_message', 'Unknown error')}[/red]"
            )
            raise typer.Exit(1)

        # Get report data
        report_data = asyncio.run(
            call_api(f"/api/v1/reports/{report_id}", auth_token=api_key)
        )

        # Display preview
        display_report_preview(report_data)

        # Save report if requested
        if save_dir or filename:
            # Determine save path
            if not save_dir:
                save_dir = Path.cwd()
            else:
                save_dir = save_dir.expanduser().resolve()
                save_dir.mkdir(parents=True, exist_ok=True)

            if not filename:
                filename = f"{report_type.value}_report_{report_id}"

            extension = get_file_extension(output.value)
            save_path = save_dir / f"{filename}.{extension}"

            # Download report
            console.print("\n[yellow]Downloading report...[/yellow]")

            file_size = asyncio.run(
                download_report(
                    report_id, api_format_map[output], save_path, auth_token=api_key
                )
            )

            console.print(f"[green]✅ Report saved to: {save_path}[/green]")
            console.print(f"[dim]File size: {file_size:,} bytes[/dim]")
        else:
            # Provide download URL
            console.print(
                f"\n[yellow]ℹ️  To download this report later:[/yellow]\n"
                f"[dim]cidadao report download {report_id} --format {output.value}[/dim]"
            )

        # Summary
        console.print(
            f"\n[bold green]✅ Report generated successfully![/bold green]\n"
            f"Report ID: {report_id}\n"
            f"Word count: {report_data.get('word_count', 0):,}"
        )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def download(
    report_id: str = typer.Argument(help="Report ID to download"),
    format: OutputFormat = typer.Option(
        OutputFormat.PDF, "--format", "-f", help="Download format"
    ),
    save_dir: Optional[Path] = typer.Option(
        None, "--save-dir", "-d", help="Directory to save report"
    ),
    filename: Optional[str] = typer.Option(
        None, "--filename", help="Custom filename (without extension)"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", envvar="CIDADAO_API_KEY", help="API key"
    ),
):
    """
    📥 Download an existing report.

    Download a previously generated report in the specified format.
    """
    # Determine save path
    if not save_dir:
        save_dir = Path.cwd()
    else:
        save_dir = save_dir.expanduser().resolve()
        save_dir.mkdir(parents=True, exist_ok=True)

    if not filename:
        filename = f"report_{report_id}"

    extension = get_file_extension(format.value)
    save_path = save_dir / f"{filename}.{extension}"

    console.print(f"[yellow]📥 Downloading report {report_id}...[/yellow]")

    try:
        # Convert format
        api_format_map = {
            OutputFormat.PDF: "pdf",
            OutputFormat.MARKDOWN: "markdown",
            OutputFormat.HTML: "html",
            OutputFormat.EXCEL: "excel",
            OutputFormat.JSON: "json",
        }

        file_size = asyncio.run(
            download_report(
                report_id, api_format_map[format], save_path, auth_token=api_key
            )
        )

        console.print("[green]✅ Report downloaded successfully![/green]")
        console.print(f"[green]Saved to: {save_path}[/green]")
        console.print(f"[dim]File size: {file_size:,} bytes[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list(
    report_type: Optional[ReportType] = typer.Option(
        None, "--type", "-t", help="Filter by report type"
    ),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of reports to show"),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", envvar="CIDADAO_API_KEY", help="API key"
    ),
):
    """
    📋 List your generated reports.

    Show a list of previously generated reports.
    """
    try:
        # Build query params
        params = {"limit": limit}
        if report_type:
            params["report_type"] = report_type.value

        # Get reports
        reports = asyncio.run(
            call_api("/api/v1/reports/", params=params, auth_token=api_key)
        )

        if not reports:
            console.print("[yellow]No reports found[/yellow]")
            return

        # Display reports table
        table = Table(
            title="Your Reports", show_header=True, header_style="bold magenta"
        )
        table.add_column("Report ID", style="dim")
        table.add_column("Type")
        table.add_column("Title", width=30)
        table.add_column("Status")
        table.add_column("Created", style="dim")
        table.add_column("Words", justify="right")

        for report in reports:
            status = report.get("status", "unknown")
            status_color = (
                "green"
                if status == "completed"
                else "yellow" if status == "running" else "red"
            )

            table.add_row(
                report.get("report_id", "N/A"),
                report.get("report_type", "N/A"),
                report.get("title", "N/A")[:30],
                f"[{status_color}]{status}[/{status_color}]",
                datetime.fromisoformat(report.get("started_at", "")).strftime(
                    "%Y-%m-%d %H:%M"
                ),
                f"{report.get('word_count', 0):,}" if report.get("word_count") else "-",
            )

        console.print(table)

        console.print(f"\n[dim]Showing {len(reports)} most recent reports[/dim]")
        console.print(
            "[dim]Use 'cidadao report download <report_id>' to download a report[/dim]"
        )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
