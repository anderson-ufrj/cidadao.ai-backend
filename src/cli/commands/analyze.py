"""
Module: cli.commands.analyze
Description: Analysis command for CLI - pattern and correlation analysis
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.columns import Columns
from rich.syntax import Syntax
import httpx
from pydantic import BaseModel, Field
import pandas as pd

# CLI app
app = typer.Typer(help="Analyze patterns and correlations in government data")
console = Console()


class AnalysisType(str, Enum):
    """Analysis type options."""
    TEMPORAL = "temporal"
    SUPPLIER = "supplier"
    CATEGORY = "category"
    REGIONAL = "regional"
    CORRELATION = "correlation"
    COMPREHENSIVE = "comprehensive"


class OutputFormat(str, Enum):
    """Output format options."""
    DASHBOARD = "dashboard"
    TABLE = "table"
    JSON = "json"
    CSV = "csv"


class AnalysisRequest(BaseModel):
    """Analysis request model."""
    analysis_type: AnalysisType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    organizations: List[str] = Field(default_factory=list)
    suppliers: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    regions: List[str] = Field(default_factory=list)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    include_trends: bool = True
    include_outliers: bool = True
    correlation_threshold: float = 0.7


class AnalysisResult(BaseModel):
    """Analysis result model."""
    id: str
    analysis_type: str
    created_at: datetime
    status: str
    summary: Dict[str, Any]
    patterns: List[Dict[str, Any]]
    correlations: List[Dict[str, Any]]
    trends: List[Dict[str, Any]]
    outliers: List[Dict[str, Any]]
    statistics: Dict[str, Any]


async def call_api(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    auth_token: Optional[str] = None
) -> Dict[str, Any]:
    """Make API call to backend."""
    api_url = "http://localhost:8000"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Cidadao.AI-CLI/1.0"
    }
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=method,
            url=f"{api_url}{endpoint}",
            headers=headers,
            json=data,
            params=params,
            timeout=120.0  # Longer timeout for analysis
        )
        
        if response.status_code >= 400:
            error_detail = response.json().get("detail", "Unknown error")
            raise Exception(f"API Error: {error_detail}")
        
        return response.json()


def display_dashboard(result: AnalysisResult):
    """Display analysis results as a dashboard."""
    # Title
    console.print(
        Panel(
            f"[bold blue]📊 Analysis Dashboard[/bold blue]\n"
            f"Type: {result.analysis_type.upper()}\n"
            f"Generated: {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            title="Cidadão.AI Analysis",
            border_style="blue"
        )
    )
    
    # Summary statistics
    stats = result.statistics
    console.print("\n[bold]📈 Summary Statistics:[/bold]")
    
    stats_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    stats_table.add_column("Metric", style="dim")
    stats_table.add_column("Value", justify="right")
    
    for key, value in stats.items():
        if isinstance(value, float):
            stats_table.add_row(key.replace("_", " ").title(), f"{value:,.2f}")
        else:
            stats_table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(stats_table)
    
    # Patterns
    if result.patterns:
        console.print("\n[bold]🔍 Patterns Detected:[/bold]")
        for i, pattern in enumerate(result.patterns[:5], 1):
            console.print(
                Panel(
                    f"[yellow]Pattern {i}: {pattern.get('name', 'Unknown')}[/yellow]\n"
                    f"Confidence: {pattern.get('confidence', 0):.2%}\n"
                    f"Description: {pattern.get('description', 'N/A')}\n"
                    f"Impact: {pattern.get('impact', 'N/A')}",
                    border_style="yellow"
                )
            )
    
    # Top correlations
    if result.correlations:
        console.print("\n[bold]🔗 Strong Correlations:[/bold]")
        corr_table = Table(show_header=True, header_style="bold green")
        corr_table.add_column("Variable 1", width=25)
        corr_table.add_column("Variable 2", width=25)
        corr_table.add_column("Correlation", justify="center")
        corr_table.add_column("Strength", justify="center")
        
        for corr in result.correlations[:5]:
            strength = abs(corr.get('value', 0))
            color = "red" if strength >= 0.9 else "yellow" if strength >= 0.7 else "green"
            corr_table.add_row(
                corr.get('var1', 'N/A'),
                corr.get('var2', 'N/A'),
                f"{corr.get('value', 0):.3f}",
                f"[{color}]{'●' * int(strength * 5)}[/{color}]"
            )
        
        console.print(corr_table)
    
    # Trends
    if result.trends:
        console.print("\n[bold]📈 Key Trends:[/bold]")
        for trend in result.trends[:3]:
            direction = "↗️" if trend.get('direction') == 'up' else "↘️" if trend.get('direction') == 'down' else "→"
            console.print(
                f"{direction} [cyan]{trend.get('name', 'Unknown')}:[/cyan] "
                f"{trend.get('description', 'N/A')} "
                f"([dim]{trend.get('change', 0):+.1%}[/dim])"
            )
    
    # Outliers alert
    if result.outliers:
        console.print(f"\n[bold red]⚠️  {len(result.outliers)} outliers detected![/bold red]")
        console.print("[dim]Use --show-outliers flag to see details[/dim]")


def display_table(result: AnalysisResult):
    """Display results in table format."""
    # Main results table
    table = Table(title="Analysis Results", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="dim")
    table.add_column("Items", justify="right")
    
    table.add_row("Patterns Found", str(len(result.patterns)))
    table.add_row("Correlations", str(len(result.correlations)))
    table.add_row("Trends", str(len(result.trends)))
    table.add_row("Outliers", str(len(result.outliers)))
    
    console.print(table)
    
    # Detailed patterns
    if result.patterns:
        console.print("\n[bold]Patterns:[/bold]")
        patterns_table = Table(show_header=True)
        patterns_table.add_column("Name", width=30)
        patterns_table.add_column("Type", style="dim")
        patterns_table.add_column("Confidence", justify="center")
        patterns_table.add_column("Description", width=40)
        
        for pattern in result.patterns[:10]:
            patterns_table.add_row(
                pattern.get('name', 'Unknown'),
                pattern.get('type', 'N/A'),
                f"{pattern.get('confidence', 0):.1%}",
                pattern.get('description', 'N/A')[:40]
            )
        
        console.print(patterns_table)


def display_json(result: AnalysisResult):
    """Display results in JSON format."""
    import json
    json_str = json.dumps(result.dict(), indent=2, default=str, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
    console.print(syntax)


def export_csv(result: AnalysisResult, filename: Path):
    """Export results to CSV files."""
    # Export patterns
    if result.patterns:
        patterns_df = pd.DataFrame(result.patterns)
        patterns_file = filename.parent / f"{filename.stem}_patterns.csv"
        patterns_df.to_csv(patterns_file, index=False)
        console.print(f"[green]✓ Patterns exported to: {patterns_file}[/green]")
    
    # Export correlations
    if result.correlations:
        corr_df = pd.DataFrame(result.correlations)
        corr_file = filename.parent / f"{filename.stem}_correlations.csv"
        corr_df.to_csv(corr_file, index=False)
        console.print(f"[green]✓ Correlations exported to: {corr_file}[/green]")
    
    # Export statistics
    stats_df = pd.DataFrame([result.statistics])
    stats_file = filename.parent / f"{filename.stem}_statistics.csv"
    stats_df.to_csv(stats_file, index=False)
    console.print(f"[green]✓ Statistics exported to: {stats_file}[/green]")


@app.command()
def analyze(
    analysis_type: AnalysisType = typer.Argument(help="Type of analysis to perform"),
    period: Optional[str] = typer.Option(None, "--period", "-p", help="Analysis period (e.g., 2024, 2024-Q1, last-30-days)"),
    organizations: Optional[List[str]] = typer.Option(None, "--org", "-o", help="Organization codes to analyze"),
    suppliers: Optional[List[str]] = typer.Option(None, "--supplier", "-s", help="Supplier names to analyze"),
    categories: Optional[List[str]] = typer.Option(None, "--category", "-c", help="Contract categories to analyze"),
    regions: Optional[List[str]] = typer.Option(None, "--region", "-r", help="Regions to analyze"),
    min_value: Optional[float] = typer.Option(None, "--min-value", help="Minimum contract value"),
    max_value: Optional[float] = typer.Option(None, "--max-value", help="Maximum contract value"),
    output: OutputFormat = typer.Option(OutputFormat.DASHBOARD, "--output", "-f", help="Output format"),
    save: Optional[Path] = typer.Option(None, "--save", help="Save results to file"),
    show_outliers: bool = typer.Option(False, "--show-outliers", help="Show detailed outlier information"),
    correlation_threshold: float = typer.Option(0.7, "--corr-threshold", help="Minimum correlation threshold"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="CIDADAO_API_KEY", help="API key"),
):
    """
    📊 Analyze patterns and correlations in government data.
    
    This command performs deep analysis on government contracts and spending
    to identify patterns, trends, correlations, and anomalies.
    
    Analysis Types:
    - temporal: Time-based patterns and seasonality
    - supplier: Supplier behavior and concentration
    - category: Spending by category analysis
    - regional: Geographic distribution analysis
    - correlation: Variable correlation analysis
    - comprehensive: All analyses combined
    
    Examples:
        cidadao analyze temporal --period 2024
        cidadao analyze supplier --org MIN_SAUDE --show-outliers
        cidadao analyze comprehensive --period last-90-days --output json
    """
    # Parse period
    start_date, end_date = parse_period(period)
    
    # Display start message
    console.print(f"\n[bold blue]📊 Starting {analysis_type.value} Analysis[/bold blue]")
    if period:
        console.print(f"Period: [green]{period}[/green]")
    if organizations:
        console.print(f"Organizations: [cyan]{', '.join(organizations)}[/cyan]")
    
    # Create request
    request = AnalysisRequest(
        analysis_type=analysis_type,
        start_date=start_date,
        end_date=end_date,
        organizations=organizations or [],
        suppliers=suppliers or [],
        categories=categories or [],
        regions=regions or [],
        min_value=min_value,
        max_value=max_value,
        correlation_threshold=correlation_threshold
    )
    
    try:
        # Execute analysis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            # Start analysis
            task = progress.add_task("Initializing analysis...", total=100)
            
            result_data = asyncio.run(
                call_api(
                    "/api/v1/analysis/execute",
                    method="POST",
                    data=request.dict(),
                    auth_token=api_key
                )
            )
            
            analysis_id = result_data.get("analysis_id")
            progress.update(task, advance=20, description=f"Analysis ID: {analysis_id}")
            
            # Poll for completion
            while True:
                status_data = asyncio.run(
                    call_api(
                        f"/api/v1/analysis/{analysis_id}",
                        auth_token=api_key
                    )
                )
                
                status = status_data.get("status", "unknown")
                progress_pct = status_data.get("progress", 0) * 100
                
                progress.update(
                    task,
                    completed=int(progress_pct),
                    description=f"Analyzing... ({status})"
                )
                
                if status in ["completed", "failed"]:
                    break
                
                asyncio.run(asyncio.sleep(1))
        
        if status == "failed":
            console.print(f"[red]❌ Analysis failed: {status_data.get('error', 'Unknown error')}[/red]")
            raise typer.Exit(1)
        
        # Create result object
        result = AnalysisResult(
            id=analysis_id,
            analysis_type=analysis_type.value,
            created_at=datetime.fromisoformat(status_data["created_at"]),
            status=status,
            summary=status_data.get("summary", {}),
            patterns=status_data.get("patterns", []),
            correlations=status_data.get("correlations", []),
            trends=status_data.get("trends", []),
            outliers=status_data.get("outliers", []),
            statistics=status_data.get("statistics", {})
        )
        
        # Display results
        console.print()
        if output == OutputFormat.DASHBOARD:
            display_dashboard(result)
            if show_outliers and result.outliers:
                console.print("\n[bold]🔴 Outliers Detail:[/bold]")
                for outlier in result.outliers[:10]:
                    console.print(f"  • {outlier.get('description', 'N/A')} [dim](score: {outlier.get('score', 0):.2f})[/dim]")
        elif output == OutputFormat.TABLE:
            display_table(result)
        elif output == OutputFormat.JSON:
            display_json(result)
        elif output == OutputFormat.CSV:
            if not save:
                save = Path(f"analysis_{analysis_id}.csv")
            export_csv(result, save)
        
        # Save results if requested
        if save and output != OutputFormat.CSV:
            save_path = save.expanduser().resolve()
            
            if output == OutputFormat.JSON:
                import json
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(result.dict(), f, indent=2, default=str, ensure_ascii=False)
            else:
                # Save as markdown
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(generate_analysis_report(result))
            
            console.print(f"\n[green]✅ Results saved to: {save_path}[/green]")
        
        # Summary
        patterns_found = len(result.patterns)
        if patterns_found > 0:
            console.print(
                f"\n[bold green]✅ Analysis complete: "
                f"{patterns_found} patterns found[/bold green]"
            )
        else:
            console.print("\n[yellow]⚠️  Analysis complete: No significant patterns found[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


def parse_period(period: Optional[str]) -> tuple[Optional[datetime], Optional[datetime]]:
    """Parse period string into start and end dates."""
    if not period:
        return None, None
    
    now = datetime.now()
    
    # Year format (e.g., 2024)
    if period.isdigit() and len(period) == 4:
        year = int(period)
        return datetime(year, 1, 1), datetime(year, 12, 31, 23, 59, 59)
    
    # Quarter format (e.g., 2024-Q1)
    if "-Q" in period:
        year, quarter = period.split("-Q")
        year = int(year)
        quarter = int(quarter)
        quarter_starts = {1: 1, 2: 4, 3: 7, 4: 10}
        quarter_ends = {1: 3, 2: 6, 3: 9, 4: 12}
        start_month = quarter_starts[quarter]
        end_month = quarter_ends[quarter]
        
        start = datetime(year, start_month, 1)
        # Last day of quarter
        if end_month == 12:
            end = datetime(year, 12, 31, 23, 59, 59)
        else:
            end = datetime(year, end_month + 1, 1) - timedelta(seconds=1)
        
        return start, end
    
    # Relative periods
    if period.startswith("last-"):
        days_match = period.replace("last-", "").replace("-days", "")
        if days_match.isdigit():
            days = int(days_match)
            return now - timedelta(days=days), now
    
    # Default to current year
    return datetime(now.year, 1, 1), now


def generate_analysis_report(result: AnalysisResult) -> str:
    """Generate markdown analysis report."""
    report = f"""# Cidadão.AI Analysis Report

**Analysis Type**: {result.analysis_type}
**Generated**: {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}

## Summary

"""
    
    # Add summary items
    for key, value in result.summary.items():
        report += f"- **{key.replace('_', ' ').title()}**: {value}\n"
    
    # Patterns section
    if result.patterns:
        report += "\n## Patterns Detected\n\n"
        for i, pattern in enumerate(result.patterns, 1):
            report += f"### Pattern {i}: {pattern.get('name', 'Unknown')}\n\n"
            report += f"- **Type**: {pattern.get('type', 'N/A')}\n"
            report += f"- **Confidence**: {pattern.get('confidence', 0):.1%}\n"
            report += f"- **Description**: {pattern.get('description', 'N/A')}\n"
            report += f"- **Impact**: {pattern.get('impact', 'N/A')}\n\n"
    
    # Correlations section
    if result.correlations:
        report += "\n## Correlations\n\n"
        report += "| Variable 1 | Variable 2 | Correlation | p-value |\n"
        report += "|------------|------------|-------------|--------|\n"
        for corr in result.correlations:
            report += f"| {corr.get('var1', 'N/A')} | {corr.get('var2', 'N/A')} | "
            report += f"{corr.get('value', 0):.3f} | {corr.get('p_value', 0):.4f} |\n"
    
    # Statistics
    report += "\n## Statistics\n\n"
    for key, value in result.statistics.items():
        if isinstance(value, float):
            report += f"- **{key.replace('_', ' ').title()}**: {value:,.2f}\n"
        else:
            report += f"- **{key.replace('_', ' ').title()}**: {value}\n"
    
    report += "\n---\n*Analysis performed by Cidadão.AI - Multi-agent AI system for government transparency*"
    
    return report


if __name__ == "__main__":
    app()