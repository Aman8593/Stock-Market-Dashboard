import React, { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Navbar.css"; // Assuming you have some styles for the navbar
import { TrendingUp, Menu, X } from "lucide-react";

const Navbar = () => {
  const navigate = useNavigate();
  const [BurgerNav, setBurgerNav] = useState(false);
  const navbarRef = useRef(null);

  const handleLogout = () => {
    // Clear authentication state
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("user");

    // Redirect to login page
    navigate("/");
  };

  // Handle click outside to close navbar
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (navbarRef.current && !navbarRef.current.contains(event.target)) {
        setBurgerNav(false);
      }
    };

    // Add event listener when burger nav is open
    if (BurgerNav) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    // Cleanup event listener
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [BurgerNav]);

  // Close burger nav when clicking on a link
  const closeBurgerNav = () => {
    setBurgerNav(false);
  };

  return (
    <nav className="navbar" ref={navbarRef}>
      <div className="navbar-container">
        <div className="navbar-logo">
          <TrendingUp />
          <span>Stock Sage</span>
        </div>

        {/* Burger Menu Toggle */}
        <div
          className={`navbar-burger ${BurgerNav ? "active" : ""}`}
          onClick={() => setBurgerNav(!BurgerNav)}
        >
          {BurgerNav ? (
            <X className="burger-icon" />
          ) : (
            <Menu className="burger-icon" />
          )}
        </div>

        {/* Navigation Links */}
        <div className={`navbar-links ${BurgerNav ? "active" : ""}`}>
          <Link to="/home" className="nav-link" onClick={closeBurgerNav}>
            Stock Analysis
          </Link>
          <Link
            to="/home/fundamentals"
            className="nav-link"
            onClick={closeBurgerNav}
          >
            Fundamental Analysis
          </Link>
          <Link
            to="/home/options"
            className="nav-link"
            onClick={closeBurgerNav}
          >
            Options Strategies
          </Link>
          <button
            onClick={() => {
              handleLogout();
              closeBurgerNav();
            }}
            className="logout-btn"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
