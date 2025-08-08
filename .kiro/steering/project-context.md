---
inclusion: always
---

# Stock Sage Project Context

## Project Overview

Stock Sage is a comprehensive financial analysis platform that combines:

- Real-time stock analysis for Indian (NSE) and US markets
- AI-powered sentiment analysis using FinBERT
- Options trading strategies with P&L calculations
- Technical indicators (RSI, MACD, Bollinger Bands)
- Fundamental analysis with financial ratios

## Technology Stack

- **Frontend**: React 19 + Vite + Material-UI
- **Backend**: FastAPI + Python
- **Database**: MongoDB (with fallback to in-memory storage)
- **Authentication**: Google OAuth
- **AI/ML**: HuggingFace FinBERT for sentiment analysis

## Key Components

- **StockAnalyzer**: Main analysis interface with live market signals
- **Fundamentals**: Financial data display for both Indian and US stocks
- **OptionStrategies**: Options P&L calculator with multiple strategies
- **Authentication**: Google OAuth integration with profile completion

## API Endpoints

- `/analyze/{symbol}` - Comprehensive stock analysis
- `/fundamentals/{symbol}` - Financial fundamentals
- `/options-strategy-pnl` - Options P&L calculations
- `/api/v1/live-top-signals` - Real-time market signals
- `/google-login` - Authentication endpoint

## Development Guidelines

- Use responsive design for all components
- Implement proper error handling and loading states
- Follow the established CSS naming conventions (stock-sage-\*)
- Ensure mobile-first responsive design
- Use TypeScript-style JSDoc comments for better documentation

## Current Status

- ✅ Core functionality implemented
- ✅ Responsive design completed
- ✅ Authentication flow working
- ✅ Options calculator functional
- ✅ Live market signals implemented
- 🔄 Documentation alignment in progress
