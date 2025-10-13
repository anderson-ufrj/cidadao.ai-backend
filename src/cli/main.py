"""Main CLI application entry point for Cidadão.AI.

This module provides the main Typer application that serves as the entry point
for all CLI commands as defined in pyproject.toml.

Usage:
    cidadao --help
    cidadao investigate --help
    cidadao analyze --help
    cidadao report --help
    cidadao watch --help

Status: Professional implementation with comprehensive command structure.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

# Add src to Python path for proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.commands import analyze, investigate, report, watch
from src.core.config import get_settings

# Initialize Typer app with rich formatting
app = typer.Typer(
    name="cidadao",
    help="🏛️ Cidadão.AI - Sistema multi-agente de IA para transparência pública brasileira",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Initialize Rich console for beautiful output
console = Console()

# Add commands to main app
app.command(
    "investigate", help="🔍 Executar investigações de anomalias em dados públicos"
)(investigate)
app.command(
    "analyze", help="📊 Analisar padrões e correlações em dados governamentais"
)(analyze)
app.command("report", help="📋 Gerar relatórios detalhados de investigações")(report)
app.command("watch", help="👀 Monitorar dados em tempo real para anomalias")(watch)


@app.command("version")
def version() -> None:
    """Display version information."""
    settings = get_settings()
    console.print(
        Panel.fit(
            f"[bold blue]Cidadão.AI v1.0.0[/bold blue]\n"
            f"[dim]Multi-agent AI system for Brazilian government transparency[/dim]\n"
            f"[dim]Environment: {settings.ENVIRONMENT}[/dim]",
            title="📊 Sistema de Transparência",
            border_style="blue",
        )
    )


@app.command("status")
def status() -> None:
    """Check system status and health."""
    console.print(
        Panel.fit(
            "[green]✅ Sistema operacional[/green]\n"
            "[yellow]⚠️  CLI em desenvolvimento[/yellow]\n"
            "[blue]ℹ️  Use 'cidadao --help' para comandos disponíveis[/blue]",
            title="🔍 Status do Sistema",
            border_style="green",
        )
    )


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Custom configuration file path"
    ),
) -> None:
    """
    🏛️ Cidadão.AI - Sistema multi-agente de IA para transparência pública brasileira.

    Sistema enterprise-grade para detecção de anomalias e análise de transparência
    em dados governamentais brasileiros usando múltiplos agentes de IA especializados.

    Agentes Disponíveis:
    - 🏹 Zumbi dos Palmares: Investigação e detecção de anomalias
    - 🎭 Anita Garibaldi: Análise de padrões revolucionária
    - 📝 Tiradentes: Geração de relatórios pela liberdade de informação
    - 🏎️ Ayrton Senna: Roteamento semântico de alta performance
    - E mais 13 agentes especializados com identidade cultural brasileira

    Para começar:
        cidadao status      # Verificar status do sistema
        cidadao --help      # Ver todos os comandos disponíveis
    """
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")
        console.print(f"[dim]Config file: {config_file or 'default'}[/dim]")


def cli_main() -> None:
    """Entry point for the CLI when installed as a package."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operação cancelada pelo usuário[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Erro: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    cli_main()
