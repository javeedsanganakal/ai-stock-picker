"""Trading strategy modules — each modeled after a legendary trader."""

from .soros import soros_macro_scan
from .simons import simons_quant_screen
from .jones import jones_technical_scan
from .paulson import paulson_contrarian_scan
from .dalio import dalio_allweather
from .livermore import livermore_momentum_scan
from .kotegawa import kotegawa_reversal_scan
from .selector import pick_todays_strategy

TRADER_STRATEGIES = {
    "soros": {
        "name": "George Soros — Macro Thesis",
        "style": "Find the big macro trend and bet heavily on it",
        "best_when": "Major macro shifts — rate changes, currency moves, geopolitical events",
        "func": soros_macro_scan,
    },
    "simons": {
        "name": "Jim Simons — Quantitative Edge",
        "style": "Pure numbers. Statistical patterns. Remove all emotion",
        "best_when": "Normal market conditions with mean-reverting patterns",
        "func": simons_quant_screen,
    },
    "jones": {
        "name": "Paul Tudor Jones — Technical Macro",
        "style": "Chart patterns + macro awareness. Trend following with conviction",
        "best_when": "Strong trends forming or reversing",
        "func": jones_technical_scan,
    },
    "paulson": {
        "name": "John Paulson — Contrarian Asymmetry",
        "style": "What is the crowd wrong about? Where is the asymmetric bet?",
        "best_when": "Market extremes — euphoria or panic",
        "func": paulson_contrarian_scan,
    },
    "dalio": {
        "name": "Ray Dalio — All-Weather Principles",
        "style": "Systematic. Balanced. Survive any environment",
        "best_when": "Uncertainty — when you don't know what's coming",
        "func": dalio_allweather,
    },
    "livermore": {
        "name": "Jesse Livermore — Momentum Master",
        "style": "Ride the winners. Cut the losers. Pyramid into strength",
        "best_when": "Trending markets with clear winners emerging",
        "func": livermore_momentum_scan,
    },
    "kotegawa": {
        "name": "Takashi Kotegawa — Crash Buyer",
        "style": "Buy the blood. Aggressive mean reversion on oversold names",
        "best_when": "Selloffs, panics, and individual stock crashes",
        "func": kotegawa_reversal_scan,
    },
}
