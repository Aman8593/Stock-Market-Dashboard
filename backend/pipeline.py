import os
import requests
import yfinance as yf
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from stocks import US_STOCKS, INDIA_STOCKS, is_valid_stock
load_dotenv()
# Configuration
HF_MODEL = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
HF_TOKEN = os.getenv("HF_API_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ALPHA_VANTAGE_KEY = os.getenv("ALPHAVANTAGE_KEY")

# ---- Helper Functions ----
def calculate_rsi(prices, window=14):
    """Calculate RSI from price series"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs)).iloc[-1]

# ---- Scrapers ----
def scrape_news(symbol: str) -> List[str]:
    """Unified scraper for US/India markets with proper error handling"""
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        try:
            query = f"{symbol} site:moneycontrol.com OR site:economictimes.indiatimes.com"
            url = f"https://news.google.com/rss/search?q={query}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")

            headlines = [item.title.text for item in items[:5]]
            return headlines if headlines else [f"No headlines found for {symbol}"]

        except Exception as e:
            print(f"Error scraping Indian news: {str(e)}")
            return [f"News unavailable for {symbol}"]
    
    else:  # US stock
        try:
            response = requests.get(
                f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWS_API_KEY}",
                timeout=10
            )
            response.raise_for_status()
            news = response.json()
            
            if 'articles' not in news or not news['articles']:
                print(f"No articles found for {symbol}. Response: {news}")
                return [f"No recent news found for {symbol}"]
                
            return [a['title'] for a in news['articles'][:5]]
            
        except Exception as e:
            print(f"Error scraping US news: {str(e)}")
            return [f"News API error for {symbol}"]

# ---- Sentiment Analysis ----
def analyze_sentiment(headlines: List[str]) -> List[Dict]:
    """Analyze headlines using Hugging Face's finance-specific model"""
    results = []
    for headline in headlines:
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{HF_MODEL}",
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json={"inputs": headline},
                timeout=10
            )
            response.raise_for_status()
            prediction = response.json()[0][0]
            results.append({
                "headline": headline,
                "label": prediction["label"].upper(),  # POSITIVE/NEGATIVE
                "score": float(prediction["score"])
            })
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            results.append({
                "headline": headline,
                "label": "NEUTRAL",
                "score": 0.5
            })
    return results

# ---- Stock Data ----
def get_stock_data(symbol: str) -> Dict:
    """Fetch stock data using yfinance (US + India) and calculate RSI"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1mo")
        
        if hist.empty:
            return {"price": "N/A", "rsi": "N/A"}
        
        latest_price = round(hist["Close"].iloc[-1], 2)
        rsi = calculate_rsi(hist["Close"]) if len(hist) >= 14 else "N/A"
        
        return {
            "price": latest_price,
            "rsi": round(rsi, 2) if isinstance(rsi, float) else rsi
        }

    except Exception as e:
        print(f"Error fetching stock data: {str(e)}")
        return {"price": "N/A", "rsi": "N/A"}

# ---- Signal Generator ----
# def get_stock_signal(symbol: str) -> Dict:
#     """Complete stock analysis with guaranteed response structure"""
#     try:
#         # Get all data components
#         stock_data = get_stock_data(symbol)
#         headlines = scrape_news(symbol)
        
#         # Check for news availability
#         if not headlines or any(headline.startswith(("News unavailable", "No recent", "News API error")) for headline in headlines):
#             return {
#                 "symbol": symbol,
#                 "price": stock_data["price"],
#                 "rsi": stock_data["rsi"],
#                 "signal": "HOLD",
#                 "confidence": "0%",
#                 "headlines": headlines[:3] if headlines else ["No news available"],
#                 "analysis": [],
#                 "reason": "No valid news available",
#                 "error": None
#             }
        
#         # Analyze sentiment if news exists
#         sentiments = analyze_sentiment(headlines)
        
#         # Calculate signal strength
#         valid_sentiments = [s for s in sentiments if s["label"] in ["POSITIVE", "NEGATIVE"]]
#         if valid_sentiments:
#             buy_score = sum(
#                 s["score"] if s["label"] == "POSITIVE" else -s["score"] 
#                 for s in valid_sentiments
#             ) / len(valid_sentiments)
#             confidence = f"{abs(buy_score)*100:.0f}%"
#             signal = "BUY" if buy_score > 0.3 else "SELL" if buy_score < -0.3 else "HOLD"
#         else:
#             confidence = "0%"
#             signal = "HOLD"
        
#         return {
#             "symbol": symbol,
#             "price": stock_data["price"],
#             "rsi": stock_data["rsi"],
#             "signal": signal,
#             "confidence": confidence,
#             "headlines": headlines[:3],
#             "analysis": sentiments[:3],
#             "reason": None,
#             "error": None
#         }
        
#     except Exception as e:
#         print(f"Error generating signal for {symbol}: {str(e)}")
#         return {
#             "symbol": symbol,
#             "price": "N/A",
#             "rsi": "N/A",
#             "signal": "HOLD",
#             "confidence": "0%",
#             "headlines": [f"Error processing {symbol}"],
#             "analysis": [],
#             "reason": str(e),
#             "error": "Processing error"
#         }

def get_stock_signal(symbol: str) -> Dict:
    """Enhanced signal combining technical (RSI) + sentiment analysis"""
    try:
        # Stock price + RSI
        stock_data = get_stock_data(symbol)
        price = stock_data["price"]
        rsi = stock_data["rsi"]

        # News
        headlines = scrape_news(symbol)

        # Handle no-news edge case
        if not headlines or any(headline.startswith(("News unavailable", "No recent", "News API error")) for headline in headlines):
            sentiment_signal = "HOLD"
            confidence = "0%"
            sentiments = []
        else:
            sentiments = analyze_sentiment(headlines)
            valid_sentiments = [s for s in sentiments if s["label"] in ["POSITIVE", "NEGATIVE"]]

            # Compute sentiment score
            if valid_sentiments:
                score = sum(s["score"] if s["label"] == "POSITIVE" else -s["score"] for s in valid_sentiments) / len(valid_sentiments)
                sentiment_signal = "BUY" if score > 0.3 else "SELL" if score < -0.3 else "HOLD"
                confidence = f"{abs(score)*100:.0f}%"
            else:
                sentiment_signal = "HOLD"
                confidence = "0%"

        # Determine RSI-based technical signal
        if isinstance(rsi, float):
            if rsi < 30:
                tech_signal = "BUY"
            elif rsi > 70:
                tech_signal = "SELL"
            else:
                tech_signal = "HOLD"
        else:
            tech_signal = "HOLD"

        # Combine both signals
        if tech_signal == sentiment_signal:
            final_signal = tech_signal
        elif "HOLD" in [tech_signal, sentiment_signal]:
            final_signal = tech_signal if sentiment_signal == "HOLD" else sentiment_signal
        else:
            final_signal = "HOLD"

        return {
            "symbol": symbol,
            "price": price,
            "rsi": rsi,
            "signal": final_signal,
            "confidence": confidence,
            "headlines": headlines[:3],
            "analysis": sentiments[:3] if sentiments else [],
            "tech_signal": tech_signal,
            "sentiment_signal": sentiment_signal,
            "error": None
        }

    except Exception as e:
        print(f"Error generating signal for {symbol}: {str(e)}")
        return {
            "symbol": symbol,
            "price": "N/A",
            "rsi": "N/A",
            "signal": "HOLD",
            "confidence": "0%",
            "headlines": [f"Error processing {symbol}"],
            "analysis": [],
            "error": str(e)
        }

# ---- Stock List ----
def get_top_stocks(market: str) -> List[str]:
    """Get top 50 stocks by market cap"""
    return US_STOCKS if market == "us" else INDIA_STOCKS