# 🎯 Options Trading Strategies Documentation

Comprehensive guide to the options trading strategies calculator in Stock Sage, covering all supported strategies, calculations, and API usage.

## 📋 Table of Contents

- [Overview](#overview)
- [Supported Strategies](#supported-strategies)
- [API Endpoints](#api-endpoints)
- [Strategy Calculations](#strategy-calculations)
- [Premium Handling](#premium-handling)
- [Risk Management](#risk-management)
- [Usage Examples](#usage-examples)
- [Frontend Integration](#frontend-integration)

## 🎯 Overview

The Options Strategies module provides comprehensive profit/loss calculations for various options trading strategies. It supports both market-based premiums from Yahoo Finance and custom premium inputs for scenario analysis.

### Key Features

- **12 Popular Strategies**: From basic calls/puts to complex spreads
- **Real-time Data**: Live options data from Yahoo Finance
- **Custom Premiums**: Override market prices for scenario testing
- **P&L Visualization**: Detailed profit/loss calculations across price ranges
- **Risk Metrics**: Breakeven points, maximum profit/loss analysis
- **Multi-expiry Support**: Analysis across different expiration dates

### Architecture

```
Options Module
├── Data Layer (Yahoo Finance API)
├── Strategy Engine (P&L Calculations)
├── Premium Manager (Market + Custom)
├── Risk Calculator (Greeks & Metrics)
└── API Layer (FastAPI Endpoints)
```

## 🎯 Supported Strategies

### 1. **Basic Strategies**

#### Long Call

- **Description**: Buy a call option expecting price to rise
- **Max Profit**: Unlimited (Price - Strike - Premium)
- **Max Loss**: Premium paid
- **Breakeven**: Strike + Premium
- **Market View**: Bullish

#### Long Put

- **Description**: Buy a put option expecting price to fall
- **Max Profit**: Strike - Premium (when price goes to 0)
- **Max Loss**: Premium paid
- **Breakeven**: Strike - Premium
- **Market View**: Bearish

#### Covered Call

- **Description**: Own stock + sell call option
- **Max Profit**: Strike - Stock Cost + Premium
- **Max Loss**: Stock Cost - Premium
- **Breakeven**: Stock Cost - Premium
- **Market View**: Neutral to slightly bullish

#### Protective Put

- **Description**: Own stock + buy put option
- **Max Profit**: Unlimited (Stock appreciation - Premium)
- **Max Loss**: Stock Cost - Strike + Premium
- **Breakeven**: Stock Cost + Premium
- **Market View**: Bullish with downside protection

### 2. **Volatility Strategies**

#### Straddle (Long)

- **Description**: Buy call and put at same strike
- **Max Profit**: Unlimited (large price moves in either direction)
- **Max Loss**: Total premiums paid
- **Breakeven**: Strike ± Total Premium
- **Market View**: High volatility expected

#### Strangle (Long)

- **Description**: Buy call and put at different strikes
- **Max Profit**: Unlimited (large price moves)
- **Max Loss**: Total premiums paid
- **Breakeven**: Lower Strike - Premium, Upper Strike + Premium
- **Market View**: High volatility, wider breakeven range

### 3. **Spread Strategies**

#### Bull Call Spread

- **Description**: Buy lower strike call + sell higher strike call
- **Max Profit**: Strike Difference - Net Premium
- **Max Loss**: Net premium paid
- **Breakeven**: Lower Strike + Net Premium
- **Market View**: Moderately bullish

#### Bear Put Spread

- **Description**: Buy higher strike put + sell lower strike put
- **Max Profit**: Strike Difference - Net Premium
- **Max Loss**: Net premium paid
- **Breakeven**: Higher Strike - Net Premium
- **Market View**: Moderately bearish

#### Bear Call Spread

- **Description**: Sell lower strike call + buy higher strike call
- **Max Profit**: Net premium received
- **Max Loss**: Strike Difference - Net Premium
- **Breakeven**: Lower Strike + Net Premium
- **Market View**: Moderately bearish

#### Bull Put Spread

- **Description**: Sell higher strike put + buy lower strike put
- **Max Profit**: Net premium received
- **Max Loss**: Strike Difference - Net Premium
- **Breakeven**: Higher Strike - Net Premium
- **Market View**: Moderately bullish

### 4. **Advanced Strategies**

#### Iron Condor

- **Description**: Sell put spread + sell call spread
- **Components**:
  - Sell put at lower strike
  - Buy put at even lower strike
  - Sell call at higher strike
  - Buy call at even higher strike
- **Max Profit**: Net premium received
- **Max Loss**: Strike Width - Net Premium
- **Breakeven**: Two points between the strikes
- **Market View**: Low volatility, range-bound

#### Butterfly Spread

- **Description**: Buy 2 options at outer strikes + sell 2 at middle strike
- **Max Profit**: Middle Strike - Lower Strike - Net Premium
- **Max Loss**: Net premium paid
- **Breakeven**: Two points around middle strike
- **Market View**: Very low volatility, price stays near middle strike

## 🔌 API Endpoints

### GET /options-strategy-pnl

Get P&L calculations for all strategies using market premiums.

**Parameters:**

- `ticker` (required): Stock symbol (e.g., "AAPL")
- `expiry` (optional): Expiry date in YYYY-MM-DD format
- `strike` (optional): Strike price for analysis

**Example Request:**

```bash
curl "http://localhost:8000/options-strategy-pnl?ticker=AAPL&expiry=2024-03-15&strike=180"
```

**Response Structure:**

```json
{
  "ticker": "AAPL",
  "current_price": 185.25,
  "atm_strike": 185.0,
  "selected_strike": 180.0,
  "expiry": "2024-03-15",
  "available_expiries": ["2024-03-15", "2024-03-22", "2024-04-19"],
  "available_strikes": [170, 175, 180, 185, 190, 195, 200],
  "strategies": [
    {
      "Price at Expiry": "$170.00",
      "long_call": -550.0,
      "long_put": 450.0,
      "bull_call_spread": -200.0,
      "iron_condor": 150.0,
      "premium_breakdown": {
        "long_call": {
          "call_strike": 180,
          "call_premium": 5.5
        }
      }
    }
  ],
  "premiums": {
    "calls": {
      "180.0": 5.5,
      "185.0": 3.25
    },
    "puts": {
      "180.0": 2.75,
      "185.0": 4.5
    }
  }
}
```

### POST /options-strategy-pnl-custom

Calculate P&L with custom premium inputs for scenario analysis.

**Request Body Options:**

1. **Legacy Format** (calls/puts by strike):

```json
{
  "calls": {
    "180": 6.0,
    "185": 3.5
  },
  "puts": {
    "180": 3.0,
    "185": 5.0
  }
}
```

2. **Strategy-Specific Format**:

```json
{
  "bull_call_spread": {
    "buy_premium": 6.0,
    "sell_premium": 3.5
  },
  "iron_condor": {
    "put_buy_premium": 1.5,
    "put_sell_premium": 3.0,
    "call_sell_premium": 3.25,
    "call_buy_premium": 1.75
  }
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8000/options-strategy-pnl-custom?ticker=AAPL&strike=180" \
  -H "Content-Type: application/json" \
  -d '{
    "bull_call_spread": {
      "buy_premium": 6.00,
      "sell_premium": 3.50
    }
  }'
```

## 🧮 Strategy Calculations

### Calculation Engine

The `OptionStrategies` class handles all P&L calculations with the following key methods:

```python
class OptionStrategies:
    def __init__(self, price, selected_strike, current_price, calls, puts,
                 user_premiums=None, user_strategy_premiums=None):
        self.price = price  # Price at expiry
        self.selected_strike = selected_strike  # Analysis strike
        self.current_price = current_price  # Current stock price
        self.calls = calls  # Call options data
        self.puts = puts  # Put options data
        self.user_premiums = user_premiums  # Custom premiums by strike
        self.user_strategy_premiums = user_strategy_premiums  # Custom strategy premiums
```

### Premium Resolution Logic

1. **Custom Strategy Premiums**: Check user_strategy_premiums first
2. **Custom Strike Premiums**: Check user_premiums by strike
3. **Market Data**: Use bid-ask midpoint or last price
4. **Fallback**: Use nearest available strike

### Example Calculation: Bull Call Spread

```python
def bull_call_spread(self):
    # Get custom premiums if provided
    strat_prem = self.user_strategy_premiums.get("bull_call_spread", {})

    lower = self.selected_strike
    upper = self.get_nearest_strike(lower + 10, is_call=True)

    # Premium resolution
    lower_price = strat_prem.get("buy_premium") or self.get_price(self.calls, lower, is_call=True)
    upper_price = strat_prem.get("sell_premium") or self.get_price(self.calls, upper, is_call=True)

    # P&L calculation
    profit = (max(self.price - lower, 0) - max(self.price - upper, 0) - (lower_price - upper_price)) * LOT_SIZE
    return round(profit, 3)
```

### Strike Selection Logic

- **ATM Strike**: Closest to current stock price
- **Strategy Strikes**: Based on ATM ± offset (typically 5-10 points)
- **Available Strikes**: Filtered to ±15 strikes around ATM
- **Price Range**: Analysis from 90% to 110% of selected strike

## 💰 Premium Handling

### Market Premium Sources

1. **Primary**: Bid-Ask Midpoint

   ```python
   if bid > 0 and ask > 0:
       premium = (bid + ask) / 2
   ```

2. **Fallback**: Last Traded Price

   ```python
   else:
       premium = last_price
   ```

3. **Nearest Strike**: If exact strike unavailable
   ```python
   closest_strike = min(available_strikes, key=lambda x: abs(x - target_strike))
   ```

### Custom Premium Integration

**Strike-Based Override:**

```python
# Override specific strikes
{
  "calls": {"180": 6.00, "185": 3.50},
  "puts": {"180": 3.00, "185": 5.00}
}
```

**Strategy-Based Override:**

```python
# Override specific strategy components
{
  "bull_call_spread": {
    "buy_premium": 6.00,    # Lower strike call
    "sell_premium": 3.50    # Higher strike call
  }
}
```

### Premium Validation

- **Range Check**: 0.01 to 50.00 per contract
- **Arbitrage Check**: Basic arbitrage validation
- **Strike Validation**: Must exist in options chain
- **Expiry Validation**: Must be valid expiration date

## ⚠️ Risk Management

### Position Sizing

- **Standard Lot**: 100 contracts per lot
- **Scaling**: All P&L multiplied by LOT_SIZE (100)
- **Rounding**: Results rounded to 2-3 decimal places

### Risk Metrics

**Maximum Loss Scenarios:**

```python
# Long strategies: Limited to premium paid
max_loss = premium_paid * LOT_SIZE

# Short strategies: Limited to strike difference minus premium
max_loss = (strike_diff - net_premium) * LOT_SIZE

# Undefined risk: Covered calls, naked options
max_loss = "Unlimited" or stock_value
```

**Breakeven Calculations:**

```python
# Long call: Strike + Premium
breakeven = strike + premium

# Bull spread: Lower strike + Net premium
breakeven = lower_strike + net_premium

# Straddle: Strike ± Total premium
breakeven_upper = strike + total_premium
breakeven_lower = strike - total_premium
```

### Risk Warnings

The system provides warnings for:

- **High Risk Strategies**: Naked options, undefined risk
- **Liquidity Issues**: Wide bid-ask spreads
- **Time Decay**: Strategies sensitive to theta
- **Volatility Risk**: Strategies sensitive to vega

## 💡 Usage Examples

### Basic Analysis

```python
# Get standard P&L analysis
response = requests.get(
    "http://localhost:8000/options-strategy-pnl",
    params={"ticker": "AAPL", "strike": 180}
)
data = response.json()

# Extract specific strategy P&L
for row in data["strategies"]:
    price = row["Price at Expiry"]
    bull_call_pnl = row["bull_call_spread"]
    print(f"At {price}: Bull Call Spread P&L = ${bull_call_pnl}")
```

### Custom Premium Analysis

```python
# Test different premium scenarios
custom_premiums = {
    "bull_call_spread": {
        "buy_premium": 7.00,  # Higher than market
        "sell_premium": 3.00   # Lower than market
    }
}

response = requests.post(
    "http://localhost:8000/options-strategy-pnl-custom",
    params={"ticker": "AAPL", "strike": 180},
    json=custom_premiums
)
```

### Strategy Comparison

```python
# Compare multiple strategies at specific price
target_price = 185
strategies_to_compare = ["long_call", "bull_call_spread", "straddle"]

for row in data["strategies"]:
    if row["Price at Expiry"] == f"${target_price}":
        for strategy in strategies_to_compare:
            pnl = row[strategy]
            print(f"{strategy}: ${pnl}")
```

## 🖥️ Frontend Integration

### Component Structure

```javascript
// OptionStrategies.jsx
const OptionStrategies = () => {
  const [ticker, setTicker] = useState("AAPL");
  const [stockInfo, setStockInfo] = useState(null);
  const [selectedStrategy, setSelectedStrategy] = useState("");
  const [customPremiums, setCustomPremiums] = useState({});

  // Fetch market data
  const fetchStrategyData = async (symbol, expiry, strike) => {
    const response = await axios.get(`/options-strategy-pnl`, {
      params: { ticker: symbol, expiry, strike },
    });
    setStockInfo(response.data);
  };

  // Update with custom premiums
  const fetchCustomStrategyData = async (premiums) => {
    const response = await axios.post(
      `/options-strategy-pnl-custom`,
      premiums,
      {
        params: { ticker, expiry: selectedExpiry, strike: selectedStrike },
      }
    );
    setStockInfo(response.data);
  };
};
```

### Premium Input Handling

```javascript
// Handle premium changes
const handlePremiumChange = (legKey, value) => {
  setCustomPremiums((prev) => ({
    ...prev,
    [legKey]: parseFloat(value),
  }));
};

// Submit on Enter key
const handlePremiumKeyDown = (e, legKey) => {
  if (e.key === "Enter") {
    const updatedPremiums = {
      [selectedStrategy]: {
        [legKey]: parseFloat(e.target.value),
      },
    };
    fetchCustomStrategyData(updatedPremiums);
  }
};
```

### Strategy Selection

```javascript
// Dynamic strategy selection
const availableStrategies = stockInfo?.strategies?.[0]
  ? Object.keys(stockInfo.strategies[0]).filter(
      (key) => key !== "Price at Expiry" && key !== "premium_breakdown"
    )
  : [];

// Strategy dropdown
<select value={selectedStrategy} onChange={handleStrategyChange}>
  {availableStrategies.map((strategy) => (
    <option key={strategy} value={strategy}>
      {formatStrategyName(strategy)}
    </option>
  ))}
</select>;
```

### P&L Visualization

```javascript
// P&L table with color coding
{
  stockInfo?.strategies?.map((row, idx) => (
    <tr key={idx}>
      <td>{row["Price at Expiry"]}</td>
      <td className={getPnLColorClass(row[selectedStrategy])}>
        ${Number(row[selectedStrategy]).toFixed(2)}
      </td>
    </tr>
  ));
}

// Color coding function
const getPnLColorClass = (pnl) => {
  const value = Number(pnl);
  if (value > 0) return "text-green";
  if (value < 0) return "text-red";
  return "";
};
```

## 🔧 Configuration & Customization

### Strategy Parameters

```python
# Configurable parameters
LOT_SIZE = 100  # Contracts per lot
STRIKE_OFFSET = 10  # Default strike spacing
ANALYSIS_RANGE = 0.2  # ±20% price range
MAX_STRIKES = 15  # Maximum strikes to analyze
```

### Adding New Strategies

1. **Add Strategy Method**:

```python
def new_strategy(self):
    # Get custom premiums
    strat_prem = self.user_strategy_premiums.get("new_strategy", {})

    # Calculate components
    premium1 = strat_prem.get("premium1") or self.get_price(...)
    premium2 = strat_prem.get("premium2") or self.get_price(...)

    # Calculate P&L
    profit = (payoff_calculation) * LOT_SIZE
    return round(profit, 3)
```

2. **Add to Premium Breakdown**:

```python
def premium_breakdown(self):
    # ... existing strategies ...

    breakdown["new_strategy"] = {
        "component1_strike": strike1,
        "component1_premium": premium1,
        "component2_strike": strike2,
        "component2_premium": premium2
    }
```

3. **Update Strategy List**:

```python
# In both endpoints
strategies_list = [
    "long_call", "long_put", "covered_call", "protective_put",
    "straddle", "strangle", "bull_call_spread", "bear_put_spread",
    "bear_call_spread", "bull_put_spread", "iron_condor",
    "butterfly_spread", "new_strategy"  # Add here
]
```

## 🚨 Error Handling

### Common Errors

1. **Invalid Ticker**: Stock not found or no options available
2. **Invalid Expiry**: Expiry date not in available list
3. **Invalid Strike**: Strike not in options chain
4. **Premium Errors**: Invalid premium values or format
5. **Calculation Errors**: Division by zero, invalid operations

### Error Response Format

```json
{
  "error": "Detailed error message",
  "status_code": 400,
  "details": {
    "ticker": "AAPL",
    "issue": "No options data available for this expiry"
  }
}
```

### Debugging Tips

1. **Check Options Availability**: Not all stocks have liquid options
2. **Verify Expiry Dates**: Use only available expiration dates
3. **Strike Validation**: Ensure strikes exist in the options chain
4. **Premium Ranges**: Keep premiums within reasonable bounds
5. **Market Hours**: Some data may be stale outside trading hours

## 📊 Performance Considerations

### Optimization Strategies

1. **Caching**: Cache options data for frequently requested symbols
2. **Batch Processing**: Process multiple strategies simultaneously
3. **Strike Filtering**: Limit analysis to relevant strike range
4. **Data Validation**: Validate inputs before expensive calculations

### Scalability

- **Concurrent Requests**: Handle multiple simultaneous calculations
- **Memory Management**: Efficient data structures for large options chains
- **Rate Limiting**: Respect Yahoo Finance API limits
- **Error Recovery**: Graceful handling of data source failures

---

This comprehensive documentation covers all aspects of the Options Strategies module, from basic usage to advanced customization. For additional support or feature requests, please refer to the [Contributing Guide](CONTRIBUTING.md).
