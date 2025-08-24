from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List
from datetime import datetime, timedelta
from news_analysis import AdvancedStockAnalyzer
from stocks import INDIA_STOCKS, US_STOCKS
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

router = APIRouter(prefix="/api/v1", tags=["signals"])
analyzer = AdvancedStockAnalyzer()

# Thread pool for heavy operations
executor = ThreadPoolExecutor(max_workers=2)

# In-memory cache with status tracking
signal_cache = {
    "last_updated": None,
    "data": None,
    "is_analyzing": False,
    "analysis_progress": 0
}


def analyze_all_stocks_sync() -> Dict[str, Dict[str, List[Dict]]]:
    """Synchronous stock analysis function to run in thread pool."""
    try:
        print("🔄 Starting daily stock analysis in background...")
        start_time = datetime.now()
        
        # Mark as analyzing
        signal_cache["is_analyzing"] = True
        signal_cache["analysis_progress"] = 0

        # Run the heavy analysis
        results = analyzer.analyze_portfolio(INDIA_STOCKS + US_STOCKS)
        signal_cache["analysis_progress"] = 50

        # Validate results
        if not results or not isinstance(results, list):
            raise ValueError("Invalid results from analyzer")

        # Internal helper to process market data
        def process_stocks(stock_list):
            market_results = [r for r in results if r.symbol in stock_list]

            # Filter signals with minimum confidence threshold and sort by confidence
            buy_candidates = [r for r in market_results if r.signal in ("STRONG_BUY", "BUY") and r.confidence >= 30.0]
            sell_candidates = [r for r in market_results if r.signal in ("STRONG_SELL", "SELL") and r.confidence >= 30.0]
            
            buy_signals = sorted(buy_candidates, key=lambda x: x.confidence, reverse=True)[:5]
            sell_signals = sorted(sell_candidates, key=lambda x: x.confidence, reverse=True)[:5]
            
            # Debug logging for US market (after buy_signals is defined)
            # if "AAPL" in [r.symbol for r in market_results]:
            #     print(f"🔍 US Market Analysis Results:")
            #     print(f"  Total US stocks analyzed: {len(market_results)}")
            #     print(f"  Buy candidates (≥30% confidence): {len(buy_candidates)}")
            #     print(f"  Top 10 Buy Candidates:")
            #     for i, r in enumerate(sorted(buy_candidates, key=lambda x: x.confidence, reverse=True)[:10], 1):
            #         print(f"    {i}. {r.symbol}: {r.signal} - {r.confidence:.1f}%")
                
            #     print(f"  📋 Final Top 8 Selected:")
            #     for i, r in enumerate(buy_signals, 1):
            #         print(f"    {i}. {r.symbol}: {r.signal} - {r.confidence:.1f}%")
                
            #     # Check specific stocks mentioned
            #     for stock in ["AAPL", "COST"]:
            #         stock_result = next((r for r in market_results if r.symbol == stock), None)
            #         if stock_result:
            #             in_top_8 = stock_result in buy_signals
            #             print(f"  📊 {stock}: {stock_result.signal} - {stock_result.confidence:.1f}% (In top 8: {'Yes' if in_top_8 else 'No'})")
            #         else:
            #             print(f"  ❌ {stock}: Not found in analysis results")

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

        signal_cache["analysis_progress"] = 75

        # Update cache AFTER successful processing
        processed_data = {
            "india": process_stocks(INDIA_STOCKS),
            "us": process_stocks(US_STOCKS)
        }

        signal_cache["data"] = processed_data
        signal_cache["last_updated"] = datetime.now()
        signal_cache["is_analyzing"] = False
        signal_cache["analysis_progress"] = 100

        print(f"✅ Analysis completed in {datetime.now() - start_time}")
        print(f"📅 Cache updated at: {signal_cache['last_updated']}")
        return processed_data

    except Exception as e:
        signal_cache["is_analyzing"] = False
        signal_cache["analysis_progress"] = 0
        print(f"❌ [ERROR] Stock analysis failed: {str(e)}")
        raise Exception(f"Stock analysis failed: {str(e)}")


async def analyze_all_stocks_async() -> Dict[str, Dict[str, List[Dict]]]:
    """Async wrapper for stock analysis using thread pool."""
    loop = asyncio.get_event_loop()
    try:
        # Run the synchronous analysis in a thread pool
        result = await loop.run_in_executor(executor, analyze_all_stocks_sync)
        return result
    except Exception as e:
        signal_cache["is_analyzing"] = False
        signal_cache["analysis_progress"] = 0
        raise HTTPException(
            status_code=500,
            detail=f"Stock analysis failed: {str(e)}"
        )


def start_background_analysis():
    """Start analysis in background without blocking."""
    def run_analysis():
        try:
            analyze_all_stocks_sync()
        except Exception as e:
            print(f"Background analysis failed: {e}")
    
    # Start in a separate thread
    analysis_thread = threading.Thread(target=run_analysis, daemon=True)
    analysis_thread.start()


@router.get("/live-top-signals", response_model=Dict[str, Dict[str, List[Dict]]])
async def get_live_top_signals():
    """Return cached stock signals or trigger new analysis if cache is outdated."""
    try:
        now = datetime.now()

        # Check if analysis is currently running
        if signal_cache["is_analyzing"]:
            print(f"📊 Analysis in progress ({signal_cache['analysis_progress']}%)...")
            
            # Return cached data if available, otherwise return status
            if signal_cache["data"] is not None:
                return {
                    **signal_cache["data"],
                    "status": {
                        "analyzing": True,
                        "progress": signal_cache["analysis_progress"],
                        "message": "Analysis in progress, showing cached data"
                    }
                }
            else:
                raise HTTPException(
                    status_code=202,  # Accepted, processing
                    detail={
                        "message": "Analysis in progress",
                        "progress": signal_cache["analysis_progress"],
                        "estimated_time": "2-3 minutes"
                    }
                )

        # Check if cache is stale
        cache_is_stale = (
            signal_cache["data"] is None
            or signal_cache["last_updated"] is None
            or (now - signal_cache["last_updated"]) > timedelta(hours=24)
        )

        if cache_is_stale:
            print("🔄 Cache is stale or empty. Starting background analysis...")
            
            # Start analysis in background (non-blocking)
            start_background_analysis()
            
            # Return immediate response
            raise HTTPException(
                status_code=202,  # Accepted, processing
                detail={
                    "message": "Analysis started in background",
                    "progress": 0,
                    "estimated_time": "2-3 minutes",
                    "check_again_in": "30 seconds"
                }
            )

        print("✅ Returning cached signal data.")
        return signal_cache["data"]

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [ERROR] Failed to get live signals: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get signals: {str(e)}"
        )


@router.get("/analysis-status")
async def get_analysis_status():
    """Get current analysis status without triggering new analysis."""
    return {
        "is_analyzing": signal_cache["is_analyzing"],
        "progress": signal_cache["analysis_progress"],
        "last_updated": signal_cache["last_updated"].isoformat() if signal_cache["last_updated"] else None,
        "has_data": signal_cache["data"] is not None,
        "cache_age_hours": (
            (datetime.now() - signal_cache["last_updated"]).total_seconds() / 3600
            if signal_cache["last_updated"] else None
        )
    }


@router.post("/force-analysis")
async def force_analysis(background_tasks: BackgroundTasks):
    """Force start a new analysis (admin endpoint)."""
    if signal_cache["is_analyzing"]:
        raise HTTPException(
            status_code=409,  # Conflict
            detail="Analysis already in progress"
        )
    
    print("🔄 Force starting analysis...")
    start_background_analysis()
    
    return {
        "message": "Analysis started in background",
        "estimated_time": "2-3 minutes"
    }
