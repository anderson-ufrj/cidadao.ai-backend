"""
Module: cli.commands.investigate
Description: Investigation command for CLI
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
app = typer.Typer(help="Execute investigations on government data")
console = Console()


class OutputFormat(str, Enum):
    """Output format options."""

    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    TABLE = "table"


class InvestigationRequest(BaseModel):
    """Investigation request model."""

    query: str = Field(description="Natural language query")
    organization_code: Optional[str] = Field(None, description="Organization code")
    year: Optional[int] = Field(None, description="Year filter")
    threshold: float = Field(0.7, description="Anomaly detection threshold")
    max_results: int = Field(100, description="Maximum results")
    include_contracts: bool = Field(True, description="Include contract analysis")


class InvestigationResult(BaseModel):
    """Investigation result model."""

    id: str
    status: str
    created_at: datetime
    summary: Optional[str] = None
    anomalies_count: int = 0
    total_analyzed: int = 0
    risk_score: float = 0.0
    anomalies: list[dict[str, Any]] = []
    contracts: list[dict[str, Any]] = []


async def call_api(
    endpoint: str,
    method: str = "GET",
    data: Optional[dict[str, Any]] = None,
    params: Optional[dict[str, Any]] = None,
    auth_token: Optional[str] = None,
) -> dict[str, Any]:
    """Make API call to backend."""
    # Get API URL from environment or use default
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
            timeout=60.0,
        )

        if response.status_code >= 400:
            error_detail = response.json().get("detail", "Unknown error")
            raise Exception(f"API Error: {error_detail}")

        return response.json()


def format_anomaly(anomaly: dict[str, Any]) -> str:
    """Format anomaly for display."""
    severity_color = (
        "red"
        if anomaly.get("severity", 0) >= 0.8
        else "yellow" if anomaly.get("severity", 0) >= 0.5 else "green"
    )

    return (
        f"[{severity_color}]● Severidade: {anomaly.get('severity', 0):.2f}[/{severity_color}]\n"
        f"  Tipo: {anomaly.get('type', 'Unknown')}\n"
        f"  Descrição: {anomaly.get('description', 'N/A')}\n"
        f"  Explicação: {anomaly.get('explanation', 'N/A')}"
    )


def display_results_table(result: InvestigationResult):
    """Display results in table format."""
    # Summary panel
    summary_text = f"""
[bold]Investigation ID:[/bold] {result.id}
[bold]Status:[/bold] {result.status}
[bold]Created:[/bold] {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}
[bold]Risk Score:[/bold] [{get_risk_color(result.risk_score)}]{result.risk_score:.2f}[/]
[bold]Anomalies Found:[/bold] {result.anomalies_count} / {result.total_analyzed}
"""

    console.print(
        Panel(
            summary_text.strip(), title="📊 Investigation Summary", border_style="blue"
        )
    )

    # Anomalies table
    if result.anomalies:
        console.print("\n[bold]🚨 Anomalies Detected:[/bold]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Type", style="dim", width=20)
        table.add_column("Severity", justify="center")
        table.add_column("Description", width=50)
        table.add_column("Contract", style="dim")

        for anomaly in result.anomalies[:10]:  # Show first 10
            severity = anomaly.get("severity", 0)
            severity_color = get_risk_color(severity)

            table.add_row(
                anomaly.get("type", "Unknown"),
                f"[{severity_color}]{severity:.2f}[/{severity_color}]",
                anomaly.get("description", "N/A")[:50],
                anomaly.get("contract_id", "N/A"),
            )

        console.print(table)

        if len(result.anomalies) > 10:
            console.print(
                f"\n[dim]... and {len(result.anomalies) - 10} more anomalies[/dim]"
            )


def display_results_markdown(result: InvestigationResult):
    """Display results in markdown format."""
    markdown = f"""# Investigation Report

**ID**: {result.id}
**Status**: {result.status}
**Created**: {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}
**Risk Score**: {result.risk_score:.2f}
**Anomalies**: {result.anomalies_count} found out of {result.total_analyzed} analyzed

## Summary

{result.summary or 'Investigation completed successfully.'}

## Anomalies Detected

"""

    for i, anomaly in enumerate(result.anomalies, 1):
        markdown += f"""### Anomaly {i}
- **Type**: {anomaly.get('type', 'Unknown')}
- **Severity**: {anomaly.get('severity', 0):.2f}
- **Description**: {anomaly.get('description', 'N/A')}
- **Explanation**: {anomaly.get('explanation', 'N/A')}
- **Contract ID**: {anomaly.get('contract_id', 'N/A')}

"""

    syntax = Syntax(markdown, "markdown", theme="monokai", line_numbers=False)
    console.print(syntax)


def display_results_json(result: InvestigationResult):
    """Display results in JSON format."""
    import json

    json_str = json.dumps(result.dict(), indent=2, default=str, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
    console.print(syntax)


def get_risk_color(risk_score: float) -> str:
    """Get color based on risk score."""
    if risk_score >= 0.8:
        return "red"
    elif risk_score >= 0.5:
        return "yellow"
    else:
        return "green"


@app.command()
def investigate(
    query: str = typer.Argument(
        help="Natural language description of what to investigate"
    ),
    org: Optional[str] = typer.Option(
        None, "--org", "-o", help="Organization code to focus investigation"
    ),
    year: Optional[int] = typer.Option(
        None, "--year", "-y", help="Year to investigate"
    ),
    threshold: float = typer.Option(
        0.7, "--threshold", "-t", min=0.0, max=1.0, help="Anomaly detection threshold"
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.TABLE, "--output", "-f", help="Output format"
    ),
    max_results: int = typer.Option(
        100, "--max-results", "-m", help="Maximum number of results"
    ),
    no_contracts: bool = typer.Option(
        False, "--no-contracts", help="Exclude contract analysis"
    ),
    save: Optional[Path] = typer.Option(
        None, "--save", "-s", help="Save results to file"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", envvar="CIDADAO_API_KEY", help="API key for authentication"
    ),
):
    """
    🔍 Execute an investigation on government spending data.

    This command starts a comprehensive investigation using multiple AI agents
    to analyze government contracts and spending patterns for anomalies.

    Examples:
        cidadao investigate "contratos suspeitos em 2024"
        cidadao investigate "gastos com educação" --org MIN_EDUCACAO --year 2024
        cidadao investigate "anomalias em licitações" --threshold 0.8 --output json
    """
    # Display start message
    console.print("\n[bold blue]🔍 Starting Investigation[/bold blue]")
    console.print(f"Query: [green]{query}[/green]")

    if org:
        console.print(f"Organization: [cyan]{org}[/cyan]")
    if year:
        console.print(f"Year: [cyan]{year}[/cyan]")

    console.print(f"Anomaly threshold: [yellow]{threshold}[/yellow]")
    console.print(f"Max results: [yellow]{max_results}[/yellow]")
    console.print()

    # Create investigation request
    request = InvestigationRequest(
        query=query,
        organization_code=org,
        year=year,
        threshold=threshold,
        max_results=max_results,
        include_contracts=not no_contracts,
    )

    try:
        # Execute investigation with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing investigation...", total=None)

            # Start investigation
            progress.update(task, description="Starting investigation...")
            result_data = asyncio.run(
                call_api(
                    "/api/v1/investigations/analyze",
                    method="POST",
                    data=request.dict(),
                    auth_token=api_key,
                )
            )

            investigation_id = result_data.get("investigation_id")
            progress.update(task, description=f"Investigation ID: {investigation_id}")

            # Poll for results
            while True:
                progress.update(task, description="Checking investigation status...")

                status_data = asyncio.run(
                    call_api(
                        f"/api/v1/investigations/{investigation_id}", auth_token=api_key
                    )
                )

                status = status_data.get("status", "unknown")
                progress_pct = status_data.get("progress", 0) * 100

                progress.update(
                    task, description=f"Status: {status} ({progress_pct:.0f}%)"
                )

                if status in ["completed", "failed"]:
                    break

                asyncio.run(asyncio.sleep(2))

        # Process results
        if status == "failed":
            console.print(
                f"[red]❌ Investigation failed: {status_data.get('error', 'Unknown error')}[/red]"
            )
            raise typer.Exit(1)

        # Create result object
        result = InvestigationResult(
            id=investigation_id,
            status=status,
            created_at=datetime.fromisoformat(status_data["created_at"]),
            summary=status_data.get("summary"),
            anomalies_count=len(status_data.get("anomalies", [])),
            total_analyzed=status_data.get("total_analyzed", 0),
            risk_score=status_data.get("risk_score", 0.0),
            anomalies=status_data.get("anomalies", []),
            contracts=status_data.get("contracts", []),
        )

        # Display results based on format
        console.print()

        if output == OutputFormat.TABLE:
            display_results_table(result)
        elif output == OutputFormat.MARKDOWN:
            display_results_markdown(result)
        elif output == OutputFormat.JSON:
            display_results_json(result)
        elif output == OutputFormat.HTML:
            # For HTML, we'll convert markdown to HTML
            console.print(
                "[yellow]HTML output not yet implemented, showing markdown[/yellow]"
            )
            display_results_markdown(result)

        # Save results if requested
        if save:
            save_path = save.expanduser().resolve()

            if output == OutputFormat.JSON:
                import json

                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(
                        result.dict(), f, indent=2, default=str, ensure_ascii=False
                    )
            else:
                # Save as text for other formats
                with open(save_path, "w", encoding="utf-8") as f:
                    if output == OutputFormat.MARKDOWN:
                        f.write(generate_markdown_report(result))
                    else:
                        f.write(generate_text_report(result))

            console.print(f"\n[green]✅ Results saved to: {save_path}[/green]")

        # Summary message
        if result.anomalies_count > 0:
            risk_color = get_risk_color(result.risk_score)
            console.print(
                f"\n[bold {risk_color}]⚠️  Investigation complete: "
                f"{result.anomalies_count} anomalies detected "
                f"(risk score: {result.risk_score:.2f})[/bold {risk_color}]"
            )
        else:
            console.print(
                "\n[green]✅ Investigation complete: No anomalies detected[/green]"
            )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


def generate_markdown_report(result: InvestigationResult) -> str:
    """Generate full markdown report."""
    report = f"""# Cidadão.AI Investigation Report

**Investigation ID**: {result.id}
**Date**: {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}
**Status**: {result.status}

## Executive Summary

**Risk Score**: {result.risk_score:.2f}
**Anomalies Found**: {result.anomalies_count}
**Total Items Analyzed**: {result.total_analyzed}

{result.summary or 'Investigation completed successfully.'}

## Detailed Findings

### Anomalies Detected

"""

    for i, anomaly in enumerate(result.anomalies, 1):
        report += f"""#### Anomaly {i}

- **Type**: {anomaly.get('type', 'Unknown')}
- **Severity**: {anomaly.get('severity', 0):.2f}
- **Description**: {anomaly.get('description', 'N/A')}
- **Explanation**: {anomaly.get('explanation', 'N/A')}
- **Contract ID**: {anomaly.get('contract_id', 'N/A')}
- **Value**: R$ {anomaly.get('value', 0):,.2f}

"""

    if result.contracts:
        report += "\n### Related Contracts\n\n"
        for contract in result.contracts[:10]:
            report += f"""- **{contract.get('id', 'N/A')}**: {contract.get('description', 'N/A')}
  - Value: R$ {contract.get('value', 0):,.2f}
  - Supplier: {contract.get('supplier', 'N/A')}

"""

    report += "\n---\n*Report generated by Cidadão.AI - Multi-agent AI system for government transparency*"

    return report


def generate_text_report(result: InvestigationResult) -> str:
    """Generate plain text report."""
    report = f"""CIDADÃO.AI INVESTIGATION REPORT
================================

Investigation ID: {result.id}
Date: {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Status: {result.status}

SUMMARY
-------
Risk Score: {result.risk_score:.2f}
Anomalies Found: {result.anomalies_count}
Total Analyzed: {result.total_analyzed}

{result.summary or 'Investigation completed successfully.'}

ANOMALIES
---------
"""

    for i, anomaly in enumerate(result.anomalies, 1):
        report += f"""
{i}. {anomaly.get('type', 'Unknown')} (Severity: {anomaly.get('severity', 0):.2f})
   Description: {anomaly.get('description', 'N/A')}
   Contract: {anomaly.get('contract_id', 'N/A')}
   Value: R$ {anomaly.get('value', 0):,.2f}
"""

    return report


if __name__ == "__main__":
    app()
