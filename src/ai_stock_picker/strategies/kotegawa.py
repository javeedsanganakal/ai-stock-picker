"""Takashi Kotegawa Strategy — Crash Buying / Mean Reversion.

The legendary Japanese day trader who turned $13,000 into $150 million.
His approach: buy stocks that have crashed hard and fast, expecting a bounce.

Kotegawa looks for:
- Stocks down 10-20%+ in a short period (1-5 days)
- High volume on the selloff (capitulation = sellers exhausted)
- Stock was healthy before the crash (not a broken company)
- Quick bounce back expected — hold hours to days, not weeks
"""

from dataclasses import dataclass

from ai_stock_picker.market_data import get_stock_history, get_stock_info
from ai_stock_picker.analysis import fundamental_analysis, technical_analysis
from ai_stock_picker.sp500 import SP500_ALL


@dataclass
class KotegawaSetup:
    symbol: str
    name: str
    price: float
    drop_1w_pct: float
    drop_1m_pct: float
    rsi: float | None
    volume_spike: float | None
    was_healthy: bool
    bounce_target: str
    reason: str


@dataclass
class KotegawaScreen:
    crash_candidates: list[KotegawaSetup]
    market_fear_level: str  # "extreme_fear", "fear", "neutral", "greedy"
    kotegawa_would_say: str


def _market_fear() -> str:
    """Simple fear gauge based on SPY recent action."""
    try:
        hist = get_stock_history("SPY", period="1mo")
        close = hist["Close"]
        r1w = float((close.iloc[-1] / close.iloc[-5] - 1) * 100) if len(close) >= 5 else 0
        r1m = float((close.iloc[-1] / close.iloc[0] - 1) * 100) if len(close) > 1 else 0

        if r1w < -5:
            return "extreme_fear"
        elif r1w < -2 or r1m < -5:
            return "fear"
        elif r1w > 3:
            return "greedy"
        else:
            return "neutral"
    except Exception:
        return "neutral"


def kotegawa_reversal_scan(universe: list[str] | None = None) -> KotegawaScreen:
    """Think like Kotegawa: find the crashes and buy the bounce.

    Scans the S&P 500 for stocks that have dropped sharply but have
    solid fundamentals — oversold bounces in quality names.
    """
    symbols = universe or SP500_ALL
    candidates = []
    fear = _market_fear()

    for sym in symbols:
        try:
            hist = get_stock_history(sym, period="3mo")
            if len(hist) < 20:
                continue

            close = hist["Close"]
            volume = hist["Volume"]
            current = float(close.iloc[-1])

            # 1-week and 1-month drops
            r1w = float((current / float(close.iloc[-5]) - 1) * 100) if len(close) >= 5 else 0
            r1m = float((current / float(close.iloc[-21]) - 1) * 100) if len(close) >= 21 else 0

            # Kotegawa wants sharp drops — at least -8% in a week or -15% in a month
            if r1w > -5 and r1m > -12:
                continue

            # Volume spike on the selloff (capitulation signal)
            avg_vol = float(volume.rolling(20).mean().iloc[-1])
            recent_vol = float(volume.iloc[-5:].mean())
            vol_spike = recent_vol / avg_vol if avg_vol > 0 else 1

            # Was it healthy before? Check fundamentals
            fund = fundamental_analysis(sym)
            healthy = True
            health_points = 0
            if fund.profit_margin and fund.profit_margin > 0.05:
                health_points += 1
            if fund.revenue_growth and fund.revenue_growth > -0.05:
                health_points += 1
            if fund.debt_to_equity and fund.debt_to_equity < 150:
                health_points += 1
            if fund.return_on_equity and fund.return_on_equity > 0.05:
                health_points += 1

            healthy = health_points >= 2

            if not healthy:
                continue  # Kotegawa avoids broken companies

            # RSI
            tech = technical_analysis(sym)

            # Bounce target: previous support level (20-day SMA)
            sma20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else current * 1.05
            bounce_pct = (sma20 - current) / current * 100

            candidates.append(KotegawaSetup(
                symbol=sym,
                name=fund.name,
                price=current,
                drop_1w_pct=round(r1w, 2),
                drop_1m_pct=round(r1m, 2),
                rsi=tech.rsi_14,
                volume_spike=round(vol_spike, 2),
                was_healthy=healthy,
                bounce_target=f"Target 20-SMA at ${sma20:.0f} (+{bounce_pct:.0f}%)",
                reason=f"Down {r1w:.0f}% this week, {r1m:.0f}% this month. Healthy company. Vol spike {vol_spike:.1f}x.",
            ))

        except Exception:
            continue

    # Sort by severity of drop (most crashed first)
    candidates.sort(key=lambda x: x.drop_1w_pct)
    candidates = candidates[:10]

    # Kotegawa's take
    if fear == "extreme_fear" and candidates:
        says = (
            f"Blood in the streets. {len(candidates)} quality names have crashed. "
            f"This is my moment. Buy the fear. But size small per position — "
            f"spread across multiple names. Quick in, quick out."
        )
    elif candidates:
        says = (
            f"Found {len(candidates)} selloff candidates. Not full panic yet, "
            f"but some names are oversold. Pick the ones with strongest fundamentals "
            f"and highest volume spikes — that's where capitulation happened."
        )
    else:
        says = (
            "No crashes to buy right now. The market hasn't given us the setup. "
            "Patience. The $13,000 to $150 million came from waiting for the RIGHT crashes."
        )

    return KotegawaScreen(
        crash_candidates=candidates,
        market_fear_level=fear,
        kotegawa_would_say=says,
    )
