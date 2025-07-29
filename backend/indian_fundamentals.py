import yfinance as yf

def get_fundamentals(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            "symbol": symbol,
            "company": info.get("longName"),
            "sector": info.get("sector"),
            "marketCap": info.get("marketCap"),
            "incomeStatement": stock.financials.to_dict(),
            "balanceSheet": stock.balance_sheet.to_dict(),
            "cashFlow": stock.cashflow.to_dict(),
            "shareholding": "N/A (not available via yfinance NSE stocks)"
        }
    except Exception as e:
        return {"error": "Failed to fetch Indian fundamentals", "details": str(e)}
