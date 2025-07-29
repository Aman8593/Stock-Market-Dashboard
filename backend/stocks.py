# Top 50 US stocks (S&P 50)
US_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "BRK.B", "JPM", "V",
    "UNH", "XOM", "LLY", "AVGO", "JNJ",
    "MA", "PG", "HD", "MRK", "COST",
    "ABBV", "PEP", "CRM", "ADBE", "CVX",
    "WMT", "ACN", "MCD", "BAC", "AMD",
    "TMO", "CSCO", "LIN", "KO", "INTC",
    "NFLX", "ORCL", "ABT", "VZ", "NKE",
    "NEE", "DHR", "TXN", "PM", "QCOM",
    "UPS", "AMGN", "IBM", "LOW", "MS"
]


# Top 50 India stocks (Nifty 50)
INDIA_STOCKS = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS",
    "INFY.NS", "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTIM.NS",
    "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS",
    "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS",
    "SUNPHARMA.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS",
    "TITAN.NS", "TCS.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS"
]


def is_valid_stock(symbol: str) -> bool:
    symbol = symbol.upper()
    return (
        symbol in US_STOCKS or
        symbol in INDIA_STOCKS or
        (symbol + ".NS") in INDIA_STOCKS  # Support cases like RELIANCE -> RELIANCE.NS
    )

