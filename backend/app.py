from fastapi import FastAPI, HTTPException
from pipeline import get_stock_signal, get_top_stocks
from stocks import INDIA_STOCKS, is_valid_stock
from fundamentals import get_fundamentals
from fastapi.middleware.cors import CORSMiddleware
from option_strategies import router as strategy_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility: Normalize symbol to include .NS if Indian
def get_full_symbol(symbol: str) -> str:
    symbol = symbol.upper()
    if symbol in INDIA_STOCKS:
        return symbol
    elif (symbol + ".NS") in INDIA_STOCKS:
        return symbol + ".NS"
    else:
        return symbol  # fallback for US stocks or unknown

@app.get("/stocks/{market}")
def get_stocks(market: str):
    """Synchronous endpoint for stock list"""
    if market.lower() not in ["us", "india"]:
        raise HTTPException(status_code=400, detail="Market must be 'us' or 'india'")
    return {"stocks": get_top_stocks(market.lower())}

@app.get("/analyze/{symbol}")
def analyze(symbol: str):
    full_symbol = get_full_symbol(symbol)

    if not is_valid_stock(full_symbol):
        raise HTTPException(status_code=400, detail="Not a top 50 stock")

    result = get_stock_signal(full_symbol)

    if result.get("error"):
        print(f"❌ Signal generation failed: {result}")
        raise HTTPException(status_code=500, detail=result.get("reason", "Unknown error"))

    return {
        "symbol": result.get("symbol", full_symbol),
        "price": result.get("price", "N/A"),
        "rsi": result.get("rsi", "N/A"),
        "signal": result.get("signal", "HOLD"),
        "confidence": result.get("confidence", "0%"),
        "news": result.get("headlines", []),
        "analysis": result.get("analysis", []),
        "tech_signal": result.get("tech_signal", []),
        "sentiment_signal":  result.get("sentiment_signal", [])
    }

@app.get("/fundamentals/{symbol}")
def fundamentals(symbol: str):
    full_symbol = get_full_symbol(symbol)

    if not is_valid_stock(full_symbol):
        raise HTTPException(status_code=400, detail="Not a top 50 stock")

    return get_fundamentals(full_symbol)

# Add strategy endpoints
app.include_router(strategy_router)
