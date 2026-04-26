"""Risk analytics — volatility, beta, Sharpe ratio, drawdown, VaR."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import yfinance as yf

from .market_data import get_stock_history


@dataclass
class RiskProfile:
    symbol: str
    volatility_annual: float  # annualized std dev of returns
    beta: float  # vs SPY
    sharpe_ratio: float  # risk-adjusted return (rf=4.5%)
    sortino_ratio: float  # downside risk-adjusted return
    max_drawdown_pct: float  # worst peak-to-trough decline
    var_95: float  # 95% Value at Risk (daily)
    avg_daily_return: float
    win_rate: float  # % of positive days
    signals: list[str]


def _daily_returns(hist: pd.DataFrame) -> pd.Series:
    return hist["Close"].pct_change().dropna()


def _max_drawdown(close: pd.Series) -> float:
    peak = close.cummax()
    drawdown = (close - peak) / peak
    return float(drawdown.min()) * 100


def risk_analysis(symbol: str, period: str = "1y", risk_free_rate: float = 0.045) -> RiskProfile:
    """Full risk profile for a stock.

    Args:
        symbol: Ticker symbol.
        period: Lookback period.
        risk_free_rate: Annual risk-free rate (default 4.5% — current T-bill).
    """
    hist = get_stock_history(symbol, period=period)
    if len(hist) < 30:
        raise ValueError(f"Not enough data for {symbol}")

    returns = _daily_returns(hist)
    close = hist["Close"]

    # Basic stats
    avg_daily = float(returns.mean())
    std_daily = float(returns.std())
    trading_days = 252

    # Annualized volatility
    vol_annual = std_daily * np.sqrt(trading_days)

    # Beta vs S&P 500
    spy_hist = get_stock_history("SPY", period=period)
    spy_returns = _daily_returns(spy_hist)
    # Align dates
    aligned = pd.DataFrame({"stock": returns, "spy": spy_returns}).dropna()
    if len(aligned) > 20:
        cov = np.cov(aligned["stock"], aligned["spy"])
        beta = cov[0, 1] / cov[1, 1] if cov[1, 1] != 0 else 1.0
    else:
        beta = 1.0

    # Sharpe ratio
    excess_daily = avg_daily - risk_free_rate / trading_days
    sharpe = (excess_daily / std_daily * np.sqrt(trading_days)) if std_daily > 0 else 0

    # Sortino ratio (only downside deviation)
    downside = returns[returns < 0]
    downside_std = float(downside.std()) if len(downside) > 0 else std_daily
    sortino = (excess_daily / downside_std * np.sqrt(trading_days)) if downside_std > 0 else 0

    # Max drawdown
    max_dd = _max_drawdown(close)

    # VaR 95%
    var_95 = float(np.percentile(returns, 5))

    # Win rate
    win_rate = float((returns > 0).sum() / len(returns))

    # Signals
    signals = []
    if vol_annual < 0.15:
        signals.append(f"Low volatility ({vol_annual:.0%}) — defensive stock")
    elif vol_annual > 0.40:
        signals.append(f"High volatility ({vol_annual:.0%}) — aggressive/speculative")
    else:
        signals.append(f"Moderate volatility ({vol_annual:.0%})")

    if beta < 0.8:
        signals.append(f"Low beta ({beta:.2f}) — less sensitive to market moves")
    elif beta > 1.3:
        signals.append(f"High beta ({beta:.2f}) — amplifies market moves")
    else:
        signals.append(f"Beta {beta:.2f} — moves roughly with the market")

    if sharpe > 1.5:
        signals.append(f"Excellent risk-adjusted returns (Sharpe {sharpe:.2f})")
    elif sharpe > 0.8:
        signals.append(f"Good risk-adjusted returns (Sharpe {sharpe:.2f})")
    elif sharpe < 0:
        signals.append(f"Negative Sharpe ({sharpe:.2f}) — underperforming risk-free rate")

    if max_dd < -30:
        signals.append(f"Severe max drawdown ({max_dd:.1f}%) — significant downside risk")
    elif max_dd < -15:
        signals.append(f"Moderate max drawdown ({max_dd:.1f}%)")

    if win_rate > 0.55:
        signals.append(f"High win rate ({win_rate:.0%} of days positive)")

    return RiskProfile(
        symbol=symbol.upper(),
        volatility_annual=round(vol_annual, 4),
        beta=round(beta, 3),
        sharpe_ratio=round(sharpe, 3),
        sortino_ratio=round(sortino, 3),
        max_drawdown_pct=round(max_dd, 2),
        var_95=round(var_95, 4),
        avg_daily_return=round(avg_daily, 5),
        win_rate=round(win_rate, 4),
        signals=signals,
    )
