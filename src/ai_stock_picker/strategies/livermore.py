"""Jesse Livermore Strategy — Momentum & Pyramiding.

"It never was my thinking that made the big money for me. It always was my sitting.
Got that? My sitting tight!"

Livermore looks for:
- Stocks making new highs on heavy volume — the leaders
- Pyramid into winners (add to positions that are working)
- Cut losers immediately — never average down
- The path of least resistance — trade with the trend
"""

from dataclasses import dataclass

from ai_stock_picker.momentum import momentum_scan, find_breakout_candidates
from ai_stock_picker.analysis import technical_analysis
from ai_stock_picker.risk import risk_analysis
from ai_stock_picker.sp500 import SP500_ALL


@dataclass
class LivermorePlay:
    symbol: str
    price: float
    pct_from_52w_high: float
    return_1m: float
    return_3m: float
    volume_signal: str
    trend_strength: str
    pyramid_plan: str
    reason: str


@dataclass
class LivermoreScreen:
    market_direction: str
    leaders: list[LivermorePlay]
    livermore_would_say: str


def livermore_momentum_scan() -> LivermoreScreen:
    """Think like Livermore: find the leaders and ride them.

    Scans for:
    1. Stocks at or near 52-week highs (leaders, not laggards)
    2. Volume confirmation (heavy volume on up days = institutional buying)
    3. Accelerating momentum (getting stronger, not weaker)
    """
    # Market direction
    spy_m = momentum_scan("SPY")
    if spy_m.return_1m > 3 and spy_m.above_200sma:
        market = "Bullish — market trending up. Go long the leaders aggressively."
    elif spy_m.return_1m < -3:
        market = "Bearish — market weak. Livermore would be flat or short. Cash is a position."
    else:
        market = "Neutral — wait for a clear direction before committing capital."

    # Find breakout candidates (near 52w highs with volume)
    breakouts = find_breakout_candidates(top_n=20)

    leaders = []
    for b in breakouts:
        sym = b["symbol"]
        try:
            m = momentum_scan(sym)
            tech = technical_analysis(sym)

            # Livermore only wants the strongest
            if m.return_3m < 5:
                continue

            # Volume signal
            vol_sig = "neutral"
            if tech.volume_ratio and tech.volume_ratio > 1.5:
                vol_sig = f"Heavy volume ({tech.volume_ratio:.1f}x) — institutions are buying"
            elif tech.volume_ratio and tech.volume_ratio < 0.7:
                vol_sig = "Low volume breakout — less conviction, smaller position"

            # Trend strength
            if m.price_acceleration == "accelerating" and m.return_1m > m.return_3m / 3:
                trend = "Accelerating — strongest signal"
            elif m.above_200sma and m.return_3m > 10:
                trend = "Strong uptrend"
            else:
                trend = "Moderate trend"

            # Pyramid plan (Livermore-style: 1/4, 1/4, 1/4, 1/4)
            pyramid = (
                f"Entry: ${tech.current_price:.0f}. "
                f"Add at +2%: ${tech.current_price * 1.02:.0f}. "
                f"Add at +4%: ${tech.current_price * 1.04:.0f}. "
                f"Stop: ${tech.current_price * 0.95:.0f} (-5%)"
            )

            leaders.append(LivermorePlay(
                symbol=sym,
                price=tech.current_price,
                pct_from_52w_high=b["pct_from_52w_high"],
                return_1m=m.return_1m,
                return_3m=m.return_3m,
                volume_signal=vol_sig,
                trend_strength=trend,
                pyramid_plan=pyramid,
                reason=f"Near 52w high ({b['pct_from_52w_high']:+.1f}%), 3m return +{m.return_3m:.0f}%, momentum {m.price_acceleration}",
            ))

        except Exception:
            continue

    leaders = leaders[:8]

    if leaders:
        says = (
            f"I see {len(leaders)} leaders near new highs. "
            f"'A stock is never too high to buy or too low to sell.' "
            f"The market tells you which stocks are the leaders — buy them. "
            f"But remember: 'Cut your losses quickly. Let your profits run.'"
        )
    else:
        says = (
            "'There is a time to go long, a time to go short, and a time to go fishing.' "
            "I don't see clear leaders right now. Stay in cash and wait."
        )

    return LivermoreScreen(
        market_direction=market,
        leaders=leaders,
        livermore_would_say=says,
    )
