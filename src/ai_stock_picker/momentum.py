"""Momentum & relative strength — the bread and butter of desk trading."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .market_data import get_stock_history
from .sp500 import SP500_BY_SECTOR, get_sector_tickers


@dataclass
class MomentumReport:
    symbol: str
    return_1w: float
    return_1m: float
    return_3m: float
    return_6m: float
    return_ytd: float
    relative_strength_vs_spy: float  # 3m return vs SPY 3m return
    breakout_proximity_pct: float  # how close to 52w high
    above_200sma: bool
    price_acceleration: str  # "accelerating", "decelerating", "steady"
    signals: list[str]


def _period_return(close: pd.Series, days: int) -> float | None:
    if len(close) < days:
        return None
    return float((close.iloc[-1] / close.iloc[-days] - 1) * 100)


def momentum_scan(symbol: str) -> MomentumReport:
    """Momentum analysis — what a JPM desk looks at before market open."""
    hist = get_stock_history(symbol, period="1y")
    if len(hist) < 50:
        raise ValueError(f"Not enough data for {symbol}")

    close = hist["Close"]
    current = float(close.iloc[-1])

    # Returns over various periods
    r1w = _period_return(close, 5)
    r1m = _period_return(close, 21)
    r3m = _period_return(close, 63)
    r6m = _period_return(close, 126)

    # YTD return
    this_year = close[close.index >= f"{pd.Timestamp.now().year}-01-01"]
    r_ytd = float((current / float(this_year.iloc[0]) - 1) * 100) if len(this_year) > 1 else 0

    # Relative strength vs SPY
    spy_hist = get_stock_history("SPY", period="1y")
    spy_close = spy_hist["Close"]
    spy_3m = _period_return(spy_close, 63) or 0
    rs_vs_spy = (r3m or 0) - spy_3m

    # Breakout proximity
    high_52w = float(close.max())
    breakout_pct = (current - high_52w) / high_52w * 100

    # 200 SMA
    sma200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None
    above_200 = current > sma200 if sma200 else True

    # Price acceleration (is momentum increasing or fading?)
    if r1m is not None and r3m is not None:
        monthly_pace = r1m
        quarterly_monthly_pace = (r3m or 0) / 3
        if monthly_pace > quarterly_monthly_pace * 1.3:
            accel = "accelerating"
        elif monthly_pace < quarterly_monthly_pace * 0.7:
            accel = "decelerating"
        else:
            accel = "steady"
    else:
        accel = "steady"

    # Signals
    signals = []
    if r1w and r1w > 5:
        signals.append(f"Hot this week (+{r1w:.1f}%) — watch for continuation or pullback")
    elif r1w and r1w < -5:
        signals.append(f"Sold off this week ({r1w:.1f}%) — watch for reversal or more downside")

    if rs_vs_spy > 10:
        signals.append(f"Strong relative strength vs S&P 500 (+{rs_vs_spy:.1f}pp)")
    elif rs_vs_spy < -10:
        signals.append(f"Weak relative strength vs S&P 500 ({rs_vs_spy:.1f}pp)")

    if breakout_pct > -2:
        signals.append(f"Near 52-week high ({breakout_pct:+.1f}%) — breakout territory")
    elif breakout_pct < -25:
        signals.append(f"Deep below 52-week high ({breakout_pct:.1f}%) — beaten down")

    if accel == "accelerating":
        signals.append("Momentum accelerating — recent gains outpacing trend")
    elif accel == "decelerating":
        signals.append("Momentum decelerating — gains slowing down")

    if not above_200:
        signals.append("Below 200-day SMA — long-term downtrend")

    if r_ytd > 30:
        signals.append(f"Strong YTD performer (+{r_ytd:.1f}%)")
    elif r_ytd < -15:
        signals.append(f"YTD laggard ({r_ytd:.1f}%)")

    return MomentumReport(
        symbol=symbol.upper(),
        return_1w=round(r1w or 0, 2),
        return_1m=round(r1m or 0, 2),
        return_3m=round(r3m or 0, 2),
        return_6m=round(r6m or 0, 2),
        return_ytd=round(r_ytd, 2),
        relative_strength_vs_spy=round(rs_vs_spy, 2),
        breakout_proximity_pct=round(breakout_pct, 2),
        above_200sma=above_200,
        price_acceleration=accel,
        signals=signals,
    )


def sector_rotation_scan() -> list[dict]:
    """Sector rotation analysis — which sectors are leading/lagging.

    This is how macro desks decide where to allocate.
    Returns sectors ranked by 1-month performance.
    """
    import yfinance as yf

    sector_etfs = {
        "Information Technology": "XLK",
        "Health Care": "XLV",
        "Financials": "XLF",
        "Consumer Discretionary": "XLY",
        "Communication Services": "XLC",
        "Industrials": "XLI",
        "Consumer Staples": "XLP",
        "Energy": "XLE",
        "Utilities": "XLU",
        "Real Estate": "XLRE",
        "Materials": "XLB",
    }

    results = []
    for sector, etf in sector_etfs.items():
        try:
            hist = get_stock_history(etf, period="6mo")
            close = hist["Close"]
            r1m = _period_return(close, 21) or 0
            r3m = _period_return(close, 63) or 0
            r1w = _period_return(close, 5) or 0

            results.append({
                "sector": sector,
                "etf": etf,
                "return_1w": round(r1w, 2),
                "return_1m": round(r1m, 2),
                "return_3m": round(r3m, 2),
            })
        except Exception:
            continue

    results.sort(key=lambda x: x["return_1m"], reverse=True)
    return results


def find_breakout_candidates(sector: str | None = None, top_n: int = 10) -> list[dict]:
    """Find stocks near 52-week highs — potential breakout candidates.

    Classic JPM equity desk screen: stocks within 5% of 52w high with
    volume confirmation.
    """
    from .sp500 import SP500_ALL

    universe = get_sector_tickers(sector) if sector else SP500_ALL
    candidates = []

    for symbol in universe:
        try:
            hist = get_stock_history(symbol, period="1y")
            if len(hist) < 50:
                continue
            close = hist["Close"]
            volume = hist["Volume"]
            current = float(close.iloc[-1])
            high_52w = float(close.max())
            pct_from_high = (current - high_52w) / high_52w * 100

            # Within 5% of 52w high
            if pct_from_high < -5:
                continue

            # Volume confirmation: recent volume above average
            avg_vol = float(volume.rolling(20).mean().iloc[-1])
            recent_vol = float(volume.iloc[-5:].mean())
            vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1

            r1m = _period_return(close, 21) or 0

            candidates.append({
                "symbol": symbol,
                "price": round(current, 2),
                "pct_from_52w_high": round(pct_from_high, 2),
                "return_1m": round(r1m, 2),
                "volume_ratio": round(vol_ratio, 2),
            })
        except Exception:
            continue

    candidates.sort(key=lambda x: x["pct_from_52w_high"], reverse=True)
    return candidates[:top_n]
