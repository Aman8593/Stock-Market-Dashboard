import React, { useEffect, useState } from "react";
import { getFundamentals } from "../api/stockApi";
import "./Fundamentals.css";

const Fundamentals = ({ symbol, setSymbol, data, setData, allSymbols }) => {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isIndian = (sym) => sym.trim().toUpperCase().endsWith(".NS");

  useEffect(() => {
    const storedData = localStorage.getItem("fundamentalsData");
    const storedSymbol = localStorage.getItem("fundamentalsSymbol");

    if (storedData && storedSymbol) {
      try {
        const parsedData = JSON.parse(storedData);
        if (parsedData && typeof parsedData === "object") {
          setSymbol(storedSymbol);
          setData(parsedData);
          return; // Exit early if we have stored data
        }
      } catch (error) {
        console.error("Error parsing localStorage fundamentals data:", error);
      }
    }

    // If no stored data, load INFY by default
    const loadDefaultFundamentals = async () => {
      setSymbol("INFY");
      setLoading(true);

      try {
        const response = await getFundamentals("INFY");
        setData(response);
        localStorage.setItem("fundamentalsData", JSON.stringify(response));
        localStorage.setItem("fundamentalsSymbol", "INFY");
      } catch (err) {
        console.error("Error loading default fundamentals:", err);
        setError("Failed to load default fundamentals data.");
      } finally {
        setLoading(false);
      }
    };

    loadDefaultFundamentals();
  }, []);

  // useEffect(() => {
  //   if (symbol) {
  //     handleSearch();
  //   }
  // }, [symbol]);

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
      localStorage.setItem("fundamentalsData", JSON.stringify(response));
      localStorage.setItem("fundamentalsSymbol", cleanedSymbol);
    } catch (err) {
      setError("Failed to fetch data.");
      console.error("❌ Error fetching fundamentals:", err);
    } finally {
      setLoading(false);
    }
  };

  const renderSummary = () => {
    if (!data) return null;
    const { company, market, sector, market_cap, pe, roce, roe } = data;

    return (
      <div className="valuation-summary" style={{ marginTop: 30 }}>
        <h3>📋 Valuation Summary</h3>
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
          <strong>Market Cap:</strong> {market_cap || "N/A"}
        </p>
        <p>
          <strong>P/E Ratio:</strong> {pe || "N/A"}
        </p>
        <p>
          <strong>ROCE:</strong> {roce ? `${roce}%` : "N/A"}
        </p>
        <p>
          <strong>ROE:</strong> {roe ? `${roe}%` : "N/A"}
        </p>
      </div>
    );
  };

  const renderFinancialSection = (section, title) => {
    if (!section) return null;

    // Handle Indian stocks format (array of objects with label property)
    if (Array.isArray(section)) {
      if (section.length === 0) return null;

      // Get all unique date keys from the first object (excluding 'label')
      const sampleObject = section[0];
      const years = Object.keys(sampleObject)
        .filter((key) => key !== "label")
        .map((date) => {
          // Handle different date formats
          if (date.includes("Mar") || date.includes("Dec")) {
            return date; // Keep as is for Indian format like "Mar 2024"
          } else if (date === "TTM") {
            return "TTM";
          } else {
            return new Date(date).getFullYear();
          }
        })
        .sort((a, b) => {
          if (a === "TTM") return 1; // TTM should be last
          if (b === "TTM") return -1;
          if (typeof a === "string" && typeof b === "string") {
            // For "Mar 2024" format, extract year and compare
            const yearA = parseInt(a.split(" ")[1]) || parseInt(a);
            const yearB = parseInt(b.split(" ")[1]) || parseInt(b);
            return yearA - yearB;
          }
          return a - b;
        });

      return (
        <div style={{ marginTop: 30 }}>
          <h3>{title}</h3>
          <div className="table-wrapper">
            <table className="financial-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  {years.map((year) => (
                    <th key={year}>{year}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {section.map((item, i) => (
                  <tr key={i}>
                    <td>{item.label}</td>
                    {years.map((year) => (
                      <td key={year}>
                        {item[year] !== null && item[year] !== undefined
                          ? item[year]
                          : "-"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    // Handle US stocks format (object with metric names as keys)
    if (typeof section === "object") {
      const metrics = Object.entries(section);
      if (metrics.length === 0) return null;

      const years = Object.keys(metrics[0][1]).map((date) =>
        new Date(date).getFullYear()
      );

      return (
        <div style={{ marginTop: 30 }}>
          <h3>{title}</h3>
          <div className="table-wrapper">
            <table className="financial-table">
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
        </div>
      );
    }

    return null;
  };

  const renderInvestors = (investors) => {
    if (!Array.isArray(investors) || investors.length === 0) return null;

    return (
      <div style={{ marginTop: 30 }}>
        <h3>Top Institutional Investors</h3>

        <div className="table-wrapper">
          <table className="simple-table">
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
      </div>
    );
  };

  const renderShareholding = (shareData) => {
    if (!Array.isArray(shareData) || shareData.length === 0) return null;

    return (
      <div style={{ marginTop: 30 }}>
        <h3>Shareholding Pattern</h3>
        <div className="table-wrapper">
          <table className="simple-table">
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
      </div>
    );
  };

  return (
    <div className="fundamentals-container">
      <h2 className="fundamentals-title">📊 Stock Fundamentals</h2>

      <p className="fundamentals-description">
        Enter a stock symbol to view its fundamentals. For Indian stocks and US
        stocks.
      </p>
      <div>
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
          {renderFinancialSection(data?.income_statement, "Income Statement")}
          {renderFinancialSection(data?.balance_sheet, "Balance Sheet")}
          {renderFinancialSection(data?.cash_flow, "Cash Flow")}
          {!isIndian(symbol) && renderInvestors(data?.investors)}
          {data?.market === "India" &&
            renderShareholding(data?.shareholding_pattern)}
        </>
      )}
    </div>
  );
};

export default Fundamentals;
