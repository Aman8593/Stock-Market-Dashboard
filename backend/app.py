from fastapi import FastAPI, HTTPException
from stocks import INDIA_STOCKS, US_STOCKS, is_valid_stock
from fundamentals import get_fundamentals
from fastapi.middleware.cors import CORSMiddleware
from routers.option_strategies import router as strategy_router
from routers.users import router as user_router
import asyncio
from concurrent.futures import Executor, ThreadPoolExecutor
from routers.live_signal import router as signals_router
from database import test_db_connection
import logging

from news_analysis import AdvancedStockAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock Sage API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Test database connection on startup"""
    logger.info("🚀 Starting Stock Sage API...")
    db_connected = await test_db_connection()
    if not db_connected:
        logger.warning("⚠️ Database connection failed, but continuing startup...")
    logger.info("✅ Stock Sage API started successfully")

# Initialize the analyzer (singleton pattern)
analyzer = AdvancedStockAnalyzer()

# Thread pool for async operations

executor = ThreadPoolExecutor(max_workers=10)

# CORS configuration for production
import os
from dotenv import load_dotenv

load_dotenv()

# Get CORS origins from environment variable or use defaults
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"  # Changed from require-corp
    return response

def get_full_symbol(symbol: str) -> str:
    """Normalize symbol to include .NS if Indian"""
    symbol = symbol.upper()
    if symbol in INDIA_STOCKS:
        return symbol
    elif (symbol + ".NS") in INDIA_STOCKS:
        return symbol + ".NS"
    else:
        return symbol  # fallback for US stocks or unknown

def get_top_stocks(market: str) -> list:
    """Get top stocks for a given market"""
    if market.lower() == "india":
        return INDIA_STOCKS
    elif market.lower() == "us":
        return US_STOCKS
    else:
        return []

@app.get("/stocks")
def get_stocks():
    """Get combined list of US and India stock symbols with normalized symbols"""
    # Get all stocks (both US and India)
    all_stocks = get_top_stocks("us") + get_top_stocks("india")
    
    # Normalize all symbols using get_full_symbol
    normalized_stocks = [get_full_symbol(symbol) for symbol in all_stocks]
    
    return {"stocks": normalized_stocks}

# # Utility: Normalize symbol to include .NS if Indian
# def get_full_symbol(symbol: str) -> str:
#     symbol = symbol.upper()
#     if symbol in INDIA_STOCKS:
#         return symbol
#     elif (symbol + ".NS") in INDIA_STOCKS:
#         return symbol + ".NS"
#     else:
#         return symbol  # fallback for US stocks or unknown

# @app.get("/stocks")
# def get_stocks():
#     """Get combined list of US and India stock symbols"""
#     return {"stocks": get_top_stocks("us") + get_top_stocks("india")}

# @app.get("/analyze/{symbol}")
# def analyze(symbol: str):
#     full_symbol = get_full_symbol(symbol)

#     if not is_valid_stock(full_symbol):
#         raise HTTPException(status_code=400, detail="Not a top 50 stock")

#     result = get_stock_signal(full_symbol)

#     if result.get("error"):
#         print(f"❌ Signal generation failed: {result}")
#         raise HTTPException(status_code=500, detail=result.get("reason", "Unknown error"))

#     return {
#         "symbol": result.get("symbol", full_symbol),
#         "price": result.get("price", "N/A"),
#         "rsi": result.get("rsi", "N/A"),
#         "signal": result.get("signal", "HOLD"),
#         "confidence": result.get("confidence", "0%"),
#         "news": result.get("headlines", []),
#         "analysis": result.get("analysis", []),
#         "tech_signal": result.get("tech_signal", []),
#         "sentiment_signal":  result.get("sentiment_signal", [])
#     }

@app.get("/analyze/{symbol}")
async def analyze_stock(symbol: str):
    """
    Main endpoint - All calculations handled in backend
    Frontend can pick whatever data it needs from the response
    """
    try:
        # Validate symbol
        full_symbol = get_full_symbol(symbol)
        
        if not is_valid_stock(full_symbol):
            raise HTTPException(status_code=400, detail="Not a top 50 stock")
        
        # Run comprehensive analysis in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor, analyzer.get_comprehensive_signal, full_symbol
        )
        
        if result.error:
            raise HTTPException(status_code=500, detail=result.error)
        
        # Return ALL calculated data - frontend picks what it needs
        return {
            # Basic Info
            "symbol": result.symbol,
            "price": result.price,
            "timestamp": "2025-07-31T12:00:00Z",  # Add current timestamp if needed
            
            # Main Signal & Confidence (Backend calculated)
            "signal": result.signal,  # STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
            "confidence": result.confidence,  # 0-100 numerical value
            "confidence_text": f"{result.confidence:.1f}%",  # Formatted for display
            
            # Technical Analysis (All calculations done in backend)
            "technical_analysis": {
                "rsi": result.technical_signals.rsi,
                "rsi_signal": "OVERSOLD" if result.technical_signals.rsi < 30 else "OVERBOUGHT" if result.technical_signals.rsi > 70 else "NEUTRAL",
                "macd": result.technical_signals.macd,
                "macd_signal": result.technical_signals.macd_signal,
                "macd_trend": "BULLISH" if result.technical_signals.macd > result.technical_signals.macd_signal else "BEARISH",
                "bollinger_position": result.technical_signals.bb_position,
                "bollinger_signal": "OVERSOLD" if result.technical_signals.bb_position < 0.2 else "OVERBOUGHT" if result.technical_signals.bb_position > 0.8 else "NEUTRAL",
                "volume_ratio": result.technical_signals.volume_ratio,
                "volume_signal": "HIGH" if result.technical_signals.volume_ratio > 1.5 else "LOW" if result.technical_signals.volume_ratio < 0.7 else "NORMAL",
                "volatility": result.technical_signals.volatility,
                "volatility_percent": f"{result.technical_signals.volatility * 100:.1f}%",
                "price_momentum": result.technical_signals.price_momentum,
                "momentum_signal": "POSITIVE" if result.technical_signals.price_momentum > 2 else "NEGATIVE" if result.technical_signals.price_momentum < -2 else "NEUTRAL",
                "support_level": result.technical_signals.support_level,
                "resistance_level": result.technical_signals.resistance_level,
                "technical_score": result.technical_score  # -100 to +100
            },
            
            # Sentiment Analysis (All calculations done in backend)
            "sentiment_analysis": {
                "sentiment_score": result.sentiment_score,  # -100 to +100
                "sentiment_signal": "POSITIVE" if result.sentiment_score > 20 else "NEGATIVE" if result.sentiment_score < -20 else "NEUTRAL",
                "news_count": len(result.headlines),
                "headlines": result.headlines,
                "detailed_analysis": result.analysis  # Individual headline sentiments
            },
            
            # Risk Assessment (All calculations done in backend)
            "risk_analysis": {
                "risk_score": result.risk_score,  # 0-100 (higher = riskier)
                "risk_level": "HIGH" if result.risk_score > 70 else "MEDIUM" if result.risk_score > 40 else "LOW",
                "position_size": result.position_size,
                "entry_price": result.entry_price,
                "stop_loss": result.stop_loss,
                "take_profit": result.take_profit,
                "risk_reward_ratio": round((result.take_profit - result.entry_price) / (result.entry_price - result.stop_loss), 2) if result.entry_price > result.stop_loss else 0
            },
            
            # Market Context (All calculations done in backend)
            "market_context": {
                "volatility_regime": result.market_context.volatility_regime,  # LOW, MEDIUM, HIGH
                "trend_direction": result.market_context.trend_direction,      # BULL, BEAR, SIDEWAYS
                "sector_rotation": result.market_context.sector_rotation,      # GROWTH, VALUE, DEFENSIVE
                "market_sentiment": result.market_context.market_sentiment     # FEAR, GREED, NEUTRAL
            },
            
            # Performance Metrics (All calculations done in backend)
            "backtest_performance": result.backtest_metrics,
            
            # Summary Scores (Pre-calculated for easy frontend use)
            "summary": {
                "overall_signal": result.signal,
                "buy_probability": max(0, result.confidence) if result.signal in ["BUY", "STRONG_BUY"] else 0,
                "sell_probability": max(0, result.confidence) if result.signal in ["SELL", "STRONG_SELL"] else 0,
                "hold_probability": max(0, result.confidence) if result.signal == "HOLD" else 0,
                "technical_strength": "STRONG" if abs(result.technical_score) > 50 else "MODERATE" if abs(result.technical_score) > 25 else "WEAK",
                "sentiment_strength": "STRONG" if abs(result.sentiment_score) > 50 else "MODERATE" if abs(result.sentiment_score) > 25 else "WEAK",
                "investment_grade": "A" if result.confidence > 80 and result.risk_score < 40 else "B" if result.confidence > 60 and result.risk_score < 60 else "C" if result.confidence > 40 else "D"
            },
            
            # Quick Reference (For simple frontend displays)
            "quick_stats": {
            "current_price": result.price,
            "signal_emoji": "🚀 STRONG_BUY" if result.signal == "STRONG_BUY" else "📈 BUY" if result.signal == "BUY" else "⏸️ HOLD" if result.signal == "HOLD" else "📉 SELL" if result.signal == "SELL" else "🔻 STRONG_SELL",
            "confidence_emoji": "🎯 HIGH_CONFIDENCE" if result.confidence > 80 else "✅ MODERATE_CONFIDENCE" if result.confidence > 60 else "⚠️ LOW_CONFIDENCE" if result.confidence > 40 else "❌ WEAK_CONFIDENCE",
            "risk_emoji": "🔴 HIGH_RISK" if result.risk_score > 70 else "🟡 MEDIUM_RISK" if result.risk_score > 40 else "🟢 LOW_RISK",
            "trend_emoji": "📈 BULLISH" if result.market_context.trend_direction == "BULL" else "📉 BEARISH" if result.market_context.trend_direction == "BEAR" else "➡️ NEUTRAL"
            }
        }
            

        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error analyzing {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/fundamentals/{symbol}")
def fundamentals(symbol: str):
    full_symbol = get_full_symbol(symbol)

    if not is_valid_stock(full_symbol):
        raise HTTPException(status_code=400, detail="Not a top 50 stock")

    return get_fundamentals(full_symbol)


# Add strategy endpoints
app.include_router(strategy_router)

# Add user authentication endpoints
app.include_router(user_router)

# Test endpoint for debugging
@app.get("/test-auth")
async def test_auth():
    """Test endpoint to verify API is working"""
    return {"status": "API is working", "message": "Authentication endpoints are available"}

@app.get("/health")
async def health_check():
    """Health check endpoint - always responds quickly"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-15T12:00:00Z",
        "message": "Stock Sage API is running"
    }

# Add live signal endpoints
app.include_router(signals_router)

