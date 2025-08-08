# 📊 Technical Indicator Functions Documentation

This document provides explanations, code snippets, and practical use cases for several commonly used technical analysis indicators.

---

## 1. `calculate_rsi`

### 📌 Purpose

The Relative Strength Index (RSI) is a momentum oscillator used in technical analysis to measure the speed and change of price movements.

### 🧠 How it Works

```python
def calculate_rsi(self, prices: pd.Series, window: int = 14) -> float:
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
```

### 🎯 Use Cases

- RSI > 70 → Overbought
- RSI < 30 → Oversold
- Detect divergences and confirm trends

---

## 2. `calculate_macd`

### 📌 Purpose

The MACD (Moving Average Convergence Divergence) is a trend-following momentum indicator showing the relationship between two EMAs.

### 🧠 How it Works

```python
def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
    if len(prices) < slow + signal:
        return 0.0, 0.0, 0.0

    exp1 = prices.ewm(span=fast).mean()
    exp2 = prices.ewm(span=slow).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal).mean()
    histogram = macd - signal_line

    return float(macd.iloc[-1]), float(signal_line.iloc[-1]), float(histogram.iloc[-1])
```

### 🎯 Use Cases

- MACD crossovers
- Histogram divergence
- Trend strength analysis

---

## 3. `calculate_bollinger_bands`

### 📌 Purpose

Bollinger Bands are volatility bands placed above and below a moving average. They expand and contract based on price volatility.

### 🧠 How it Works

```python
def calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, std_dev: int = 2) -> Tuple[float, float, float, float]:
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
```

### 🎯 Use Cases

- Detect overbought/oversold conditions
- Volatility tracking
- Breakout strategies

---

## 4. `calculate_volume_analysis`

### 📌 Purpose

Evaluates recent trading volume against historical averages to gauge investor interest.

### 🧠 How it Works

```python
def calculate_volume_analysis(self, hist: pd.DataFrame) -> float:
    if len(hist) < 10:
        return 1.0

    recent_volume = hist['Volume'].tail(5).mean()
    avg_volume = hist['Volume'].rolling(20).mean().iloc[-1]

    return float(recent_volume / avg_volume) if avg_volume > 0 else 1.0
```

### 🎯 Use Cases

- Confirm price movements
- Detect accumulation/distribution
- Validate breakouts

---

## 5. `calculate_volatility`

### 📌 Purpose

Calculates the annualized volatility of price returns, which reflects the riskiness of an asset.

### 🧠 How it Works

```python
def calculate_volatility(self, prices: pd.Series, window: int = 30) -> float:
    if len(prices) < window:
        return 0.2

    returns = prices.pct_change().dropna()
    volatility = returns.rolling(window).std().iloc[-1] * np.sqrt(252)

    return float(volatility) if not pd.isna(volatility) else 0.2
```

### 🎯 Use Cases

- Risk assessment
- Portfolio optimization
- Options pricing

---

## 6. `calculate_support_resistance`

### 📌 Purpose

Identifies dynamic support and resistance levels from recent high and low price data.

### 🧠 How it Works

```python
def calculate_support_resistance(self, hist: pd.DataFrame, window: int = 20) -> Tuple[float, float]:
    if len(hist) < window:
        current_price = float(hist['Close'].iloc[-1])
        return current_price * 0.95, current_price * 1.05

    highs = hist['High'].rolling(window).max()
    lows = hist['Low'].rolling(window).min()

    resistance = float(highs.iloc[-1])
    support = float(lows.iloc[-1])

    return support, resistance
```

### 🎯 Use Cases

- Trade planning (entry/exit)
- Risk management
- Detecting price breakouts

---

# 📈 Market Context & Risk Management Functions

This section documents functions used to assess **market conditions**, determine **position sizing**, and evaluate **trading risk** based on volatility, technical indicators, and broader market context.

---

## 7. `get_market_context`

### 📌 Purpose

Analyzes the broader market context using index data (e.g., NIFTY 50 or S&P 500) to determine the overall trading environment.

### 🧠 How it Works

```python
def get_market_context(self, symbol: str) -> MarketContext:
    ...
```

- **Index Selection**: Based on the symbol suffix (`.NS`, `.BO`, etc.)
- **Volatility Regime**: Uses the `calculate_volatility()` method on index data to classify as `HIGH`, `MEDIUM`, or `LOW`.
- **Trend Direction**:
  - BULL: Price > 50-SMA > 200-SMA
  - BEAR: Price < 50-SMA < 200-SMA
  - SIDEWAYS: otherwise
- **Sector Rotation & Sentiment**: Hardcoded placeholders for now.

### 🎯 Use Cases

- Strategy filters (e.g., only trade during BULL regimes)
- Adaptive risk or leverage adjustment
- Macro environment modeling

---

## 8. `_default_market_context`

### 📌 Purpose

Returns a neutral default `MarketContext` in case of errors or missing data.

### 🧠 How it Works

```python
def _default_market_context(self) -> MarketContext:
    ...
```

Returns:

- Volatility: MEDIUM
- Trend: SIDEWAYS
- Sector: GROWTH
- Sentiment: NEUTRAL

---

## 9. `calculate_position_sizing`

### 📌 Purpose

Determines how many shares to buy based on **account size**, **volatility**, and **risk per trade** using **Kelly-like sizing**.

### 🧠 How it Works

```python
def calculate_position_sizing(self, price: float, volatility: float, account_size: float = 10000) -> Dict[str, float]:
    ...
```

- Risk per trade = 2% of account
- Stop-loss = 2 × daily volatility × price
- Position size = `risk / stop-loss distance`
- Calculates:
  - Number of shares
  - Position value
  - Stop-loss and take-profit targets

### 🎯 Use Cases

- Volatility-adjusted risk
- Systematic trade sizing
- Risk-reward optimization

---

## 10. `calculate_risk_score`

### 📌 Purpose

Computes a **comprehensive risk score** (0–100) based on volatility, technical signals, and market conditions.

### 🧠 How it Works

```python
def calculate_risk_score(self, technical_signals: TechnicalSignals, market_context: MarketContext) -> float:
    ...
```

- **Volatility Risk** (0–30 points)
- **Technical Risk** (0–25 points):
  - Extreme RSI
  - BB extremes
  - Low volume
- **Market Risk** (0–25 points):
  - High volatility regime
  - Bearish trend
- **Liquidity Risk** (0–20 points)

### 🎯 Use Cases

- Trade filtering (avoid trades above certain risk score)
- Portfolio rebalancing
- Dynamic hedging strategy

---
