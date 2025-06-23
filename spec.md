# A2A Financial Fraud Detection System — Project Specification

## Overview

This is an **end-to-end, multi-agent financial fraud detection platform** built for the Google Cloud Multi-Agents Hackathon. The system provides real-time transaction monitoring, AI-powered fraud analysis, intelligent alerting, and comprehensive reporting using Google Cloud services and Gemini LLM.

**Project**: `fraud-detection-adkhackathon`  
**Google Cloud Region**: `us-central1`  
**Primary AI Model**: `gemini-2.5-pro-preview-05-06`

---

## System Architecture

### **Core Components**

### 1. **Transaction Monitoring Agent** (`monitor_agent.py`)
- Real-time transaction ingestion from Google Pub/Sub
- Credit card transaction processing using ML models
- Initial fraud flagging and risk scoring
- Streams flagged transactions to analysis pipeline

### 2. **AI Analysis Agent** (`analysis_agent.py`)
- **Primary Gemini Integration**: Uses `gemini-2.5-pro-preview-05-06` via Vertex AI
- Advanced fraud risk assessment and pattern recognition
- Detailed transaction analysis with risk scoring (0.0-1.0)
- Generates AI-powered fraud explanations and recommendations
- Handles batch and individual transaction analysis

### 3. **Hybrid Analysis Agent** (`hybrid_analysis_agent.py`)
- Intelligent decision engine combining AI and local ML models
- Routes high-risk cases to Gemini for detailed analysis
- Uses local ML models for standard transactions
- Optimizes cost and performance based on risk levels

### 4. **Alert Agent** (`alert_agent.py`)
- Multi-channel notification system
- **Email**: SMTP integration (Gmail configured)
- **Console**: Structured logging
- **Pub/Sub**: Real-time alert streaming
- Risk-based alert prioritization
- Failed alert recovery and retry logic

### 5. **Reporting Agent** (`reporting_agent.py`)
- Comprehensive data pipeline to BigQuery
- Automated daily/weekly fraud analytics
- Trend analysis and statistical reporting
- Looker Studio dashboard configuration
- Real-time metrics and KPI tracking

### 6. **Main Orchestrator** (`main.py`)
- Central coordination of all agents
- FastAPI-based health monitoring
- System lifecycle management
- Graceful shutdown handling

---

## Google Cloud Integration

### **Pub/Sub Topics & Subscriptions**
- **Topic**: `transactions-topic` - Incoming transaction stream
- **Subscription**: `transactions-sub` - Agent message processing
- **Alerts Topic**: Real-time fraud alerts
- **Reports Topic**: Analytics and reporting data

### **BigQuery Data Warehouse**
- **Dataset**: `fraud_detection`
- **Tables**: 
  - `fraud_transactions` - Raw transaction data
  - `fraud_analysis` - AI analysis results
  - `fraud_alerts` - Alert history
  - `fraud_reports` - Analytical reports

### **Vertex AI Integration**
- **Model**: `gemini-2.5-pro-preview-05-06`
- **Region**: `us-central1`
- **Use Cases**: Fraud pattern analysis, risk assessment, natural language explanations

---

## Machine Learning Pipeline

### **Local ML Models**
- **Framework**: TensorFlow/Keras
- **Model File**: `models/fraud_detection_model.keras`
- **Dataset**: Credit card transactions (`models/creditcard.csv`)
- **Features**: PCA-transformed transaction features (V1-V28)

### **AI-Enhanced Analysis**
- **Gemini Integration**: Advanced pattern recognition
- **Risk Scoring**: Probabilistic fraud assessment
- **Explanability**: Natural language fraud explanations
- **Recommendations**: Actionable fraud prevention insights

---

## Required Features

- [x] Real-time transaction ingestion and analysis
- [x] Multi-channel alerting (console, email, Pub/Sub)
- [x] Batch and real-time data streaming to BigQuery
- [x] Automated daily/weekly analytics reports
- [x] Data quality checks and error recovery logging
- [x] Environment variable-based config for secure deployment
- [x] Comprehensive testing suite for all agents
- [x] **Gemini LLM Integration** for intelligent fraud analysis
- [x] **Hybrid AI/ML approach** for cost optimization
- [x] **Multi-agent orchestration** with ADK framework

---

## Technical Stack

### **Core Dependencies**
```
google-adk                    # Agent Development Kit
google-genai                  # Gemini API integration
google-cloud-aiplatform       # Vertex AI services
google-cloud-pubsub          # Message streaming
google-cloud-bigquery        # Data warehouse
vertexai                     # AI platform SDK
tensorflow                   # ML models
fastapi                      # API framework
```

### **Development Tools**
```
pytest                       # Testing framework
python-dotenv                # Environment management
colorlog                     # Enhanced logging
uvicorn                      # ASGI server
```

---

## Project Structure

```
a2aFinancialFraud/
├── agents/                  # Multi-agent system
│   ├── analysis_agent.py    # Gemini-powered fraud analysis
│   ├── hybrid_analysis_agent.py  # AI/ML hybrid engine
│   ├── alert_agent.py       # Multi-channel alerting
│   ├── reporting_agent.py   # Analytics and reporting
│   ├── monitor_agent.py     # Transaction monitoring
│   └── agents.py           # ADK configuration
├── api/                     # FastAPI services
│   ├── fraud_api.py        # REST API endpoints
│   └── health.py           # Health monitoring
├── config/                  # System configuration
│   └── settings.py         # Centralized settings
├── models/                  # ML models and data
│   ├── fraud_detection_model.keras
│   └── creditcard.csv
├── tests/                   # Comprehensive test suite
├── recovery/                # Failed transaction recovery
├── visualization/          # Data analysis charts
├── main.py                 # System orchestrator
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── docker-compose.yml     # Container orchestration
└── Dockerfile             # Container definition
```

---

## Environment Configuration

### **Required Variables (.env)**
```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=fraud-detection-adkhackathon
GOOGLE_API_KEY=your-gemini-api-key

# Email Alerting
ALERT_EMAIL_SENDER=your-email@gmail.com
ALERT_EMAIL_PASSWORD=your-app-password
ALERT_EMAIL_RECIPIENTS=alerts@domain.com

# Model Configuration
GEMINI_MODEL=gemini-2.5-pro-preview-05-06

# System Configuration
ENVIRONMENT=development
HIGH_RISK_THRESHOLD=0.8
MEDIUM_RISK_THRESHOLD=0.5
ENABLE_EMAIL_ALERTS=true
```

---

## Deployment Options

### **Local Development**
```bash
pip install -r requirements.txt
python main.py
```

### **Docker Deployment**
```bash
docker-compose up --build
```

### **Google Cloud Run**
```bash
gcloud builds submit --tag gcr.io/fraud-detection-adkhackathon/fraud-system
gcloud run deploy fraud-detection \
  --image gcr.io/fraud-detection-adkhackathon/fraud-system \
  --platform managed \
  --region us-central1
```

---

## Key Innovations

### **1. Multi-Agent Architecture**
- Specialized agents for different fraud detection tasks
- Coordinated via Google ADK framework
- Scalable and maintainable design

### **2. Hybrid AI/ML Approach**
- Gemini LLM for complex fraud pattern analysis
- Local ML models for high-throughput processing
- Intelligent routing based on risk assessment

### **3. Real-time Processing**
- Stream processing via Google Pub/Sub
- Immediate fraud detection and alerting
- Continuous learning and adaptation

### **4. Comprehensive Observability**
- Multi-channel alerting system
- Detailed analytics and reporting
- Recovery mechanisms for failed operations

---

## Testing Strategy

### **Test Coverage**
- Unit tests for all agent components
- Integration tests for Google Cloud services
- End-to-end fraud detection scenarios
- Performance and load testing

### **Test Execution**
```bash
pytest tests/ -v --cov=agents
```

---

## Future Extensions

- [ ] Advanced ML model ensemble techniques
- [ ] Real-time model retraining pipeline
- [ ] Enhanced Gemini prompt engineering
- [ ] Custom dashboard frontend
- [ ] Advanced fraud pattern library
- [ ] Multi-language support for alerts

---

## Hackathon Compliance

✅ **Multi-Agent System**: Specialized agents with distinct responsibilities  
✅ **Google Cloud Integration**: Pub/Sub, BigQuery, Vertex AI  
✅ **Gemini LLM Usage**: Core fraud analysis and explanation generation  
✅ **Real-world Application**: Financial fraud detection use case  
✅ **Scalable Architecture**: Production-ready design patterns  
✅ **Comprehensive Documentation**: Complete technical specification  

---

## Maintainers

* Innovation Team - A2A Financial Fraud Detection
* Project: Google Cloud Multi-Agents Hackathon
* Contact: Technical implementation and system architecture

---

## Development Status

- [x] Core agent architecture implemented
- [x] Gemini LLM integration complete
- [x] Google Cloud services integrated
- [x] Multi-channel alerting system
- [x] Comprehensive testing suite
- [x] Docker containerization
- [x] Documentation and specification
- [ ] Production deployment optimization
- [ ] Advanced analytics dashboard