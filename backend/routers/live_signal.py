from fastapi import APIRouter, HTTPException
from typing import Dict, List
from datetime import datetime, timedelta
from news_analysis import AdvancedStockAnalyzer
from stocks import INDIA_STOCKS, US_STOCKS

router = APIRouter(prefix="/api/v1", tags=["signals"])
analyzer = AdvancedStockAnalyzer()

# In-memory cache
signal_cache = {
    "last_updated": None,
    "data": None
}


async def analyze_all_stocks() -> Dict[str, Dict[str, List[Dict]]]:
    """Analyze all stocks and update cache."""
    try:
        print("Starting daily stock analysis...")
        start_time = datetime.now()

        results = analyzer.analyze_portfolio(INDIA_STOCKS + US_STOCKS)

        # Validate results
        if not results or not isinstance(results, list):
            raise ValueError("Invalid results from analyzer")

        # Internal helper to process market data
        def process_stocks(stock_list):
            market_results = [r for r in results if r.symbol in stock_list]

            buy_signals = sorted(
                [r for r in market_results if r.signal in ("STRONG_BUY", "BUY")],
                key=lambda x: x.confidence,
                reverse=True
            )[:5]

            sell_signals = sorted(
                [r for r in market_results if r.signal in ("STRONG_SELL", "SELL")],
                key=lambda x: x.confidence,
                reverse=True
            )[:5]

            def format_signal(r):
                try:
                    return {
                        "symbol": r.symbol,
                        "price": round(r.price, 2) if r.price is not None else None,
                        "signal": r.signal,
                        "confidence": round(r.confidence, 1) if r.confidence is not None else None,
                        "rsi": round(getattr(r.technical_signals, "rsi", 0.0), 1),
                        "change": round(getattr(r.technical_signals, "price_momentum", 0.0), 1),
                        "last_updated": datetime.now().isoformat()
                    }
                except Exception as e:
                    print(f"Error formatting signal for {r.symbol}: {e}")
                    return {
                        "symbol": r.symbol,
                        "price": None,
                        "signal": r.signal,
                        "confidence": None,
                        "rsi": None,
                        "change": None,
                        "last_updated": datetime.now().isoformat()
                    }

            return {
                "buy": [format_signal(r) for r in buy_signals],
                "sell": [format_signal(r) for r in sell_signals]
            }

        # Update cache AFTER successful processing
        processed_data = {
            "india": process_stocks(INDIA_STOCKS),
            "us": process_stocks(US_STOCKS)
        }

        signal_cache["data"] = processed_data
        signal_cache["last_updated"] = datetime.now()

        print(f"Analysis completed in {datetime.now() - start_time}")
        return processed_data

    except Exception as e:
        print(f"[ERROR] Stock analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Stock analysis failed: {str(e)}"
        )


@router.get("/live-top-signals", response_model=Dict[str, Dict[str, List[Dict]]])
async def get_live_top_signals():
    """Return cached stock signals or trigger new analysis if cache is outdated."""
    try:
        now = datetime.now()

        if (
            signal_cache["data"] is None
            or signal_cache["last_updated"] is None
            or (now - signal_cache["last_updated"]) > timedelta(hours=24)
        ):
            print("Cache is stale or empty. Running fresh analysis...")
            return await analyze_all_stocks()

        print("Returning cached signal data.")
        return signal_cache["data"]

    except Exception as e:
        print(f"[ERROR] Failed to get live signals: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get signals: {str(e)}"
        )
