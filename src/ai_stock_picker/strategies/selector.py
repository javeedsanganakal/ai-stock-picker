"""Strategy Selector — picks the right trader mindset for today's market.

Looks at market conditions and recommends which legendary trader's
approach is most relevant right now.
"""

from dataclasses import dataclass

from ai_stock_picker.momentum import sector_rotation_scan, momentum_scan
from ai_stock_picker.market_data import get_stock_history


@dataclass
class StrategyRecommendation:
    primary: str  # trader key
    secondary: str  # backup trader key
    market_conditions: dict
    reasoning: str


def pick_todays_strategy() -> StrategyRecommendation:
    """Analyze today's market and recommend the best trader mindset.

    Decision tree:
    - Market crashing? → Kotegawa (buy the crash) or Paulson (contrarian)
    - Strong trend? → Livermore (momentum) or Jones (technical)
    - No clear direction? → Dalio (all-weather) or Simons (quant)
    - Macro shift? → Soros (macro thesis)
    """
    spy_hist = get_stock_history("SPY", period="3mo")
    close = spy_hist["Close"]
    volume = spy_hist["Volume"]

    r1w = float((close.iloc[-1] / close.iloc[-5] - 1) * 100) if len(close) >= 5 else 0
    r1m = float((close.iloc[-1] / close.iloc[-21] - 1) * 100) if len(close) >= 21 else 0
    r3m = float((close.iloc[-1] / close.iloc[0] - 1) * 100) if len(close) > 1 else 0

    # Volatility of last 20 days
    returns = close.pct_change().dropna()
    recent_vol = float(returns.iloc[-20:].std()) * (252 ** 0.5) if len(returns) >= 20 else 0.15

    # Volume trend
    avg_vol = float(volume.rolling(20).mean().iloc[-1]) if len(volume) >= 20 else 0
    recent_vol_avg = float(volume.iloc[-5:].mean())
    vol_ratio = recent_vol_avg / avg_vol if avg_vol > 0 else 1

    # Sector dispersion (are sectors moving together or diverging?)
    sectors = sector_rotation_scan()
    if sectors:
        returns_1m = [s["return_1m"] for s in sectors]
        sector_spread = max(returns_1m) - min(returns_1m)
    else:
        sector_spread = 0

    conditions = {
        "spy_1w_return": round(r1w, 2),
        "spy_1m_return": round(r1m, 2),
        "spy_3m_return": round(r3m, 2),
        "annualized_volatility": round(recent_vol, 3),
        "volume_ratio": round(vol_ratio, 2),
        "sector_spread": round(sector_spread, 2),
    }

    # Decision logic
    if r1w < -5:
        # Market crashing
        primary = "kotegawa"
        secondary = "paulson"
        reasoning = (
            f"Market down {r1w:.1f}% this week — crash/selloff conditions. "
            f"Kotegawa's mean reversion is primary (buy the oversold bounce). "
            f"Paulson's contrarian approach is backup (look for quality in the wreckage)."
        )
    elif r1m < -8:
        # Extended decline
        primary = "paulson"
        secondary = "kotegawa"
        reasoning = (
            f"Market down {r1m:.1f}% over the month — extended decline. "
            f"Paulson's contrarian lens is primary (find asymmetric bets in hated sectors). "
            f"Kotegawa backup for any sharp single-stock crashes."
        )
    elif r1m > 5 and r3m > 10:
        # Strong uptrend
        primary = "livermore"
        secondary = "jones"
        reasoning = (
            f"Market up {r1m:.1f}% this month, {r3m:.1f}% over 3 months — strong uptrend. "
            f"Livermore: ride the leaders, pyramid into winners. "
            f"Jones backup: use technical levels for entry timing."
        )
    elif sector_spread > 15:
        # Big sector rotation happening
        primary = "soros"
        secondary = "jones"
        reasoning = (
            f"Sector spread is {sector_spread:.0f}pp — major rotation underway. "
            f"Soros macro lens is primary (identify the macro theme driving rotation). "
            f"Jones backup for technical confirmation of the trend."
        )
    elif recent_vol > 0.25:
        # High volatility, unclear direction
        primary = "simons"
        secondary = "dalio"
        reasoning = (
            f"Volatility elevated at {recent_vol:.0%} annualized. "
            f"Simons' quant approach is primary (find statistical edges in the noise). "
            f"Dalio backup: all-weather allocation if no clear quant signals."
        )
    elif abs(r1m) < 2:
        # Flat/choppy
        primary = "dalio"
        secondary = "simons"
        reasoning = (
            f"Market flat ({r1m:+.1f}% this month) — no clear direction. "
            f"Dalio's all-weather is primary (build a balanced portfolio for any outcome). "
            f"Simons backup: look for mean reversion setups in the chop."
        )
    else:
        # Moderate uptrend
        primary = "jones"
        secondary = "livermore"
        reasoning = (
            f"Market moderately positive ({r1m:+.1f}% this month). "
            f"Jones' technical approach is primary (follow the trend with discipline). "
            f"Livermore backup: if leaders emerge, ride them."
        )

    return StrategyRecommendation(
        primary=primary,
        secondary=secondary,
        market_conditions=conditions,
        reasoning=reasoning,
    )
