import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import "./App.css";
import Home from "./components/Home.jsx";
import Intro from "./components/Intro.jsx";

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem("isAuthenticated");
  return isAuthenticated ? children : <Navigate to="/" replace />;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Intro />} />

        <Route
          path="/home/*"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        {/* Redirect old routes to home */}
        {/* <Route
          path="/news_analysis"
          element={<Navigate to="/home/news_analysis" replace />}
        />
        <Route
          path="/fundamentals"
          element={<Navigate to="/home/fundamentals" replace />}
        />
        <Route
          path="/options"
          element={<Navigate to="/home/options" replace />}
        /> */}
      </Routes>
    </Router>
  );
}

export default App;
