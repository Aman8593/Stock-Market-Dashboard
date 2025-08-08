# Top 50 US stocks (S&P 50)
US_STOCKS = [
    "AAPL","ABBV","ABT","ACN","ADBE","AIG","AMD","AMGN","AMT","AMZN",
    "AVGO","AXP","BA","BAC","BK","BKNG","BLK","BMY","BRK.B","C","CAT",
    "CHTR","CL","CMCSA","COF","COP","COST","CRM","CSCO","CVS","CVX","DE",
    "DHR","DIS","DUK","EMR","FDX","GD","GE","GILD","GM","GOOG","GOOGL",
    "GS","HD","HON","IBM","INTC","INTU","ISRG","JNJ","JPM","KO","LIN",
    "LLY","LMT","LOW","MA","MCD","MDLZ","MDT","MET","META","MMM","MO",
    "MRK","MS","MSFT","NEE","NFLX","NKE","NOW","NVDA","ORCL","PEP","PFE",
    "PG","PLTR","PM","PYPL","QCOM","RTX","SBUX","SCHW","SO","SPG","T",
    "TGT","TMO","TMUS","TSLA","TXN","UNH","UNP","UPS","USB","V","VZ","WFC",
    "WMT","XOM"
]


# Top 50 India stocks (Nifty 50)
INDIA_STOCKS = [
   'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'BHARTIARTL.NS', 'ICICIBANK.NS',
    'INFY.NS', 'SBIN.NS', 'LICI.NS', 'ITC.NS', 'HINDUNILVR.NS',
    'LT.NS', 'HCLTECH.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'BAJFINANCE.NS',
    'ONGC.NS', 'TATAMOTORS.NS', 'TITAN.NS', 'WIPRO.NS', 'ASIANPAINT.NS',
    'M&M.NS', 'ULTRACEMCO.NS', 'DMART.NS', 'NESTLEIND.NS', 'KOTAKBANK.NS',
    'AXISBANK.NS', 'BAJAJFINSV.NS', 'NTPC.NS', 'HDFCLIFE.NS', 'TECHM.NS',
    'POWERGRID.NS', 'JSWSTEEL.NS', 'COALINDIA.NS', 'SBILIFE.NS', 'GRASIM.NS',
    'INDUSINDBK.NS', 'ADANIENT.NS', 'TATACONSUM.NS', 'CIPLA.NS', 'BRITANNIA.NS',
    'BPCL.NS', 'EICHERMOT.NS', 'APOLLOHOSP.NS', 'TATASTEEL.NS', 'HINDALCO.NS',
    'DRREDDY.NS', 'BAJAJ-AUTO.NS', 'HEROMOTOCO.NS', 'ADANIPORTS.NS', 'DIVISLAB.NS'
]


def is_valid_stock(symbol: str) -> bool:
    symbol = symbol.upper()
    return (
        symbol in US_STOCKS or
        symbol in INDIA_STOCKS or
        (symbol + ".NS") in INDIA_STOCKS  # Support cases like RELIANCE -> RELIANCE.NS
    )

