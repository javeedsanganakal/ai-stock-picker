"""Full S&P 500 universe organized by GICS sector."""

SP500_BY_SECTOR: dict[str, list[str]] = {
    "Communication Services": [
        "CHTR", "CMCSA", "DIS", "EA", "FOX", "FOXA", "GOOG", "GOOGL", "LYV", "META",
        "NFLX", "NWS", "NWSA", "OMC", "T", "TKO", "TMUS", "TTD", "TTWO", "VZ", "WBD",
    ],
    "Consumer Discretionary": [
        "ABNB", "AMZN", "APTV", "AZO", "BBY", "BKNG", "CCL", "CMG", "CVNA", "DASH",
        "DECK", "DHI", "DPZ", "DRI", "EBAY", "EXPE", "F", "GM", "GPC", "GRMN", "HAS",
        "HD", "HLT", "LEN", "LOW", "LULU", "LVS", "MAR", "MCD", "MGM", "NCLH", "NKE",
        "NVR", "ORLY", "PHM", "POOL", "RCL", "RL", "ROST", "SBUX", "TJX", "TPR", "TSCO",
        "TSLA", "ULTA", "WSM", "WYNN", "YUM",
    ],
    "Consumer Staples": [
        "ADM", "BF-B", "BG", "CAG", "CASY", "CHD", "CL", "CLX", "COST", "CPB", "DG",
        "DLTR", "EL", "GIS", "HRL", "HSY", "KDP", "KHC", "KMB", "KO", "KR", "KVUE",
        "MDLZ", "MKC", "MNST", "MO", "PEP", "PG", "PM", "SJM", "STZ", "SYY", "TAP",
        "TGT", "TSN", "WMT",
    ],
    "Energy": [
        "APA", "BKR", "COP", "CTRA", "CVX", "DVN", "EOG", "EQT", "EXE", "FANG", "HAL",
        "KMI", "MPC", "OKE", "OXY", "PSX", "SLB", "TPL", "TRGP", "VLO", "WMB", "XOM",
    ],
    "Financials": [
        "ACGL", "AFL", "AIG", "AIZ", "AJG", "ALL", "AMP", "AON", "APO", "ARES", "AXP",
        "BAC", "BEN", "BK", "BLK", "BRK-B", "BRO", "BX", "C", "CB", "CBOE", "CFG",
        "CINF", "CME", "COF", "COIN", "CPAY", "EG", "ERIE", "FDS", "FIS", "FISV",
        "FITB", "GL", "GPN", "GS", "HBAN", "HIG", "HOOD", "IBKR", "ICE", "IVZ", "JKHY",
        "JPM", "KEY", "KKR", "L", "MA", "MCO", "MET", "MS", "MSCI", "MTB", "NDAQ",
        "NTRS", "PFG", "PGR", "PNC", "PRU", "PYPL", "RF", "RJF", "SCHW", "SPGI", "STT",
        "SYF", "TFC", "TROW", "TRV", "USB", "V", "WFC", "WRB", "WTW",
    ],
    "Health Care": [
        "A", "ABBV", "ABT", "ALGN", "AMGN", "BAX", "BDX", "BIIB", "BMY", "BSX", "CAH",
        "CI", "CNC", "COO", "COR", "CRL", "CVS", "DGX", "DHR", "DVA", "DXCM", "ELV",
        "EW", "GEHC", "GILD", "HCA", "HSIC", "HUM", "IDXX", "INCY", "IQV", "ISRG",
        "JNJ", "LH", "LLY", "MCK", "MDT", "MRK", "MRNA", "MTD", "PFE", "PODD", "REGN",
        "RMD", "RVTY", "SOLV", "STE", "SYK", "TECH", "TMO", "UHS", "UNH", "VRTX",
        "VTRS", "WAT", "WST", "ZBH", "ZTS",
    ],
    "Industrials": [
        "ADP", "ALLE", "AME", "AOS", "AXON", "BA", "BLDR", "BR", "CARR", "CAT", "CHRW",
        "CMI", "CPRT", "CSX", "CTAS", "DAL", "DE", "DOV", "EFX", "EME", "EMR", "ETN",
        "EXPD", "FAST", "FDX", "FIX", "FTV", "GD", "GE", "GEV", "GNRC", "GWW", "HII",
        "HON", "HUBB", "HWM", "IEX", "IR", "ITW", "J", "JBHT", "JCI", "LDOS", "LHX",
        "LII", "LMT", "LUV", "MAS", "MMM", "NDSN", "NOC", "NSC", "ODFL", "OTIS", "PAYX",
        "PCAR", "PH", "PNR", "PWR", "ROK", "ROL", "RSG", "RTX", "SNA", "SWK", "TDG",
        "TT", "TXT", "UAL", "UBER", "UNP", "UPS", "URI", "VLTO", "VRSK", "VRT", "WAB",
        "WM", "XYL",
    ],
    "Information Technology": [
        "AAPL", "ACN", "ADBE", "ADI", "ADSK", "AKAM", "AMAT", "AMD", "ANET", "APH",
        "APP", "AVGO", "CDNS", "CDW", "CRM", "CRWD", "CSCO", "CTSH", "DDOG", "DELL",
        "EPAM", "FFIV", "FICO", "FSLR", "FTNT", "GDDY", "GEN", "GLW", "HPE", "HPQ",
        "IBM", "INTC", "INTU", "IT", "JBL", "KEYS", "KLAC", "LRCX", "MCHP", "MPWR",
        "MSFT", "MSI", "MU", "NOW", "NTAP", "NVDA", "NXPI", "ON", "ORCL", "PANW",
        "PLTR", "PTC", "QCOM", "ROP", "SMCI", "SNPS", "STX", "SWKS", "TDY", "TEL",
        "TER", "TRMB", "TXN", "TYL", "VRSN", "WDAY", "WDC", "ZBRA",
    ],
    "Materials": [
        "ALB", "AMCR", "APD", "AVY", "BALL", "CF", "CRH", "CTVA", "DD", "DOW", "ECL",
        "FCX", "IFF", "IP", "LIN", "LYB", "MLM", "MOS", "NEM", "NUE", "PKG", "PPG",
        "SHW", "STLD", "VMC",
    ],
    "Real Estate": [
        "AMT", "ARE", "AVB", "BXP", "CBRE", "CCI", "CPT", "CSGP", "DLR", "DOC", "EQIX",
        "EQR", "ESS", "EXR", "FRT", "HST", "INVH", "IRM", "KIM", "MAA", "O", "PLD",
        "PSA", "REG", "SBAC", "SPG", "UDR", "VICI", "VTR", "WELL", "WY",
    ],
    "Utilities": [
        "AEE", "AEP", "AES", "ATO", "AWK", "CEG", "CMS", "CNP", "D", "DTE", "DUK",
        "ED", "EIX", "ES", "ETR", "EVRG", "EXC", "FE", "LNT", "NEE", "NI", "NRG",
        "PCG", "PEG", "PNW", "PPL", "SO", "SRE", "VST", "WEC", "XEL",
    ],
}

# Flat list of all S&P 500 tickers
SP500_ALL: list[str] = []
for _tickers in SP500_BY_SECTOR.values():
    SP500_ALL.extend(_tickers)

SECTOR_NAMES = list(SP500_BY_SECTOR.keys())


def get_sector_tickers(sector: str) -> list[str]:
    """Get all tickers in a sector."""
    return SP500_BY_SECTOR.get(sector, [])


def get_stock_sector(symbol: str) -> str | None:
    """Look up which sector a stock belongs to."""
    for sector, tickers in SP500_BY_SECTOR.items():
        if symbol.upper() in tickers:
            return sector
    return None
