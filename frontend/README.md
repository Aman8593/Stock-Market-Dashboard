# 📈 Stock Sage - Advanced Stock Analysis Platform

Stock Sage is a comprehensive stock analysis platform that combines technical analysis, sentiment analysis, and options trading strategies to provide intelligent investment insights for both Indian and US markets.

## 🚀 Key Features

### 1. **Live Market Signals Dashboard**

- Real-time market signals for top Indian (NSE) and US stocks
- Automated daily analysis of top 50 stocks from both markets
- Quick overview of best buy/sell opportunities with confidence scores
- Market trend indicators and price change tracking

### 2. **Advanced Stock Analysis Engine**

- **Multi-factor Analysis**: Combines technical indicators with news sentiment
- **Technical Indicators**: RSI, MACD, Bollinger Bands, volume analysis, support/resistance levels
- **Sentiment Analysis**: AI-powered news sentiment using FinBERT model
- **Risk Assessment**: Comprehensive risk scoring with position sizing recommendations
- **Market Context**: Volatility regime, trend direction, and sector rotation analysis

### 3. **Comprehensive Fundamental Analysis**

- **Financial Statements**: Income statement, balance sheet, and cash flow analysis
- **Key Ratios**: PE ratio, ROE, ROCE, market cap, and sector information
- **Shareholding Patterns**: Institutional and retail investor breakdown (Indian stocks)
- **Multi-source Data**: Yahoo Finance for US stocks, Screener.in for Indian stocks

### 4. **Options Trading Strategies**

- **Strategy Calculator**: Profit/Loss analysis for various options strategies
- **Real-time Pricing**: Live options data with customizable premium inputs
- **Multiple Strategies**: Support for calls, puts, spreads, straddles, and complex strategies
- **Interactive Analysis**: Dynamic strike price and expiry date selection
- **Custom Scenarios**: Test different market scenarios with custom premium values

### 5. **Intelligent Signal Generation**

- **Multi-layered Approach**: Technical + Sentiment + Risk analysis
- **Confidence Scoring**: Quantified confidence levels (0-100%)
- **Signal Classification**: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
- **Entry/Exit Points**: Precise entry prices with stop-loss and take-profit levels
- **Position Sizing**: Risk-adjusted position size recommendations

## 🛠️ Technology Stack

### Backend (Python/FastAPI)

- **FastAPI**: High-performance API framework
- **yfinance**: Real-time stock data and financial information
- **Pandas/NumPy**: Data processing and technical analysis
- **BeautifulSoup**: Web scraping for Indian stock fundamentals
- **HuggingFace**: AI-powered sentiment analysis
- **Concurrent Processing**: Multi-threaded analysis for faster results

### Frontend (React)

- **React 19**: Modern React with hooks and context
- **Material-UI**: Professional UI components
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **Responsive Design**: Mobile-friendly interface

## 📊 Analysis Methodology

### Technical Analysis

- **RSI (Relative Strength Index)**: 14-period momentum oscillator
- **MACD**: Moving Average Convergence Divergence with signal line
- **Bollinger Bands**: Price volatility and mean reversion analysis
- **Volume Analysis**: Trading volume trends and anomalies
- **Support/Resistance**: Dynamic price level identification
- **Price Momentum**: Multi-timeframe momentum analysis

### Sentiment Analysis

- **News Aggregation**: Multiple sources (Google News, NewsAPI, Yahoo Finance)
- **AI Processing**: FinBERT model for financial sentiment classification
- **Quality Filtering**: Advanced filtering to remove noise and generic content
- **Weighted Scoring**: Recent news weighted higher than older news
- **Confidence Weighting**: High-confidence predictions weighted more heavily

### Risk Management

- **Volatility Assessment**: Historical and implied volatility analysis
- **Position Sizing**: Kelly Criterion-based position sizing
- **Risk-Reward Ratios**: Calculated risk-reward for each trade setup
- **Market Regime Detection**: Bull/bear/sideways market identification
- **Correlation Analysis**: Cross-asset correlation considerations

## 🎯 Signal Accuracy & Performance

### Backtesting Results

- **Win Rate**: Historical performance tracking
- **Risk-Adjusted Returns**: Sharpe ratio and maximum drawdown analysis
- **Market Regime Performance**: Performance across different market conditions
- **Confidence Calibration**: Actual vs predicted confidence validation

### Quality Assurance

- **Multi-source Validation**: Cross-verification of data sources
- **Error Handling**: Robust error handling and fallback mechanisms
- **Data Quality Checks**: Automated data validation and cleaning
- **Performance Monitoring**: Real-time system performance tracking

## 🌍 Market Coverage

### Indian Market (NSE)

- **Top 50 Stocks**: Nifty 50 constituents
- **Sector Coverage**: IT, Banking, Pharma, Auto, Steel, Oil & Gas
- **Local News Sources**: Economic Times, MoneyControl, Business Standard
- **Currency**: Indian Rupees (₹)

### US Market

- **Top 50 Stocks**: S&P 500 major constituents
- **Sector Coverage**: Technology, Healthcare, Finance, Consumer, Energy
- **News Sources**: Reuters, Bloomberg, CNBC, MarketWatch
- **Currency**: US Dollars ($)

## 🔐 Security & Authentication

- **Google OAuth**: Secure authentication system
- **Session Management**: JWT-based session handling
- **Protected Routes**: Authenticated access to analysis features
- **Data Privacy**: No storage of personal financial information

## 📱 User Experience

### Dashboard Features

- **Intuitive Interface**: Clean, professional design
- **Real-time Updates**: Live data refresh capabilities
- **Mobile Responsive**: Optimized for all device sizes
- **Fast Loading**: Optimized performance with caching
- **Error Handling**: User-friendly error messages and recovery

### Analysis Workflow

1. **Market Overview**: Start with live market signals
2. **Stock Selection**: Choose from comprehensive stock list
3. **Deep Analysis**: Get detailed technical and sentiment analysis
4. **Risk Assessment**: Review risk metrics and position sizing
5. **Action Plan**: Receive clear buy/sell/hold recommendations

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn
- Python 3.8+ with pip
- API keys for news sources (optional for enhanced features)

### Installation

```bash
# Clone the repository
git clone <repository-url>

# Backend setup
cd backend
pip install -r requirements.txt
python app.py

# Frontend setup
cd frontend
npm install
npm run dev
```

### Configuration

- Set up environment variables for API keys
- Configure CORS settings for your domain
- Customize stock lists and analysis parameters

## 📈 Future Enhancements

- **Portfolio Management**: Track and analyze entire portfolios
- **Alerts System**: Real-time price and signal alerts
- **Social Features**: Community insights and shared analysis
- **Advanced Charting**: Interactive technical analysis charts
- **Machine Learning**: Enhanced prediction models
- **Cryptocurrency**: Extend analysis to crypto markets

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on how to submit pull requests, report issues, and suggest improvements.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Disclaimer**: Stock Sage is for educational and informational purposes only. Always conduct your own research and consult with financial advisors before making investment decisions. Past performance does not guarantee future results.
