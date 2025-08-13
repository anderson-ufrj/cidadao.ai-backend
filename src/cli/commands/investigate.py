"""Investigation command for CLI."""

import click
from typing import Optional


@click.command()
@click.argument('query', required=True)
@click.option('--org', help='Organization code to focus investigation')
@click.option('--year', type=int, help='Year to investigate')
@click.option('--threshold', type=float, default=0.7, help='Anomaly detection threshold')
@click.option('--output', type=click.Choice(['json', 'markdown', 'html']), default='markdown')
def investigate_command(
    query: str,
    org: Optional[str] = None,
    year: Optional[int] = None,
    threshold: float = 0.7,
    output: str = 'markdown'
):
    """Start an investigation on government spending.
    
    QUERY: Natural language description of what to investigate
    """
    click.echo(f"🔍 Iniciando investigação: {query}")
    
    if org:
        click.echo(f"📊 Organização: {org}")
    
    if year:
        click.echo(f"📅 Ano: {year}")
    
    click.echo(f"⚖️ Limite de anomalia: {threshold}")
    click.echo(f"📄 Formato de saída: {output}")
    
    # TODO: Implement actual investigation logic
    click.echo("⚠️  Funcionalidade em desenvolvimento")
    click.echo("📋 Status: Implementação planejada para fase de produção")


if __name__ == '__main__':
    investigate_command()