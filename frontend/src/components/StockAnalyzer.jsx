import React, { useState } from "react";
import { analyzeStock } from "../api/stockApi";
import "./StockAnalyzer.css";

const StockAnalyzer = ({ symbol, setSymbol, data, setData }) => {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false); // 👈 add loading state

  const handleAnalyze = async () => {
    setError("");
    setData(null);
    setLoading(true); // 👈 start loader

    try {
      const result = await analyzeStock(symbol.toUpperCase());
      setData(result);
    } catch (err) {
      console.error("Error analyzing stock:", err);
      setError("Failed to fetch data.");
    } finally {
      setLoading(false); // 👈 stop loader
    }
  };

  return (
    <div className="analyzer-container">
      <h2 className="analyzer-title">Stock Analyzer</h2>
      <input
        type="text"
        placeholder="Enter stock symbol (e.g., AAPL)"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
        className="input-field"
      />
      <button onClick={handleAnalyze} className="button-analyze">
        Analyze
      </button>

      {error && <p className="error-message">{error}</p>}

      {loading && (
        <div className="loader-container">
          <div className="loader"></div>
        </div>
      )}

      {data && !loading && (
        <div className="result-box">
          <h3>{data.symbol}</h3>
          <p>
            💲 Price: <strong>{data.price}</strong>
          </p>
          <p>
            📊 RSI: <strong>{data.rsi}</strong>
          </p>
          <p>
            📌 Signal: <strong>{data.signal}</strong>
          </p>
          <p>
            ✅ Confidence: <strong>{data.confidence}</strong>
          </p>

          <h4>📰 News Headlines:</h4>
          <ul>
            {data.news.map((headline, idx) => (
              <li key={idx}>{headline}</li>
            ))}
          </ul>

          <h4>🧠 Sentiment Analysis:</h4>
          <ul>
            {data.analysis.map((item, idx) => (
              <li key={idx}>
                <strong>{item.label}</strong> - {item.headline} (
                {(item.score * 100).toFixed(2)}%)
              </li>
            ))}
          </ul>

          <p>
            📈 Technical Signal: <strong>{data.tech_signal}</strong>
          </p>
          <p>
            🗣️ Sentiment Signal: <strong>{data.sentiment_signal}</strong>
          </p>
        </div>
      )}
    </div>
  );
};

export default StockAnalyzer;
