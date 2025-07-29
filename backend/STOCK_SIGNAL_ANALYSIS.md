
# 📊 Stock Signal Analysis: RSI + Sentiment

This module analyzes stocks and generates **Buy / Sell / Hold** signals using:

- 💹 Technical Indicator: **RSI (Relative Strength Index)**
- 🧠 NLP Sentiment Model: HuggingFace (finance-tuned)

---

## ⚙️ How It Works

### 1. 📈 RSI Calculation
- Calculated over 14-day window using stock's closing prices.
- Signal:
  - **BUY**: RSI < 30 (oversold)
  - **SELL**: RSI > 70 (overbought)
  - **HOLD**: 30 <= RSI <= 70

---

### 2. 📰 News-Based Sentiment
- Fetches 3–5 recent news headlines.
  - **Indian Stocks**: Google RSS (MoneyControl, ET)
  - **US Stocks**: NewsAPI
- Each headline is sent to Hugging Face model:
  - `mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis`

### 3. 🧠 Sentiment Score Calculation
```python
score = sum(
  s["score"] if s["label"] == "POSITIVE" else -s["score"]
  for s in sentiments
) / len(sentiments)
```

### Sentiment Signal Logic:
| Score Threshold | Signal |
|-----------------|--------|
| > +0.3          | BUY    |
| < -0.3          | SELL   |
| otherwise       | HOLD   |

Confidence is:
```python
confidence = f"{abs(score)*100:.0f}%"
```

---

## 🔁 Final Signal Combination

| RSI Signal | Sentiment Signal | Final Signal |
|------------|------------------|--------------|
| BUY        | BUY              | BUY          |
| SELL       | SELL             | SELL         |
| HOLD       | BUY              | BUY          |
| BUY        | HOLD             | BUY          |
| SELL       | HOLD             | SELL         |
| BUY        | SELL             | HOLD         |
| SELL       | BUY              | HOLD         |

---

## 🧾 Output Sample
```json
{
  "symbol": "AAPL",
  "price": 195.24,
  "rsi": 48.1,
  "signal": "BUY",
  "confidence": "78%",
  "headlines": [...],
  "analysis": [...],
  "tech_signal": "BUY",
  "sentiment_signal": "BUY",
  "error": null
}
```

---

## 🧰 Dependencies
- yfinance
- requests
- BeautifulSoup
- HuggingFace Inference API
- dotenv

---
