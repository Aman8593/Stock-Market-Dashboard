import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import StockAnalyzer from "./components/StockAnalyzer.jsx";
import Fundamentals from "./components/Fundamentals.jsx";
import OptionStrategies from "./components/OptionStrategies.jsx";
import "./App.css";
function App() {
  const [stockSymbol, setStockSymbol] = useState("");
  const [stockData, setStockData] = useState(null);
  const [fundamentalsData, setFundamentalsData] = useState(null);

  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <h1>📈 Stock Dashboard</h1>

        <Routes>
          <Route
            path="/"
            element={
              <StockAnalyzer
                symbol={stockSymbol}
                setSymbol={setStockSymbol}
                data={stockData}
                setData={setStockData}
              />
            }
          />
          <Route
            path="/fundamentals"
            element={
              <Fundamentals
                symbol={stockSymbol}
                data={fundamentalsData}
                setData={setFundamentalsData}
              />
            }
          />
          <Route path="/options" element={<OptionStrategies />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
