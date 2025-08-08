# 🛣️ API Routes Documentation

FastAPI router modules for Stock Sage backend services.

## 📁 Router Structure

```
routers/
├── option_strategies.py       # Options trading endpoints
├── users.py                  # User authentication & management
└── live_signal.py           # Real-time market signals
```

## 🔗 Route Modules

### **option_strategies.py**

Options trading and P&L calculation endpoints.

#### Endpoints:

- `GET /options-strategy-pnl` - Calculate P&L for options strategies
- `POST /options-strategy-pnl-custom` - Custom premium P&L calculations

#### Parameters:

```python
# GET /options-strategy-pnl
ticker: str          # Stock symbol (e.g., "AAPL")
expiry: str         # Expiry date (optional)
strike: float       # Strike price (optional)

# POST /options-strategy-pnl-custom
ticker: str          # Stock symbol
expiry: str         # Expiry date
strike: float       # Strike price
# Body: Custom premium data
{
  "strategy_name": {
    "buy_premium": float,
    "sell_premium": float,
    "call_premium": float,
    "put_premium": float
  }
}
```

#### Response Format:

```json
{
  "ticker": "AAPL",
  "current_price": 195.24,
  "expiry": "2024-02-16",
  "selected_strike": 195.0,
  "atm_strike": 195.0,
  "available_expiries": ["2024-02-16", "2024-02-23"],
  "available_strikes": [190, 195, 200, 205],
  "strategies": [
    {
      "Price at Expiry": 180,
      "long_call": -5.5,
      "short_call": 5.5,
      "long_put": 14.5,
      "premium_breakdown": {
        "long_call": {
          "call_strike": 195,
          "call_premium": 5.5
        }
      }
    }
  ]
}
```

### **users.py**

User authentication and profile management.

#### Endpoints:

- `POST /auth/google` - Google OAuth authentication
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update user profile
- `DELETE /auth/logout` - User logout

#### Authentication Flow:

```python
# Google OAuth
POST /auth/google
Body: {
  "credential": "google_jwt_token"
}

Response: {
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

### **live_signal.py**

Real-time market signals and analysis.

#### Endpoints:

- `GET /live-signals` - Get live market signals for top stocks
- `GET /market-overview` - Market summary and trends

#### Response Format:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
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
    "sell": [...]
  },
  "us": {
    "buy": [...],
    "sell": [...]
  }
}
```

## 🔐 Authentication Middleware

### **JWT Token Validation**

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### **Protected Routes**

```python
@router.get("/protected-endpoint")
async def protected_route(current_user: str = Depends(get_current_user)):
    return {"user_id": current_user, "data": "protected_data"}
```

## 📊 Error Handling

### **Standard Error Responses**

```python
# 400 Bad Request
{
  "detail": "Invalid stock symbol"
}

# 401 Unauthorized
{
  "detail": "Authentication required"
}

# 404 Not Found
{
  "detail": "Stock not found"
}

# 500 Internal Server Error
{
  "detail": "Analysis failed: connection timeout"
}
```

### **Custom Exception Handlers**

```python
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )
```

## 🔧 Development Guidelines

### **Adding New Routes**

1. Create new router file in `/routers/`
2. Define route functions with proper type hints
3. Add authentication decorators where needed
4. Include comprehensive error handling
5. Add route to main app in `app.py`
6. Update this documentation

### **Route Naming Conventions**

- Use kebab-case for URLs: `/options-strategy-pnl`
- Use descriptive names: `/live-signals` not `/signals`
- Group related endpoints: `/auth/login`, `/auth/logout`
- Use HTTP methods appropriately: GET for retrieval, POST for creation

### **Response Standards**

- Always return JSON responses
- Include timestamp for time-sensitive data
- Use consistent field naming (snake_case)
- Provide meaningful error messages
- Include pagination for large datasets

## 🧪 Testing Routes

```python
# Example test for options endpoint
def test_options_strategy_pnl():
    response = client.get("/options-strategy-pnl?ticker=AAPL")
    assert response.status_code == 200
    data = response.json()
    assert "ticker" in data
    assert "strategies" in data
    assert len(data["strategies"]) > 0
```

## 📈 Performance Considerations

- Use async/await for I/O operations
- Implement caching for expensive calculations
- Add rate limiting for external API calls
- Use connection pooling for database operations
- Monitor endpoint response times
