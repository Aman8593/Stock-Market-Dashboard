import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css"; // Assuming you have some styles for the navbar
const Navbar = () => {
  return (
    <nav>
      <Link to="/" className="nav-link">
        Stock Analysis
      </Link>
      <Link to="/fundamentals" className="nav-link">
        Fundamental Analysis
      </Link>
      <Link to="/options" className="nav-link">
        Options Strategies
      </Link>
    </nav>
  );
};

export default Navbar;
