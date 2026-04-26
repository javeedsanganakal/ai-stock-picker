"""Fetch market data using yfinance."""

from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import yfinance as yf


@dataclass
class StockSnapshot:
    symbol: str
    name: str
    price: float
    change_pct: float
    volume: int
    market_cap: float | None
    pe_ratio: float | None
    sector: str | None
    industry: str | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None
    dividend_yield: float | None
    timestamp: datetime


def get_stock_info(symbol: str) -> StockSnapshot:
    """Get current snapshot for a single stock."""
    ticker = yf.Ticker(symbol)
    info = ticker.info

    price = info.get("currentPrice") or info.get("regularMarketPrice", 0.0)
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose", 0.0)
    change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0

    return StockSnapshot(
        symbol=symbol.upper(),
        name=info.get("shortName", symbol),
        price=price,
        change_pct=round(change_pct, 2),
        volume=info.get("volume") or info.get("regularMarketVolume", 0),
        market_cap=info.get("marketCap"),
        pe_ratio=info.get("trailingPE"),
        sector=info.get("sector"),
        industry=info.get("industry"),
        fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
        fifty_two_week_low=info.get("fiftyTwoWeekLow"),
        dividend_yield=info.get("dividendYield"),
        timestamp=datetime.now(),
    )


def get_stock_history(symbol: str, period: str = "6mo") -> pd.DataFrame:
    """Get historical price data.

    Args:
        symbol: Stock ticker symbol.
        period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max).
    """
    ticker = yf.Ticker(symbol)
    return ticker.history(period=period)


def get_multiple_stocks(symbols: list[str]) -> list[StockSnapshot]:
    """Get snapshots for multiple stocks."""
    results = []
    for symbol in symbols:
        try:
            results.append(get_stock_info(symbol))
        except Exception:
            continue
    return results


# Common stock universes for screening
SP500_TOP_50 = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "BRK-B", "LLY", "TSM", "AVGO",
    "JPM", "UNH", "V", "XOM", "MA", "COST", "HD", "PG", "JNJ", "ABBV",
    "MRK", "ORCL", "BAC", "CRM", "NFLX", "AMD", "CVX", "KO", "TMO", "PEP",
    "LIN", "ACN", "MCD", "CSCO", "ADBE", "ABT", "WMT", "DHR", "TXN", "PM",
    "NEE", "INTC", "DIS", "VZ", "CMCSA", "RTX", "BMY", "QCOM", "HON", "UNP",
]

SECTORS = [
    "Technology", "Healthcare", "Financial Services", "Consumer Cyclical",
    "Communication Services", "Industrials", "Consumer Defensive",
    "Energy", "Utilities", "Real Estate", "Basic Materials",
]
