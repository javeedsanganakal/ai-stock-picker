"""CLI interface for ai-stock-picker."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()


@click.group()
def main():
    """AI Stock Picker — research and suggest stocks."""
    pass


@main.command()
@click.argument("symbol")
def info(symbol: str):
    """Get a quick snapshot of a stock."""
    from .market_data import get_stock_info

    with console.status(f"Fetching {symbol.upper()}..."):
        stock = get_stock_info(symbol)

    table = Table(title=f"{stock.name} ({stock.symbol})")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Price", f"${stock.price:.2f}")
    table.add_row("Change", f"{stock.change_pct:+.2f}%")
    table.add_row("Volume", f"{stock.volume:,}")
    table.add_row("Market Cap", _fmt_large_num(stock.market_cap))
    table.add_row("P/E Ratio", f"{stock.pe_ratio:.2f}" if stock.pe_ratio else "N/A")
    table.add_row("Sector", stock.sector or "N/A")
    table.add_row("Industry", stock.industry or "N/A")
    table.add_row("52W High", f"${stock.fifty_two_week_high:.2f}" if stock.fifty_two_week_high else "N/A")
    table.add_row("52W Low", f"${stock.fifty_two_week_low:.2f}" if stock.fifty_two_week_low else "N/A")
    table.add_row("Dividend Yield", f"{stock.dividend_yield:.2f}%" if stock.dividend_yield else "N/A")

    console.print(table)


@main.command()
@click.argument("symbol")
def analyze(symbol: str):
    """Run fundamental + technical analysis on a stock."""
    from .analysis import fundamental_analysis, technical_analysis

    with console.status(f"Analyzing {symbol.upper()}..."):
        fund = fundamental_analysis(symbol)
        tech = technical_analysis(symbol)

    # Fundamental
    console.print(Panel(f"[bold]{fund.name}[/bold] ({fund.symbol})", subtitle="Fundamental Analysis"))

    ft = Table(show_header=False)
    ft.add_column("Metric", style="cyan", width=20)
    ft.add_column("Value", style="white")

    ft.add_row("Market Cap", _fmt_large_num(fund.market_cap))
    ft.add_row("P/E (Trailing)", f"{fund.pe_ratio:.2f}" if fund.pe_ratio else "N/A")
    ft.add_row("P/E (Forward)", f"{fund.forward_pe:.2f}" if fund.forward_pe else "N/A")
    ft.add_row("PEG Ratio", f"{fund.peg_ratio:.2f}" if fund.peg_ratio else "N/A")
    ft.add_row("Debt/Equity", f"{fund.debt_to_equity:.0f}" if fund.debt_to_equity else "N/A")
    ft.add_row("Revenue Growth", f"{fund.revenue_growth:.1%}" if fund.revenue_growth else "N/A")
    ft.add_row("Earnings Growth", f"{fund.earnings_growth:.1%}" if fund.earnings_growth else "N/A")
    ft.add_row("Profit Margin", f"{fund.profit_margin:.1%}" if fund.profit_margin else "N/A")
    ft.add_row("ROE", f"{fund.return_on_equity:.1%}" if fund.return_on_equity else "N/A")
    ft.add_row("Free Cash Flow", _fmt_large_num(fund.free_cash_flow))
    ft.add_row("Analyst Target", f"${fund.target_price:.2f}" if fund.target_price else "N/A")
    ft.add_row("Recommendation", fund.recommendation or "N/A")
    console.print(ft)

    if fund.signals:
        console.print("\n[bold cyan]Fundamental Signals:[/bold cyan]")
        for s in fund.signals:
            console.print(f"  -> {s}")

    # Technical
    console.print()
    console.print(Panel("Technical Analysis", subtitle=f"Price: ${tech.current_price:.2f}"))

    tt = Table(show_header=False)
    tt.add_column("Metric", style="cyan", width=20)
    tt.add_column("Value", style="white")

    tt.add_row("SMA 20", f"${tech.sma_20:.2f}" if tech.sma_20 else "N/A")
    tt.add_row("SMA 50", f"${tech.sma_50:.2f}" if tech.sma_50 else "N/A")
    tt.add_row("SMA 200", f"${tech.sma_200:.2f}" if tech.sma_200 else "N/A")
    tt.add_row("RSI (14)", f"{tech.rsi_14:.1f}" if tech.rsi_14 else "N/A")
    tt.add_row("Avg Volume (20d)", f"{tech.avg_volume_20d:,.0f}" if tech.avg_volume_20d else "N/A")
    tt.add_row("Volume Ratio", f"{tech.volume_ratio:.2f}x" if tech.volume_ratio else "N/A")
    tt.add_row("vs 52W High", f"{tech.price_vs_52w_high_pct:+.1f}%" if tech.price_vs_52w_high_pct is not None else "N/A")
    tt.add_row("vs 52W Low", f"{tech.price_vs_52w_low_pct:+.1f}%" if tech.price_vs_52w_low_pct is not None else "N/A")
    console.print(tt)

    if tech.signals:
        console.print("\n[bold cyan]Technical Signals:[/bold cyan]")
        for s in tech.signals:
            console.print(f"  -> {s}")


@main.command()
@click.option("--sector", "-s", multiple=True, help="Filter by sector (e.g., Technology)")
@click.option("--max-price", "-mp", type=float, help="Maximum stock price")
@click.option("--min-price", type=float, help="Minimum stock price")
@click.option("--budget", "-b", type=float, help="Your total budget")
@click.option("--top", "-n", default=5, help="Number of picks (default: 5)")
def suggest(sector, max_price, min_price, budget, top):
    """Suggest stocks based on your criteria.

    Examples:
        ai-stock-picker suggest --sector Technology --max-price 200
        ai-stock-picker suggest --budget 5000 --top 3
    """
    from .suggest import suggest_stocks

    sectors = list(sector) if sector else None

    console.print(Panel("[bold]AI Stock Picker[/bold] — Finding the best picks for you..."))

    with console.status("Screening and analyzing stocks..."):
        picks = suggest_stocks(
            sectors=sectors,
            max_price=max_price,
            min_price=min_price,
            budget=budget,
            top_n=top,
        )

    if not picks:
        console.print("[yellow]No stocks matched your criteria. Try broadening your filters.[/yellow]")
        return

    for i, pick in enumerate(picks, 1):
        score_color = "green" if pick.score >= 65 else "yellow" if pick.score >= 50 else "red"

        console.print()
        console.print(
            Panel(
                f"[bold]{pick.name}[/bold] ({pick.symbol})  —  "
                f"${pick.price:.2f}  |  "
                f"[{score_color}]Score: {pick.score}/100[/{score_color}]",
                title=f"#{i} Pick",
            )
        )

        if pick.reasons:
            for reason in pick.reasons:
                console.print(f"  [green]+[/green] {reason}")

    console.print()
    console.print(
        "[dim]Disclaimer: This is for research purposes only. "
        "Not financial advice. Always do your own due diligence.[/dim]"
    )


@main.command()
def sectors():
    """List available sector names for filtering."""
    from .market_data import SECTORS

    console.print("[bold]Available Sectors:[/bold]")
    for s in SECTORS:
        console.print(f"  - {s}")


def _fmt_large_num(n: float | None) -> str:
    if n is None:
        return "N/A"
    if abs(n) >= 1e12:
        return f"${n / 1e12:.2f}T"
    if abs(n) >= 1e9:
        return f"${n / 1e9:.2f}B"
    if abs(n) >= 1e6:
        return f"${n / 1e6:.2f}M"
    return f"${n:,.0f}"


if __name__ == "__main__":
    main()
