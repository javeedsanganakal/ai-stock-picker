"""Ray Dalio Strategy — All-Weather Principles-Based Investing.

"He who lives by the crystal ball will eat shattered glass."

Dalio looks for:
- Balance across environments (growth up/down, inflation up/down)
- Risk parity — equalize risk contribution, not dollar amounts
- Systematic rules, not gut feelings
- Diversification that actually works (uncorrelated assets)
"""

from dataclasses import dataclass

from ai_stock_picker.analysis import fundamental_analysis
from ai_stock_picker.risk import risk_analysis
from ai_stock_picker.momentum import sector_rotation_scan
from ai_stock_picker.sp500 import SP500_BY_SECTOR


@dataclass
class DalioAllocation:
    symbol: str
    name: str
    sector: str
    role: str  # "growth", "defensive", "inflation_hedge", "stability"
    weight_pct: float
    beta: float
    sharpe: float
    reason: str


@dataclass
class DalioPortfolio:
    allocations: list[DalioAllocation]
    environment_assessment: str
    portfolio_beta: float
    portfolio_strategy: str
    dalio_would_say: str


def dalio_allweather(budget: float = 10000) -> DalioPortfolio:
    """Think like Dalio: build a portfolio that survives any environment.

    The All-Weather approach:
    - Growth assets (tech, discretionary) for rising growth
    - Defensive assets (staples, healthcare, utilities) for falling growth
    - Inflation hedges (energy, materials) for rising inflation
    - Stability anchors (low-beta blue chips) for everything else

    Risk parity: allocate MORE to low-volatility assets, LESS to high-volatility.
    """
    # Assess current environment from sector rotation
    sectors = sector_rotation_scan()
    sector_perf = {s["sector"]: s for s in sectors}

    # Classify environment
    growth_sectors = ["Information Technology", "Consumer Discretionary", "Communication Services"]
    defensive_sectors = ["Consumer Staples", "Health Care", "Utilities"]
    inflation_sectors = ["Energy", "Materials"]

    growth_avg = sum(sector_perf.get(s, {}).get("return_1m", 0) for s in growth_sectors) / 3
    defensive_avg = sum(sector_perf.get(s, {}).get("return_1m", 0) for s in defensive_sectors) / 3
    inflation_avg = sum(sector_perf.get(s, {}).get("return_1m", 0) for s in inflation_sectors) / 2

    if growth_avg > defensive_avg and growth_avg > inflation_avg:
        environment = "Growth rising — risk appetite is healthy"
    elif inflation_avg > growth_avg:
        environment = "Inflation trade active — commodities and real assets leading"
    elif defensive_avg > growth_avg:
        environment = "Defensive rotation — market pricing in slowdown"
    else:
        environment = "Mixed signals — true all-weather allocation needed"

    # Build balanced portfolio: pick 1-2 strong stocks per bucket
    buckets = {
        "growth": {
            "sectors": ["Information Technology", "Consumer Discretionary"],
            "target_weight": 0.30,
            "role": "growth",
        },
        "defensive": {
            "sectors": ["Consumer Staples", "Health Care"],
            "target_weight": 0.30,
            "role": "defensive",
        },
        "inflation_hedge": {
            "sectors": ["Energy", "Materials"],
            "target_weight": 0.15,
            "role": "inflation_hedge",
        },
        "stability": {
            "sectors": ["Utilities", "Financials"],
            "target_weight": 0.25,
            "role": "stability",
        },
    }

    allocations = []

    for bucket_name, config in buckets.items():
        candidates = []
        for sector in config["sectors"]:
            tickers = SP500_BY_SECTOR.get(sector, [])[:8]
            for sym in tickers:
                try:
                    risk = risk_analysis(sym, period="6mo")
                    fund = fundamental_analysis(sym)

                    # Dalio wants: low vol, good Sharpe, strong fundamentals
                    score = risk.sharpe_ratio * 2 - risk.volatility_annual
                    if fund.profit_margin and fund.profit_margin > 0.1:
                        score += 0.5
                    if fund.debt_to_equity and fund.debt_to_equity < 80:
                        score += 0.3

                    candidates.append({
                        "symbol": sym,
                        "name": fund.name,
                        "sector": sector,
                        "beta": risk.beta,
                        "sharpe": risk.sharpe_ratio,
                        "volatility": risk.volatility_annual,
                        "score": score,
                    })
                except Exception:
                    continue

        # Pick best 1-2 from this bucket
        candidates.sort(key=lambda x: x["score"], reverse=True)
        picks = candidates[:2]

        for i, pick in enumerate(picks):
            weight = config["target_weight"] / len(picks)
            allocations.append(DalioAllocation(
                symbol=pick["symbol"],
                name=pick["name"],
                sector=pick["sector"],
                role=config["role"],
                weight_pct=round(weight * 100, 1),
                beta=pick["beta"],
                sharpe=pick["sharpe"],
                reason=f"{bucket_name.replace('_', ' ').title()} bucket — Sharpe {pick['sharpe']:.2f}, Beta {pick['beta']:.2f}",
            ))

    # Portfolio-level beta
    portfolio_beta = sum(a.beta * a.weight_pct / 100 for a in allocations) if allocations else 1.0

    says = (
        f"Current environment: {environment}. "
        f"But we don't predict — we prepare. This portfolio is designed to perform "
        f"reasonably well in all four quadrants: growth up, growth down, inflation up, inflation down. "
        f"Portfolio beta is {portfolio_beta:.2f}. "
        f"'Diversifying well is the most important thing you need to do in order to invest well.'"
    )

    return DalioPortfolio(
        allocations=allocations,
        environment_assessment=environment,
        portfolio_beta=round(portfolio_beta, 3),
        portfolio_strategy="Risk-parity inspired all-weather allocation across growth, defensive, inflation, and stability buckets",
        dalio_would_say=says,
    )
