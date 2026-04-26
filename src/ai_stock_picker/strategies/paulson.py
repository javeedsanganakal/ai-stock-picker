"""John Paulson Strategy — Contrarian Asymmetric Bets.

"Many investors make the mistake of buying high and selling low while
the exact opposite is required to outperform the market."

Paulson looks for:
- What the crowd is wrong about
- Massive risk/reward asymmetry (small downside, huge upside)
- Beaten-down quality stocks (strong fundamentals + terrible price action)
- Sectors everyone hates — that's where the opportunity is
"""

from dataclasses import dataclass

from ai_stock_picker.analysis import fundamental_analysis
from ai_stock_picker.momentum import momentum_scan, sector_rotation_scan
from ai_stock_picker.risk import risk_analysis
from ai_stock_picker.sp500 import SP500_BY_SECTOR


@dataclass
class PaulsonBet:
    symbol: str
    sector: str
    price_decline: float  # % from 52w high
    pe_ratio: float | None
    quality_score: str  # "high_quality", "decent", "speculative"
    asymmetry: str  # description of the risk/reward
    reason: str


@dataclass
class PaulsonScreen:
    hated_sectors: list[dict]
    contrarian_picks: list[PaulsonBet]
    paulson_would_say: str


def paulson_contrarian_scan() -> PaulsonScreen:
    """Think like Paulson: find what everyone hates and ask 'are they wrong?'

    Scans for:
    1. Most hated sectors (worst 1-month performance)
    2. Quality stocks in those sectors (good fundamentals, bad price)
    3. Asymmetric setups (strong balance sheet + oversold = mispriced)
    """
    # Step 1: Find the most hated sectors
    sectors = sector_rotation_scan()
    hated = sectors[-3:]  # worst performing

    # Step 2: Dig into hated sectors for quality names
    contrarian_picks = []

    for sector_data in hated:
        sector_name = sector_data["sector"]
        tickers = SP500_BY_SECTOR.get(sector_name, [])

        for sym in tickers[:12]:
            try:
                m = momentum_scan(sym)
                fund = fundamental_analysis(sym)

                # Only interested if stock is significantly down
                if m.breakout_proximity_pct > -15:
                    continue

                # Quality check: is this a good company having a bad time?
                quality = "speculative"
                quality_points = 0
                if fund.profit_margin and fund.profit_margin > 0.1:
                    quality_points += 1
                if fund.debt_to_equity and fund.debt_to_equity < 100:
                    quality_points += 1
                if fund.return_on_equity and fund.return_on_equity > 0.1:
                    quality_points += 1
                if fund.revenue_growth and fund.revenue_growth > 0:
                    quality_points += 1
                if fund.recommendation in ("buy", "strong_buy"):
                    quality_points += 1

                if quality_points >= 4:
                    quality = "high_quality"
                elif quality_points >= 2:
                    quality = "decent"
                else:
                    continue  # skip low quality

                # Asymmetry: how much upside vs analyst target?
                upside = ""
                if fund.target_price and fund.target_price > 0:
                    pct_upside = (fund.target_price - m.return_1m) / fund.target_price * 100
                    upside = f"Analyst target implies significant recovery potential"

                contrarian_picks.append(PaulsonBet(
                    symbol=sym,
                    sector=sector_name,
                    price_decline=m.breakout_proximity_pct,
                    pe_ratio=fund.pe_ratio,
                    quality_score=quality,
                    asymmetry=upside or f"Down {m.breakout_proximity_pct:.0f}% with {quality} fundamentals",
                    reason=f"{quality.replace('_', ' ').title()} company down {m.breakout_proximity_pct:.0f}% from highs in hated {sector_name} sector",
                ))

            except Exception:
                continue

    # Sort: high quality first, then by magnitude of decline
    contrarian_picks.sort(key=lambda x: (x.quality_score != "high_quality", x.price_decline))
    contrarian_picks = contrarian_picks[:8]

    # Paulson's take
    hated_names = [s["sector"] for s in hated]
    if any(p.quality_score == "high_quality" for p in contrarian_picks):
        says = (
            f"The market hates {', '.join(hated_names)}. But there are quality names being "
            f"thrown out with the bathwater. 'Buy when there's blood in the streets.' — "
            f"just make sure the balance sheet can survive."
        )
    else:
        says = (
            f"Sectors under pressure: {', '.join(hated_names)}. But I'm not seeing strong "
            f"quality at a discount yet. Paulson would say: 'Be patient. The big asymmetric "
            f"trades don't come every day.'"
        )

    return PaulsonScreen(
        hated_sectors=hated,
        contrarian_picks=contrarian_picks,
        paulson_would_say=says,
    )
