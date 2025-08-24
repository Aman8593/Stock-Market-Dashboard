import React, { useState, useEffect, useCallback } from "react";
import {
  analyzeStock,
  getLiveSignals,
  getAnalysisStatus,
  forceAnalysis,
} from "../api/stockApi";
import "./StockAnalyzer.css";

const StockAnalyzer = ({ symbol, setSymbol, data, setData, allSymbols }) => {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState({
    market: true,
    stock: false,
  });
  const [marketData, setMarketData] = useState(null);
  const [analysisStatus, setAnalysisStatus] = useState({
    analyzing: false,
    progress: 0,
    message: "",
    estimatedTime: "",
    lastUpdated: null,
  });

  // Fetch market data with new analysis system
  const fetchMarketData = useCallback(async (forceRefresh = false) => {
    try {
      setLoading((prev) => ({ ...prev, market: true }));
      setError("");

      const result = await getLiveSignals();

      if (result.success) {
        // Successfully got data
        console.log("Market data received:", result.data); // Debug log

        // Validate data structure
        if (result.data && typeof result.data === "object") {
          // Extract metadata if present
          const metadata = result.data.metadata || {};
          const marketData = { ...result.data };
          delete marketData.metadata; // Remove metadata from market data

          setMarketData(marketData);
          setAnalysisStatus({
            analyzing: metadata.is_analyzing || false,
            progress: metadata.analysis_progress || 100,
            message: metadata.message || "Data loaded successfully",
            estimatedTime: metadata.is_analyzing ? "2-3 minutes" : "",
            lastUpdated: metadata.last_updated || new Date().toISOString(),
            cacheAge: metadata.cache_age_hours || 0,
            status: metadata.status || "ready",
          });

          // Cache the successful result
          localStorage.setItem("marketData", JSON.stringify(marketData));
          localStorage.setItem("lastMarketFetch", new Date().toISOString());

          // If analysis is still running, set up polling
          if (metadata.is_analyzing) {
            setTimeout(() => {
              fetchMarketData();
            }, 30000); // Check again in 30 seconds
          }
        } else {
          console.error("Invalid data structure received:", result.data);
          setError("Invalid data received from server");
        }
      } else if (result.analyzing) {
        // Analysis in progress (first time or no cached data)
        setAnalysisStatus({
          analyzing: true,
          progress: result.progress,
          message: result.message,
          estimatedTime: result.estimatedTime,
          lastUpdated: new Date().toISOString(),
        });

        // Try to load cached data while analysis is running
        const cachedData = localStorage.getItem("marketData");
        if (cachedData && !forceRefresh) {
          try {
            const parsedData = JSON.parse(cachedData);
            setMarketData(parsedData);
          } catch (err) {
            console.error("Error parsing cached data:", err);
          }
        }

        // Set up retry after specified time
        const retryDelay = result.checkAgainIn === "30 seconds" ? 30000 : 60000;
        setTimeout(() => {
          fetchMarketData();
        }, retryDelay);
      }
    } catch (err) {
      console.error("Error fetching market data:", err);
      setError("Failed to load market signals. Please try again.");
      setAnalysisStatus({
        analyzing: false,
        progress: 0,
        message: "Error loading data",
        estimatedTime: "",
        lastUpdated: new Date().toISOString(),
      });
    } finally {
      setLoading((prev) => ({ ...prev, market: false }));
    }
  }, []);

  // Load market data on component mount
  useEffect(() => {
    const lastFetch = localStorage.getItem("lastMarketFetch");
    const cachedData = localStorage.getItem("marketData");

    // Check if we should use cached data (less than 24 hours old)
    const shouldUseCached =
      lastFetch &&
      new Date() - new Date(lastFetch) < 24 * 60 * 60 * 1000 &&
      cachedData;

    if (shouldUseCached) {
      try {
        const parsedData = JSON.parse(cachedData);
        setMarketData(parsedData);
        setLoading((prev) => ({ ...prev, market: false }));
        setAnalysisStatus({
          analyzing: false,
          progress: 100,
          message: "Loaded from cache",
          estimatedTime: "",
          lastUpdated: lastFetch,
        });

        // Still check for updates in background
        setTimeout(() => fetchMarketData(), 2000);
      } catch (err) {
        console.error("Error parsing cached market data:", err);
        fetchMarketData();
      }
    } else {
      fetchMarketData();
    }
  }, [fetchMarketData]);

  // Force refresh handler
  const handleForceRefresh = async () => {
    try {
      setError("");
      await forceAnalysis();
      setAnalysisStatus({
        analyzing: true,
        progress: 0,
        message: "Starting fresh analysis...",
        estimatedTime: "2-3 minutes",
        lastUpdated: new Date().toISOString(),
      });

      // Start polling for results
      setTimeout(() => fetchMarketData(true), 5000);
    } catch (err) {
      console.error("Error forcing analysis:", err);
      setError("Failed to start analysis. Please try again.");
    }
  };

  // Load last analyzed stock from localStorage or default to INFY
  useEffect(() => {
    const storedData = localStorage.getItem("lastStockData");
    const storedSymbol = localStorage.getItem("lastStockSymbol");

    if (storedData && storedSymbol) {
      try {
        const parsedData = JSON.parse(storedData);
        if (parsedData && typeof parsedData === "object") {
          setSymbol(storedSymbol);
          setData(parsedData);
          return; // Exit early if we have stored data
        }
      } catch (error) {
        console.error("Error parsing localStorage data:", error);
      }
    }

    // If no stored data, load INFY by default
    const loadDefaultStock = async () => {
      setSymbol("INFY");
      setLoading((prev) => ({ ...prev, stock: true }));

      try {
        const result = await analyzeStock("INFY");
        setData(result);
        localStorage.setItem("lastStockData", JSON.stringify(result));
        localStorage.setItem("lastStockSymbol", "INFY");
      } catch (err) {
        console.error("Error loading default stock:", err);
        setError("Failed to load default stock data.");
      } finally {
        setLoading((prev) => ({ ...prev, stock: false }));
      }
    };

    loadDefaultStock();
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
        <div className="signals-header">
          <h2>Live Market Signals</h2>
          <div className="signals-controls">
            {analysisStatus.lastUpdated && (
              <span className="last-updated">
                Last updated:{" "}
                {new Date(analysisStatus.lastUpdated).toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>

        {/* Analysis Status Display */}
        {(analysisStatus.analyzing || analysisStatus.cacheAge > 24) && (
          <div className="analysis-status">
            <div className="status-content">
              {analysisStatus.analyzing && (
                <div className="progress-container">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${analysisStatus.progress}%` }}
                    ></div>
                  </div>
                  <span className="progress-text">
                    {analysisStatus.progress}%
                  </span>
                </div>
              )}
              <p className="status-message">
                {analysisStatus.analyzing ? (
                  <>
                    📊 {analysisStatus.message}
                    {analysisStatus.estimatedTime && (
                      <span className="estimated-time">
                        {" "}
                        (ETA: {analysisStatus.estimatedTime})
                      </span>
                    )}
                  </>
                ) : (
                  <>
                    ⏰ Data is {analysisStatus.cacheAge?.toFixed(1)}h old -
                    Fresh analysis will start automatically
                  </>
                )}
              </p>
              {analysisStatus.lastUpdated && (
                <p className="last-updated-detail">
                  Last updated:{" "}
                  {new Date(analysisStatus.lastUpdated).toLocaleString()}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading.market && !analysisStatus.analyzing && (
          <div className="loader-container">
            <div className="loader"></div>
            <p>Loading market data...</p>
          </div>
        )}

        {/* Market Data Display */}
        {marketData && !loading.market && (
          <div className="markets-grid-container">
            <div className="grid-container">
              {/* Indian Market - Buy */}
              <div className="market-table">
                <h3>Indian Market - 📈 Top Buys</h3>
                <MarketTable
                  stocks={marketData?.india?.buy || []}
                  currency="₹"
                  loading={loading.market}
                />
              </div>

              {/* Indian Market - Sell */}
              <div className="market-table">
                <h3>Indian Market - 📉 Top Sells</h3>
                <MarketTable
                  stocks={marketData?.india?.sell || []}
                  currency="₹"
                  loading={loading.market}
                />
              </div>

              {/* US Market - Buy */}
              <div className="market-table">
                <h3>US Market - 📈 Top Buys</h3>
                <MarketTable
                  stocks={marketData?.us?.buy || []}
                  currency="$"
                  loading={loading.market}
                />
              </div>

              {/* US Market - Sell */}
              <div className="market-table">
                <h3>US Market - 📉 Top Sells</h3>
                <MarketTable
                  stocks={marketData?.us?.sell || []}
                  currency="$"
                  loading={loading.market}
                />
              </div>
            </div>
          </div>
        )}

        {/* No Data State - This should rarely show now */}
        {!marketData && !loading.market && !analysisStatus.analyzing && (
          <div className="no-data-container">
            <p>
              🔄 Loading market data... Analysis is running in the background.
            </p>
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

  // Helper function to format signal display
  const formatSignal = (signal) => {
    switch (signal) {
      case "STRONG_BUY":
        return "BUY";
      case "STRONG_SELL":
        return "SELL";
      default:
        return signal;
    }
  };

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
            <td className="market-table-td">{formatSignal(stock.signal)}</td>
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
