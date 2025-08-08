# 🧩 Stock Sage Components

React components for the Stock Sage frontend application.

## 📁 Component Structure

```
components/
├── Home.jsx                   # Main dashboard container
├── Navbar.jsx                 # Navigation component
├── Intro.jsx                  # Landing page
├── StockAnalyzer.jsx          # Stock analysis interface
├── Fundamentals.jsx           # Financial fundamentals display
├── OptionStrategies.jsx       # Options trading calculator
└── *.css                     # Component-specific styles
```

## 🎯 Component Overview

### **Home.jsx**

- Main dashboard container
- Handles routing between different sections
- Manages shared state for stock symbols and data
- Fetches initial stock list from API

### **StockAnalyzer.jsx**

- Real-time stock analysis interface
- Live market signals dashboard
- Individual stock analysis with technical indicators
- Sentiment analysis display
- Auto-loads INFY data on first visit

### **Fundamentals.jsx**

- Financial fundamentals display
- Income statement, balance sheet, cash flow
- Shareholding patterns (Indian stocks)
- Institutional investors (US stocks)
- Auto-loads INFY fundamentals on first visit

### **OptionStrategies.jsx**

- Options trading P&L calculator
- Multiple strategy support (calls, puts, spreads)
- Real-time options pricing
- Custom premium input functionality
- Interactive strike price and expiry selection

### **Navbar.jsx**

- Navigation between different sections
- User authentication status
- Responsive design for mobile/desktop

### **Intro.jsx**

- Landing page with Google OAuth
- Feature overview and benefits
- User onboarding flow

## 🔄 State Management

### **Shared Props Pattern**

Components receive shared state through props from Home.jsx:

```jsx
// Example from Home.jsx
<StockAnalyzer
  symbol={stockSymbol}
  setSymbol={setStockSymbol}
  data={stockData}
  setData={setStockData}
  allSymbols={allSymbols}
/>
```

### **Local Storage Integration**

- **StockAnalyzer**: Stores last analyzed stock in `lastStockData`/`lastStockSymbol`
- **Fundamentals**: Stores fundamentals in `fundamentalsData`/`fundamentalsSymbol`
- **Market Data**: Caches live signals with 24-hour expiry

## 🎨 Styling Approach

### **CSS Modules**

Each component has its own CSS file:

- `StockAnalyzer.css` - Analysis interface styles
- `Fundamentals.css` - Financial data table styles
- `OptionStrategies.css` - Options calculator styles
- `Navbar.css` - Navigation styles
- `Intro.css` - Landing page styles

### **Responsive Design**

- Mobile-first approach
- Flexible grid layouts
- Responsive tables with horizontal scroll
- Touch-friendly interface elements

## 🔧 Component APIs

### **StockAnalyzer Props**

```jsx
{
  symbol: string,           // Current stock symbol
  setSymbol: function,      // Update stock symbol
  data: object,            // Analysis data
  setData: function,       // Update analysis data
  allSymbols: array        // Available stock symbols
}
```

### **Fundamentals Props**

```jsx
{
  symbol: string,           // Current stock symbol
  setSymbol: function,      // Update stock symbol
  data: object,            // Fundamentals data
  setData: function,       // Update fundamentals data
  allSymbols: array        // Available stock symbols
}
```

## 🚀 Development Guidelines

### **Adding New Components**

1. Create component file in `/components/`
2. Create corresponding CSS file
3. Add to routing in `Home.jsx` if needed
4. Update navigation in `Navbar.jsx`
5. Add to this README

### **State Management Best Practices**

- Use shared state for data that needs to persist across components
- Use local state for component-specific UI state
- Implement localStorage for data persistence
- Handle loading and error states consistently

### **Styling Guidelines**

- Follow existing CSS class naming conventions
- Use CSS custom properties for consistent theming
- Ensure responsive design for all screen sizes
- Test on mobile devices

## 🧪 Testing Components

```bash
# Run component tests
npm test

# Run tests in watch mode
npm test -- --watch

# Generate coverage report
npm test -- --coverage
```

## 📱 Mobile Considerations

- Touch-friendly button sizes (minimum 44px)
- Horizontal scrolling for wide tables
- Collapsible sections for better mobile UX
- Optimized loading states for slower connections
