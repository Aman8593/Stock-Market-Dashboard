# 🔧 Stock Sage Backend

FastAPI-based backend service providing stock analysis, sentiment analysis, and options trading calculations.

## 📁 Project Structure

```
backend/
├── app.py                     # Main FastAPI application & route configuration
├── database.py                # Database connection & configuration
├── stocks.py                  # Stock symbols validation & market data
├── news_analysis.py           # Advanced sentiment analysis engine
├── fundamentals.py            # Financial data scraping & processing
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
├── .gitignore                # Git ignore patterns
├── README.md                  # This documentation
├── routers/                   # API route modules
│   ├── users.py              # User authentication & management
│   ├── option_strategies.py   # Options P&L calculations
│   ├── live_signal.py        # Real-time market signals
│   └── README.md             # Router-specific documentation
├── models/                    # Database models & schemas
│   ├── user.py               # User model definitions
│   └── __pycache__/          # Python bytecode cache
└── __pycache__/              # Python bytecode cache (auto-generated)
```

### Key Files Overview

- **app.py**: FastAPI application setup, middleware configuration, and route inclusion
- **stocks.py**: Contains top 50 Indian (NSE) and US stock symbols with validation logic
- **news_analysis.py**: Advanced sentiment analysis using FinBERT model with multi-source news aggregation
- **fundamentals.py**: Financial data extraction from Yahoo Finance (US) and Screener.in (Indian stocks)
- **database.py**: SQLAlchemy database configuration and session management

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ installed
- pip package manager
- API keys for external services (optional for basic functionality)

### Installation & Setup

1. **Navigate to backend directory**:

   ```bash
   cd backend
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your API keys (see Environment Variables section)
   ```

5. **Run the development server**:

   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**:
   - API Base URL: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - OpenAPI Schema: http://localhost:8000/openapi.json

## 🚀 API Endpoints

### Stock Analysis

- `GET /analyze/{symbol}` - Comprehensive multi-factor stock analysis
- `GET /stocks` - List of supported Indian and US stocks
- `GET /fundamentals/{symbol}` - Financial fundamentals and ratios

### Options Trading

- `GET /options-strategy-pnl` - Options P&L calculator with multiple strategies
- `POST /options-strategy-pnl-custom` - Custom premium P&L calculations

### Market Data

- `GET /live-signals` - Real-time market signals for top 50 stocks
- `GET /market-overview` - Market summary and trends

### Authentication

- `POST /auth/google` - Google OAuth authentication
- `GET /auth/profile` - User profile information
- `DELETE /auth/logout` - User logout

> 📚 **Detailed API Documentation**: See [docs/API.md](../docs/API.md) for complete endpoint documentation with examples.

## 🔑 Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Required for AI-powered sentiment analysis
HF_API_TOKEN=your_huggingface_token

# Optional: Enhanced news data (fallback methods available)
NEWS_API_KEY=your_news_api_key
ALPHAVANTAGE_KEY=your_alpha_vantage_key

# Database configuration
DATABASE_URL=sqlite:///./stock_sage.db

# Security (for production)
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS settings (for production)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### API Key Setup

1. **HuggingFace Token** (Required for sentiment analysis):

   - Visit: https://huggingface.co/settings/tokens
   - Create a new token with read permissions
   - Add to `.env` as `HF_API_TOKEN`

2. **News API Key** (Optional - enhances news coverage):

   - Visit: https://newsapi.org/register
   - Get free API key (500 requests/day)
   - Add to `.env` as `NEWS_API_KEY`

3. **Alpha Vantage Key** (Optional - additional market data):
   - Visit: https://www.alphavantage.co/support/#api-key
   - Get free API key
   - Add to `.env` as `ALPHAVANTAGE_KEY`

> ⚠️ **Note**: The application will work without optional API keys but with reduced functionality. Core features like technical analysis and basic news scraping will still function.

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_analysis.py
```

## 📊 Core Features & Analysis Components

### 🔍 Multi-Factor Stock Analysis

- **Technical Indicators**: RSI, MACD, Bollinger Bands, Volume Analysis, Support/Resistance
- **Sentiment Analysis**: AI-powered news sentiment using FinBERT model
- **Risk Assessment**: Position sizing, risk-reward ratios, volatility analysis
- **Market Context**: Trend direction, volatility regime, sector rotation

### 🌍 Market Coverage

- **Indian Market**: Top 50 NSE stocks (Nifty 50)
- **US Market**: Top 50 S&P 500 stocks
- **Data Sources**: Yahoo Finance, Screener.in, Google News, NewsAPI

### 📈 Live Market Signals

- Real-time analysis of top performing stocks
- Automated buy/sell signal generation
- Confidence scoring for each recommendation
- Market trend indicators

### 🎯 Options Trading

- P&L calculations for multiple strategies
- Support for calls, puts, spreads, straddles
- Custom premium input functionality
- Real-time options data integration

### 🏦 Fundamental Analysis

- **Financial Statements**: Income statement, balance sheet, cash flow
- **Key Ratios**: PE, ROE, ROCE, market cap analysis
- **Shareholding Patterns**: Institutional vs retail breakdown (Indian stocks)
- **Sector Analysis**: Industry comparison and metrics

## 🔧 Development

### Development Server

```bash
# Run with auto-reload (recommended for development)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Run with specific log level
uvicorn app:app --reload --log-level debug

# Run with custom port
uvicorn app:app --reload --port 8080
```

### Code Quality & Formatting

```bash
# Install development dependencies
pip install black isort flake8 pytest

# Format code
black .
isort .

# Lint code
flake8 .

# Type checking (if using mypy)
mypy .
```

### Database Management

```bash
# Initialize database (if using migrations)
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Reset database (development only)
rm stock_sage.db  # SQLite only
```

### Adding New Features

1. **New API Endpoints**: Add to appropriate router in `/routers/`
2. **New Analysis Logic**: Extend `news_analysis.py` or create new service files
3. **Database Models**: Add to `/models/` directory
4. **External Integrations**: Add API clients to utility modules

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for public methods
- Add unit tests for new features
- Update API documentation when adding endpoints

> 📚 **Contributing**: See [docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md) for detailed development guidelines.

## 📈 Performance & Architecture

### Performance Optimizations

- **Concurrent Processing**: Multi-threaded analysis for faster results
- **Intelligent Caching**: Redis-based caching for frequently requested data
- **Connection Pooling**: Optimized database connections
- **Rate Limiting**: Smart rate limiting for external API calls
- **Async Operations**: Non-blocking I/O for better throughput

### Scalability Features

- **Horizontal Scaling**: Stateless design for easy scaling
- **Background Tasks**: Celery integration for heavy computations
- **Database Optimization**: Indexed queries and connection pooling
- **Memory Management**: Efficient data structures and garbage collection

### Monitoring & Observability

- **Health Checks**: Built-in health check endpoints
- **Logging**: Structured logging with different levels
- **Metrics**: Performance metrics collection
- **Error Tracking**: Comprehensive error handling and reporting

## 🔗 Related Documentation

- **[API Reference](../docs/API.md)**: Complete API endpoint documentation
- **[Architecture Guide](../docs/ARCHITECTURE.md)**: System architecture and design decisions
- **[Deployment Guide](../docs/DEPLOYMENT.md)**: Production deployment instructions
- **[Contributing Guide](../docs/CONTRIBUTING.md)**: Development and contribution guidelines
- **[Router Documentation](./routers/README.md)**: Detailed router-specific documentation

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated and dependencies installed
2. **API Key Issues**: Verify API keys in `.env` file and check rate limits
3. **Database Errors**: Check database connection and permissions
4. **Port Conflicts**: Ensure port 8000 is available or use different port

### Debug Mode

```bash
# Run with debug logging
uvicorn app:app --reload --log-level debug

# Check API health
curl http://localhost:8000/health

# View interactive API docs
# Visit: http://localhost:8000/docs
```

### Getting Help

- Check the [GitHub Issues](https://github.com/your-repo/issues) for known problems
- Review the [Contributing Guide](../docs/CONTRIBUTING.md) for development setup
- Join our community discussions for support

---

**Happy Coding! 🚀**
