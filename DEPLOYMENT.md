# ADK Financial Fraud Detection System - Deployment Guide

## System Overview

The ADK Financial Fraud Detection System is a real-time fraud detection platform built for the Google Cloud Multi-Agents Hackathon. It uses Google ADK (Agent Development Kit) to orchestrate multiple AI agents for comprehensive fraud analysis.

## Architecture

### Multi-Agent System
- **MonitoringAgent**: Real-time transaction surveillance and initial flagging
- **AnalysisAgent**: AI-powered fraud analysis using Gemini 2.5 Pro
- **HybridAnalysisAgent**: Intelligent routing between AI and local ML models
- **AlertAgent**: Multi-channel alert generation and severity classification

### Technology Stack
- **Framework**: Google ADK (Agent Development Kit)
- **AI Model**: Gemini 2.5 Pro Preview via Vertex AI
- **Cloud Platform**: Google Cloud Platform
- **Language**: Python 3.11+
- **Data Storage**: Google BigQuery
- **Messaging**: Google Cloud Pub/Sub
- **API**: FastAPI
- **ML Framework**: TensorFlow/Keras (optional for local models)

## Prerequisites

### Required Tools
- Python 3.11 or higher
- Google Cloud SDK
- Docker (for Cloud Run deployment)
- Google Cloud Project with billing enabled

## Deployment Options

### ⭐ Google Cloud Run (Recommended)
**Best for production deployment with automatic scaling**

See detailed guide: [CLOUD_RUN_DEPLOYMENT.md](CLOUD_RUN_DEPLOYMENT.md)

Quick deployment:
```bash
# Enable required APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# Deploy directly from source
gcloud run deploy fraud-detection \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi
```

### Local Development
**Best for development and testing**

### Required APIs
- Vertex AI API
- Pub/Sub API
- BigQuery API
- Cloud Storage API

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd a2aFinancialFraud

# Create virtual environment
python -m venv venv312
source venv312/bin/activate  # On Windows: venv312\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy and configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-gemini-api-key

# Model Configuration
GEMINI_MODEL=gemini-2.5-pro-preview-05-06

# Development Settings
BYPASS_CLOUD_VALIDATION=false
LOG_LEVEL=INFO
```

### 3. Google Cloud Setup

```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud config set project your-project-id

# Create required resources
python scripts/setup_gcp_resources.py
```

### 4. Testing

Run the comprehensive test suite:
```bash
python test_system.py
```

Run individual demos:
```bash
# Basic demo
python demos/demo_main.py

# High-risk scenario demo
python demos/demo_high_risk.py

# Simple agent test
python agents/simple_analysis_agent.py
```

## Deployment Options

### Development Mode

For local development and testing:
```bash
python demos/demo_main.py
```

### Production Mode

For full system deployment:
```bash
python main.py
```

### Docker Deployment

```bash
# Build the container
docker build -t fraud-detection .

# Run with environment variables
docker run --env-file .env fraud-detection
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Configuration Details

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | GCP Project ID | `fraud-detection-adkhackathon` |
| `GOOGLE_API_KEY` | Gemini API Key | Required |
| `GEMINI_MODEL` | Gemini model version | `gemini-2.5-pro-preview-05-06` |
| `BYPASS_CLOUD_VALIDATION` | Skip cloud connectivity checks | `false` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

### Google Cloud Resources

The system requires these GCP resources:

**Pub/Sub Topics:**
- `transaction-stream` - Incoming transactions
- `flagged-transactions` - Suspicious transactions
- `analysis-results` - Analysis outputs
- `fraud-alerts` - Alert notifications

**BigQuery Datasets:**
- `fraud_detection` - Main dataset
- Tables: `transactions`, `analysis_results`, `alerts`

**Vertex AI:**
- Gemini 2.5 Pro Preview model access
- Vertex AI API enabled

## Monitoring and Observability

### Health Checks

The system provides health check endpoints:
- `/health` - Basic health status
- `/health/detailed` - Comprehensive system status
- `/metrics` - System metrics and statistics

### Logging

Structured logging is configured with different levels:
- `DEBUG` - Detailed debugging information
- `INFO` - General operational information
- `WARNING` - Warning conditions
- `ERROR` - Error conditions
- `CRITICAL` - Critical issues requiring immediate attention

### Metrics

Key metrics tracked:
- Transaction processing rate
- Fraud detection accuracy
- Alert generation frequency
- AI/ML model performance
- System resource utilization

## Security Considerations

### API Keys
- Store API keys securely in environment variables
- Never commit keys to version control
- Use Google Cloud Secret Manager in production

### Network Security
- Configure VPC firewall rules
- Use private Google access for internal communication
- Implement TLS for all external connections

### Data Protection
- Encrypt sensitive data at rest and in transit
- Implement data retention policies
- Follow PCI DSS compliance for financial data

## Troubleshooting

### Common Issues

**ADK Import Errors:**
```bash
pip install google-adk
```

**Vertex AI Authentication:**
```bash
gcloud auth application-default login
```

**Missing Dependencies:**
```bash
pip install -r requirements.txt
```

**Pub/Sub Permissions:**
Ensure the service account has:
- Pub/Sub Publisher
- Pub/Sub Subscriber
- BigQuery Data Editor

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python demos/demo_main.py
```

### Test Connectivity

Test individual components:
```bash
python test_simple_agent.py  # Test basic ADK connectivity
python agents/simple_analysis_agent.py  # Test analysis agent
```

## Performance Tuning

### Scaling Considerations
- Use Google Cloud Run for auto-scaling
- Configure Pub/Sub subscription settings
- Optimize BigQuery query performance
- Implement connection pooling

### Cost Optimization
- Use the hybrid analysis approach (AI + local ML)
- Configure appropriate batch sizes
- Implement intelligent routing based on transaction value
- Monitor Gemini API usage

## Support and Maintenance

### Monitoring
- Set up alerts for system failures
- Monitor fraud detection accuracy
- Track API usage and costs
- Review security logs regularly

### Updates
- Keep dependencies updated
- Monitor for ADK framework updates
- Update Gemini model versions as available
- Regular security patches

## Contact

For technical support or questions about deployment:
- GitHub Issues: [Repository Issues Page]
- Documentation: [System Documentation]
- Hackathon Support: [Google Cloud Multi-Agents Hackathon]

---

**Note**: This system was developed for the Google Cloud Multi-Agents Hackathon and demonstrates advanced AI agent orchestration for financial fraud detection. It serves as a proof-of-concept and foundation for production fraud detection systems.