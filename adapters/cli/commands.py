"""CLI commands for price app operations."""

import click
from typing import Optional
import asyncio
from main import (
    get_fetch_prices_use_case,
    get_compute_indicators_use_case,
    get_store_data_use_case
)


@click.group()
def cli():
    """Price App CLI - Manage price data and indicators."""
    pass


@cli.command()
@click.argument('symbol')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--store', is_flag=True, help='Store fetched data')
def fetch(symbol: str, start_date: Optional[str], end_date: Optional[str], store: bool):
    """Fetch price data for a symbol."""
    use_case = get_fetch_prices_use_case()
    result = use_case.execute(symbol, start_date, end_date, store=store)
    
    click.echo(f"Fetched {result.count} records for {symbol}")
    if result.error:
        click.echo(f"Error: {result.error}", err=True)


@cli.command()
@click.argument('symbol')
@click.argument('indicator')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
def compute(symbol: str, indicator: str, start_date: Optional[str], end_date: Optional[str]):
    """Compute indicator for a symbol."""
    click.echo(f"Computing {indicator} for {symbol}...")
    click.echo("Note: This command requires price data to be stored first.")
    # Implementation would fetch prices and compute indicator
    click.echo("Use the API or tasks for full functionality.")


if __name__ == '__main__':
    cli()

