# AI Stock Picker

AI-powered stock research and suggestion engine. Screens stocks, runs fundamental + technical analysis, and suggests picks with reasoning.

## Install

```bash
pip install -e .
```

## Usage

### Get stock info
```bash
ai-stock-picker info AAPL
```

### Analyze a stock (fundamental + technical)
```bash
ai-stock-picker analyze NVDA
```

### Get AI-powered suggestions
```bash
# Suggest tech stocks under $200
ai-stock-picker suggest --sector Technology --max-price 200

# Suggest top 3 picks within a $5000 budget
ai-stock-picker suggest --budget 5000 --top 3

# List available sectors
ai-stock-picker sectors
```

### Use as a Python library
```python
from ai_stock_picker.market_data import get_stock_info
from ai_stock_picker.analysis import fundamental_analysis, technical_analysis
from ai_stock_picker.suggest import suggest_stocks

# Get suggestions
picks = suggest_stocks(sectors=["Technology"], max_price=200, top_n=5)
for pick in picks:
    print(f"{pick.symbol}: {pick.score}/100 - {pick.reasons}")
```

## Disclaimer

This tool is for research and educational purposes only. It is not financial advice. Always do your own due diligence before making investment decisions.
