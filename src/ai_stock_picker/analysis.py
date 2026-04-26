"""Fundamental and technical analysis for stocks."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import yfinance as yf

from .market_data import get_stock_history


@dataclass
class FundamentalReport:
    symbol: str
    name: str
    sector: str | None
    market_cap: float | None
    pe_ratio: float | None
    forward_pe: float | None
    peg_ratio: float | None
    price_to_book: float | None
    debt_to_equity: float | None
    revenue_growth: float | None
    earnings_growth: float | None
    profit_margin: float | None
    return_on_equity: float | None
    free_cash_flow: float | None
    recommendation: str | None
    target_price: float | None
    signals: list[str]


@dataclass
class TechnicalReport:
    symbol: str
    current_price: float
    sma_20: float | None
    sma_50: float | None
    sma_200: float | None
    rsi_14: float | None
    avg_volume_20d: float | None
    volume_ratio: float | None  # current vol / avg vol
    price_vs_52w_high_pct: float | None
    price_vs_52w_low_pct: float | None
    signals: list[str]


def fundamental_analysis(symbol: str) -> FundamentalReport:
    """Run fundamental analysis on a stock."""
    ticker = yf.Ticker(symbol)
    info = ticker.info
    signals = []

    pe = info.get("trailingPE")
    forward_pe = info.get("forwardPE")
    peg = info.get("pegRatio")
    debt_eq = info.get("debtToEquity")
    profit_margin = info.get("profitMargins")
    roe = info.get("returnOnEquity")
    rev_growth = info.get("revenueGrowth")
    earn_growth = info.get("earningsGrowth")

    # Generate signals
    if pe and pe < 15:
        signals.append("Low P/E ratio — potentially undervalued")
    elif pe and pe > 30:
        signals.append("High P/E ratio — priced for growth or overvalued")

    if peg and peg < 1:
        signals.append("PEG < 1 — growth looks cheap relative to earnings")

    if debt_eq and debt_eq < 50:
        signals.append("Low debt-to-equity — strong balance sheet")
    elif debt_eq and debt_eq > 200:
        signals.append("High debt-to-equity — leverage risk")

    if profit_margin and profit_margin > 0.2:
        signals.append(f"Strong profit margin ({profit_margin:.0%})")

    if roe and roe > 0.2:
        signals.append(f"Strong return on equity ({roe:.0%})")

    if rev_growth and rev_growth > 0.15:
        signals.append(f"Strong revenue growth ({rev_growth:.0%})")
    elif rev_growth and rev_growth < 0:
        signals.append(f"Revenue declining ({rev_growth:.0%})")

    if earn_growth and earn_growth > 0.2:
        signals.append(f"Strong earnings growth ({earn_growth:.0%})")

    rec = info.get("recommendationKey")
    if rec:
        signals.append(f"Analyst consensus: {rec}")

    return FundamentalReport(
        symbol=symbol.upper(),
        name=info.get("shortName", symbol),
        sector=info.get("sector"),
        market_cap=info.get("marketCap"),
        pe_ratio=pe,
        forward_pe=forward_pe,
        peg_ratio=peg,
        price_to_book=info.get("priceToBook"),
        debt_to_equity=debt_eq,
        revenue_growth=rev_growth,
        earnings_growth=earn_growth,
        profit_margin=profit_margin,
        return_on_equity=roe,
        free_cash_flow=info.get("freeCashflow"),
        recommendation=rec,
        target_price=info.get("targetMeanPrice"),
        signals=signals,
    )


def _compute_rsi(series: pd.Series, period: int = 14) -> float | None:
    """Compute RSI for a price series."""
    if len(series) < period + 1:
        return None
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean().iloc[-1]
    avg_loss = loss.rolling(window=period).mean().iloc[-1]
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def technical_analysis(symbol: str) -> TechnicalReport:
    """Run technical analysis on a stock."""
    hist = get_stock_history(symbol, period="1y")
    if hist.empty:
        raise ValueError(f"No historical data for {symbol}")

    close = hist["Close"]
    volume = hist["Volume"]
    current_price = float(close.iloc[-1])
    signals = []

    sma_20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else None
    sma_50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
    sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None

    rsi = _compute_rsi(close)

    avg_vol_20 = float(volume.rolling(20).mean().iloc[-1]) if len(volume) >= 20 else None
    current_vol = float(volume.iloc[-1])
    vol_ratio = round(current_vol / avg_vol_20, 2) if avg_vol_20 and avg_vol_20 > 0 else None

    high_52w = float(close.max())
    low_52w = float(close.min())
    pct_from_high = round((current_price - high_52w) / high_52w * 100, 2)
    pct_from_low = round((current_price - low_52w) / low_52w * 100, 2)

    # Generate signals
    if sma_50 and sma_200 and sma_50 > sma_200:
        signals.append("Golden cross — 50-day SMA above 200-day (bullish)")
    elif sma_50 and sma_200 and sma_50 < sma_200:
        signals.append("Death cross — 50-day SMA below 200-day (bearish)")

    if sma_20 and current_price > sma_20:
        signals.append("Price above 20-day SMA (short-term bullish)")
    elif sma_20:
        signals.append("Price below 20-day SMA (short-term bearish)")

    if rsi is not None:
        if rsi > 70:
            signals.append(f"RSI {rsi} — overbought territory")
        elif rsi < 30:
            signals.append(f"RSI {rsi} — oversold territory (potential buy)")
        else:
            signals.append(f"RSI {rsi} — neutral")

    if vol_ratio and vol_ratio > 2.0:
        signals.append(f"Volume spike ({vol_ratio}x average) — high activity")

    if pct_from_high > -5:
        signals.append(f"Near 52-week high ({pct_from_high:+.1f}%)")
    elif pct_from_high < -20:
        signals.append(f"Well below 52-week high ({pct_from_high:+.1f}%) — potential value")

    return TechnicalReport(
        symbol=symbol.upper(),
        current_price=round(current_price, 2),
        sma_20=round(sma_20, 2) if sma_20 else None,
        sma_50=round(sma_50, 2) if sma_50 else None,
        sma_200=round(sma_200, 2) if sma_200 else None,
        rsi_14=rsi,
        avg_volume_20d=avg_vol_20,
        volume_ratio=vol_ratio,
        price_vs_52w_high_pct=pct_from_high,
        price_vs_52w_low_pct=pct_from_low,
        signals=signals,
    )
