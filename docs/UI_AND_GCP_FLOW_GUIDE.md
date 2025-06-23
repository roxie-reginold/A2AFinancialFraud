# ADK Financial Fraud Detection System - UI & GCP Flow Guide

## Overview

This guide provides step-by-step flows for using the fraud detection system's web interface and monitoring Google Cloud Platform resources.

## 🖥️ UI Flow - Using the Web Dashboard

### Prerequisites
- System running on `localhost:8001` (API) and `localhost:8080` (Health)
- Frontend running on `http://localhost:5173` (Vite dev server)

### Step 1: Start the System
```bash
# Option 1: Full system with GCP integration
python main.py

# Option 2: Development mode (no GCP required)
python run_dev.py

# Option 3: Start frontend separately
cd frontend
npm install
npm run dev
```

### Step 2: Access the Dashboard
1. **Open Browser**: Navigate to `http://localhost:5173`
2. **Dashboard Components**:
   - Sidebar navigation
   - Alert banner (shows fraud alerts)
   - Transaction input form
   - Real-time status bar
   - Analysis results card
   - Charts (transactions over time, fraud detection)

### Step 3: Submit a Transaction for Analysis
1. **Fill Transaction Form**:
   - **Account Number**: Enter any account number (e.g., "ACC123456")
   - **Amount**: Enter transaction amount (e.g., 1500.00)
   - **Description**: Enter transaction description (e.g., "Online purchase electronics")

2. **Submit for Analysis**:
   - Click "Analyze Transaction" button
   - Watch progress bar during processing
   - System generates V1-V28 features automatically based on amount and description

### Step 4: View Analysis Results
1. **Status Updates**:
   - Progress bar shows analysis progress (0-100%)
   - Status changes: idle → in_progress → completed/error

2. **Results Display**:
   - **Risk Score**: 0.0 to 1.0 (higher = more fraudulent)
   - **Fraud Classification**: "Fraudulent" or "Not Fraudulent"
   - **Risk Level**: LOW/MEDIUM/HIGH based on score thresholds

3. **Alert Handling**:
   - High-risk transactions (>0.8) trigger red warning banner
   - Alert auto-dismisses or can be manually closed

### Step 5: Monitor System Health
1. **Health Dashboard**: `http://localhost:8080/docs`
   - `/health` - Overall system status
   - `/health/agents` - Individual agent health
   - `/health/detailed` - Comprehensive health info
   - `/metrics` - Prometheus metrics
   - `/ready` - Kubernetes readiness probe
   - `/live` - Kubernetes liveness probe

### Step 6: API Testing (Optional)
1. **API Documentation**: `http://localhost:8001/docs`
   - Test endpoints directly via Swagger UI
   - `/api/v1/analyze` - Single transaction analysis
   - `/api/v1/analyze/bulk` - Bulk transaction processing
   - `/api/v1/alerts` - Alert management

---

## ☁️ Google Cloud Platform Monitoring Flow

### Prerequisites
- Google Cloud Project set up
- Service account with appropriate permissions
- Environment variables configured

### Step 1: Environment Setup
```bash
# Set required environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_API_KEY="your-api-key"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"

# Optional: For development without GCP
export BYPASS_CLOUD_VALIDATION="true"
```

### Step 2: Initialize GCP Resources
```bash
# Run the GCP setup script
python scripts/setup_gcp_resources.py
```

**This script creates**:
- **Pub/Sub Topics**:
  - `transactions-topic` - Incoming transactions
  - `flagged-transactions` - Flagged for analysis
  - `analysis-results` - Analysis outcomes
  - `hybrid-analysis-results` - Hybrid analysis results
  - `fraud-alerts` - High-risk alerts

- **Pub/Sub Subscriptions**:
  - `transactions-sub` - Monitor transactions
  - `flagged-sub` - Process flagged transactions
  - `analysis-sub` - Handle analysis results
  - `alerts-sub` - Manage fraud alerts

- **BigQuery Dataset**: `fraud_detection`
  - `fraud_transactions` - Transaction records
  - `fraud_analysis` - Analysis results
  - `fraud_alerts` - Alert records
  - `fraud_reports` - Generated reports

### Step 3: Monitor Pub/Sub Activity

#### Using Google Cloud Console
1. **Navigate to Pub/Sub**: `https://console.cloud.google.com/cloudpubsub`
2. **Check Topics**:
   - View message throughput
   - Monitor publish rates
   - Check for message backlogs
3. **Check Subscriptions**:
   - Monitor pull rates
   - Check unacknowledged messages
   - View delivery attempts

#### Using gcloud CLI
```bash
# List all topics
gcloud pubsub topics list

# Monitor specific topic
gcloud pubsub topics describe transactions-topic

# Check subscription status
gcloud pubsub subscriptions describe transactions-sub

# Pull messages manually (for testing)
gcloud pubsub subscriptions pull transactions-sub --limit=5
```

### Step 4: Monitor BigQuery Data

#### Using Google Cloud Console
1. **Navigate to BigQuery**: `https://console.cloud.google.com/bigquery`
2. **Check Dataset**: `fraud_detection`
3. **Query Transaction Data**:
```sql
-- Recent transactions
SELECT * FROM `fraud_detection.fraud_transactions` 
ORDER BY created_at DESC 
LIMIT 10;

-- Analysis results
SELECT 
  transaction_id,
  risk_score,
  analysis_method,
  fraud_indicators,
  created_at
FROM `fraud_detection.fraud_analysis`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR);

-- Active alerts
SELECT * FROM `fraud_detection.fraud_alerts`
WHERE status = 'ACTIVE'
ORDER BY created_at DESC;
```

#### Using bq CLI
```bash
# Query recent transactions
bq query --use_legacy_sql=false "
SELECT COUNT(*) as transaction_count 
FROM \`fraud_detection.fraud_transactions\`
WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
"

# Export data
bq extract --destination_format=CSV \
  fraud_detection.fraud_analysis \
  gs://your-bucket/analysis_export.csv
```

### Step 5: System Health Monitoring

#### Application Metrics
```bash
# Check system health
curl http://localhost:8080/health

# Get detailed agent status
curl http://localhost:8080/health/agents

# Prometheus metrics
curl http://localhost:8080/metrics
```

#### GCP Resource Monitoring
1. **Cloud Monitoring Dashboard**:
   - Create custom dashboards for Pub/Sub metrics
   - Monitor BigQuery job statistics
   - Set up alerting policies

2. **Key Metrics to Monitor**:
   - Pub/Sub message publish/pull rates
   - BigQuery query job success rates
   - API response times and error rates
   - Resource utilization (CPU, memory)

### Step 6: Troubleshooting Common Issues

#### Pub/Sub Issues
```bash
# Check if topics exist
python -c "
from google.cloud import pubsub_v1
client = pubsub_v1.PublisherClient()
project_path = f'projects/{client.project}'
topics = list(client.list_topics(request={'project': project_path}))
print(f'Found {len(topics)} topics')
"

# Test message publishing
python -c "
from google.cloud import pubsub_v1
import json
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('your-project-id', 'transactions-topic')
message_data = json.dumps({'test': 'message'}).encode('utf-8')
future = publisher.publish(topic_path, message_data)
print(f'Message ID: {future.result()}')
"
```

#### BigQuery Issues
```bash
# Test BigQuery connectivity
python -c "
from google.cloud import bigquery
client = bigquery.Client()
datasets = list(client.list_datasets())
print(f'Found {len(datasets)} datasets')
"

# Check table schemas
bq show --schema fraud_detection.fraud_transactions
```

#### API Issues
```bash
# Test API endpoints
curl -X GET http://localhost:8080/health
curl -X GET http://localhost:8001/api/v1/health

# Test transaction analysis
curl -X POST http://localhost:8001/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "transaction_id": "test_001",
    "amount": 100.0,
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

---

## 📊 Complete Workflow Example

### End-to-End Transaction Processing

1. **Start System**: `python main.py`
2. **Open UI**: Browser to `http://localhost:5173`
3. **Submit Transaction**: Amount $2500, Description "Cash withdrawal ATM"
4. **Monitor Processing**:
   - Watch progress bar in UI
   - Check Pub/Sub messages: `gcloud pubsub subscriptions pull transactions-sub --limit=1`
   - Verify BigQuery insert: Query `fraud_detection.fraud_transactions`
5. **Review Results**:
   - High amount triggers fraud detection
   - Alert generated and displayed in UI
   - Data stored in BigQuery for reporting
6. **GCP Verification**:
   - Check Pub/Sub topic activity
   - Verify BigQuery data insertion
   - Monitor system metrics

### Health Check Workflow

1. **Automated Checks**: System runs health checks every 30 seconds
2. **Manual Verification**:
   ```bash
   # Application health
   curl http://localhost:8080/health
   
   # Agent-specific health
   curl http://localhost:8080/health/agents
   
   # Prometheus metrics
   curl http://localhost:8080/metrics
   
   # GCP resource status
   python scripts/setup_gcp_resources.py  # includes verification
   ```

---

## 🔧 Configuration Notes

### Development vs Production

**Development Mode** (`ENVIRONMENT=development`):
- Uses mock data and local processing
- Bypasses GCP validation
- Simplified logging
- CORS allows all origins

**Production Mode** (`ENVIRONMENT=production`):
- Requires all GCP resources
- Strict authentication
- Comprehensive logging
- Security middleware enabled

### Environment Variables

```bash
# Required for production
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-api-key
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Optional configurations
HIGH_RISK_THRESHOLD=0.8
MEDIUM_RISK_THRESHOLD=0.5
ENABLE_EMAIL_ALERTS=true
EMAIL_SENDER=alerts@yourcompany.com
EMAIL_RECIPIENTS=admin@yourcompany.com,security@yourcompany.com

# Development bypass
BYPASS_CLOUD_VALIDATION=true
```

---

This guide provides complete flows for both UI interaction and GCP monitoring, enabling effective use and maintenance of the fraud detection system.