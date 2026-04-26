"""Paul Tudor Jones Strategy — Technical Analysis + Macro Awareness.

"The secret to being successful from a trading perspective is to have
an indefatigable and an undying and unquenchable thirst for information."

Jones looks for:
- Trend confirmation via moving averages (200-day is the line in the sand)
- Volume confirming price action
- Risk/reward at least 5:1 before entering
- Macro context — understand WHY the trend exists
"""

from dataclasses import dataclass

from ai_stock_picker.analysis import technical_analysis
from ai_stock_picker.momentum import momentum_scan, sector_rotation_scan
from ai_stock_picker.risk import risk_analysis
from ai_stock_picker.sp500 import SP500_ALL


@dataclass
class JonesSetup:
    symbol: str
    trend: str  # "strong_uptrend", "uptrend", "downtrend", "reversal_candidate"
    sma_alignment: str  # "bullish" (20>50>200), "bearish", "mixed"
    risk_reward: str
    key_level: str  # nearest support/resistance
    reason: str


@dataclass
class JonesScreen:
    market_trend: str
    setups: list[JonesSetup]
    jones_would_say: str


def _sma_alignment(tech) -> str:
    if not all([tech.sma_20, tech.sma_50, tech.sma_200]):
        return "insufficient_data"
    if tech.sma_20 > tech.sma_50 > tech.sma_200:
        return "bullish"
    elif tech.sma_20 < tech.sma_50 < tech.sma_200:
        return "bearish"
    else:
        return "mixed"


def jones_technical_scan(universe: list[str] | None = None) -> JonesScreen:
    """Think like Jones: follow the trend, but know the risk/reward.

    Scans for:
    1. Perfect SMA alignment (20 > 50 > 200) = strong uptrend
    2. Price pulling back to 50-day SMA in an uptrend = buy the dip
    3. Trend reversals — death cross flipping to golden cross
    """
    symbols = universe or SP500_ALL[:80]
    setups = []

    # Market trend via SPY
    spy_tech = technical_analysis("SPY")
    spy_align = _sma_alignment(spy_tech)
    if spy_align == "bullish":
        market_trend = "Bullish — SPY SMAs aligned upward"
    elif spy_align == "bearish":
        market_trend = "Bearish — SPY SMAs aligned downward"
    else:
        market_trend = "Mixed — no clear trend in S&P 500"

    for sym in symbols:
        try:
            tech = technical_analysis(sym)
            m = momentum_scan(sym)
            alignment = _sma_alignment(tech)

            # Setup 1: Strong uptrend with pullback to 50 SMA
            if (alignment == "bullish" and tech.sma_50 and
                    tech.current_price < tech.sma_20 and
                    tech.current_price >= tech.sma_50 * 0.98):
                setups.append(JonesSetup(
                    symbol=sym,
                    trend="uptrend_pullback",
                    sma_alignment=alignment,
                    risk_reward=f"Buy near 50-SMA ${tech.sma_50:.0f}, stop below ${tech.sma_50 * 0.97:.0f}",
                    key_level=f"50-day SMA at ${tech.sma_50:.2f}",
                    reason=f"Bullish SMA stack, pulled back to 50-day — classic Jones entry",
                ))

            # Setup 2: Perfect trend — all SMAs aligned, RSI not overbought
            elif (alignment == "bullish" and tech.rsi_14 and
                    tech.rsi_14 < 65 and m.price_acceleration == "accelerating"):
                setups.append(JonesSetup(
                    symbol=sym,
                    trend="strong_uptrend",
                    sma_alignment=alignment,
                    risk_reward=f"Trend intact, stop below 50-SMA ${tech.sma_50:.0f}" if tech.sma_50 else "Trend intact",
                    key_level=f"20-day SMA at ${tech.sma_20:.2f}" if tech.sma_20 else "N/A",
                    reason=f"Perfect trend + accelerating momentum. RSI {tech.rsi_14:.0f} — room to run",
                ))

            # Setup 3: Potential trend reversal (bearish to bullish crossover)
            elif (alignment == "mixed" and tech.sma_50 and tech.sma_200 and
                    tech.sma_50 > tech.sma_200 and
                    tech.current_price > tech.sma_50 and
                    m.return_1m > 5):
                setups.append(JonesSetup(
                    symbol=sym,
                    trend="reversal_candidate",
                    sma_alignment=alignment,
                    risk_reward=f"New golden cross, stop below 200-SMA ${tech.sma_200:.0f}",
                    key_level=f"200-day SMA at ${tech.sma_200:.2f}",
                    reason=f"Golden cross just formed, price above both — early trend reversal",
                ))

        except Exception:
            continue

    setups = setups[:10]

    if spy_align == "bullish":
        says = "Market is trending up. 'Don't be a hero. Don't have an ego.' — go with the trend. Buy pullbacks to the 50-day."
    elif spy_align == "bearish":
        says = "Market is bearish. 'Losers average losers.' — don't buy dips in a downtrend. Wait for the 200-day to flatten."
    else:
        says = "Market is choppy. Reduce size. 'The most important rule of trading is to play great defense.'"

    return JonesScreen(
        market_trend=market_trend,
        setups=setups,
        jones_would_say=says,
    )
