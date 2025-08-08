import React, { useState, useEffect } from "react";
import { analyzeStock, getLiveSignals } from "../api/stockApi";
import "./StockAnalyzer.css";

const StockAnalyzer = ({ symbol, setSymbol, data, setData, allSymbols }) => {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState({
    market: true,
    stock: false,
  });
  const [marketData, setMarketData] = useState(null);

  // Load market data on component mount and daily
  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        setLoading((prev) => ({ ...prev, market: true }));
        const result = await getLiveSignals();
        setMarketData(result);

        localStorage.setItem("marketData", JSON.stringify(result));
        localStorage.setItem("lastMarketFetch", new Date().toISOString());
      } catch (err) {
        console.error("Error fetching market data:", err);
        setError("Failed to load market signals");
      } finally {
        setLoading((prev) => ({ ...prev, market: false }));
      }
    };

    const lastFetch = localStorage.getItem("lastMarketFetch");
    const cachedData = localStorage.getItem("marketData");

    const shouldRefetch =
      !lastFetch || new Date() - new Date(lastFetch) > 24 * 60 * 60 * 1000;

    if (!shouldRefetch && cachedData) {
      try {
        const parsedData = JSON.parse(cachedData);
        setMarketData(parsedData);
        setLoading((prev) => ({ ...prev, market: false }));
      } catch (err) {
        console.error("Error parsing cached market data:", err);
        fetchMarketData();
      }
    } else {
      fetchMarketData();
    }
  }, []);

  // Load last analyzed stock from localStorage
  useEffect(() => {
    const storedData = localStorage.getItem("lastStockData");
    const storedSymbol = localStorage.getItem("lastStockSymbol");

    if (storedData && storedSymbol) {
      try {
        const parsedData = JSON.parse(storedData);
        if (parsedData && typeof parsedData === "object") {
          setSymbol(storedSymbol);
          setData(parsedData);
        }
      } catch (error) {
        console.error("Error parsing localStorage data:", error);
      }
    }
  }, []);

  const handleAnalyze = async () => {
    setError("");
    setLoading((prev) => ({ ...prev, stock: true }));

    const cleanedSymbol = symbol.trim().toUpperCase();
    if (!cleanedSymbol) {
      setError("Please enter a stock symbol.");
      return;
    }

    try {
      const result = await analyzeStock(cleanedSymbol);
      setData(result);
      localStorage.setItem("lastStockData", JSON.stringify(result));
      localStorage.setItem("lastStockSymbol", cleanedSymbol);
    } catch (err) {
      console.error("Error analyzing stock:", err);
      setError("Failed to fetch stock data.");
    } finally {
      setLoading((prev) => ({ ...prev, stock: false }));
    }
  };

  return (
    <div className="analyzer-container">
      {/* Market Signals Section */}
      <div className="live-signals-container">
        <h2>Live Market Signals</h2>
        {loading.market && (
          <div className="loader-container">
            <div className="loader"></div>
            <p>Loading market data...</p>
          </div>
        )}

        {marketData && !loading.market && (
          <div className="markets-grid-container">
            <div className="grid-container">
              {/* Indian Market - Buy */}
              <div className="market-table">
                <h3>Indian Market - 📈 Top Buys</h3>
                <MarketTable
                  stocks={marketData.india.buy}
                  currency="₹"
                  loading={loading.market}
                />
              </div>

              {/* Indian Market - Sell */}
              <div className="market-table">
                <h3>Indian Market - 📉 Top Sells</h3>
                <MarketTable
                  stocks={marketData.india.sell}
                  currency="₹"
                  loading={loading.market}
                />
              </div>

              {/* US Market - Buy */}
              <div className="market-table">
                <h3>US Market - 📈 Top Buys</h3>
                <MarketTable
                  stocks={marketData.us.buy}
                  currency="$"
                  loading={loading.market}
                />
              </div>

              {/* US Market - Sell */}
              <div className="market-table">
                <h3>US Market - 📉 Top Sells</h3>
                <MarketTable
                  stocks={marketData.us.sell}
                  currency="$"
                  loading={loading.market}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Individual Stock Analysis Section */}
      <div className="stock-analysis-section">
        <h2 className="analyzer-title">Stock Analyzer</h2>
        <p className="analysis-description">
          Enter a stock symbol to view its Stock News and Technical Analysis.
          For Indian stocks and US stocks.
        </p>
        <div className="analysis-controls">
          <input
            type="text"
            list="stock-options"
            placeholder="Enter stock symbol (e.g., AAPL or INFY)"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="input-field"
          />
          <datalist id="stock-options">
            {allSymbols.map((sym, i) => (
              <option key={i} value={sym} />
            ))}
          </datalist>

          <button
            onClick={handleAnalyze}
            className="button-analyze"
            disabled={loading.stock}
          >
            {loading.stock ? "Analyzing..." : "Analyze"}
          </button>
        </div>

        {error && <p className="error-message">{error}</p>}

        {loading.stock && (
          <div className="loader-container">
            <div className="loader"></div>
          </div>
        )}

        {data && !loading.stock && <StockAnalysisResult data={data} />}
      </div>
    </div>
  );
};

// Reusable Market Table Component
const MarketTable = ({ stocks, currency, loading }) => {
  if (loading) return <div>Loading...</div>;
  if (!stocks || stocks.length === 0) return <div>No data available</div>;

  return (
    <table className="market-table-table">
      <thead>
        <tr>
          <th className="market-table-th">Symbol</th>
          <th className="market-table-th">Price ({currency})</th>
          <th className="market-table-th">Signal</th>
          <th className="market-table-th">Confidence</th>
          <th className="market-table-th">Change</th>
        </tr>
      </thead>
      <tbody>
        {stocks.map((stock, index) => (
          <tr key={`${currency}-${index}`}>
            <td className="market-table-td">
              {stock.symbol.replace(".NS", "")}
            </td>
            <td className="market-table-td">
              {stock.price?.toFixed(2) ?? "N/A"}
            </td>
            <td className="market-table-td">{stock.signal}</td>
            <td className="market-table-td">
              {stock.confidence?.toFixed(2) ?? "N/A"}%
            </td>
            <td
              className={`market-table-td ${
                stock.change >= 0 ? "positive" : "negative"
              }`}
            >
              {stock.change >= 0 ? "↑" : "↓"}{" "}
              {Math.abs(stock.change)?.toFixed(2) ?? "N/A"}%
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

// Reusable Stock Analysis Component
const StockAnalysisResult = ({ data }) => {
  return (
    <div className="result-box">
      <h3>{data.symbol}</h3>
      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-label">💲 Price:</span>
          <span className="stat-value">{data.price ?? "N/A"}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">📊 RSI:</span>
          <span className="stat-value">
            {data?.technical_analysis?.rsi ?? "N/A"}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">📌 Signal:</span>
          <span className="stat-value">{data.signal}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">✅ Confidence:</span>
          <span className="stat-value">{data.confidence_text}</span>
        </div>
      </div>

      <div className="news-section">
        <h4>📰 News Headlines</h4>
        <ul>
          {data?.sentiment_analysis?.headlines?.length > 0 ? (
            data.sentiment_analysis.headlines.map((headline, idx) => (
              <li key={idx}>{headline}</li>
            ))
          ) : (
            <li>No headlines found</li>
          )}
        </ul>
      </div>

      <div className="sentiment-section">
        <h4>🧠 Sentiment Analysis</h4>
        <ul>
          {data?.sentiment_analysis?.detailed_analysis?.length > 0 ? (
            data.sentiment_analysis.detailed_analysis.map((item, idx) => (
              <li key={idx}>
                <strong>{item.label}</strong> - {item.headline} (
                {(item.score * 100).toFixed(2)}%)
              </li>
            ))
          ) : (
            <li>No analysis found</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default StockAnalyzer;
