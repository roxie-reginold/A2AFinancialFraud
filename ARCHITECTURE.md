# A2A Financial Fraud Detection System - Architecture

## System Overview

The A2A Financial Fraud Detection System is a comprehensive, cloud-native application that uses AI agents and machine learning to detect fraudulent transactions in real-time.

## Architecture Diagram

```mermaid
graph TB
    %% Frontend Layer
    subgraph "Frontend (Vercel)"
        FE[React/TypeScript Frontend]
        FE --> |API Calls| API
    end
    
    %% API Gateway Layer
    subgraph "Backend API (Render)"
        API[FastAPI Web Service]
        API --> |Routes| HEALTH[Health Endpoints]
        API --> |Routes| FRAUD[Fraud Analysis API]
        API --> |Routes| ALERTS[Alert Management API]
    end
    
    %% Core Application Layer
    subgraph "Fraud Detection Engine"
        ORCH[Fraud Detection Orchestrator]
        ORCH --> |Coordinates| AGENTS
        
        subgraph "AI Agents"
            MONITOR[Monitoring Agent]
            ANALYSIS[Analysis Agent]
            HYBRID[Hybrid Analysis Agent]
            ALERT[Alert Agent]
            REPORT[Reporting Agent]
        end
    end
    
    %% Data Layer
    subgraph "Data & Models"
        ML[ML Models]
        CSV[Credit Card Dataset]
        FEATURES[Feature Engineering]
    end
    
    %% External Services
    subgraph "Google Cloud Services"
        GCP[Google Cloud AI Platform]
        GEMINI[Gemini 2.5 Pro API]
        PUBSUB[Cloud Pub/Sub]
        BQ[BigQuery]
    end
    
    subgraph "Notification Services"
        EMAIL[Email Alerts]
        SLACK[Slack Notifications]
    end
    
    %% Data Flow Connections
    API --> ORCH
    ORCH --> MONITOR
    MONITOR --> |Flagged Transactions| ANALYSIS
    MONITOR --> |Flagged Transactions| HYBRID
    ANALYSIS --> |Risk Analysis| ALERT
    HYBRID --> |Risk Analysis| ALERT
    ALERT --> |High Risk| EMAIL
    ALERT --> |High Risk| SLACK
    ALERT --> REPORT
    
    %% External Integrations
    AGENTS --> |AI Processing| GEMINI
    AGENTS --> |Cloud Services| GCP
    ANALYSIS --> |Data| ML
    HYBRID --> |Data| ML
    ML --> CSV
    ML --> FEATURES
    
    %% Monitoring & Storage
    ORCH --> |Events| PUBSUB
    REPORT --> |Analytics| BQ
    
    %% Styling
    classDef frontend fill:#e1f5fe
    classDef backend fill:#f3e5f5
    classDef agents fill:#e8f5e8
    classDef external fill:#fff3e0
    classDef data fill:#fce4ec
    
    class FE frontend
    class API,HEALTH,FRAUD,ALERTS backend
    class ORCH,MONITOR,ANALYSIS,HYBRID,ALERT,REPORT agents
    class GCP,GEMINI,PUBSUB,BQ,EMAIL,SLACK external
    class ML,CSV,FEATURES data
```

## Component Details

### Frontend Layer (Vercel)
- **Technology**: React with TypeScript, Vite build system
- **Features**: 
  - Real-time transaction analysis interface
  - Agent workflow visualization
  - Dashboard with charts and metrics
  - Alert management interface
- **Deployment**: Vercel with automatic GitHub integration

### Backend API (Render)
- **Technology**: FastAPI with Python 3.11
- **Endpoints**:
  - `/api/v1/analyze` - Single transaction analysis
  - `/api/v1/analyze/bulk` - Batch transaction processing
  - `/api/v1/alerts` - Alert management
  - `/health` - Health monitoring
- **Features**: CORS support, request logging, background tasks

### Fraud Detection Engine

#### Orchestrator
- **Role**: Coordinates all AI agents and manages system lifecycle
- **Features**: Agent health monitoring, graceful shutdown, system statistics

#### AI Agents
1. **Monitoring Agent**: Continuous transaction monitoring and flagging
2. **Analysis Agent**: Standard fraud analysis using ML models
3. **Hybrid Analysis Agent**: Advanced analysis combining multiple techniques
4. **Alert Agent**: Manages and dispatches fraud alerts
5. **Reporting Agent**: Generates analytics and reports

### Data Layer
- **ML Models**: Keras-based fraud detection models
- **Dataset**: Credit card transaction dataset with anonymized features
- **Feature Engineering**: Real-time feature extraction and normalization

### External Integrations

#### Google Cloud Services
- **Gemini 2.5 Pro**: AI-powered transaction analysis
- **Cloud Pub/Sub**: Event streaming and messaging
- **BigQuery**: Analytics and data warehousing
- **AI Platform**: Model serving and inference

#### Notification Services
- **Email Alerts**: SMTP-based email notifications for high-risk transactions
- **Slack Integration**: Real-time Slack notifications (configurable)

## Data Flow

1. **Transaction Input**: User submits transaction through frontend
2. **API Processing**: FastAPI receives and validates transaction data
3. **Orchestration**: Orchestrator coordinates agent workflow
4. **Monitoring**: Transaction is evaluated for risk indicators
5. **Analysis**: Flagged transactions undergo detailed AI analysis
6. **Risk Assessment**: ML models and AI provide risk scores
7. **Alert Generation**: High-risk transactions trigger alerts
8. **Notification**: Alerts sent via email/Slack
9. **Reporting**: Results stored for analytics and reporting

## Security Features

- Environment variable management for API keys
- CORS configuration for cross-origin requests
- Request logging and monitoring
- Secure credential handling in deployment

## Deployment Architecture

```mermaid
graph LR
    subgraph "Development"
        GIT[GitHub Repository]
    end
    
    subgraph "Frontend Deployment"
        GIT --> |Auto Deploy| VERCEL[Vercel]
        VERCEL --> |Serves| FE_PROD[Production Frontend]
    end
    
    subgraph "Backend Deployment"
        GIT --> |Auto Deploy| RENDER[Render]
        RENDER --> |Runs| BE_PROD[Production API]
    end
    
    subgraph "External Services"
        GOOGLE[Google Cloud]
        EMAIL_SVC[Email Service]
    end
    
    FE_PROD --> |API Calls| BE_PROD
    BE_PROD --> |AI Processing| GOOGLE
    BE_PROD --> |Notifications| EMAIL_SVC
    
    classDef deployment fill:#e3f2fd
    classDef production fill:#e8f5e8
    classDef external fill:#fff3e0
    
    class GIT,VERCEL,RENDER deployment
    class FE_PROD,BE_PROD production
    class GOOGLE,EMAIL_SVC external
```

## Key Technologies

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Recharts
- **Backend**: FastAPI, Python 3.11, Uvicorn, Pydantic
- **AI/ML**: Google Gemini API, TensorFlow/Keras, Scikit-learn
- **Cloud**: Google Cloud Platform, Vercel, Render
- **Data**: Pandas, NumPy, Matplotlib, Seaborn
- **DevOps**: Docker, GitHub Actions, Environment Variables

## Environment Configuration

- **Development**: Local development with `.env.local`
- **Production**: Environment variables managed through deployment platforms
- **Security**: API keys and secrets managed as environment variables
- **Monitoring**: Health checks and logging across all components