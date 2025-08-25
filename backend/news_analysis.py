import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from dataclasses import dataclass
import json

warnings.filterwarnings('ignore')
load_dotenv()

# Configuration
HF_MODEL = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
HF_TOKEN = os.getenv("HF_API_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ALPHA_VANTAGE_KEY = os.getenv("ALPHAVANTAGE_KEY")

@dataclass
class MarketContext:
    """Market regime and context information"""
    volatility_regime: str  # LOW, MEDIUM, HIGH
    trend_direction: str    # BULL, BEAR, SIDEWAYS
    sector_rotation: str    # GROWTH, VALUE, DEFENSIVE
    market_sentiment: str   # FEAR, GREED, NEUTRAL

@dataclass
class TechnicalSignals:
    """Container for all technical indicators"""
    rsi: float
    macd: float
    macd_signal: float
    bb_position: float  # Position relative to Bollinger Bands
    volume_ratio: float
    price_momentum: float
    volatility: float
    support_level: float
    resistance_level: float

@dataclass
class SignalResult:
    """Complete signal analysis result"""
    symbol: str
    price: float
    signal: str
    confidence: float
    technical_score: float
    sentiment_score: float
    risk_score: float
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    market_context: MarketContext
    technical_signals: TechnicalSignals
    headlines: List[str]
    analysis: List[Dict]
    backtest_metrics: Dict
    error: Optional[str]

class AdvancedStockAnalyzer:
    def __init__(self):
        self.cache = {}
        self.market_data = {}
        self.last_request_time = 0
        self.min_request_interval = 2  # Minimum 2 seconds between requests
    
    def _fetch_stock_data_with_retry(self, symbol: str, max_retries: int = 3):
        """Fetch stock data with comprehensive retry logic and rate limiting"""
        import time
        import requests
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            print(f"Rate limiting: waiting {sleep_time:.1f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        
        # Try different approaches
        approaches = [
            # Approach 1: Standard yfinance
            lambda: self._fetch_with_standard_yfinance(symbol),
            # Approach 2: Custom session with headers
            lambda: self._fetch_with_custom_session(symbol),
            # Approach 3: Different time periods
            lambda: self._fetch_with_fallback_periods(symbol),
        ]
        
        for attempt, approach in enumerate(approaches):
            try:
                print(f"Attempt {attempt + 1}: Fetching data for {symbol}")
                hist = approach()
                if hist is not None and not hist.empty:
                    print(f"✅ Successfully fetched {len(hist)} days of data for {symbol}")
                    return hist
                else:
                    print(f"❌ No data returned from approach {attempt + 1}")
            except Exception as e:
                print(f"❌ Approach {attempt + 1} failed: {str(e)}")
                if attempt < len(approaches) - 1:
                    # Wait before next attempt
                    wait_time = (attempt + 1) * 2
                    print(f"Waiting {wait_time} seconds before next attempt...")
                    time.sleep(wait_time)
        
        return None
    
    def _fetch_with_standard_yfinance(self, symbol: str):
        """Standard yfinance fetch"""
        stock = yf.Ticker(symbol)
        return stock.history(period="5d")
    
    def _fetch_with_custom_session(self, symbol: str):
        """Fetch with custom session and headers"""
        import requests
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        stock = yf.Ticker(symbol, session=session)
        return stock.history(period="1mo")
    
    def _fetch_with_fallback_periods(self, symbol: str):
        """Try different time periods"""
        import requests
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        stock = yf.Ticker(symbol, session=session)
        
        # Try different periods
        periods = ["1d", "5d", "1mo", "3mo"]
        for period in periods:
            try:
                hist = stock.history(period=period)
                if not hist.empty:
                    return hist
            except:
                continue
        
        return None
        
    # ===================== TECHNICAL ANALYSIS =====================
    
    def calculate_rsi(self, prices: pd.Series, window: int = 14) -> float:
        """Enhanced RSI calculation with proper handling"""
        if len(prices) < window + 1:
            return 50.0
            
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window, min_periods=window).mean()
        avg_loss = loss.rolling(window, min_periods=window).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """MACD calculation with histogram"""
        if len(prices) < slow + signal:
            return 0.0, 0.0, 0.0
            
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        
        return float(macd.iloc[-1]), float(signal_line.iloc[-1]), float(histogram.iloc[-1])
    
    def calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, std_dev: int = 2) -> Tuple[float, float, float, float]:
        """Bollinger Bands with position calculation"""
        if len(prices) < window:
            current_price = float(prices.iloc[-1])
            return current_price, current_price, current_price, 0.5
            
        rolling_mean = prices.rolling(window).mean()
        rolling_std = prices.rolling(window).std()
        upper_band = rolling_mean + (rolling_std * std_dev)
        lower_band = rolling_mean - (rolling_std * std_dev)
        
        current_price = float(prices.iloc[-1])
        bb_position = (current_price - float(lower_band.iloc[-1])) / (float(upper_band.iloc[-1]) - float(lower_band.iloc[-1]))
        
        return float(upper_band.iloc[-1]), float(lower_band.iloc[-1]), float(rolling_mean.iloc[-1]), bb_position
    
    def calculate_volume_analysis(self, hist: pd.DataFrame) -> float:
        """Volume trend analysis"""
        if len(hist) < 10:
            return 1.0
            
        recent_volume = hist['Volume'].tail(5).mean()
        avg_volume = hist['Volume'].rolling(20).mean().iloc[-1]
        
        return float(recent_volume / avg_volume) if avg_volume > 0 else 1.0
    
    def calculate_volatility(self, prices: pd.Series, window: int = 30) -> float:
        """Annualized volatility calculation"""
        if len(prices) < window:
            return 0.2
            
        returns = prices.pct_change().dropna()
        volatility = returns.rolling(window).std().iloc[-1] * np.sqrt(252)
        
        return float(volatility) if not pd.isna(volatility) else 0.2
    
    def calculate_support_resistance(self, hist: pd.DataFrame, window: int = 20) -> Tuple[float, float]:
        """Dynamic support and resistance levels"""
        if len(hist) < window:
            current_price = float(hist['Close'].iloc[-1])
            return current_price * 0.95, current_price * 1.05
            
        highs = hist['High'].rolling(window).max()
        lows = hist['Low'].rolling(window).min()
        
        resistance = float(highs.iloc[-1])
        support = float(lows.iloc[-1])
        
        return support, resistance
    
    def get_technical_signals(self, symbol: str) -> TechnicalSignals:
        """Comprehensive technical analysis"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="6mo")
            
            if hist.empty:
                return self._default_technical_signals()
            
            prices = hist['Close']
            
            # Calculate all indicators
            rsi = self.calculate_rsi(prices)
            macd, macd_signal, macd_hist = self.calculate_macd(prices)
            bb_upper, bb_lower, bb_mid, bb_position = self.calculate_bollinger_bands(prices)
            volume_ratio = self.calculate_volume_analysis(hist)
            volatility = self.calculate_volatility(prices)
            support, resistance = self.calculate_support_resistance(hist)
            
            # Price momentum (20-day change)
            price_momentum = float((prices.iloc[-1] / prices.iloc[-20] - 1) * 100) if len(prices) >= 20 else 0.0
            
            return TechnicalSignals(
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                bb_position=bb_position,
                volume_ratio=volume_ratio,
                price_momentum=price_momentum,
                volatility=volatility,
                support_level=support,
                resistance_level=resistance
            )
            
        except Exception as e:
            print(f"Error in technical analysis for {symbol}: {e}")
            return self._default_technical_signals()
    
    def _default_technical_signals(self) -> TechnicalSignals:
        """Default technical signals for error cases"""
        return TechnicalSignals(
            rsi=50.0, macd=0.0, macd_signal=0.0, bb_position=0.5,
            volume_ratio=1.0, price_momentum=0.0, volatility=0.2,
            support_level=100.0, resistance_level=110.0
        )
    
    
    # ===================== IMPROVED SENTIMENT ANALYSIS =====================

    def scrape_news(self, symbol: str) -> List[str]:
        """Enhanced news scraping with quality filtering"""
        headlines = []
        
        # Indian stocks
        if symbol.endswith((".NS", ".BO")):
            headlines.extend(self._scrape_indian_news(symbol))
        else:
            # US stocks
            headlines.extend(self._scrape_us_news(symbol))
            headlines.extend(self._scrape_yahoo_news(symbol))
        
        # Filter quality headlines
        quality_headlines = self._filter_quality_headlines(headlines)
        
        # If no quality headlines, try fallback methods
        if not quality_headlines:
            quality_headlines = self._fallback_news_scraping(symbol)
        
        return quality_headlines[:10] if quality_headlines else [f"No news available for {symbol}"]

    def _filter_quality_headlines(self, headlines: List[str]) -> List[str]:
        """Filter out generic page titles and low-quality content"""
        if not headlines:
            return []
        
        filtered = []
        
        # Keywords that indicate generic pages (not news)
        generic_keywords = [
            "share price", "stock price", "live bse", "live nse", "bids offers",
            "buy/sell", "quotes", "finder", "homepage", "market investment",
            "portfolio", "tips", "forecast news", "stock/share market"
        ]
        
        # Keywords that indicate quality news
        news_keywords = [
            "profit", "loss", "earnings", "revenue", "acquisition", "merger",
            "launch", "contract", "partnership", "growth", "decline", "surge",
            "beats", "misses", "announces", "reports", "plans", "expands",
            "investment", "dividend", "results", "outlook", "guidance"
        ]
        
        for headline in headlines:
            if not headline or len(headline.strip()) < 10:
                continue
                
            headline_lower = headline.lower()
            
            # Skip very long headlines (likely page titles)
            if len(headline) > 150:
                continue
                
            # Skip if contains too many generic keywords
            generic_count = sum(1 for keyword in generic_keywords if keyword in headline_lower)
            if generic_count > 2:
                continue
                
            # Skip obvious page titles
            if any(phrase in headline_lower for phrase in [
                "moneycontrol", "economic times", "business standard",
                "the economic times", "bse/nse", "ifsc code"
            ]) and not any(keyword in headline_lower for keyword in news_keywords):
                continue
                
            # Accept if contains news keywords
            if any(keyword in headline_lower for keyword in news_keywords):
                filtered.append(headline.strip())
            # Accept if reasonable length and no generic keywords
            elif 20 <= len(headline) <= 100 and generic_count == 0:
                filtered.append(headline.strip())
        
        return filtered

    def _scrape_indian_news(self, symbol: str) -> List[str]:
        """Improved Indian stock news scraping with multiple methods"""
        headlines = []
        base_symbol = symbol.replace(".NS", "").replace(".BO", "")
        
        # Method 1: Try yfinance first (most reliable)
        try:
            stock = yf.Ticker(symbol)
            if hasattr(stock, 'news') and stock.news:
                for item in stock.news[:5]:
                    if 'title' in item and item['title']:
                        headlines.append(item['title'])
        except Exception as e:
            print(f"yfinance news failed for {symbol}: {e}")
        
        # Method 2: Google News with better queries
        try:
            # Get company name for better search
            company_queries = [
                f'"{base_symbol}" earnings profit revenue',
                f'"{base_symbol}" stock news India',
                f'"{base_symbol}" announcement results'
            ]
            
            for query in company_queries:
                try:
                    url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=IN&ceid=IN:en"
                    response = requests.get(url, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, "xml")
                    items = soup.find_all("item")
                    
                    for item in items[:3]:
                        if item.title and item.title.text:
                            title = item.title.text.strip()
                            if len(title) > 20 and len(title) < 120:
                                headlines.append(title)
                                
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Google News failed for {symbol}: {e}")
        
        # Method 3: Alternative RSS feeds
        try:
            rss_feeds = [
                f"https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
                f"https://www.business-standard.com/rss/markets-106.rss"
            ]
            
            for feed_url in rss_feeds:
                try:
                    response = requests.get(feed_url, timeout=10)
                    soup = BeautifulSoup(response.content, "xml")
                    items = soup.find_all("item")
                    
                    for item in items[:5]:
                        if item.title and base_symbol.lower() in item.title.text.lower():
                            headlines.append(item.title.text.strip())
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"RSS feeds failed for {symbol}: {e}")
        
        return headlines

    def _scrape_us_news(self, symbol: str) -> List[str]:
        """Enhanced US stock news scraping"""
        headlines = []
        
        # Method 1: News API with better queries
        try:
            if NEWS_API_KEY:
                queries = [
                    f"{symbol} earnings",
                    f"{symbol} stock news",
                    f"{symbol} financial results"
                ]
                
                for query in queries:
                    try:
                        response = requests.get(
                            "https://newsapi.org/v2/everything",
                            params={
                                "q": query,
                                "apiKey": NEWS_API_KEY,
                                "sortBy": "publishedAt",
                                "pageSize": 3,
                                "language": "en",
                                "domains": "reuters.com,bloomberg.com,cnbc.com,marketwatch.com"
                            },
                            timeout=10
                        )
                        response.raise_for_status()
                        
                        news = response.json()
                        if 'articles' in news and news['articles']:
                            for article in news['articles']:
                                if article.get('title'):
                                    headlines.append(article['title'])
                                    
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"News API failed for {symbol}: {e}")
        
        # Method 2: Alpha Vantage News (if available)
        try:
            if ALPHA_VANTAGE_KEY:
                url = f"https://www.alphavantage.co/query"
                params = {
                    "function": "NEWS_SENTIMENT",
                    "tickers": symbol,
                    "apikey": ALPHA_VANTAGE_KEY,
                    "limit": 5
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'feed' in data:
                        for item in data['feed']:
                            if 'title' in item:
                                headlines.append(item['title'])
                                
        except Exception as e:
            print(f"Alpha Vantage news failed for {symbol}: {e}")
        
        return headlines

    def _scrape_yahoo_news(self, symbol: str) -> List[str]:
        """Enhanced Yahoo Finance news scraping"""
        headlines = []
        
        try:
            stock = yf.Ticker(symbol)
            
            # Try multiple yfinance attributes
            news_sources = []
            
            # Primary news attribute
            if hasattr(stock, 'news') and stock.news:
                news_sources.extend(stock.news)
                
            # Try get_news method if available
            try:
                recent_news = stock.get_news()
                if recent_news:
                    news_sources.extend(recent_news)
            except:
                pass
            
            # Extract headlines
            for item in news_sources[:8]:
                if isinstance(item, dict) and 'title' in item:
                    title = item['title'].strip()
                    if 10 <= len(title) <= 120:
                        headlines.append(title)
                        
        except Exception as e:
            print(f"Yahoo news failed for {symbol}: {e}")
        
        return headlines

    def _fallback_news_scraping(self, symbol: str) -> List[str]:
        """Fallback news scraping when primary methods fail"""
        headlines = []
        
        try:
            # Method 1: Try direct company name search
            base_symbol = symbol.replace(".NS", "").replace(".BO", "")
            
            # Simple Google search fallback
            search_terms = [
                f"{base_symbol} company news today",
                f"{base_symbol} stock latest news",
                f"{base_symbol} quarterly results"
            ]
            
            for term in search_terms:
                try:
                    # Use a simple news aggregator or RSS feed
                    url = f"https://news.google.com/rss/search?q={term}&hl=en"
                    response = requests.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, "xml")
                        items = soup.find_all("item")[:2]
                        
                        for item in items:
                            if item.title:
                                title = item.title.text.strip()
                                if 15 <= len(title) <= 100:
                                    headlines.append(title)
                                    
                except:
                    continue
                    
        except Exception as e:
            print(f"Fallback news scraping failed for {symbol}: {e}")
        
        # If still no headlines, create a neutral placeholder
        if not headlines:
            headlines = [f"No recent news found for {symbol}"]
        
        return headlines

    def analyze_sentiment(self, headlines: List[str]) -> Tuple[List[Dict], float]:
        """Enhanced sentiment analysis with better error handling"""
        if not headlines or not HF_TOKEN:
            return [], 0.0
        
        results = []
        valid_scores = []
        
        # Filter out placeholder messages
        actual_headlines = [h for h in headlines if not h.startswith("No news available") 
                        and not h.startswith("No recent news found")]
        
        if not actual_headlines:
            return [], 0.0
        
        for i, headline in enumerate(actual_headlines):
            try:
                # Skip very short or very long headlines
                if len(headline.strip()) < 10 or len(headline) > 200:
                    continue
                    
                response = requests.post(
                    f"https://api-inference.huggingface.co/models/{HF_MODEL}",
                    headers={"Authorization": f"Bearer {HF_TOKEN}"},
                    json={"inputs": headline.strip()},
                    timeout=15
                )
                
                if response.status_code == 200:
                    try:
                        prediction = response.json()
                        
                        # Handle different response formats
                        if isinstance(prediction, list) and len(prediction) > 0:
                            if isinstance(prediction[0], list) and len(prediction[0]) > 0:
                                result = prediction[0][0]
                            else:
                                result = prediction[0]
                        else:
                            continue
                        
                        label = result.get("label", "NEUTRAL").upper()
                        score = float(result.get("score", 0.5))
                        
                        # Convert to numerical score (-1 to 1)
                        if label == "POSITIVE":
                            numerical_score = score
                        elif label == "NEGATIVE":
                            numerical_score = -score
                        else:
                            numerical_score = 0.0
                        
                        valid_scores.append(numerical_score)
                        
                        results.append({
                            "headline": headline,
                            "label": label,
                            "score": score,
                            "numerical_score": numerical_score,
                            "confidence": score
                        })
                        
                    except (KeyError, IndexError, ValueError) as e:
                        print(f"Error parsing sentiment response: {e}")
                        continue
                        
                elif response.status_code == 503:
                    # Model loading, wait and retry once
                    time.sleep(2)
                    try:
                        retry_response = requests.post(
                            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
                            headers={"Authorization": f"Bearer {HF_TOKEN}"},
                            json={"inputs": headline.strip()},
                            timeout=15
                        )
                        if retry_response.status_code == 200:
                            # Process retry response (same logic as above)
                            pass
                    except:
                        pass
                else:
                    print(f"Sentiment API error: {response.status_code}")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error analyzing sentiment for headline: {e}")
                # Add neutral result for failed analysis
                results.append({
                    "headline": headline,
                    "label": "NEUTRAL",
                    "score": 0.5,
                    "numerical_score": 0.0,
                    "confidence": 0.5
                })
        
        # Calculate weighted average sentiment
        if valid_scores:
            # Weight recent news higher and high-confidence scores more
            weights = []
            for i, result in enumerate([r for r in results if r.get("numerical_score") is not None]):
                base_weight = 1.0 + (i * 0.1)  # Recent news weight
                confidence_weight = result.get("confidence", 0.5)  # Confidence weight
                weights.append(base_weight * confidence_weight)
            
            if weights and len(weights) == len(valid_scores):
                weighted_sentiment = np.average(valid_scores, weights=weights)
            else:
                weighted_sentiment = np.mean(valid_scores)
        else:
            weighted_sentiment = 0.0
        
        return results, float(weighted_sentiment)


    # ===================== MARKET CONTEXT ANALYSIS =====================
    
    def get_market_context(self, symbol: str) -> MarketContext:
        """Analyze broader market context"""
        try:
            # Determine market index based on symbol
            if symbol.endswith((".NS", ".BO")):
                index_symbol = "^NSEI"  # NIFTY 50
            else:
                index_symbol = "^GSPC"  # S&P 500
            
            # Get market index data
            index = yf.Ticker(index_symbol)
            index_hist = index.history(period="6mo")
            
            if index_hist.empty:
                return self._default_market_context()
            
            # Calculate market volatility (VIX-like)
            market_volatility = self.calculate_volatility(index_hist['Close'])
            volatility_regime = "HIGH" if market_volatility > 0.25 else "LOW" if market_volatility < 0.15 else "MEDIUM"
            
            # Trend analysis
            sma_50 = index_hist['Close'].rolling(50).mean().iloc[-1]
            sma_200 = index_hist['Close'].rolling(200).mean().iloc[-1] if len(index_hist) >= 200 else sma_50
            current_price = index_hist['Close'].iloc[-1]
            
            if current_price > sma_50 > sma_200:
                trend_direction = "BULL"
            elif current_price < sma_50 < sma_200:
                trend_direction = "BEAR"
            else:
                trend_direction = "SIDEWAYS"
            
            # Simplified sector rotation and sentiment
            sector_rotation = "GROWTH"  # Could be enhanced with sector ETF analysis
            market_sentiment = "NEUTRAL"  # Could be enhanced with fear/greed index
            
            return MarketContext(
                volatility_regime=volatility_regime,
                trend_direction=trend_direction,
                sector_rotation=sector_rotation,
                market_sentiment=market_sentiment
            )
            
        except Exception as e:
            print(f"Error getting market context: {e}")
            return self._default_market_context()
    
    def _default_market_context(self) -> MarketContext:
        """Default market context"""
        return MarketContext(
            volatility_regime="MEDIUM",
            trend_direction="SIDEWAYS",
            sector_rotation="GROWTH",
            market_sentiment="NEUTRAL"
        )
    
    def calculate_position_sizing(self, price: float, volatility: float, signal_type: str, account_size: float = 10000) -> Dict[str, float]:
        """Kelly Criterion based position sizing for both long and short positions"""
        # Risk per trade (2% of account)
        risk_per_trade = account_size * 0.02
        
        # ATR-based stop loss (2 * daily volatility)
        daily_volatility = volatility / np.sqrt(252)
        stop_loss_distance = price * daily_volatility * 2
        
        # Position size calculation
        position_size = risk_per_trade / stop_loss_distance if stop_loss_distance > 0 else 0
        shares = int(position_size / price) if price > 0 else 0
        
        # Risk-reward targets based on signal type
        if signal_type in ["BUY", "STRONG_BUY"]:
            # Long position
            stop_loss = price - stop_loss_distance
            take_profit = price + (stop_loss_distance * 2)  # 2:1 reward:risk
            position_direction = "LONG"
        elif signal_type in ["SELL", "STRONG_SELL"]:
            # Short position
            stop_loss = price + stop_loss_distance
            take_profit = price - (stop_loss_distance * 2)  # 2:1 reward:risk
            position_direction = "SHORT"
            shares = -shares  # Negative shares for short position
        else:
            # HOLD signal
            stop_loss = price
            take_profit = price
            position_direction = "HOLD"
            shares = 0
        
        return {
            "shares": shares,
            "position_value": abs(shares) * price,
            "position_direction": position_direction,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_amount": risk_per_trade,
            "max_loss_percent": (stop_loss_distance / price) * 100 if price > 0 else 0,
            "risk_reward_ratio": 2.0
        }

    def calculate_risk_score(self, technical_signals: TechnicalSignals, market_context: MarketContext, signal_type: str = None) -> float:
        """Comprehensive risk assessment (0-100, higher = riskier)"""
        risk_components = []
        
        # Volatility risk (0-30 points)
        vol_risk = min(technical_signals.volatility * 100, 30)
        risk_components.append(vol_risk)
        
        # Technical risk (0-25 points)
        tech_risk = 0
        if technical_signals.rsi > 80 or technical_signals.rsi < 20:
            tech_risk += 10  # Extreme RSI
        if abs(technical_signals.bb_position - 0.5) > 0.4:
            tech_risk += 10  # Near BB extremes
        if technical_signals.volume_ratio < 0.5:
            tech_risk += 5   # Low volume
        risk_components.append(tech_risk)
        
        # Market risk (0-25 points)
        market_risk = 0
        if market_context.volatility_regime == "HIGH":
            market_risk += 15
        if market_context.trend_direction == "BEAR":
            market_risk += 10
        risk_components.append(market_risk)
        
        # Liquidity risk (0-20 points)
        liquidity_risk = max(0, 20 - technical_signals.volume_ratio * 10)
        risk_components.append(liquidity_risk)
        
        # Signal-specific risk adjustments
        if signal_type:
            if signal_type in ["SELL", "STRONG_SELL"] and market_context.trend_direction == "BULL":
                risk_components.append(10)  # Extra risk for shorting in bull market
            elif signal_type in ["BUY", "STRONG_BUY"] and market_context.trend_direction == "BEAR":
                risk_components.append(5)   # Some risk for buying in bear market
        
        total_risk = sum(risk_components)
        return min(total_risk, 100)
    # ===================== SIGNAL GENERATION =====================
    
    def generate_technical_score(self, signals: TechnicalSignals) -> float:
        """Generate technical analysis score (-100 to 100)"""
        score = 0
        
        # RSI component (-30 to 30)
        if signals.rsi < 30:
            score += 30 - signals.rsi  # Max +30 for oversold
        elif signals.rsi > 70:
            score -= signals.rsi - 70  # Max -30 for overbought
        
        # MACD component (-25 to 25)
        if signals.macd > signals.macd_signal:
            score += min(25, (signals.macd - signals.macd_signal) * 100)
        else:
            score += max(-25, (signals.macd - signals.macd_signal) * 100)
        
        # Bollinger Bands component (-20 to 20)
        if signals.bb_position < 0.2:
            score += 20  # Near lower band = bullish
        elif signals.bb_position > 0.8:
            score -= 20  # Near upper band = bearish
        
        # Volume confirmation (-15 to 15)
        if signals.volume_ratio > 1.5:
            score += 15  # High volume confirmation
        elif signals.volume_ratio < 0.7:
            score -= 10  # Low volume warning
        
        # Momentum component (-10 to 10)
        score += max(-10, min(10, signals.price_momentum / 2))
        
        return max(-100, min(100, score))
    
    def combine_signals(self, technical_score: float, sentiment_score: float, 
                       market_context: MarketContext) -> Tuple[str, float]:
        """Advanced signal combination with market context weighting"""
        
        # Base weights
        tech_weight = 0.6
        sentiment_weight = 0.4
        
        # Adjust weights based on market context
        if market_context.volatility_regime == "HIGH":
            tech_weight = 0.7  # Trust technicals more in volatile markets
            sentiment_weight = 0.3
        elif market_context.trend_direction == "BEAR":
            sentiment_weight = 0.5  # Sentiment more important in bear markets
            tech_weight = 0.5
        
        # Calculate combined score
        combined_score = (technical_score * tech_weight) + (sentiment_score * 100 * sentiment_weight)
        
        # Generate signal with confidence
        if combined_score > 30:
            signal = "STRONG_BUY"
            confidence = min(95, abs(combined_score))
        elif combined_score > 15:
            signal = "BUY"
            confidence = min(85, abs(combined_score))
        elif combined_score < -30:
            signal = "STRONG_SELL"
            confidence = min(95, abs(combined_score))
        elif combined_score < -15:
            signal = "SELL"
            confidence = min(85, abs(combined_score))
        else:
            signal = "HOLD"
            confidence = max(50, 100 - abs(combined_score))
        
        return signal, confidence
    
    # ===================== BACKTESTING =====================
    
    def backtest_strategy(self, symbol: str, days: int = 252) -> Dict:
        """Simple backtesting framework"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=f"{days}d")
            
            if len(hist) < 50:
                return {"error": "Insufficient data for backtesting"}
            
            # Initialize tracking variables
            positions = []
            returns = []
            signals_history = []
            
            # Rolling window backtesting
            for i in range(50, len(hist) - 5):  # Leave 5 days for forward testing
                window_data = hist.iloc[i-50:i]
                
                # Generate signal for this point
                rsi = self.calculate_rsi(window_data['Close'])
                macd, macd_signal, _ = self.calculate_macd(window_data['Close'])
                
                # Simple signal logic for backtesting
                if rsi < 35 and macd > macd_signal:
                    signal = "BUY"
                elif rsi > 65 and macd < macd_signal:
                    signal = "SELL"
                else:
                    signal = "HOLD"
                
                signals_history.append({
                    'date': hist.index[i],
                    'price': hist['Close'].iloc[i],
                    'signal': signal,
                    'rsi': rsi
                })
                
                # Calculate forward returns (5-day holding period)
                if i + 5 < len(hist):
                    forward_return = (hist['Close'].iloc[i+5] / hist['Close'].iloc[i] - 1) * 100
                    if signal == "BUY":
                        returns.append(forward_return)
                    elif signal == "SELL":
                        returns.append(-forward_return)
            
            # Calculate metrics
            if returns:
                total_return = sum(returns)
                win_rate = len([r for r in returns if r > 0]) / len(returns) * 100
                avg_return = np.mean(returns)
                max_loss = min(returns) if returns else 0
                max_gain = max(returns) if returns else 0
                sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
                
                return {
                    "total_trades": len(returns),
                    "total_return": round(total_return, 2),
                    "win_rate": round(win_rate, 2),
                    "avg_return": round(avg_return, 2),
                    "max_gain": round(max_gain, 2),
                    "max_loss": round(max_loss, 2),
                    "sharpe_ratio": round(sharpe_ratio, 2),
                    "signals_count": len(signals_history)
                }
            else:
                return {"error": "No trades generated in backtest period"}
                
        except Exception as e:
            return {"error": f"Backtesting failed: {str(e)}"}
    
    # ===================== MAIN ANALYSIS FUNCTION =====================
    
    def get_comprehensive_signal(self, symbol: str) -> SignalResult:
        """Complete stock analysis with all capabilities"""
        try:
            print(f"Analyzing {symbol}...")
            
            # Get current price with enhanced retry mechanism and rate limiting
            hist = self._fetch_stock_data_with_retry(symbol)
            
            if hist is None or hist.empty:
                raise Exception(f"Unable to fetch price data for {symbol}. Yahoo Finance may be rate limiting or blocking requests from this server.")
            
            current_price = float(hist['Close'].iloc[-1])
            
            # Parallel processing for faster analysis
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit all analysis tasks
                technical_future = executor.submit(self.get_technical_signals, symbol)
                news_future = executor.submit(self.scrape_news, symbol)
                market_future = executor.submit(self.get_market_context, symbol)
                backtest_future = executor.submit(self.backtest_strategy, symbol)
                
                # Collect results
                technical_signals = technical_future.result()
                headlines = news_future.result()
                market_context = market_future.result()
                backtest_metrics = backtest_future.result()
            
            # Sentiment analysis
            sentiment_analysis, sentiment_score = self.analyze_sentiment(headlines)
            
            # Generate scores
            technical_score = self.generate_technical_score(technical_signals)
            
            # Combine signals to get final signal and confidence
            final_signal, confidence = self.combine_signals(
                technical_score, sentiment_score, market_context
            )
            
            # Calculate risk score with signal context
            risk_score = self.calculate_risk_score(technical_signals, market_context, final_signal)
            
            # Position sizing and risk management with signal type
            position_info = self.calculate_position_sizing(
                current_price, technical_signals.volatility, final_signal
            )
            
            # Create comprehensive result
            result = SignalResult(
                symbol=symbol,
                price=current_price,
                signal=final_signal,
                confidence=confidence,
                technical_score=technical_score,
                sentiment_score=sentiment_score * 100,  # Convert to percentage
                risk_score=risk_score,
                entry_price=current_price,
                stop_loss=position_info["stop_loss"],
                take_profit=position_info["take_profit"],
                position_size=position_info["shares"],
                market_context=market_context,
                technical_signals=technical_signals,
                headlines=headlines[:5],
                analysis=sentiment_analysis[:5],
                backtest_metrics=backtest_metrics,
                error=None
            )
            
            print(f"✓ Analysis complete for {symbol}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Error analyzing {symbol}: {error_msg}")
            
            # Provide more specific error messages
            if "price data" in error_msg.lower():
                detailed_error = f"Failed to fetch price data for {symbol}. This is likely due to Yahoo Finance rate limiting or blocking requests from the server IP address. Please try again later or contact support."
            elif "429" in error_msg:
                detailed_error = f"Rate limit exceeded when fetching data for {symbol}. Please wait a few minutes before trying again."
            elif "timeout" in error_msg.lower():
                detailed_error = f"Request timeout when fetching data for {symbol}. The external data provider may be experiencing issues."
            else:
                detailed_error = f"Analysis failed for {symbol}: {error_msg}"
            
            return SignalResult(
                symbol=symbol,
                price=0.0,
                signal="HOLD",
                confidence=0.0,
                technical_score=0.0,
                sentiment_score=0.0,
                risk_score=100.0,
                entry_price=0.0,
                stop_loss=0.0,
                take_profit=0.0,
                position_size=0,
                market_context=self._default_market_context(),
                technical_signals=self._default_technical_signals(),
                headlines=[f"Error processing {symbol}"],
                analysis=[],
                backtest_metrics={"error": error_msg},
                error=detailed_error
            )
    

    
    # ===================== BATCH PROCESSING =====================
    
    def analyze_portfolio(self, symbols: List[str], max_workers: int = 5) -> List[SignalResult]:
        """Analyze multiple stocks in parallel"""
        results = []
        
        print(f"Starting analysis of {len(symbols)} stocks...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all analysis tasks
            future_to_symbol = {
                executor.submit(self.get_comprehensive_signal, symbol): symbol 
                for symbol in symbols
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Failed to analyze {symbol}: {e}")
                    # Add error result
                    error_result = SignalResult(
                        symbol=symbol, price=0.0, signal="HOLD", confidence=0.0,
                        technical_score=0.0, sentiment_score=0.0, risk_score=100.0,
                        entry_price=0.0, stop_loss=0.0, take_profit=0.0, position_size=0,
                        market_context=self._default_market_context(),
                        technical_signals=self._default_technical_signals(),
                        headlines=[], analysis=[], backtest_metrics={}, error=str(e)
                    )
                    results.append(error_result)
        
        # Sort by confidence score
        results.sort(key=lambda x: x.confidence, reverse=True)
        
        print(f"✓ Portfolio analysis complete. {len(results)} stocks analyzed.")
        return results
    
    # ===================== REPORTING & UTILITIES =====================
    
    def generate_report(self, results: List[SignalResult]) -> str:
        """Generate comprehensive analysis report"""
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE STOCK ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Stocks Analyzed: {len(results)}") 

