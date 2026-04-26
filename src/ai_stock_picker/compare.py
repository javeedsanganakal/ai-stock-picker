"""Comparative analysis — head-to-head stock comparison & portfolio construction."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .market_data import get_stock_info, get_stock_history
from .analysis import fundamental_analysis, technical_analysis
from .risk import risk_analysis


@dataclass
class ComparisonResult:
    stocks: list[dict]
    best_value: str
    best_growth: str
    best_risk_adjusted: str
    best_momentum: str
    verdict: str


def compare_stocks(symbols: list[str]) -> ComparisonResult:
    """Head-to-head comparison — the analyst's go-to when a client asks 'which one?'"""
    stocks = []

    for sym in symbols:
        try:
            info = get_stock_info(sym)
            fund = fundamental_analysis(sym)
            risk = risk_analysis(sym)
            hist = get_stock_history(sym, period="3mo")
            close = hist["Close"]
            r3m = float((close.iloc[-1] / close.iloc[0] - 1) * 100) if len(close) > 1 else 0

            stocks.append({
                "symbol": sym.upper(),
                "name": info.name,
                "price": info.price,
                "market_cap": info.market_cap,
                "pe_ratio": info.pe_ratio,
                "peg_ratio": fund.peg_ratio,
                "revenue_growth": fund.revenue_growth,
                "earnings_growth": fund.earnings_growth,
                "profit_margin": fund.profit_margin,
                "debt_to_equity": fund.debt_to_equity,
                "roe": fund.return_on_equity,
                "beta": risk.beta,
                "sharpe": risk.sharpe_ratio,
                "volatility": risk.volatility_annual,
                "max_drawdown": risk.max_drawdown_pct,
                "return_3m": round(r3m, 2),
                "analyst_target": fund.target_price,
                "recommendation": fund.recommendation,
            })
        except Exception:
            continue

    if not stocks:
        return ComparisonResult([], "", "", "", "", "No data available")

    # Find best in each category
    def _best(key, lower_better=False):
        valid = [s for s in stocks if s.get(key) is not None]
        if not valid:
            return stocks[0]["symbol"]
        if lower_better:
            return min(valid, key=lambda s: s[key])["symbol"]
        return max(valid, key=lambda s: s[key])["symbol"]

    best_value = _best("pe_ratio", lower_better=True)
    best_growth = _best("revenue_growth")
    best_risk = _best("sharpe")
    best_mom = _best("return_3m")

    # Build verdict
    winners = {}
    for cat, sym in [("Value", best_value), ("Growth", best_growth),
                     ("Risk-adjusted", best_risk), ("Momentum", best_mom)]:
        winners[sym] = winners.get(sym, [])
        winners[sym].append(cat)

    top = max(winners.items(), key=lambda x: len(x[1]))
    if len(top[1]) >= 3:
        verdict = f"{top[0]} leads in {', '.join(top[1])} — clear winner"
    elif len(top[1]) >= 2:
        verdict = f"{top[0]} leads in {', '.join(top[1])} — slight edge"
    else:
        verdict = "Mixed results — each stock has different strengths"

    return ComparisonResult(
        stocks=stocks,
        best_value=best_value,
        best_growth=best_growth,
        best_risk_adjusted=best_risk,
        best_momentum=best_mom,
        verdict=verdict,
    )


def portfolio_allocation(
    symbols: list[str],
    budget: float,
    strategy: str = "equal_weight",
) -> list[dict]:
    """Simple portfolio allocation.

    Strategies:
        equal_weight: Equal dollar amount per stock.
        risk_parity: Allocate inversely proportional to volatility.
        momentum_tilt: Overweight recent winners.
    """
    n = len(symbols)
    if n == 0:
        return []

    if strategy == "equal_weight":
        weights = {s: 1.0 / n for s in symbols}

    elif strategy == "risk_parity":
        vols = {}
        for sym in symbols:
            try:
                risk = risk_analysis(sym, period="6mo")
                vols[sym] = risk.volatility_annual
            except Exception:
                vols[sym] = 0.25  # default moderate vol
        inv_vols = {s: 1.0 / v if v > 0 else 1.0 for s, v in vols.items()}
        total = sum(inv_vols.values())
        weights = {s: v / total for s, v in inv_vols.items()}

    elif strategy == "momentum_tilt":
        returns = {}
        for sym in symbols:
            try:
                hist = get_stock_history(sym, period="3mo")
                close = hist["Close"]
                r = float(close.iloc[-1] / close.iloc[0] - 1) if len(close) > 1 else 0
                returns[sym] = max(r, 0.01)  # floor at 1% so losers still get some
            except Exception:
                returns[sym] = 0.01
        total = sum(returns.values())
        weights = {s: v / total for s, v in returns.items()}

    else:
        weights = {s: 1.0 / n for s in symbols}

    # Convert to shares and dollars
    allocation = []
    for sym in symbols:
        try:
            info = get_stock_info(sym)
            dollar_amount = budget * weights[sym]
            shares = int(dollar_amount / info.price) if info.price > 0 else 0
            actual_cost = shares * info.price

            allocation.append({
                "symbol": sym.upper(),
                "name": info.name,
                "weight_pct": round(weights[sym] * 100, 1),
                "target_dollars": round(dollar_amount, 2),
                "shares": shares,
                "actual_cost": round(actual_cost, 2),
                "price_per_share": info.price,
            })
        except Exception:
            continue

    return allocation
