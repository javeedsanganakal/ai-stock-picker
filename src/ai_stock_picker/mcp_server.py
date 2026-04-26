"""MCP Server — exposes ai-stock-picker as tools that Claude can call.

Think of this as a senior trading analyst's toolkit at your fingertips.
"""

import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ai-stock-picker", instructions="""You are a senior equity research analyst powered by the ai-stock-picker package.

Project: https://github.com/javeedsanganakal/ai-stock-picker

You have access to a full S&P 500 (503 stocks, 11 GICS sectors) research toolkit.
Use these tools to answer ANY question about stocks, investing, or portfolio building.

## Workflow

When a user asks something like "I have $10,000 and want to build a tech-heavy portfolio with low risk":

Step 1 — SECTOR CHECK: Call sector_rotation to see which sectors are hot/cold right now.
Step 2 — FIND PICKS: Call suggest_stocks with their criteria (sectors, budget, price range).
Step 3 — RISK CHECK: Call risk_profile on each candidate to filter for their risk tolerance.
Step 4 — EARNINGS CHECK: Call earnings_intel to avoid stocks reporting earnings soon (high-vol event).
Step 5 — BUILD PORTFOLIO: Call portfolio_builder with the final picks, budget, and strategy.

## Tool Guide

| Need                        | Tool                |
|-----------------------------|---------------------|
| Quick stock lookup          | get_stock_info      |
| Deep dive on one stock      | analyze_stock       |
| Risk/volatility analysis    | risk_profile        |
| Momentum & trend            | momentum_check      |
| Which sectors are hot/cold  | sector_rotation     |
| Stocks near 52w highs       | find_breakouts      |
| Earnings dates & surprises  | earnings_intel      |
| Compare 2-5 stocks          | compare_stocks      |
| Allocate budget into shares | portfolio_builder   |
| AI-scored stock picks       | suggest_stocks      |
| List all sectors            | list_sectors        |

## Legendary Trader Strategies (THE CORE FEATURE)

You have 7 strategies modeled after the greatest traders in history.
START EVERY SESSION with daily_briefing — it picks the right mindset for today.

| Trader         | Key        | Strategy                                    |
|----------------|------------|---------------------------------------------|
| George Soros   | soros      | Macro thesis — big trends, bet heavily      |
| Jim Simons     | simons     | Quantitative — statistical edges, no emotion|
| Paul Tudor Jones| jones     | Technical + macro — follow trends            |
| John Paulson   | paulson    | Contrarian — what is everyone wrong about?  |
| Ray Dalio      | dalio      | All-weather — balanced for any environment  |
| Jesse Livermore| livermore  | Momentum — ride winners, cut losers fast    |
| Takashi Kotegawa| kotegawa  | Crash buying — buy the blood, mean reversion|

Tools: daily_briefing, run_strategy, all_strategies_summary

## Analyst Mindset (think JPM senior desk)

- START with daily_briefing to pick today's strategy
- Always consider RISK alongside returns — check beta, drawdown, volatility
- Never recommend a stock without checking earnings calendar first
- Use sector rotation to confirm the sector is in favor
- Check relative strength — is it outperforming or lagging the S&P 500?
- For "low risk" requests: favor low beta (<1), low volatility, strong Sharpe, use risk_parity allocation
- For "growth" requests: favor high revenue/earnings growth, momentum, use momentum_tilt allocation
- For "value" requests: favor low P/E, low PEG, high dividend yield

## Always disclaim: This is research only, not financial advice.
""")


# ─── Core Tools ──────────────────────────────────────────────────────────────

@mcp.tool()
def get_stock_info(symbol: str) -> str:
    """Quick snapshot — price, market cap, P/E, sector.

    The first thing you pull up on any stock. Use this for quick checks.
    """
    from ai_stock_picker.market_data import get_stock_info as _get_info

    stock = _get_info(symbol)
    return json.dumps({
        "symbol": stock.symbol,
        "name": stock.name,
        "price": stock.price,
        "change_pct": stock.change_pct,
        "volume": stock.volume,
        "market_cap": stock.market_cap,
        "pe_ratio": stock.pe_ratio,
        "sector": stock.sector,
        "industry": stock.industry,
        "52w_high": stock.fifty_two_week_high,
        "52w_low": stock.fifty_two_week_low,
        "dividend_yield": stock.dividend_yield,
    }, indent=2)


@mcp.tool()
def analyze_stock(symbol: str) -> str:
    """Deep fundamental + technical analysis.

    Runs full valuation (P/E, PEG, debt, margins, growth) and technicals
    (RSI, SMAs, volume, 52w range). Returns actionable signals.
    """
    from ai_stock_picker.analysis import fundamental_analysis, technical_analysis

    fund = fundamental_analysis(symbol)
    tech = technical_analysis(symbol)

    return json.dumps({
        "fundamental": {
            "name": fund.name,
            "sector": fund.sector,
            "market_cap": fund.market_cap,
            "pe_ratio": fund.pe_ratio,
            "forward_pe": fund.forward_pe,
            "peg_ratio": fund.peg_ratio,
            "price_to_book": fund.price_to_book,
            "debt_to_equity": fund.debt_to_equity,
            "revenue_growth": fund.revenue_growth,
            "earnings_growth": fund.earnings_growth,
            "profit_margin": fund.profit_margin,
            "return_on_equity": fund.return_on_equity,
            "free_cash_flow": fund.free_cash_flow,
            "analyst_recommendation": fund.recommendation,
            "analyst_target_price": fund.target_price,
            "signals": fund.signals,
        },
        "technical": {
            "current_price": tech.current_price,
            "sma_20": tech.sma_20,
            "sma_50": tech.sma_50,
            "sma_200": tech.sma_200,
            "rsi_14": tech.rsi_14,
            "avg_volume_20d": tech.avg_volume_20d,
            "volume_ratio": tech.volume_ratio,
            "vs_52w_high_pct": tech.price_vs_52w_high_pct,
            "vs_52w_low_pct": tech.price_vs_52w_low_pct,
            "signals": tech.signals,
        },
    }, indent=2)


# ─── Risk & Volatility ──────────────────────────────────────────────────────

@mcp.tool()
def risk_profile(symbol: str) -> str:
    """Risk analytics — volatility, beta, Sharpe, Sortino, max drawdown, VaR.

    The risk desk's view. Use this before recommending any position to understand
    downside exposure. Essential for sizing positions properly.
    """
    from ai_stock_picker.risk import risk_analysis

    risk = risk_analysis(symbol)
    return json.dumps({
        "symbol": risk.symbol,
        "volatility_annual": risk.volatility_annual,
        "beta_vs_spy": risk.beta,
        "sharpe_ratio": risk.sharpe_ratio,
        "sortino_ratio": risk.sortino_ratio,
        "max_drawdown_pct": risk.max_drawdown_pct,
        "value_at_risk_95_daily": risk.var_95,
        "avg_daily_return": risk.avg_daily_return,
        "win_rate": risk.win_rate,
        "signals": risk.signals,
    }, indent=2)


# ─── Momentum & Rotation ────────────────────────────────────────────────────

@mcp.tool()
def momentum_check(symbol: str) -> str:
    """Momentum analysis — returns, relative strength, breakout proximity, trend.

    What the trading desk checks before market open. Shows 1w/1m/3m/6m/YTD returns,
    relative strength vs S&P 500, and whether momentum is accelerating or fading.
    """
    from ai_stock_picker.momentum import momentum_scan

    m = momentum_scan(symbol)
    return json.dumps({
        "symbol": m.symbol,
        "return_1w": m.return_1w,
        "return_1m": m.return_1m,
        "return_3m": m.return_3m,
        "return_6m": m.return_6m,
        "return_ytd": m.return_ytd,
        "relative_strength_vs_spy_3m": m.relative_strength_vs_spy,
        "pct_from_52w_high": m.breakout_proximity_pct,
        "above_200sma": m.above_200sma,
        "price_acceleration": m.price_acceleration,
        "signals": m.signals,
    }, indent=2)


@mcp.tool()
def sector_rotation() -> str:
    """Sector rotation scan — which sectors are leading and lagging.

    Shows 1-week, 1-month, and 3-month returns for all 11 GICS sectors via ETFs.
    This is how macro desks decide where to allocate capital.
    Use this to identify hot/cold sectors before picking individual stocks.
    """
    from ai_stock_picker.momentum import sector_rotation_scan

    results = sector_rotation_scan()
    return json.dumps(results, indent=2)


@mcp.tool()
def find_breakouts(sector: str | None = None, top_n: int = 10) -> str:
    """Find stocks near 52-week highs with volume confirmation — breakout candidates.

    Classic institutional screen: stocks within 5% of their 52w high that have
    above-average recent volume. These are potential breakout plays.

    Args:
        sector: Optional sector filter (e.g., "Information Technology").
        top_n: Number of candidates to return.
    """
    from ai_stock_picker.momentum import find_breakout_candidates

    results = find_breakout_candidates(sector=sector, top_n=top_n)
    return json.dumps(results, indent=2)


# ─── Earnings Intelligence ───────────────────────────────────────────────────

@mcp.tool()
def earnings_intel(symbol: str) -> str:
    """Earnings intelligence — upcoming dates, beat/miss history, surprise trends.

    CRITICAL to check before any position. Shows next earnings date, last 4 quarters
    of EPS surprises, beat/miss streak, and revenue/earnings growth.
    Never recommend a stock without knowing when earnings are.
    """
    from ai_stock_picker.earnings import earnings_analysis

    e = earnings_analysis(symbol)
    return json.dumps({
        "symbol": e.symbol,
        "name": e.name,
        "next_earnings_date": e.next_earnings_date,
        "days_until_earnings": e.days_until_earnings,
        "last_eps_actual": e.last_eps_actual,
        "last_eps_estimate": e.last_eps_estimate,
        "last_surprise_pct": e.last_surprise_pct,
        "quarterly_revenue_growth": e.quarterly_revenue_growth,
        "quarterly_earnings_growth": e.quarterly_earnings_growth,
        "earnings_history_last_4q": e.earnings_history,
        "signals": e.signals,
    }, indent=2)


# ─── Comparison & Portfolio ──────────────────────────────────────────────────

@mcp.tool()
def compare_stocks(symbols: list[str]) -> str:
    """Head-to-head stock comparison — value, growth, risk, momentum dimensions.

    Use when the user is choosing between 2-5 stocks. Runs full analysis on each
    and identifies the best in each category with an overall verdict.

    Args:
        symbols: List of 2-5 ticker symbols to compare (e.g., ["AAPL", "MSFT", "GOOGL"]).
    """
    from ai_stock_picker.compare import compare_stocks as _compare

    result = _compare(symbols)
    return json.dumps({
        "stocks": result.stocks,
        "best_value": result.best_value,
        "best_growth": result.best_growth,
        "best_risk_adjusted": result.best_risk_adjusted,
        "best_momentum": result.best_momentum,
        "verdict": result.verdict,
    }, indent=2)


@mcp.tool()
def portfolio_builder(
    symbols: list[str],
    budget: float,
    strategy: str = "equal_weight",
) -> str:
    """Build a portfolio allocation with share counts.

    Given a list of stocks and a budget, calculates how many shares to buy.

    Args:
        symbols: List of ticker symbols.
        budget: Total investment amount in dollars.
        strategy: Allocation strategy —
            "equal_weight" (default): Equal dollar amount per stock.
            "risk_parity": More to low-volatility stocks, less to high-vol.
            "momentum_tilt": Overweight recent winners.
    """
    from ai_stock_picker.compare import portfolio_allocation

    alloc = portfolio_allocation(symbols, budget, strategy)
    total = sum(a["actual_cost"] for a in alloc)
    remaining = budget - total

    return json.dumps({
        "strategy": strategy,
        "budget": budget,
        "allocation": alloc,
        "total_invested": round(total, 2),
        "cash_remaining": round(remaining, 2),
    }, indent=2)


# ─── Stock Picking (Original) ───────────────────────────────────────────────

@mcp.tool()
def suggest_stocks(
    sectors: list[str] | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    budget: float | None = None,
    top_n: int = 5,
) -> str:
    """AI stock picker — screens, analyzes, and ranks the best picks.

    Scans the S&P 500 universe, filters by your criteria, runs fundamental +
    technical analysis, and returns scored picks with reasoning.

    Args:
        sectors: Filter by GICS sectors (e.g., ["Information Technology", "Health Care"]).
        max_price: Maximum price per share.
        min_price: Minimum price per share.
        budget: Total investment budget.
        top_n: Number of picks (default 5).
    """
    from ai_stock_picker.suggest import suggest_stocks as _suggest

    picks = _suggest(
        sectors=sectors,
        max_price=max_price,
        min_price=min_price,
        budget=budget,
        top_n=top_n,
    )

    return json.dumps([{
        "symbol": p.symbol,
        "name": p.name,
        "price": p.price,
        "sector": p.sector,
        "score": p.score,
        "reasons": p.reasons,
    } for p in picks], indent=2)


@mcp.tool()
def list_sectors() -> str:
    """List all 11 GICS sectors and their stock counts in the S&P 500."""
    from ai_stock_picker.sp500 import SP500_BY_SECTOR
    return json.dumps({
        sector: {"count": len(tickers), "sample": tickers[:5]}
        for sector, tickers in SP500_BY_SECTOR.items()
    }, indent=2)


# ─── Legendary Trader Strategies ─────────────────────────────────────────────

@mcp.tool()
def daily_briefing() -> str:
    """MORNING BRIEFING — start every day with this.

    Analyzes today's market conditions and recommends which legendary trader's
    strategy to follow. Then runs that strategy and gives you actionable picks.

    This is the single most important tool. Use it first thing.
    """
    from ai_stock_picker.strategies import TRADER_STRATEGIES
    from ai_stock_picker.strategies.selector import pick_todays_strategy
    import dataclasses

    rec = pick_todays_strategy()

    # Run the primary strategy
    primary_info = TRADER_STRATEGIES[rec.primary]
    result = primary_info["func"]()

    return json.dumps({
        "todays_strategy": {
            "primary": primary_info["name"],
            "primary_key": rec.primary,
            "secondary": TRADER_STRATEGIES[rec.secondary]["name"],
            "secondary_key": rec.secondary,
            "reasoning": rec.reasoning,
        },
        "market_conditions": rec.market_conditions,
        "strategy_result": dataclasses.asdict(result),
    }, indent=2, default=str)


@mcp.tool()
def run_strategy(trader: str) -> str:
    """Run a specific legendary trader's strategy.

    Args:
        trader: One of: "soros", "simons", "jones", "paulson", "dalio", "livermore", "kotegawa"

    Strategies:
    - soros: Macro thesis — find the big trend and bet on it
    - simons: Quantitative — statistical edges, remove emotion
    - jones: Technical + macro — follow trends with discipline
    - paulson: Contrarian — what is the crowd wrong about?
    - dalio: All-weather — balanced portfolio for any environment
    - livermore: Momentum — ride winners, cut losers
    - kotegawa: Crash buying — buy the blood, mean reversion
    """
    import dataclasses
    from ai_stock_picker.strategies import TRADER_STRATEGIES

    trader = trader.lower()
    if trader not in TRADER_STRATEGIES:
        return json.dumps({"error": f"Unknown trader. Choose from: {list(TRADER_STRATEGIES.keys())}"})

    info = TRADER_STRATEGIES[trader]
    result = info["func"]()

    return json.dumps({
        "trader": info["name"],
        "style": info["style"],
        "best_when": info["best_when"],
        "result": dataclasses.asdict(result),
    }, indent=2, default=str)


@mcp.tool()
def all_strategies_summary() -> str:
    """List all 7 legendary trader strategies with their styles.

    Use this to help the user understand which strategy fits their personality
    or current market conditions.
    """
    from ai_stock_picker.strategies import TRADER_STRATEGIES

    return json.dumps([{
        "key": key,
        "name": info["name"],
        "style": info["style"],
        "best_when": info["best_when"],
    } for key, info in TRADER_STRATEGIES.items()], indent=2)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
