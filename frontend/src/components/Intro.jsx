import React, { useState, useEffect } from "react";
import {
  TrendingUp,
  BarChart3,
  Globe,
  Target,
  Users,
  Shield,
  X,
  Mail,
  User,
  Phone,
  MapPin,
  Import,
  Menu,
} from "lucide-react";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";
import SEO from "./SEO.jsx";
import "./Intro.css"; // Import the CSS file

const Intro = () => {
  const [showSignup, setShowSignup] = useState(false);
  const [showGoogleLogin, setShowGoogleLogin] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [signupData, setSignupData] = useState({
    fullName: "",
    email: "",
    phone: "",
    location: "",
    experience: "",
    interests: [],
  });

  const navigate = useNavigate();

  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showMobileMenu && !event.target.closest(".stock-sage-navbar")) {
        setShowMobileMenu(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showMobileMenu]);

  // Close mobile menu on scroll
  useEffect(() => {
    const handleScroll = () => {
      if (showMobileMenu) {
        setShowMobileMenu(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [showMobileMenu]);

  const handleCallbackResponse = async (response) => {
    if (!response.credential) {
      console.error("No credential returned from Google");
      alert("Google sign-in failed. Please try again.");
      return;
    }

    const userObj = jwtDecode(response.credential);
    console.log("Google user:", userObj);

    try {
      console.log("Sending request to backend...");
      const res = await fetch("http://localhost:8000/google-login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(userObj),
      });

      console.log("Response status:", res.status);

      if (!res.ok) {
        const errorText = await res.text();
        console.error("Backend error:", errorText);
        alert(`Authentication failed: ${res.status} ${res.statusText}`);
        return;
      }

      const data = await res.json();
      console.log("Backend response:", data);

      if (data.isNewUser) {
        console.log("New user detected, showing signup form");
        // Pre-fill signup data with Google info
        setSignupData((prev) => ({
          ...prev,
          fullName: userObj.name || "",
          email: userObj.email || "",
        }));
        setShowGoogleLogin(false);
        setShowSignup(true);
      } else {
        console.log("Existing user, logging in");
        // Store user authentication state
        localStorage.setItem("isAuthenticated", "true");
        localStorage.setItem("user", JSON.stringify(data.user || userObj));

        // Redirect to home page
        navigate("/home");
      }
    } catch (err) {
      console.error("Error sending user data to backend:", err);
      alert("Network error. Please check your connection and try again.");
    }
  };

  const initializeGoogleLogin = () => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    if (!clientId) {
      console.error("Missing VITE_GOOGLE_CLIENT_ID in .env");
      return;
    }

    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: handleCallbackResponse,
    });

    window.google.accounts.id.renderButton(
      document.getElementById("google-signin-button"),
      {
        theme: "outline",
        size: "large",
        width: 300,
        height: 50,
        text: "signin_with",
        shape: "rectangular",
      }
    );
  };

  useEffect(() => {
    if (showGoogleLogin) {
      // Load Google Sign-in script if not already loaded
      if (window.google && window.google.accounts) {
        initializeGoogleLogin();
      } else {
        const script = document.createElement("script");
        script.src = "https://accounts.google.com/gsi/client";
        script.async = true;
        script.defer = true;
        script.onload = initializeGoogleLogin;
        document.body.appendChild(script);
      }
    }
  }, [showGoogleLogin]);

  const handleGoogleSignIn = () => {
    setShowGoogleLogin(true);
  };

  const handleLogin = () => {
    setShowGoogleLogin(true);
  };

  const handleSignupSubmit = async () => {
    try {
      console.log("Submitting profile data:", signupData);

      const profileData = {
        email: signupData.email,
        mobile: signupData.phone,
        profession: signupData.experience,
        fullName: signupData.fullName,
        location: signupData.location,
        interests: signupData.interests,
      };

      const res = await fetch("http://localhost:8000/complete-profile", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(profileData),
      });

      console.log("Profile completion response status:", res.status);

      if (res.ok) {
        const data = await res.json();
        console.log("Profile completion successful:", data);

        // Set authentication state like existing users
        localStorage.setItem("isAuthenticated", "true");
        localStorage.setItem(
          "user",
          JSON.stringify({
            email: signupData.email,
            name: signupData.fullName,
            ...data.user, // Include user data from backend
          })
        );

        setShowSignup(false);
        console.log("Navigating to home page");
        navigate("/home");
      } else {
        const errorText = await res.text();
        console.error(
          "Profile completion failed:",
          res.status,
          res.statusText,
          errorText
        );
        alert(`Profile completion failed: ${res.status} ${res.statusText}`);
      }
    } catch (err) {
      console.error("Error completing profile:", err);
      alert("Network error during profile completion. Please try again.");
    }
  };

  const handleInterestChange = (interest) => {
    setSignupData((prev) => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter((i) => i !== interest)
        : [...prev.interests, interest],
    }));
  };

  const features = [
    {
      icon: <Globe className="w-8 h-8" />,
      title: "Global Market Coverage",
      description:
        "Real-time news analysis for US and Indian stock markets with AI-powered insights",
      highlight: "NSE, BSE, NYSE, NASDAQ",
      iconClass: "blue",
    },
    {
      icon: <Target className="w-8 h-8" />,
      title: "Options Strategies",
      description:
        "Advanced options trading strategies with live P&L calculations and risk analysis",
      highlight: "Live P&L Tracking",
      iconClass: "green",
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Fundamental Analysis",
      description:
        "Deep dive into company financials, ratios, and growth metrics for informed decisions",
      highlight: "AI-Powered Insights",
      iconClass: "purple",
    },
  ];

  const benefits = [
    "Real-time market sentiment analysis",
    "Personalized stock recommendations",
    "Risk assessment and portfolio optimization",
    "News impact prediction on stock prices",
    "Options Strategies PNL analysis",
    "Peer comparison and sector analysis",
  ];

  return (
    <div className="stock-sage-intro">
      <SEO
        title="Stock Sage - AI-Powered Stock Analysis & Trading Signals | Free Stock Market Analysis"
        description="Get free AI-powered stock analysis, real-time trading signals, and comprehensive fundamentals for Indian (NSE) and US markets. Features sentiment analysis, technical indicators, and options strategies."
        keywords="free stock analysis, AI trading signals, Indian stocks, US stocks, NSE analysis, stock market, technical analysis, sentiment analysis, options trading, stock fundamentals, real-time signals"
        url="https://stocksage.app/"
      />
      {/* Navbar */}
      <nav className="stock-sage-navbar">
        <div className="stock-sage-navbar-container">
          <div className="stock-sage-navbar-logo">
            <TrendingUp />
            <span>Stock Sage</span>
          </div>

          {/* Desktop Menu */}
          <div className="stock-sage-navbar-menu">
            <a
              href="#features"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById("features")?.scrollIntoView({
                  behavior: "smooth",
                });
              }}
            >
              Features
            </a>
            <a
              href="#about"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById("about")?.scrollIntoView({
                  behavior: "smooth",
                });
              }}
            >
              About Us
            </a>
            <button onClick={handleLogin} className="stock-sage-navbar-button">
              Sign In
            </button>
            <button
              onClick={handleGoogleSignIn}
              className="stock-sage-navbar-signup"
            >
              Get Started
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="stock-sage-mobile-menu-button"
            onClick={() => setShowMobileMenu(!showMobileMenu)}
            aria-label="Toggle mobile menu"
            aria-expanded={showMobileMenu}
          >
            <Menu size={24} />
          </button>
        </div>

        {/* Mobile Menu Dropdown */}
        {showMobileMenu && (
          <div className="stock-sage-mobile-menu">
            <a
              href="#features"
              onClick={(e) => {
                e.preventDefault();
                setShowMobileMenu(false);
                // Smooth scroll to section
                setTimeout(() => {
                  document.getElementById("features")?.scrollIntoView({
                    behavior: "smooth",
                  });
                }, 100);
              }}
            >
              Features
            </a>
            <a
              href="#about"
              onClick={(e) => {
                e.preventDefault();
                setShowMobileMenu(false);
                // Smooth scroll to section
                setTimeout(() => {
                  document.getElementById("about")?.scrollIntoView({
                    behavior: "smooth",
                  });
                }, 100);
              }}
            >
              About Us
            </a>
            <button
              onClick={() => {
                handleLogin();
                setShowMobileMenu(false);
              }}
              className="stock-sage-mobile-menu-button-item"
            >
              Sign In
            </button>
            <button
              onClick={() => {
                handleGoogleSignIn();
                setShowMobileMenu(false);
              }}
              className="stock-sage-mobile-menu-signup"
            >
              Get Started
            </button>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <div className="stock-sage-hero-section">
        <div className="stock-sage-hero-container">
          <h1 className="stock-sage-hero-title">
            Welcome to{" "}
            <span className="stock-sage-hero-title-gradient">Stock Sage</span>
          </h1>
          <p className="stock-sage-hero-subtitle">
            Your AI-powered companion for stock analysis, options trading, and
            market insights across US and Indian markets
          </p>
          <div className="stock-sage-hero-buttons">
            <button
              onClick={handleGoogleSignIn}
              className="stock-sage-google-signin-btn"
            >
              <svg
                className="stock-sage-google-icon"
                viewBox="0 0 24 24"
                width="20"
                height="20"
              >
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  fill="#4285F4"
                />
                <path
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  fill="#34A853"
                />
                <path
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  fill="#FBBC05"
                />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  fill="#EA4335"
                />
              </svg>
              Get Started with Google
            </button>
          </div>
        </div>

        {/* Animated background elements */}
        <div className="stock-sage-hero-bg-element-1"></div>
        <div className="stock-sage-hero-bg-element-2"></div>
      </div>

      {/* Features Section */}
      <section id="features" className="stock-sage-features-section">
        <div className="stock-sage-features-container">
          <div className="stock-sage-features-header">
            <h2 className="stock-sage-features-title">Platform Features</h2>
            <p className="stock-sage-features-subtitle">
              Discover how Stock Sage can transform your trading experience
            </p>
          </div>

          <div className="stock-sage-features-grid">
            {features.map((feature, index) => (
              <div key={index} className="stock-sage-feature-card">
                <div className={`stock-sage-feature-icon ${feature.iconClass}`}>
                  {feature.icon}
                </div>
                <h3 className="stock-sage-feature-title">{feature.title}</h3>
                <p className="stock-sage-feature-description">
                  {feature.description}
                </p>
                <div className="stock-sage-feature-highlight">
                  <span>{feature.highlight}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="stock-sage-benefits-section">
        <div className="stock-sage-benefits-container">
          <div className="stock-sage-benefits-grid">
            <div className="stock-sage-benefits-content">
              <h2>Why Choose Stock Sage?</h2>
              <p>
                Join thousands of traders who trust Stock Sage for their
                investment decisions
              </p>

              <div className="stock-sage-benefits-list">
                {benefits.map((benefit, index) => (
                  <div key={index} className="stock-sage-benefit-item">
                    <div className="stock-sage-benefit-dot"></div>
                    <span className="stock-sage-benefit-text">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="stock-sage-benefits-stats">
              <Users className="stock-sage-stats-icon" />
              <h3 className="stock-sage-stats-title">50,000+ Active Users</h3>
              <p className="stock-sage-stats-subtitle">
                Trusted by professional traders and investors worldwide
              </p>

              <div className="stock-sage-stats-grid">
                <div className="stock-sage-stat-item">
                  <div className="stock-sage-stat-number green">98%</div>
                  <div className="stock-sage-stat-label">Accuracy Rate</div>
                </div>
                <div className="stock-sage-stat-item">
                  <div className="stock-sage-stat-number blue">24/7</div>
                  <div className="stock-sage-stat-label">Market Coverage</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="stock-sage-about-section">
        <div className="stock-sage-about-container">
          <h2 className="stock-sage-about-title">About Stock Sage</h2>
          <p className="stock-sage-about-description">
            Stock Sage combines cutting-edge AI technology with comprehensive
            market data to provide traders and investors with actionable
            insights...
          </p>

          <div className="stock-sage-about-features">
            <div className="stock-sage-about-feature">
              <Shield className="green" />
              <h3>Secure & Reliable</h3>
              <p>Bank-grade security with 99.9% uptime guarantee</p>
            </div>
            <div className="stock-sage-about-feature">
              <BarChart3 className="blue" />
              <h3>Data-Driven</h3>
              <p>Real-time data from multiple exchanges and news sources</p>
            </div>
            <div className="stock-sage-about-feature">
              <TrendingUp className="purple" />
              <h3>AI-Powered</h3>
              <p>Advanced machine learning algorithms for market prediction</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="stock-sage-cta-section">
        <div className="stock-sage-cta-container">
          <h2 className="stock-sage-cta-title">
            Ready to Start Your Trading Journey?
          </h2>
          <p className="stock-sage-cta-description">
            Join Stock Sage today and experience the future of intelligent
            trading
          </p>
          <button
            onClick={handleGoogleSignIn}
            className="stock-sage-cta-button"
          >
            Get Started Now
          </button>
        </div>
      </section>

      {/* Popups (Google Login & Signup) */}
      {showGoogleLogin && (
        <div className="stock-sage-popup-overlay">
          <div className="stock-sage-popup-content">
            <div className="stock-sage-popup-header">
              <h2 className="stock-sage-popup-title">Sign in to Stock Sage</h2>
              <button
                onClick={() => setShowGoogleLogin(false)}
                className="stock-sage-popup-close"
              >
                <X />
              </button>
            </div>
            <div style={{ textAlign: "center", padding: "20px 0" }}>
              <p style={{ marginBottom: "20px", color: "#6b7280" }}>
                Continue with your Google account to access all features
              </p>
              <div id="google-signin-button"></div>
            </div>
          </div>
        </div>
      )}

      {showSignup && (
        <div className="stock-sage-popup-overlay">
          <div className="stock-sage-popup-content">
            <div className="stock-sage-popup-header">
              <h2 className="stock-sage-popup-title">Complete Your Profile</h2>
              <button
                onClick={() => setShowSignup(false)}
                className="stock-sage-popup-close"
              >
                <X />
              </button>
            </div>

            <div className="stock-sage-popup-form">
              <div className="stock-sage-form-group">
                <label className="stock-sage-form-label">
                  <User size={16} />
                  Full Name
                </label>
                <input
                  type="text"
                  className="stock-sage-form-input"
                  value={signupData.fullName}
                  onChange={(e) =>
                    setSignupData((prev) => ({
                      ...prev,
                      fullName: e.target.value,
                    }))
                  }
                  placeholder="Enter your full name"
                  disabled
                />
              </div>

              <div className="stock-sage-form-group">
                <label className="stock-sage-form-label">
                  <Mail size={16} />
                  Email Address
                </label>
                <input
                  type="email"
                  className="stock-sage-form-input"
                  value={signupData.email}
                  onChange={(e) =>
                    setSignupData((prev) => ({
                      ...prev,
                      email: e.target.value,
                    }))
                  }
                  placeholder="Enter your email"
                  disabled
                />
              </div>

              <div className="stock-sage-form-group">
                <label className="stock-sage-form-label">
                  <Phone size={16} />
                  Phone Number
                </label>
                <input
                  type="tel"
                  className="stock-sage-form-input"
                  value={signupData.phone}
                  onChange={(e) =>
                    setSignupData((prev) => ({
                      ...prev,
                      phone: e.target.value,
                    }))
                  }
                  placeholder="Enter your phone number"
                />
              </div>

              <div className="stock-sage-form-group">
                <label className="stock-sage-form-label">
                  <MapPin size={16} />
                  Location
                </label>
                <input
                  type="text"
                  className="stock-sage-form-input"
                  value={signupData.location}
                  onChange={(e) =>
                    setSignupData((prev) => ({
                      ...prev,
                      location: e.target.value,
                    }))
                  }
                  placeholder="Enter your location"
                />
              </div>

              <div className="stock-sage-form-group">
                <label className="stock-sage-form-label">
                  <Import size={16} />
                  Trading Experience
                </label>
                <select
                  className="stock-sage-form-select"
                  value={signupData.experience}
                  onChange={(e) =>
                    setSignupData((prev) => ({
                      ...prev,
                      experience: e.target.value,
                    }))
                  }
                >
                  <option value="">Select your experience level</option>
                  <option value="beginner">Beginner (0-1 years)</option>
                  <option value="intermediate">Intermediate (1-3 years)</option>
                  <option value="advanced">Advanced (3-5 years)</option>
                  <option value="expert">Expert (5+ years)</option>
                </select>
              </div>

              <div className="stock-sage-form-group">
                <label className="stock-sage-form-label">
                  Trading Interests (Select all that apply)
                </label>
                <div className="stock-sage-checkbox-group">
                  {[
                    "Stocks",
                    "Options",
                    "Futures",
                    "Forex",
                    "Crypto",
                    "Commodities",
                  ].map((interest) => (
                    <div key={interest} className="stock-sage-checkbox-item">
                      <input
                        type="checkbox"
                        id={interest}
                        className="stock-sage-checkbox-input"
                        checked={signupData.interests.includes(interest)}
                        onChange={() => handleInterestChange(interest)}
                      />
                      <label
                        htmlFor={interest}
                        className="stock-sage-checkbox-label"
                      >
                        {interest}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={handleSignupSubmit}
                className="stock-sage-submit-button"
                disabled={!signupData.fullName || !signupData.email}
              >
                Complete Setup
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Intro;
