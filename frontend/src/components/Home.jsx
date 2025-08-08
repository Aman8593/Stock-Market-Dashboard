import React, { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./Navbar.jsx";
import StockAnalyzer from "./StockAnalyzer.jsx";
import Fundamentals from "./Fundamentals.jsx";
import OptionStrategies from "./OptionStrategies.jsx";

function Home() {
  const [allSymbols, setAllSymbols] = useState([]);
  const [stockSymbol, setStockSymbol] = useState("");
  const [stockData, setStockData] = useState(null);
  const [symbol, setSymbol] = useState("");
  const [data, setData] = useState(null);

  // Fetch all stocks from the combined endpoint
  useEffect(() => {
    const fetchAllSymbols = async () => {
      try {
        const res = await fetch(`http://localhost:8000/stocks`);
        const json = await res.json();
        setAllSymbols(json.stocks || []);
      } catch (err) {
        console.error("Error fetching stock list:", err);
        setAllSymbols([]);
      }
    };

    fetchAllSymbols();
  }, []);

  return (
    <div className="app-container">
      <Navbar />

      <Routes>
        <Route
          path="/"
          element={
            <StockAnalyzer
              symbol={stockSymbol}
              setSymbol={setStockSymbol}
              data={stockData}
              setData={setStockData}
              allSymbols={allSymbols}
            />
          }
        />
        <Route
          path="/news_analysis"
          element={
            <StockAnalyzer
              symbol={stockSymbol}
              setSymbol={setStockSymbol}
              data={stockData}
              setData={setStockData}
              allSymbols={allSymbols}
            />
          }
        />
        <Route
          path="/fundamentals"
          element={
            <Fundamentals
              symbol={symbol}
              setSymbol={setSymbol}
              data={data}
              setData={setData}
              allSymbols={allSymbols}
            />
          }
        />
        <Route path="/options" element={<OptionStrategies />} />
      </Routes>
    </div>
  );
}

export default Home;
