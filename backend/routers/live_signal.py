from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List
from datetime import datetime, timedelta
from news_analysis import AdvancedStockAnalyzer
from stocks import INDIA_STOCKS, US_STOCKS
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import json
import os

router = APIRouter(prefix="/api/v1", tags=["signals"])
analyzer = AdvancedStockAnalyzer()

# Thread pool for heavy operations
executor = ThreadPoolExecutor(max_workers=2)

# Auto-start analysis on module load
def auto_start_analysis():
    """Auto-start analysis when the module is loaded."""
    def delayed_start():
        import time
        time.sleep(5)  # Wait 5 seconds after startup
        
        # Check if we need to start analysis
        should_start = False
        
        if signal_cache["data"] is None:
            print("🚀 No data available - starting initial analysis...")
            should_start = True
        elif signal_cache["last_updated"]:
            age_hours = (datetime.now() - signal_cache["last_updated"]).total_seconds() / 3600
            if age_hours > 24:
                print(f"🚀 Data is {age_hours:.1f}h old - starting refresh analysis...")
                should_start = True
        
        if should_start and not signal_cache["is_analyzing"]:
            start_background_analysis()
        else:
            print("✅ Using existing data, no analysis needed at startup")
    
    # Start in background thread
    auto_thread = threading.Thread(target=delayed_start, daemon=True)
    auto_thread.start()

# In-memory cache with status tracking
signal_cache = {
    "last_updated": None,
    "data": None,
    "is_analyzing": False,
    "analysis_progress": 0,
    "analysis_count": 0,  # Track number of analyses completed
    "last_error": None    # Track last error for debugging
}

# File paths for data persistence
CACHE_DIR = "cache"
SIGNALS_CACHE_FILE = os.path.join(CACHE_DIR, "live_signals.json")
METADATA_CACHE_FILE = os.path.join(CACHE_DIR, "signals_metadata.json")

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

def save_signals_to_file(data, metadata):
    """Save signals data and metadata to files for persistence."""
    try:
        # Save signals data
        with open(SIGNALS_CACHE_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        # Save metadata
        with open(METADATA_CACHE_FILE, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        print(f"💾 Signals data saved to {SIGNALS_CACHE_FILE}")
    except Exception as e:
        print(f"❌ Error saving signals to file: {e}")

def load_signals_from_file():
    """Load previously saved signals data from file."""
    try:
        # Load signals data
        if os.path.exists(SIGNALS_CACHE_FILE):
            with open(SIGNALS_CACHE_FILE, 'r') as f:
                data = json.load(f)
        else:
            return None, None
        
        # Load metadata
        metadata = {}
        if os.path.exists(METADATA_CACHE_FILE):
            with open(METADATA_CACHE_FILE, 'r') as f:
                metadata = json.load(f)
        
        # Convert string datetime back to datetime object
        if metadata.get("last_updated"):
            try:
                metadata["last_updated"] = datetime.fromisoformat(metadata["last_updated"].replace('Z', '+00:00'))
            except:
                metadata["last_updated"] = None
        
        print(f"📂 Loaded previous signals data from {SIGNALS_CACHE_FILE}")
        return data, metadata
        
    except Exception as e:
        print(f"❌ Error loading signals from file: {e}")
        return None, None

def initialize_from_previous_data():
    """Initialize cache with previously analyzed data if available."""
    if signal_cache["data"] is None:
        print("🔧 Attempting to load previous analysis data...")
        
        # Try to load from file
        saved_data, saved_metadata = load_signals_from_file()
        
        if saved_data and saved_metadata:
            # Load previous data
            signal_cache["data"] = saved_data
            signal_cache["last_updated"] = saved_metadata.get("last_updated")
            signal_cache["analysis_count"] = saved_metadata.get("analysis_count", 0)
            
            # Calculate age
            if signal_cache["last_updated"]:
                age_hours = (datetime.now() - signal_cache["last_updated"]).total_seconds() / 3600
                print(f"✅ Loaded previous analysis data (Age: {age_hours:.1f}h)")
            else:
                print("✅ Loaded previous analysis data (Age: unknown)")
        else:
            print("📝 No previous data found, will start fresh analysis")
            # Don't set any default data - let the analysis run first


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
            buy_candidates = [r for r in market_results if r.signal in ("STRONG_BUY", "BUY") and r.confidence >= 20.0]
            sell_candidates = [r for r in market_results if r.signal in ("STRONG_SELL", "SELL") and r.confidence >= 20.0]
            
            buy_signals = sorted(buy_candidates, key=lambda x: x.confidence, reverse=True)[:5]
            sell_signals = sorted(sell_candidates, key=lambda x: x.confidence, reverse=True)[:5]
            
            

            def format_signal(r):
                try:
                    # Ensure all values are properly typed and not NaN/inf
                    price = r.price if r.price is not None and str(r.price).lower() not in ['nan', 'inf', '-inf'] else None
                    confidence = r.confidence if r.confidence is not None and str(r.confidence).lower() not in ['nan', 'inf', '-inf'] else None
                    
                    # Get technical signals safely
                    rsi = getattr(r.technical_signals, "rsi", None) if hasattr(r, 'technical_signals') and r.technical_signals else None
                    change = getattr(r.technical_signals, "price_momentum", None) if hasattr(r, 'technical_signals') and r.technical_signals else None
                    
                    # Clean numeric values
                    if rsi is not None and str(rsi).lower() not in ['nan', 'inf', '-inf']:
                        rsi = round(float(rsi), 1)
                    else:
                        rsi = None
                        
                    if change is not None and str(change).lower() not in ['nan', 'inf', '-inf']:
                        change = round(float(change), 1)
                    else:
                        change = None
                    
                    return {
                        "symbol": str(r.symbol) if r.symbol else "UNKNOWN",
                        "price": round(float(price), 2) if price is not None else None,
                        "signal": str(r.signal) if r.signal else "UNKNOWN",
                        "confidence": round(float(confidence), 1) if confidence is not None else None,
                        "rsi": rsi,
                        "change": change,
                        "last_updated": datetime.now().isoformat()
                    }
                except Exception as e:
                    print(f"Error formatting signal for {getattr(r, 'symbol', 'UNKNOWN')}: {e}")
                    return {
                        "symbol": str(getattr(r, 'symbol', 'UNKNOWN')),
                        "price": None,
                        "signal": str(getattr(r, 'signal', 'UNKNOWN')),
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
        signal_cache["analysis_count"] += 1
        signal_cache["last_error"] = None

        # Save to file for persistence
        metadata = {
            "last_updated": signal_cache["last_updated"],
            "analysis_count": signal_cache["analysis_count"],
            "analysis_duration": str(datetime.now() - start_time)
        }
        save_signals_to_file(processed_data, metadata)

        print(f"✅ Analysis #{signal_cache['analysis_count']} completed in {datetime.now() - start_time}")
        print(f"📅 Cache updated at: {signal_cache['last_updated']}")
        return processed_data

    except Exception as e:
        signal_cache["is_analyzing"] = False
        signal_cache["analysis_progress"] = 0
        signal_cache["last_error"] = str(e)
        print(f"❌ [ERROR] Stock analysis failed: {str(e)}")
        # Don't clear existing data on error - keep showing last good data
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


@router.get("/live-top-signals")
async def get_live_top_signals():
    """Always return cached data if available, trigger background analysis if needed."""
    try:
        now = datetime.now()
        
        # Check if cache is stale (older than 24 hours)
        cache_is_stale = (
            signal_cache["last_updated"] is None
            or (now - signal_cache["last_updated"]) > timedelta(hours=24)
        )
        
        # Start background analysis if cache is stale and not already analyzing
        if cache_is_stale and not signal_cache["is_analyzing"]:
            print("🔄 Cache is stale. Starting background analysis...")
            start_background_analysis()
        
        # Initialize from previous data if no data exists
        if signal_cache["data"] is None:
            initialize_from_previous_data()
        
        # Always return cached data if available and valid
        if signal_cache["data"] is not None and isinstance(signal_cache["data"], dict):
            cache_age_hours = (
                (now - signal_cache["last_updated"]).total_seconds() / 3600
                if signal_cache["last_updated"] else 999
            )
            
            # Ensure all metadata values are JSON serializable
            try:
                cache_age_hours = round(float(cache_age_hours), 1) if cache_age_hours != 999 else None
                analysis_progress = int(signal_cache["analysis_progress"]) if signal_cache["analysis_progress"] is not None else 0
                analysis_count = int(signal_cache["analysis_count"]) if signal_cache["analysis_count"] is not None else 0
                
                response_data = {
                    **signal_cache["data"],
                    "metadata": {
                        "last_updated": signal_cache["last_updated"].isoformat() if signal_cache["last_updated"] else None,
                        "is_analyzing": bool(signal_cache["is_analyzing"]),
                        "analysis_progress": analysis_progress,
                        "cache_age_hours": cache_age_hours,
                        "analysis_count": analysis_count,
                        "status": "analyzing" if signal_cache["is_analyzing"] else ("stale" if cache_age_hours and cache_age_hours > 24 else "fresh"),
                        "message": (
                            f"Analysis in progress ({analysis_progress}%), showing cached data"
                            if signal_cache["is_analyzing"]
                            else f"Data is {cache_age_hours}h old" if cache_age_hours and cache_age_hours > 1
                            else "Fresh data"
                        ),
                        "next_update": "In progress" if signal_cache["is_analyzing"] else "Within 24 hours"
                    }
                }
            except Exception as e:
                print(f"Error creating response metadata: {e}")
                # Fallback to basic response
                response_data = signal_cache["data"]
            
            print(f"✅ Returning cached data (Age: {response_data['metadata']['cache_age_hours']:.1f}h, Status: {response_data['metadata']['status']})")
            return response_data
        
        # No cached data available - first time or after error
        if signal_cache["is_analyzing"]:
            # Analysis is running but no cached data yet
            print(f"📊 First-time analysis in progress ({signal_cache['analysis_progress']}%)...")
            raise HTTPException(
                status_code=202,  # Accepted, processing
                detail={
                    "message": "Initial analysis in progress",
                    "progress": signal_cache["analysis_progress"],
                    "estimated_time": "2-3 minutes",
                    "check_again_in": "30 seconds",
                    "is_first_time": True
                }
            )
        else:
            # No data and no analysis running - start analysis
            print("🔄 No cached data available. Starting initial analysis...")
            start_background_analysis()
            raise HTTPException(
                status_code=202,  # Accepted, processing
                detail={
                    "message": "Starting initial analysis",
                    "progress": 0,
                    "estimated_time": "2-3 minutes",
                    "check_again_in": "30 seconds",
                    "is_first_time": True
                }
            )

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

# Initialize from previous data and auto-start analysis
initialize_from_previous_data()
auto_start_analysis()
