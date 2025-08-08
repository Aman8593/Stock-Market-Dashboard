# 🏗️ Stock Sage Architecture Documentation

Comprehensive system architecture and design decisions for Stock Sage platform.

## 🎯 System Overview

Stock Sage is a modern financial analysis platform built with a microservices-inspired architecture, combining real-time data processing, AI-powered analysis, and interactive user interfaces.

### Core Principles

- **Scalability**: Horizontal scaling capabilities
- **Reliability**: Fault-tolerant design with graceful degradation
- **Performance**: Sub-second response times for critical operations
- **Security**: End-to-end encryption and secure authentication
- **Maintainability**: Clean code architecture with comprehensive testing

## 🏛️ High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        MOBILE[Mobile App]
    end

    subgraph "CDN/Load Balancer"
        CDN[CloudFlare CDN]
        LB[Load Balancer]
    end

    subgraph "Frontend Layer"
        REACT[React Frontend]
        NGINX[Nginx Server]
    end

    subgraph "API Gateway"
        GATEWAY[FastAPI Gateway]
        AUTH[Authentication Service]
        RATE[Rate Limiter]
    end

    subgraph "Backend Services"
        ANALYSIS[Stock Analysis Service]
        SENTIMENT[Sentiment Analysis Service]
        OPTIONS[Options Calculator Service]
        FUNDAMENTALS[Fundamentals Service]
        SIGNALS[Live Signals Service]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        REDIS[(Redis Cache)]
        S3[(File Storage)]
    end

    subgraph "External APIs"
        YAHOO[Yahoo Finance]
        NEWS[News APIs]
        HF[HuggingFace]
        SCREENER[Screener.in]
    end

    WEB --> CDN
    MOBILE --> CDN
    CDN --> LB
    LB --> NGINX
    NGINX --> REACT
    REACT --> GATEWAY
    GATEWAY --> AUTH
    GATEWAY --> RATE
    GATEWAY --> ANALYSIS
    GATEWAY --> SENTIMENT
    GATEWAY --> OPTIONS
    GATEWAY --> FUNDAMENTALS
    GATEWAY --> SIGNALS

    ANALYSIS --> POSTGRES
    ANALYSIS --> REDIS
    SENTIMENT --> HF
    SENTIMENT --> NEWS
    FUNDAMENTALS --> YAHOO
    FUNDAMENTALS --> SCREENER
    SIGNALS --> REDIS

    POSTGRES --> S3
```

## 🔧 Technology Stack

### Frontend Architecture

```
React 19 Application
├── Components (Functional + Hooks)
├── State Management (Context API + Local State)
├── Routing (React Router v6)
├── UI Framework (Material-UI)
├── HTTP Client (Axios)
├── Build Tool (Vite)
└── Styling (CSS Modules + Responsive Design)
```

### Backend Architecture

```
FastAPI Application
├── API Layer (FastAPI Routers)
├── Business Logic (Service Classes)
├── Data Access (SQLAlchemy ORM)
├── Authentication (JWT + OAuth)
├── Caching (Redis)
├── Background Tasks (Celery)
└── External Integrations (HTTP Clients)
```

### Data Architecture

```
Data Flow
├── Real-time Data (WebSocket + Server-Sent Events)
├── Batch Processing (Scheduled Jobs)
├── Caching Strategy (Multi-layer)
├── Data Validation (Pydantic Models)
└── Data Persistence (PostgreSQL + Redis)
```

## 📊 Component Architecture

### Frontend Component Hierarchy

```
App
├── AuthProvider
│   ├── Intro (Landing Page)
│   └── Home (Main Dashboard)
│       ├── Navbar
│       ├── StockAnalyzer
│       │   ├── MarketSignals
│       │   ├── StockSearch
│       │   ├── AnalysisResults
│       │   └── TechnicalCharts
│       ├── Fundamentals
│       │   ├── FinancialStatements
│       │   ├── RatiosDisplay
│       │   └── ShareholdingPattern
│       └── OptionStrategies
│           ├── StrategySelector
│           ├── PremiumInputs
│           └── PnLTable
```

### Backend Service Architecture

```
FastAPI App
├── Routers
│   ├── auth.py (Authentication)
│   ├── stocks.py (Stock Analysis)
│   ├── fundamentals.py (Financial Data)
│   ├── options.py (Options Trading)
│   └── signals.py (Live Market Data)
├── Services
│   ├── AnalysisService
│   ├── SentimentService
│   ├── OptionsService
│   ├── FundamentalsService
│   └── SignalsService
├── Models
│   ├── User

```

## 🔄 Data Flow Architecture

### Stock Analysis Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Analysis
    participant Cache
    participant External
    participant DB

    Client->>API: GET /analyze/AAPL
    API->>Cache: Check cached result

    alt Cache Hit
        Cache-->>API: Return cached data
        API-->>Client: Analysis result
    else Cache Miss
        API->>Analysis: Analyze stock
        Analysis->>External: Fetch stock data
        External-->>Analysis: Stock prices
        Analysis->>External: Fetch news
        External-->>Analysis: News headlines
        Analysis->>Analysis: Calculate indicators
        Analysis->>Analysis: Analyze sentiment
        Analysis->>Cache: Store result
        Analysis->>DB: Log analysis
        Analysis-->>API: Analysis result
        API-->>Client: Analysis result
    end
```

### Real-time Signals Flow

```mermaid
sequenceDiagram
    participant Scheduler
    participant SignalService
    participant Cache
    participant External
    participant WebSocket
    participant Client

    Scheduler->>SignalService: Trigger analysis (every 5 min)
    SignalService->>External: Fetch top 50 stocks data
    External-->>SignalService: Stock data
    SignalService->>SignalService: Analyze all stocks
    SignalService->>Cache: Update signals cache
    SignalService->>WebSocket: Broadcast updates
    WebSocket->>Client: Real-time signal updates
```

## 🗄️ Database Design

### Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Analysis : creates
    User ||--o{ Watchlist : has
    User {
        string id PK
        string email
        string name
        string picture
        datetime created_at
        datetime last_login
    }

    Stock ||--o{ Analysis : analyzed
    Stock ||--o{ Signal : generates
    Stock {
        string symbol PK
        string name
        string market
        string sector
        boolean active
    }

    Analysis ||--o{ TechnicalIndicator : contains
    Analysis {
        string id PK
        string user_id FK
        string symbol FK
        json result
        float confidence
        string signal
        datetime created_at
    }

    TechnicalIndicator {
        string id PK
        string analysis_id FK
        string indicator_type
        float value
        json metadata
    }

    Signal {
        string id PK
        string symbol FK
        string signal_type
        float confidence
        json data
        datetime timestamp
    }

    Watchlist {
        string id PK
        string user_id FK
        string name
        json symbols
        datetime created_at
    }
```

### Current Database Schema (MongoDB)

**Users Collection**

```javascript
{
  _id: ObjectId,
  google_id: String,
  name: String,
  email: String,
  picture: String,
  mobile: String,
  profession: String,
  location: String,
  interests: [String],
  profile_completed: Boolean,
  created_at: Date,
  updated_at: Date
}
```

### Data Processing Architecture

**Current Implementation (In-Memory)**

- **Stock Analysis**: Processed on-demand via FastAPI, no persistence
- **Market Signals**: Cached in-memory for 24 hours, refreshed automatically
- **Technical Indicators**: Calculated real-time using yfinance data
- **Sentiment Analysis**: Real-time processing via HuggingFace API
- **Options Data**: Fetched and calculated on-demand from Yahoo Finance

**Benefits of Current Approach:**

- Fast response times (no database queries for analysis)
- Real-time data (always fresh from external APIs)
- Simplified architecture (fewer moving parts)
- Cost-effective (no database storage costs for analysis data)

### Future Database Schema (PostgreSQL - Planned)

**Users Table**

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    picture TEXT,
    mobile VARCHAR(20),
    profession VARCHAR(100),
    location VARCHAR(100),
    interests JSONB,
    profile_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Analysis History Table (Future Enhancement)**

```sql
CREATE TABLE analysis_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(20) NOT NULL,
    analysis_result JSONB NOT NULL,
    signal VARCHAR(20),
    confidence DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_analysis_user_symbol (user_id, symbol),
    INDEX idx_analysis_created_at (created_at)
);
```

**Market Signals Cache (Future Enhancement)**

```sql
CREATE TABLE market_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    market VARCHAR(10) NOT NULL, -- 'US' or 'INDIA'
    signal_type VARCHAR(20) NOT NULL, -- 'BUY' or 'SELL'
    signals_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,

    INDEX idx_signals_market_type (market, signal_type),
    INDEX idx_signals_expires (expires_at)
);
```

## 🔐 Security Architecture

### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant Frontend
    participant Backend
    participant Google
    participant Database

    Client->>Frontend: Click "Login with Google"
    Frontend->>Google: Redirect to OAuth
    Google-->>Frontend: Authorization code
    Frontend->>Backend: POST /auth/google {code}
    Backend->>Google: Exchange code for token
    Google-->>Backend: User info + access token
    Backend->>Database: Create/update user
    Backend->>Backend: Generate JWT
    Backend-->>Frontend: JWT token
    Frontend->>Frontend: Store token
    Frontend-->>Client: Redirect to dashboard
```

### Security Layers

1. **Transport Security**

   - TLS 1.3 encryption
   - HSTS headers
   - Certificate pinning

2. **Authentication**

   - Google OAuth 2.0
   - JWT tokens with expiration
   - Refresh token rotation

3. **Authorization**

   - Role-based access control
   - Resource-level permissions
   - API rate limiting

4. **Data Protection**
   - Input validation and sanitization
   - SQL injection prevention
   - XSS protection
   - CSRF tokens

## 🚀 Performance Architecture

### Caching Strategy

```mermaid
graph LR
    Client[Client Request]
    CDN[CDN Cache<br/>Static Assets]
    Redis[Redis Cache<br/>API Responses]
    App[Application<br/>Business Logic]
    DB[(Database<br/>Persistent Data)]

    Client --> CDN
    CDN --> Redis
    Redis --> App
    App --> DB

    CDN -.->|Cache Hit| Client
    Redis -.->|Cache Hit| CDN
```

### Cache Layers

1. **CDN Cache** (CloudFlare)

   - Static assets (JS, CSS, images)
   - TTL: 1 year for versioned assets
   - Geographic distribution

2. **Application Cache** (Redis)

   - API responses
   - Stock data: 5 minutes TTL
   - Analysis results: 1 hour TTL
   - User sessions: 24 hours TTL

3. **Database Query Cache**
   - PostgreSQL query cache
   - Materialized views for complex queries
   - Connection pooling

### Performance Optimizations

1. **Frontend**

   - Code splitting and lazy loading
   - Image optimization and WebP format
   - Service worker for offline capability
   - Virtual scrolling for large lists

2. **Backend**

   - Async/await for I/O operations
   - Connection pooling
   - Background task processing
   - Response compression

3. **Database**
   - Proper indexing strategy
   - Query optimization
   - Read replicas for scaling
   - Partitioning for large tables

## 🔄 Scalability Architecture

### Horizontal Scaling Strategy

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx Load Balancer]
    end

    subgraph "Frontend Tier"
        FE1[Frontend Instance 1]
        FE2[Frontend Instance 2]
        FE3[Frontend Instance N]
    end

    subgraph "API Tier"
        API1[API Instance 1]
        API2[API Instance 2]
        API3[API Instance N]
    end

    subgraph "Service Tier"
        ANALYSIS[Analysis Service]
        SENTIMENT[Sentiment Service]
        OPTIONS[Options Service]
    end

    subgraph "Data Tier"
        MASTER[(Master DB)]
        REPLICA1[(Read Replica 1)]
        REPLICA2[(Read Replica 2)]
        REDIS_CLUSTER[Redis Cluster]
    end

    LB --> FE1
    LB --> FE2
    LB --> FE3

    FE1 --> API1
    FE2 --> API2
    FE3 --> API3

    API1 --> ANALYSIS
    API2 --> SENTIMENT
    API3 --> OPTIONS

    ANALYSIS --> MASTER
    SENTIMENT --> REPLICA1
    OPTIONS --> REPLICA2

    API1 --> REDIS_CLUSTER
    API2 --> REDIS_CLUSTER
    API3 --> REDIS_CLUSTER
```

### Auto-scaling Configuration

**Kubernetes HPA**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: stocksage-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: stocksage-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## 📊 Monitoring Architecture

### Observability Stack

```mermaid
graph TB
    subgraph "Application"
        APP[Stock Sage App]
        METRICS[Metrics Endpoint]
        LOGS[Application Logs]
    end

    subgraph "Collection"
        PROMETHEUS[Prometheus]
        LOKI[Loki]
        JAEGER[Jaeger]
    end

    subgraph "Visualization"
        GRAFANA[Grafana]
        ALERTS[AlertManager]
    end

    subgraph "Notification"
        SLACK[Slack]
        EMAIL[Email]
        PAGER[PagerDuty]
    end

    APP --> METRICS
    APP --> LOGS
    METRICS --> PROMETHEUS
    LOGS --> LOKI
    APP --> JAEGER

    PROMETHEUS --> GRAFANA
    LOKI --> GRAFANA
    JAEGER --> GRAFANA

    PROMETHEUS --> ALERTS
    ALERTS --> SLACK
    ALERTS --> EMAIL
    ALERTS --> PAGER
```

### Key Metrics

1. **Business Metrics**

   - Analysis requests per minute
   - User engagement rates
   - Signal accuracy rates
   - Revenue per user

2. **Technical Metrics**

   - Response time percentiles
   - Error rates by endpoint
   - Database connection pool usage
   - Cache hit rates

3. **Infrastructure Metrics**
   - CPU and memory utilization
   - Network I/O
   - Disk usage
   - Container health

## 🔄 Deployment Architecture

### CI/CD Pipeline

```mermaid
graph LR
    DEV[Developer]
    GIT[Git Repository]
    CI[GitHub Actions]
    TEST[Test Suite]
    BUILD[Build Images]
    REGISTRY[Container Registry]
    DEPLOY[Deploy to K8s]
    PROD[Production]

    DEV --> GIT
    GIT --> CI
    CI --> TEST
    TEST --> BUILD
    BUILD --> REGISTRY
    REGISTRY --> DEPLOY
    DEPLOY --> PROD

    TEST -.->|Fail| DEV
    BUILD -.->|Fail| DEV
    DEPLOY -.->|Fail| DEV
```

### Environment Strategy

1. **Development**

   - Local Docker Compose
   - Hot reloading enabled
   - Debug logging
   - Mock external APIs

2. **Staging**

   - Production-like environment
   - Real external API integration
   - Performance testing
   - Security scanning

3. **Production**
   - High availability setup
   - Auto-scaling enabled
   - Comprehensive monitoring
   - Disaster recovery ready

## 🎯 Future Architecture Considerations

### Microservices Migration

```mermaid
graph TB
    subgraph "Current Monolith"
        MONO[FastAPI Monolith]
    end

    subgraph "Target Microservices"
        AUTH_SVC[Auth Service]
        ANALYSIS_SVC[Analysis Service]
        SENTIMENT_SVC[Sentiment Service]
        OPTIONS_SVC[Options Service]
        FUNDAMENTALS_SVC[Fundamentals Service]
        SIGNALS_SVC[Signals Service]
    end

    subgraph "Service Mesh"
        ISTIO[Istio Service Mesh]
    end

    MONO -.->|Migrate| AUTH_SVC
    MONO -.->|Migrate| ANALYSIS_SVC
    MONO -.->|Migrate| SENTIMENT_SVC
    MONO -.->|Migrate| OPTIONS_SVC
    MONO -.->|Migrate| FUNDAMENTALS_SVC
    MONO -.->|Migrate| SIGNALS_SVC

    AUTH_SVC --> ISTIO
    ANALYSIS_SVC --> ISTIO
    SENTIMENT_SVC --> ISTIO
    OPTIONS_SVC --> ISTIO
    FUNDAMENTALS_SVC --> ISTIO
    SIGNALS_SVC --> ISTIO
```

### Event-Driven Architecture

```mermaid
graph TB
    subgraph "Event Sources"
        USER[User Actions]
        MARKET[Market Data]
        NEWS[News Updates]
    end

    subgraph "Event Bus"
        KAFKA[Apache Kafka]
    end

    subgraph "Event Consumers"
        ANALYSIS[Analysis Service]
        NOTIFICATIONS[Notification Service]
        ANALYTICS[Analytics Service]
    end

    USER --> KAFKA
    MARKET --> KAFKA
    NEWS --> KAFKA

    KAFKA --> ANALYSIS
    KAFKA --> NOTIFICATIONS
    KAFKA --> ANALYTICS
```

This architecture provides a solid foundation for scaling Stock Sage from a startup MVP to an enterprise-grade financial platform, with clear migration paths and extensibility built in.
