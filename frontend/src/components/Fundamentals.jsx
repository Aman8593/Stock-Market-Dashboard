import React, { useState } from "react";
import { getFundamentals } from "../api/stockApi";
import "./Fundamentals.css";

const Fundamentals = ({ symbol, data, setData }) => {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isIndian = (sym) => sym.trim().toUpperCase().endsWith(".NS");

  const handleSearch = async () => {
    setError("");
    setData(null);
    setLoading(true);

    const cleanedSymbol = symbol.trim().toUpperCase();
    if (!cleanedSymbol) {
      setError("Please enter a stock symbol.");
      return;
    }

    try {
      const response = await getFundamentals(cleanedSymbol);
      console.log("🔍 Response from API:", response); // ✅ LOG HERE
      setData(response);
    } catch (err) {
      setError("Failed to fetch data.");
      console.error("❌ Error fetching fundamentals:", err);
    } finally {
      setLoading(false);
    }
  };

  const renderSummary = () => {
    if (!data) return null;
    const { market, company, sector, marketCap } = data;

    return (
      <div style={{ marginTop: 30 }}>
        <p>
          <strong>Company:</strong> {company || "N/A"}
        </p>
        <p>
          <strong>Symbol:</strong> {symbol.toUpperCase()}
        </p>
        <p>
          <strong>Market:</strong> {market || "N/A"}
        </p>
        <p>
          <strong>Sector:</strong> {sector || "N/A"}
        </p>
        <p>
          <strong>Market Cap:</strong>{" "}
          {marketCap ? `$${(marketCap / 1e9).toFixed(2)} Billion` : "N/A"}
        </p>
      </div>
    );
  };

  const renderFinancialSection = (section, title) => {
    if (!section || typeof section !== "object") return null;

    const metrics = Object.entries(section);
    if (metrics.length === 0) return null;

    const years = Object.keys(metrics[0][1]).map((date) =>
      new Date(date).getFullYear()
    );

    return (
      <div style={{ marginTop: 30 }}>
        <h3>{title}</h3>
        <table>
          <thead>
            <tr>
              <th>Metric</th>
              {years.map((year) => (
                <th key={year}>{year}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {metrics.map(([label, values], i) => (
              <tr key={i}>
                <td>{label}</td>
                {years.map((year) => {
                  const dateKey = Object.keys(values).find((k) =>
                    k.includes(year)
                  );
                  return (
                    <td key={year}>
                      {dateKey && values[dateKey] !== null
                        ? values[dateKey].toLocaleString()
                        : "-"}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderInvestors = (investors) => {
    if (!Array.isArray(investors) || investors.length === 0) return null;

    return (
      <div style={{ marginTop: 30 }}>
        <h3>Top Institutional Investors</h3>
        <table>
          <thead>
            <tr>
              <th>Holder</th>
              <th>% Held</th>
              <th>Shares</th>
              <th>Value</th>
              <th>% Change</th>
              <th>Reported Date</th>
            </tr>
          </thead>
          <tbody>
            {investors.map((inv, i) => (
              <tr key={i}>
                <td>{inv.Holder}</td>
                <td>{(inv.pctHeld * 100).toFixed(2)}%</td>
                <td>{inv.Shares?.toLocaleString()}</td>
                <td>${inv.Value?.toLocaleString()}</td>
                <td>{(inv.pctChange * 100).toFixed(2)}%</td>
                <td>{new Date(inv["Date Reported"]).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderShareholding = (shareData) => {
    if (!Array.isArray(shareData) || shareData.length === 0) return null;

    return (
      <div style={{ marginTop: 30 }}>
        <h3>Shareholding Pattern</h3>
        <table>
          <thead>
            <tr>
              <th>Category</th>
              <th>Holding</th>
            </tr>
          </thead>
          <tbody>
            {shareData.map((row, i) => (
              <tr key={i}>
                <td>{row.Category}</td>
                <td>{row.Holding}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="fundamentals-container">
      <h2 className="fundamentals-title">📊 Stock Fundamentals</h2>

      <div>
        <input
          type="text"
          placeholder="Enter stock symbol (e.g., AAPL or INFY.NS)"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          className="input-field"
        />
        <button onClick={handleSearch} className="search-button">
          Search
        </button>
      </div>
      {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}

      {loading && (
        <div className="loader-container">
          <div className="loader"></div>
        </div>
      )}

      {data && (
        <>
          {renderSummary()}
          {renderFinancialSection(data.income_statement, "Income Statement")}
          {renderFinancialSection(data.balance_sheet, "Balance Sheet")}
          {renderFinancialSection(data.cash_flow, "Cash Flow")}
          {!isIndian(symbol) && renderInvestors(data.investors)}
          {data.market === "India" &&
            renderShareholding(data.shareholding_pattern)}
        </>
      )}
    </div>
  );
};

export default Fundamentals;
