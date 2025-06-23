# ADK Financial Fraud Detection System v2 - Deployment Guide

This guide covers deploying the complete full-stack fraud detection application with React frontend and Python backend.

## 🚀 Quick Deploy

**Single Command Deployment:**
```bash
cd /Users/innovation/Documents/a2aFinancialFraud
./scripts/deploy_fraud_detection_v2.sh
```

This script will:
- ✅ Build React frontend 
- ✅ Create unified Docker image
- ✅ Deploy to Google Cloud Run
- ✅ Set up all required cloud resources
- ✅ Provide you with the live URL

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Google Cloud CLI** installed and authenticated
2. **Docker** installed and running
3. **Node.js** (v18+) installed
4. **Python 3.11+** installed
5. **Google Cloud Project** with billing enabled

## 🏗️ Architecture Overview

### Full-Stack Components:
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI with multi-agent fraud detection
- **Database**: Google BigQuery for data storage
- **Messaging**: Google Pub/Sub for real-time processing
- **AI**: Google Gemini for advanced fraud analysis
- **Deployment**: Google Cloud Run (serverless)

### Agent System:
- **MonitoringAgent**: Real-time transaction screening
- **HybridAnalysisAgent**: Smart AI/ML routing
- **AnalysisAgent**: Gemini-powered deep analysis
- **AlertAgent**: Multi-channel notifications

## 🛠️ Manual Deployment Steps

If you prefer manual deployment:

### 1. Authenticate with Google Cloud
```bash
gcloud auth login
gcloud config set project fraud-detection-adkhackathon
```

### 2. Enable Required APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable bigquery.googleapis.com
```

### 3. Build Frontend
```bash
cd frontend
npm ci --only=production
npm run build
cd ..
```

### 4. Build and Deploy with Cloud Build
```bash
gcloud builds submit --config cloudbuild-v2.yaml
```

### 5. Alternative: Docker Build and Push
```bash
# Configure Docker
gcloud auth configure-docker

# Build image
docker build -t gcr.io/fraud-detection-adkhackathon/fraud-detection-v2 .

# Push image
docker push gcr.io/fraud-detection-adkhackathon/fraud-detection-v2

# Deploy to Cloud Run
gcloud run deploy fraud-detection-v2 \
  --image gcr.io/fraud-detection-adkhackathon/fraud-detection-v2 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --port 8080
```

## 🌐 Access Your Deployed App

After deployment, you'll get a Cloud Run URL like:
```
https://fraud-detection-v2-[hash]-uc.a.run.app
```

### Available Endpoints:
- **Frontend Dashboard**: `https://your-url/`
- **API Documentation**: `https://your-url/docs`
- **Health Check**: `https://your-url/health`
- **API Base**: `https://your-url/api/v1`

## 🔧 Configuration

### Environment Variables (Production):
```bash
ENVIRONMENT=production
PROJECT_ID=fraud-detection-adkhackathon
REGION=us-central1
PORT=8080
API_HOST=0.0.0.0
GOOGLE_CLOUD_PROJECT=fraud-detection-adkhackathon
```

### Cloud Resources Created:
- **Pub/Sub Topics**: 
  - `transactions-topic`
  - `fraud-alerts`
- **Pub/Sub Subscriptions**:
  - `transactions-sub`
- **BigQuery Dataset**: `fraud_detection`
- **BigQuery Tables**:
  - `fraud_transactions`
  - `fraud_analysis` 
  - `fraud_alerts`

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-url/health
```

### 2. API Test
```bash
curl -X POST "https://your-url/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "test_001",
    "amount": 1500.00,
    "merchant": "Online Store",
    "location": "New York"
  }'
```

### 3. Frontend Test
Visit `https://your-url/` in your browser and:
- Click "Sample" to generate test data
- Click "Submit" to analyze a transaction
- Verify the agent workflow visualization works
- Check that alerts appear for high-risk transactions

## 📊 Monitoring and Logs

### View Application Logs:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=fraud-detection-v2" --limit 50
```

### Monitor Performance:
- Go to Cloud Run console: https://console.cloud.google.com/run
- Select your service to view metrics, logs, and performance

## 🔄 Updates and Redeployment

To update your deployment:
```bash
# Make your changes, then redeploy
./scripts/deploy_fraud_detection_v2.sh
```

Or with Cloud Build:
```bash
gcloud builds submit --config cloudbuild-v2.yaml
```

## 🛡️ Security Configuration

### Production Settings:
- CORS properly configured for your domain
- API authentication ready (currently allows unauthenticated for demo)
- Environment variables securely managed
- Container runs as non-root user

### To Enable API Authentication:
1. Update `fraud_api.py` to enforce authentication
2. Set up API keys or OAuth
3. Configure frontend to include auth headers

## ⚠️ Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check Node.js version (need v18+)
   - Verify frontend builds: `cd frontend && npm run build`

2. **Deployment Fails**:
   - Check Docker is running
   - Verify gcloud authentication: `gcloud auth list`
   - Check project billing is enabled

3. **App Doesn't Load**:
   - Check Cloud Run logs: `gcloud logs read`
   - Verify health endpoint: `curl https://your-url/health`

4. **API Errors**:
   - Check agent initialization in logs
   - Verify environment variables are set
   - Check BigQuery/Pub/Sub permissions

### Get Support:
- View detailed logs in Cloud Console
- Check Cloud Run service health
- Verify all APIs are enabled
- Ensure billing account is active

## 🎯 Production Checklist

Before going live:
- [ ] Set up custom domain
- [ ] Configure SSL certificate
- [ ] Enable API authentication
- [ ] Set up monitoring alerts
- [ ] Configure email notifications
- [ ] Set appropriate resource limits
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

## 💡 Next Steps

1. **Configure Email Alerts**: Update agent configuration for production email notifications
2. **Set Up Monitoring**: Configure Prometheus/Grafana for detailed metrics
3. **Custom Domain**: Point your domain to the Cloud Run service
4. **CI/CD**: Set up automatic deployments on code changes
5. **Scaling**: Adjust min/max instances based on traffic patterns

Your fraud detection system is now live and ready to process transactions! 🎉