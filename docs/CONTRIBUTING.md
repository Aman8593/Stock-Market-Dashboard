# 🤝 Contributing to Stock Sage

Thank you for your interest in contributing to Stock Sage! This guide will help you get started with contributing to our financial analysis platform.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## 📜 Code of Conduct

### Our Pledge

We are committed to making participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**

- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Git** installed and configured
- **Node.js 16+** for frontend development
- **Python 3.8+** for backend development
- **Docker** for containerized development (optional)
- Basic understanding of React and FastAPI

### First-time Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/stock-sage.git
   cd stock-sage
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/stock-sage.git
   ```
4. **Create a new branch** for your contribution:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Setup

### Backend Setup

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
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the development server**:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**:

   ```bash
   cd frontend
   ```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

### Docker Setup (Alternative)

```bash
# Run the entire stack
docker-compose up --build

# Run specific services
docker-compose up backend
docker-compose up frontend
```

## 📝 Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

1. **🐛 Bug Fixes**

   - Fix existing bugs
   - Improve error handling
   - Performance optimizations

2. **✨ New Features**

   - New analysis indicators
   - UI/UX improvements
   - API enhancements

3. **📚 Documentation**

   - Code documentation
   - User guides
   - API documentation

4. **🧪 Testing**

   - Unit tests
   - Integration tests
   - End-to-end tests

5. **🎨 Design**
   - UI/UX improvements
   - Accessibility enhancements
   - Mobile responsiveness

### Issue Guidelines

Before creating a new issue:

1. **Search existing issues** to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information**:
   - Clear description of the problem/feature
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Screenshots/logs when applicable
   - Environment details (OS, browser, versions)

### Feature Requests

When proposing new features:

1. **Explain the use case** and business value
2. **Provide mockups or wireframes** if applicable
3. **Consider implementation complexity**
4. **Discuss with maintainers** before starting work

## 🔄 Pull Request Process

### Before Submitting

1. **Sync with upstream**:

   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Rebase your branch**:

   ```bash
   git checkout feature/your-feature-name
   git rebase main
   ```

3. **Run tests**:

   ```bash
   # Backend tests
   cd backend && python -m pytest

   # Frontend tests
   cd frontend && npm test
   ```

4. **Check code quality**:

   ```bash
   # Backend linting
   cd backend && flake8 . && black . --check

   # Frontend linting
   cd frontend && npm run lint
   ```

### Pull Request Template

```markdown
## Description

Brief description of changes made.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)

Add screenshots to help explain your changes.

## Checklist

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
```

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by at least one maintainer
3. **Testing** in staging environment
4. **Documentation** updates if needed
5. **Approval** and merge by maintainer

## 🎨 Coding Standards

### Python (Backend)

**Style Guide**: Follow PEP 8 with these additions:

```python
# Use type hints
def analyze_stock(symbol: str) -> Dict[str, Any]:
    """Analyze stock with comprehensive metrics.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'INFY.NS')

    Returns:
        Dictionary containing analysis results

    Raises:
        ValueError: If symbol is invalid
    """
    pass

# Use dataclasses for structured data
@dataclass
class AnalysisResult:
    symbol: str
    signal: str
    confidence: float
    timestamp: datetime

# Use async/await for I/O operations
async def fetch_stock_data(symbol: str) -> StockData:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/api/stocks/{symbol}")
        return StockData.parse_obj(response.json())
```

**Code Organization**:

```
backend/
├── app.py              # FastAPI app initialization
├── routers/            # API route handlers
├── services/           # Business logic
├── models/             # Database models
├── schemas/            # Pydantic schemas
├── utils/              # Utility functions
└── tests/              # Test files
```

### JavaScript/React (Frontend)

**Style Guide**: Follow Airbnb JavaScript Style Guide

```javascript
// Use functional components with hooks
const StockAnalyzer = ({ symbol, onAnalysisComplete }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Use useCallback for event handlers
  const handleAnalyze = useCallback(async () => {
    setLoading(true);
    try {
      const result = await analyzeStock(symbol);
      setData(result);
      onAnalysisComplete(result);
    } catch (error) {
      console.error("Analysis failed:", error);
    } finally {
      setLoading(false);
    }
  }, [symbol, onAnalysisComplete]);

  return <div className="stock-analyzer">{/* Component JSX */}</div>;
};

// Use PropTypes for type checking
StockAnalyzer.propTypes = {
  symbol: PropTypes.string.isRequired,
  onAnalysisComplete: PropTypes.func.isRequired,
};
```

**Component Structure**:

```
src/
├── components/         # Reusable components
├── pages/             # Page components
├── hooks/             # Custom hooks
├── services/          # API services
├── utils/             # Utility functions
├── styles/            # CSS files
└── tests/             # Test files
```

### CSS/Styling

```css
/* Use BEM methodology */
.stock-analyzer {
  /* Block */
}

.stock-analyzer__header {
  /* Element */
}

.stock-analyzer__header--loading {
  /* Modifier */
}

/* Use CSS custom properties */
:root {
  --primary-color: #3b82f6;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --error-color: #ef4444;
}

/* Mobile-first responsive design */
.container {
  width: 100%;
  padding: 1rem;
}

@media (min-width: 768px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

## 🧪 Testing Guidelines

### Backend Testing

**Test Structure**:

```python
# tests/test_analysis.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

class TestStockAnalysis:
    def test_analyze_valid_stock(self):
        """Test analysis with valid stock symbol."""
        response = client.get("/analyze/AAPL")
        assert response.status_code == 200
        data = response.json()
        assert "symbol" in data
        assert "signal" in data
        assert "confidence" in data

    def test_analyze_invalid_stock(self):
        """Test analysis with invalid stock symbol."""
        response = client.get("/analyze/INVALID")
        assert response.status_code == 400
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_sentiment_analysis(self):
        """Test sentiment analysis functionality."""
        from services.sentiment import analyze_sentiment

        headlines = ["Apple reports strong earnings"]
        result = await analyze_sentiment(headlines)

        assert isinstance(result, list)
        assert len(result) > 0
        assert "sentiment" in result[0]
```

**Running Tests**:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_analysis.py

# Run with verbose output
pytest -v
```

### Frontend Testing

**Test Structure**:

```javascript
// src/components/__tests__/StockAnalyzer.test.jsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import StockAnalyzer from "../StockAnalyzer";
import * as stockApi from "../../api/stockApi";

// Mock API calls
vi.mock("../../api/stockApi");

describe("StockAnalyzer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("renders stock analyzer component", () => {
    render(<StockAnalyzer symbol="AAPL" />);
    expect(screen.getByText("Stock Analyzer")).toBeInTheDocument();
  });

  test("handles stock analysis", async () => {
    const mockAnalysis = {
      symbol: "AAPL",
      signal: "BUY",
      confidence: 85.5,
    };

    stockApi.analyzeStock.mockResolvedValue(mockAnalysis);

    render(<StockAnalyzer symbol="AAPL" />);

    const analyzeButton = screen.getByText("Analyze");
    fireEvent.click(analyzeButton);

    await waitFor(() => {
      expect(screen.getByText("BUY")).toBeInTheDocument();
      expect(screen.getByText("85.5%")).toBeInTheDocument();
    });
  });
});
```

**Running Tests**:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

## 📚 Documentation

### Code Documentation

**Python Docstrings**:

```python
def calculate_rsi(prices: pd.Series, window: int = 14) -> float:
    """Calculate Relative Strength Index (RSI).

    RSI is a momentum oscillator that measures the speed and magnitude
    of recent price changes to evaluate overbought or oversold conditions.

    Args:
        prices: Series of closing prices
        window: Period for RSI calculation (default: 14)

    Returns:
        RSI value between 0 and 100

    Raises:
        ValueError: If window is less than 2 or greater than len(prices)

    Example:
        >>> prices = pd.Series([100, 102, 101, 103, 105])
        >>> rsi = calculate_rsi(prices, window=4)
        >>> print(f"RSI: {rsi:.2f}")
        RSI: 75.00
    """
```

**JavaScript JSDoc**:

```javascript
/**
 * Analyze stock with technical and sentiment analysis
 * @param {string} symbol - Stock symbol (e.g., 'AAPL', 'INFY.NS')
 * @param {Object} options - Analysis options
 * @param {boolean} options.includeSentiment - Include sentiment analysis
 * @param {number} options.rsiPeriod - RSI calculation period
 * @returns {Promise<AnalysisResult>} Analysis results
 * @throws {Error} When symbol is invalid or API request fails
 *
 * @example
 * const result = await analyzeStock('AAPL', { includeSentiment: true });
 * console.log(`Signal: ${result.signal}, Confidence: ${result.confidence}%`);
 */
async function analyzeStock(symbol, options = {}) {
  // Implementation
}
```

### README Updates

When adding new features, update relevant README files:

- Main project README
- Component-specific READMEs
- API documentation
- Deployment guides

## 🏆 Recognition

Contributors will be recognized in:

- **Contributors section** in README
- **Release notes** for significant contributions
- **Hall of Fame** for major features
- **Special mentions** in project updates

### Contributor Levels

1. **First-time Contributor**: Made first successful PR
2. **Regular Contributor**: 5+ merged PRs
3. **Core Contributor**: 20+ merged PRs + significant features
4. **Maintainer**: Trusted with review and merge permissions

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Discord Server**: Real-time chat with community
- **Email**: maintainers@stocksage.com for private matters

### Mentorship Program

New contributors can request mentorship:

1. Comment on issues tagged `good-first-issue`
2. Mention `@mentors` in your comment
3. A mentor will be assigned to guide you

## 🎉 Thank You!

Every contribution, no matter how small, makes Stock Sage better for everyone. We appreciate your time and effort in helping build an amazing financial analysis platform!

---

**Happy Contributing! 🚀**
