# 🔌 Stock Sage API Documentation

Complete API reference for Stock Sage backend services.

## 🌐 Base URL

```
Development: http://localhost:8000
Production: https://api.stocksage.com
```

## 🔐 Authentication

### Google OAuth Flow

```http
POST /auth/google
Content-Type: application/json

{
  "credential": "google_jwt_token"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://lh3.googleusercontent.com/..."
  }
}
```

### Protected Endpoints

Include the JWT token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📊 Stock Analysis Endpoints

### Get Stock List

```http
GET /stocks
```

**Response:**

```json
{
  "stocks": [
    "AAPL",
    "GOOGL",
    "MSFT",
    "TSLA",
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS"
  ]
}
```

### Analyze Stock

```http
GET /analyze/{symbol}
```

**Parameters:**

- `symbol` (path): Stock symbol (e.g., "AAPL", "INFY.NS")

**Response:**

```json
{
  "symbol": "AAPL",
  "price": 195.24,
  "timestamp": "2025-01-15T12:00:00Z",
  "signal": "BUY",
  "confidence": 78.5,
  "confidence_text": "78.5%",
  "technical_analysis": {
    "rsi": 45.2,
    "rsi_signal": "NEUTRAL",
    "macd": 1.23,
    "macd_signal": 1.15,
    "macd_trend": "BULLISH",
    "bollinger_position": 0.65,
    "bollinger_signal": "NEUTRAL",
    "volume_ratio": 1.2,
    "volume_signal": "NORMAL",
    "volatility": 0.25,
    "volatility_percent": "25.0%",
    "price_momentum": 3.2,
    "momentum_signal": "POSITIVE",
    "support_level": 190.5,
    "resistance_level": 200.75,
    "technical_score": 65
  },
  "sentiment_analysis": {
    "sentiment_score": 45,
    "sentiment_signal": "POSITIVE",
    "news_count": 5,
    "headlines": [
      "Apple reports strong Q4 earnings",
      "iPhone sales exceed expectations",
      "Apple announces new product lineup"
    ],
    "detailed_analysis": [
      {
        "headline": "Apple reports strong Q4 earnings",
        "label": "POSITIVE",
        "score": 0.89,
        "numerical_score": 0.89,
        "confidence": 0.89
      }
    ]
  },
  "risk_analysis": {
    "risk_score": 35,
    "risk_level": "LOW",
    "position_size": 0.05,
    "entry_price": 195.24,
    "stop_loss": 185.5,
    "take_profit": 210.0,
    "risk_reward_ratio": 1.5
  },
  "market_context": {
    "volatility_regime": "MEDIUM",
    "trend_direction": "BULL",
    "sector_rotation": "GROWTH",
    "market_sentiment": "GREED"
  },
  "summary": {
    "overall_signal": "BUY",
    "buy_probability": 78.5,
    "sell_probability": 0,
    "hold_probability": 0,
    "technical_strength": "STRONG",
    "sentiment_strength": "MODERATE",
    "investment_grade": "B"
  }
}
```

### Get Fundamentals

```http
GET /fundamentals/{symbol}
```

**Parameters:**

- `symbol` (path): Stock symbol

**Response (Indian Stock):**

```json
{
  "symbol": "INFY",
  "market": "India",
  "company": "Infosys Limited",
  "sector": "IT Services & Consulting",
  "market_cap": "6,85,000 Cr",
  "pe": 28.5,
  "roce": 32.1,
  "roe": 31.8,
  "income_statement": [
    {
      "label": "Sales",
      "Mar 2024": "1,87,478",
      "Mar 2023": "1,64,177",
      "Mar 2022": "1,46,767"
    }
  ],
  "balance_sheet": [...],
  "cash_flow": [...],
  "shareholding_pattern": [
    {
      "Category": "Promoters",
      "Holding": "13.04%"
    },
    {
      "Category": "FII",
      "Holding": "35.67%"
    }
  ]
}
```

## 📈 Live Market Data

### Get Live Signals

```http
GET /live-signals
```

**Response:**

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "india": {
    "buy": [
      {
        "symbol": "INFY.NS",
        "price": 1650.50,
        "signal": "BUY",
        "confidence": 85.2,
        "change": 2.3
      }
    ],
    "sell": [
      {
        "symbol": "WIPRO.NS",
        "price": 425.75,
        "signal": "SELL",
        "confidence": 72.1,
        "change": -1.8
      }
    ]
  },
  "us": {
    "buy": [
      {
        "symbol": "AAPL",
        "price": 195.24,
        "signal": "BUY",
        "confidence": 78.5,
        "change": 1.2
      }
    ],
    "sell": [...]
  }
}
```

## 🎯 Options Trading

### Get Options Strategy P&L

```http
GET /options-strategy-pnl?ticker=AAPL&expiry=2024-02-16&strike=195
```

**Parameters:**

- `ticker` (query): Stock symbol
- `expiry` (query, optional): Expiry date
- `strike` (query, optional): Strike price

**Response:**

```json
{
  "ticker": "AAPL",
  "current_price": 195.24,
  "expiry": "2024-02-16",
  "selected_strike": 195.0,
  "atm_strike": 195.0,
  "available_expiries": ["2024-02-16", "2024-02-23", "2024-03-01"],
  "available_strikes": [185, 190, 195, 200, 205, 210],
  "strategies": [
    {
      "Price at Expiry": 180,
      "long_call": -5.5,
      "short_call": 5.5,
      "long_put": 14.5,
      "short_put": -14.5,
      "bull_call_spread": -2.0,
      "bear_put_spread": 12.0,
      "premium_breakdown": {
        "long_call": {
          "call_strike": 195,
          "call_premium": 5.5
        },
        "bull_call_spread": {
          "buy_strike": 195,
          "sell_strike": 200,
          "buy_premium": 5.5,
          "sell_premium": 3.5
        }
      }
    }
  ]
}
```

### Custom Options Strategy P&L

```http
POST /options-strategy-pnl-custom?ticker=AAPL&expiry=2024-02-16&strike=195
Content-Type: application/json

{
  "long_call": {
    "call_premium": 6.00
  },
  "bull_call_spread": {
    "buy_premium": 6.00,
    "sell_premium": 4.00
  }
}
```

## ❌ Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid stock symbol"
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication required"
}
```

### 404 Not Found

```json
{
  "detail": "Stock not found in supported list"
}
```

### 422 Validation Error

```json
{
  "detail": "Validation error",
  "errors": [
    {
      "loc": ["query", "strike"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Analysis failed: connection timeout"
}
```

## 🔄 Rate Limits

- **Stock Analysis**: 60 requests per minute per user
- **Live Signals**: 10 requests per minute per user
- **Options Calculations**: 100 requests per minute per user
- **Authentication**: 5 requests per minute per IP

## 📝 Request/Response Headers

### Common Request Headers

```http
Content-Type: application/json
Authorization: Bearer <jwt_token>
User-Agent: StockSage-Frontend/1.0
```

### Common Response Headers

```http
Content-Type: application/json
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1642248000
Cache-Control: public, max-age=300
```

## 🧪 Testing the API

### Using cURL

```bash
# Get stock list
curl -X GET "http://localhost:8000/stocks"

# Analyze stock
curl -X GET "http://localhost:8000/analyze/AAPL" \
  -H "Authorization: Bearer your_jwt_token"

# Get fundamentals
curl -X GET "http://localhost:8000/fundamentals/INFY.NS"
```

### Using Python requests

```python
import requests

# Analyze stock
response = requests.get(
    "http://localhost:8000/analyze/AAPL",
    headers={"Authorization": "Bearer your_jwt_token"}
)
data = response.json()
print(f"Signal: {data['signal']}, Confidence: {data['confidence']}")
```
