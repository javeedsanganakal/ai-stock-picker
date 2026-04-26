"""Jim Simons Strategy — Quantitative/Statistical Edge.

"We search through historical data looking for anomalous patterns
that we would not expect to occur at random."

Simons looks for:
- Statistical anomalies in price patterns
- Mean reversion signals (RSI extremes + low volatility = setup)
- Volume anomalies — unusual activity precedes moves
- Risk-adjusted returns, not raw returns — Sharpe is king
"""

from dataclasses import dataclass

import numpy as np

from ai_stock_picker.market_data import get_stock_history
from ai_stock_picker.analysis import technical_analysis
from ai_stock_picker.risk import risk_analysis
from ai_stock_picker.sp500 import SP500_ALL


@dataclass
class SimonsSignal:
    symbol: str
    setup_type: str  # "mean_reversion", "momentum_anomaly", "volume_spike"
    confidence: float  # 0-1
    sharpe: float
    rsi: float | None
    volume_anomaly: float | None
    expected_edge: str


@dataclass
class SimonsScreen:
    signals: list[SimonsSignal]
    market_regime: str  # "trending", "mean_reverting", "choppy"
    simons_would_say: str


def _detect_regime(spy_hist) -> str:
    """Detect market regime using autocorrelation of returns."""
    close = spy_hist["Close"]
    returns = close.pct_change().dropna()
    if len(returns) < 30:
        return "choppy"

    # Autocorrelation of daily returns
    r1 = float(returns.autocorr(lag=1))
    r5 = float(returns.autocorr(lag=5))

    if r1 > 0.05 and r5 > 0.03:
        return "trending"
    elif r1 < -0.05:
        return "mean_reverting"
    else:
        return "choppy"


def simons_quant_screen(universe: list[str] | None = None) -> SimonsScreen:
    """Think like Simons: find statistical edges, not stories.

    Scans for:
    1. Mean reversion setups (RSI < 30 with low vol = bounce candidate)
    2. Momentum anomalies (strong trend + good Sharpe = ride it)
    3. Volume spikes (unusual volume = something is happening)
    """
    symbols = universe or SP500_ALL[:100]  # scan top 100 for speed
    signals = []

    # Detect market regime
    spy_hist = get_stock_history("SPY", period="3mo")
    regime = _detect_regime(spy_hist)

    for sym in symbols:
        try:
            tech = technical_analysis(sym)
            risk = risk_analysis(sym, period="6mo")

            # Setup 1: Mean reversion — oversold + low vol
            if tech.rsi_14 and tech.rsi_14 < 30 and risk.volatility_annual < 0.35:
                signals.append(SimonsSignal(
                    symbol=sym,
                    setup_type="mean_reversion",
                    confidence=min(0.9, (30 - tech.rsi_14) / 30 + 0.3),
                    sharpe=risk.sharpe_ratio,
                    rsi=tech.rsi_14,
                    volume_anomaly=tech.volume_ratio,
                    expected_edge=f"RSI {tech.rsi_14:.0f} oversold, vol {risk.volatility_annual:.0%} manageable — statistical bounce expected",
                ))

            # Setup 2: Momentum anomaly — high Sharpe + trending
            elif risk.sharpe_ratio > 1.5 and tech.rsi_14 and 40 < tech.rsi_14 < 70:
                signals.append(SimonsSignal(
                    symbol=sym,
                    setup_type="momentum_anomaly",
                    confidence=min(0.85, risk.sharpe_ratio / 3),
                    sharpe=risk.sharpe_ratio,
                    rsi=tech.rsi_14,
                    volume_anomaly=tech.volume_ratio,
                    expected_edge=f"Sharpe {risk.sharpe_ratio:.2f} — abnormally good risk-adjusted returns, trend intact",
                ))

            # Setup 3: Volume spike with price move
            elif tech.volume_ratio and tech.volume_ratio > 2.5:
                signals.append(SimonsSignal(
                    symbol=sym,
                    setup_type="volume_spike",
                    confidence=min(0.7, tech.volume_ratio / 5),
                    sharpe=risk.sharpe_ratio,
                    rsi=tech.rsi_14,
                    volume_anomaly=tech.volume_ratio,
                    expected_edge=f"Volume {tech.volume_ratio:.1f}x normal — unusual activity, information asymmetry likely",
                ))

        except Exception:
            continue

    signals.sort(key=lambda s: s.confidence, reverse=True)
    signals = signals[:10]

    if regime == "mean_reverting":
        says = "Market is mean-reverting. Favor RSI oversold setups. The math says fade extremes."
    elif regime == "trending":
        says = "Market is trending. Favor momentum anomalies. Don't fight the trend — ride it with size proportional to Sharpe."
    else:
        says = "Market is choppy. Reduce position sizes. When the signal is weak, bet small."

    return SimonsScreen(
        signals=signals,
        market_regime=regime,
        simons_would_say=says,
    )
