"""Earnings intelligence — upcoming earnings, surprises, and guidance."""

from dataclasses import dataclass
from datetime import datetime, timedelta

import yfinance as yf


@dataclass
class EarningsSnapshot:
    symbol: str
    name: str
    next_earnings_date: str | None
    days_until_earnings: int | None
    last_eps_actual: float | None
    last_eps_estimate: float | None
    last_surprise_pct: float | None  # positive = beat
    quarterly_revenue_growth: float | None
    quarterly_earnings_growth: float | None
    earnings_history: list[dict]  # last 4 quarters
    signals: list[str]


def earnings_analysis(symbol: str) -> EarningsSnapshot:
    """Earnings intel — what the desk checks before any position."""
    ticker = yf.Ticker(symbol)
    info = ticker.info
    signals = []

    # Next earnings date
    try:
        cal = ticker.calendar
        if cal is not None and not (hasattr(cal, 'empty') and cal.empty):
            if isinstance(cal, dict):
                next_date = cal.get("Earnings Date", [None])[0] if "Earnings Date" in cal else None
            else:
                next_date = None
        else:
            next_date = None
    except Exception:
        next_date = None

    next_earnings_str = None
    days_until = None
    if next_date:
        if hasattr(next_date, 'date'):
            next_earnings_str = str(next_date.date())
            days_until = (next_date.date() - datetime.now().date()).days
        else:
            next_earnings_str = str(next_date)

    # Earnings history (last 4 quarters)
    earnings_hist = []
    try:
        eh = ticker.earnings_dates
        if eh is not None and not eh.empty:
            for idx, row in eh.head(8).iterrows():
                eps_est = row.get("EPS Estimate")
                eps_act = row.get("Reported EPS")
                surprise = row.get("Surprise(%)")
                if eps_act is not None and not (isinstance(eps_act, float) and eps_act != eps_act):
                    earnings_hist.append({
                        "date": str(idx.date()) if hasattr(idx, 'date') else str(idx),
                        "eps_estimate": float(eps_est) if eps_est == eps_est else None,
                        "eps_actual": float(eps_act) if eps_act == eps_act else None,
                        "surprise_pct": float(surprise) if surprise == surprise else None,
                    })
    except Exception:
        pass

    # Latest surprise
    last_eps_actual = None
    last_eps_est = None
    last_surprise = None
    if earnings_hist:
        latest = earnings_hist[0]
        last_eps_actual = latest.get("eps_actual")
        last_eps_est = latest.get("eps_estimate")
        last_surprise = latest.get("surprise_pct")

    rev_growth = info.get("revenueGrowth")
    earn_growth = info.get("earningsGrowth")

    # Signals
    if days_until is not None:
        if 0 < days_until <= 14:
            signals.append(f"EARNINGS IN {days_until} DAYS — high vol event approaching")
        elif days_until is not None and days_until <= 0:
            signals.append("Just reported earnings — check for post-earnings drift")

    # Check beat/miss streak
    beats = sum(1 for e in earnings_hist[:4] if e.get("surprise_pct") and e["surprise_pct"] > 0)
    misses = sum(1 for e in earnings_hist[:4] if e.get("surprise_pct") and e["surprise_pct"] < 0)

    if beats >= 3:
        signals.append(f"Earnings beat streak ({beats}/4 quarters) — consistent execution")
    elif misses >= 3:
        signals.append(f"Earnings miss streak ({misses}/4 quarters) — execution concerns")

    if last_surprise is not None:
        if last_surprise > 10:
            signals.append(f"Big earnings beat last quarter (+{last_surprise:.1f}%)")
        elif last_surprise < -10:
            signals.append(f"Big earnings miss last quarter ({last_surprise:.1f}%)")

    if rev_growth and rev_growth > 0.2:
        signals.append(f"Strong revenue growth ({rev_growth:.0%}) — top-line momentum")
    elif rev_growth and rev_growth < -0.05:
        signals.append(f"Revenue declining ({rev_growth:.0%}) — structural concern")

    if earn_growth and earn_growth > 0.25:
        signals.append(f"Earnings growing {earn_growth:.0%} — strong bottom-line")

    return EarningsSnapshot(
        symbol=symbol.upper(),
        name=info.get("shortName", symbol),
        next_earnings_date=next_earnings_str,
        days_until_earnings=days_until,
        last_eps_actual=last_eps_actual,
        last_eps_estimate=last_eps_est,
        last_surprise_pct=last_surprise,
        quarterly_revenue_growth=rev_growth,
        quarterly_earnings_growth=earn_growth,
        earnings_history=earnings_hist[:4],
        signals=signals,
    )
