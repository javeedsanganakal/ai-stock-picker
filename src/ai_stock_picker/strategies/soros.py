"""George Soros Strategy — Macro Thesis Trading.

"It's not whether you're right or wrong, but how much money you make
when you're right and how much you lose when you're wrong."

Soros looks for:
- Major macro dislocations (interest rates, currencies, policy shifts)
- Reflexivity — when market perception creates its own reality
- Sectors that benefit/suffer from macro shifts
- Conviction sizing — bet BIG when the thesis is right
"""

from dataclasses import dataclass

from ai_stock_picker.momentum import sector_rotation_scan, momentum_scan
from ai_stock_picker.risk import risk_analysis
from ai_stock_picker.sp500 import SP500_BY_SECTOR


@dataclass
class SorosInsight:
    macro_thesis: str
    favored_sectors: list[dict]
    avoid_sectors: list[dict]
    top_picks: list[dict]
    conviction_level: str  # "high", "moderate", "low"
    soros_would_say: str


def soros_macro_scan() -> SorosInsight:
    """Think like Soros: what's the big macro picture?

    Scans sector rotation to identify macro trends, then finds
    the stocks that benefit most from those trends.
    """
    # Step 1: Sector rotation tells us the macro story
    sectors = sector_rotation_scan()

    # Top 3 and bottom 3 sectors
    favored = sectors[:3]
    avoid = sectors[-3:]

    # Step 2: Determine macro thesis from sector leadership
    top_sector = favored[0]["sector"] if favored else "Unknown"
    bottom_sector = avoid[-1]["sector"] if avoid else "Unknown"

    thesis_map = {
        "Energy": "Commodity super-cycle / inflation trade — money flowing into real assets",
        "Information Technology": "Risk-on / growth trade — market betting on innovation and AI",
        "Utilities": "Defensive rotation — market pricing in slowdown or rate cuts",
        "Health Care": "Defensive growth — market wants safety with earnings visibility",
        "Financials": "Rate-sensitive trade — banks benefit from higher rates / steeper curve",
        "Consumer Discretionary": "Consumer strength — market believes spending will hold up",
        "Consumer Staples": "Risk-off / defensive — market fleeing to safety",
        "Industrials": "Economic expansion trade — capex cycle ramping up",
        "Materials": "Reflation / infrastructure play — commodity demand rising",
        "Real Estate": "Rate sensitivity — REITS moving on rate expectations",
        "Communication Services": "Growth/tech adjacent — digital economy thesis",
    }

    macro_thesis = thesis_map.get(top_sector, f"{top_sector} leadership suggests shifting macro regime")

    # Step 3: Find best stocks in favored sectors
    top_picks = []
    for sector_data in favored[:2]:
        sector_name = sector_data["sector"]
        tickers = SP500_BY_SECTOR.get(sector_name, [])[:15]  # top 15 by listing order

        for sym in tickers[:8]:
            try:
                m = momentum_scan(sym)
                if m.relative_strength_vs_spy > 5 and m.above_200sma:
                    top_picks.append({
                        "symbol": sym,
                        "sector": sector_name,
                        "return_3m": m.return_3m,
                        "relative_strength": m.relative_strength_vs_spy,
                        "momentum": m.price_acceleration,
                        "reason": f"Strong RS in leading sector ({sector_name})",
                    })
            except Exception:
                continue

        if len(top_picks) >= 5:
            break

    top_picks.sort(key=lambda x: x["relative_strength"], reverse=True)
    top_picks = top_picks[:5]

    # Step 4: Conviction level based on how clear the rotation is
    spread = (favored[0]["return_1m"] - avoid[-1]["return_1m"]) if favored and avoid else 0
    if spread > 10:
        conviction = "high"
        soros_says = f"The macro is screaming. {top_sector} is dominating. Size up. The trend is your friend until it bends."
    elif spread > 5:
        conviction = "moderate"
        soros_says = f"{top_sector} is leading but the signal isn't overwhelming. Position, but keep stops tight."
    else:
        conviction = "low"
        soros_says = "No clear macro trend. Soros would wait. 'The trouble is not in being wrong, but in staying wrong.'"

    return SorosInsight(
        macro_thesis=macro_thesis,
        favored_sectors=favored,
        avoid_sectors=avoid,
        top_picks=top_picks,
        conviction_level=conviction,
        soros_would_say=soros_says,
    )
