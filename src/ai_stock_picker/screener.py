"""Stock screener — filter stocks by various criteria."""

from dataclasses import dataclass, field

from .market_data import StockSnapshot, get_multiple_stocks, SP500_TOP_50
from .sp500 import SP500_ALL, SP500_BY_SECTOR


@dataclass
class ScreenCriteria:
    """Criteria for filtering stocks."""

    sectors: list[str] = field(default_factory=list)
    min_price: float | None = None
    max_price: float | None = None
    min_market_cap: float | None = None
    max_market_cap: float | None = None
    min_pe: float | None = None
    max_pe: float | None = None
    min_dividend_yield: float | None = None
    min_volume: int | None = None


def _matches(stock: StockSnapshot, criteria: ScreenCriteria) -> bool:
    """Check if a stock matches all given criteria."""
    if criteria.sectors and stock.sector not in criteria.sectors:
        return False
    if criteria.min_price is not None and stock.price < criteria.min_price:
        return False
    if criteria.max_price is not None and stock.price > criteria.max_price:
        return False
    if criteria.min_market_cap is not None and (stock.market_cap or 0) < criteria.min_market_cap:
        return False
    if criteria.max_market_cap is not None and (stock.market_cap or 0) > criteria.max_market_cap:
        return False
    if criteria.min_pe is not None and (stock.pe_ratio or 0) < criteria.min_pe:
        return False
    if criteria.max_pe is not None and (stock.pe_ratio is None or stock.pe_ratio > criteria.max_pe):
        return False
    if criteria.min_dividend_yield is not None and (
        stock.dividend_yield or 0
    ) < criteria.min_dividend_yield:
        return False
    if criteria.min_volume is not None and stock.volume < criteria.min_volume:
        return False
    return True


def screen_stocks(
    criteria: ScreenCriteria,
    universe: list[str] | None = None,
) -> list[StockSnapshot]:
    """Screen stocks from a universe based on criteria.

    Args:
        criteria: Filtering criteria.
        universe: List of ticker symbols to screen. Defaults to S&P 500 top 50.

    Returns:
        List of stocks matching all criteria.
    """
    # If sectors specified and no custom universe, narrow to those sector tickers
    if not universe and criteria.sectors:
        symbols = []
        for sector in criteria.sectors:
            symbols.extend(SP500_BY_SECTOR.get(sector, []))
        if not symbols:
            symbols = SP500_TOP_50  # fallback
    else:
        symbols = universe or SP500_TOP_50
    stocks = get_multiple_stocks(symbols)
    return [s for s in stocks if _matches(s, criteria)]
