"""Suggestion engine — combines screening and analysis to pick stocks."""

from dataclasses import dataclass, field

from .analysis import fundamental_analysis, technical_analysis, FundamentalReport, TechnicalReport
from .screener import ScreenCriteria, screen_stocks


@dataclass
class StockPick:
    symbol: str
    name: str
    price: float
    sector: str | None
    score: float  # 0-100 composite score
    fundamental: FundamentalReport
    technical: TechnicalReport
    reasons: list[str] = field(default_factory=list)


def _score_stock(fund: FundamentalReport, tech: TechnicalReport) -> tuple[float, list[str]]:
    """Score a stock 0-100 based on fundamental + technical signals."""
    score = 50.0  # start neutral
    reasons = []

    # --- Fundamental scoring ---
    if fund.pe_ratio is not None:
        if fund.pe_ratio < 15:
            score += 8
            reasons.append(f"Attractive P/E of {fund.pe_ratio:.1f}")
        elif fund.pe_ratio > 35:
            score -= 5

    if fund.peg_ratio is not None and fund.peg_ratio < 1:
        score += 7
        reasons.append(f"PEG ratio {fund.peg_ratio:.2f} suggests undervalued growth")

    if fund.debt_to_equity is not None:
        if fund.debt_to_equity < 50:
            score += 5
            reasons.append("Low debt — solid balance sheet")
        elif fund.debt_to_equity > 200:
            score -= 8
            reasons.append("High debt — leverage concern")

    if fund.revenue_growth is not None and fund.revenue_growth > 0.1:
        score += 6
        reasons.append(f"Revenue growing {fund.revenue_growth:.0%}")

    if fund.earnings_growth is not None and fund.earnings_growth > 0.15:
        score += 6
        reasons.append(f"Earnings growing {fund.earnings_growth:.0%}")

    if fund.profit_margin is not None and fund.profit_margin > 0.2:
        score += 5
        reasons.append(f"Strong {fund.profit_margin:.0%} profit margin")

    if fund.return_on_equity is not None and fund.return_on_equity > 0.15:
        score += 5
        reasons.append(f"ROE of {fund.return_on_equity:.0%}")

    if fund.recommendation in ("buy", "strong_buy"):
        score += 5
        reasons.append(f"Analyst consensus: {fund.recommendation}")
    elif fund.recommendation == "sell":
        score -= 5

    if fund.target_price and fund.pe_ratio:
        # Use pe_ratio existence as proxy for having a current price
        pass  # target upside calculated below

    # --- Technical scoring ---
    if tech.rsi_14 is not None:
        if tech.rsi_14 < 30:
            score += 8
            reasons.append(f"RSI {tech.rsi_14} — oversold, potential bounce")
        elif tech.rsi_14 > 70:
            score -= 5
            reasons.append(f"RSI {tech.rsi_14} — overbought, may pull back")

    if tech.sma_50 and tech.sma_200 and tech.sma_50 > tech.sma_200:
        score += 6
        reasons.append("Golden cross (bullish trend)")
    elif tech.sma_50 and tech.sma_200 and tech.sma_50 < tech.sma_200:
        score -= 4

    if tech.sma_20 and tech.current_price > tech.sma_20:
        score += 3

    if tech.price_vs_52w_high_pct is not None and tech.price_vs_52w_high_pct < -20:
        score += 4
        reasons.append(f"{tech.price_vs_52w_high_pct:+.1f}% from 52-week high — potential value")

    if tech.volume_ratio and tech.volume_ratio > 2.0:
        reasons.append(f"High volume activity ({tech.volume_ratio}x avg)")

    # Clamp
    score = max(0.0, min(100.0, score))
    return round(score, 1), reasons


def suggest_stocks(
    sectors: list[str] | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    budget: float | None = None,
    top_n: int = 5,
    universe: list[str] | None = None,
) -> list[StockPick]:
    """Suggest top stocks based on criteria.

    Args:
        sectors: Filter to these sectors (e.g., ["Technology"]).
        max_price: Maximum stock price.
        min_price: Minimum stock price.
        budget: Total budget — used to filter stocks you can afford.
        top_n: Number of picks to return.
        universe: Custom list of tickers to evaluate.

    Returns:
        List of StockPick sorted by score (highest first).
    """
    effective_max_price = max_price
    if budget and not max_price:
        effective_max_price = budget  # at minimum you need 1 share

    criteria = ScreenCriteria(
        sectors=sectors or [],
        min_price=min_price,
        max_price=effective_max_price,
    )

    candidates = screen_stocks(criteria, universe=universe)
    if not candidates:
        return []

    picks = []
    for stock in candidates:
        try:
            fund = fundamental_analysis(stock.symbol)
            tech = technical_analysis(stock.symbol)
            score, reasons = _score_stock(fund, tech)

            # Add target price upside if available
            if fund.target_price and stock.price > 0:
                upside = (fund.target_price - stock.price) / stock.price * 100
                if upside > 10:
                    reasons.append(
                        f"Analyst target ${fund.target_price:.0f} ({upside:+.0f}% upside)"
                    )

            picks.append(
                StockPick(
                    symbol=stock.symbol,
                    name=stock.name,
                    price=stock.price,
                    sector=stock.sector,
                    score=score,
                    fundamental=fund,
                    technical=tech,
                    reasons=reasons,
                )
            )
        except Exception:
            continue

    picks.sort(key=lambda p: p.score, reverse=True)
    return picks[:top_n]
