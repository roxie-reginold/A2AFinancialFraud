#!/bin/bash
# ADK Financial Fraud Detection System - Cloud Run Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ADK Financial Fraud Detection - Unified Full-Stack Deployment${NC}"
echo "==============================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK not found. Please install it first.${NC}"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ No Google Cloud project set. Run: gcloud config set project YOUR_PROJECT_ID${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Project: $PROJECT_ID${NC}"

# Check if required APIs are enabled
echo -e "${YELLOW}📋 Checking required APIs...${NC}"
REQUIRED_APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "containerregistry.googleapis.com"
    "aiplatform.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        echo -e "${GREEN}✅ $api${NC}"
    else
        echo -e "${YELLOW}⏳ Enabling $api...${NC}"
        gcloud services enable "$api"
    fi
done

# Set deployment variables
SERVICE_NAME="fraud-detection"
REGION="us-central1"
MEMORY="2Gi"
CPU="2"
MAX_INSTANCES="10"

echo ""
echo -e "${BLUE}📦 Unified Deployment Configuration:${NC}"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo "Memory: $MEMORY"
echo "CPU: $CPU"
echo "Max Instances: $MAX_INSTANCES"
echo "Frontend: React app (built in container)"
echo "Backend: Python FastAPI + Fraud Detection"
echo ""

# Ask for confirmation
read -p "Do you want to proceed with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8080 \
    --memory "$MEMORY" \
    --cpu "$CPU" \
    --max-instances "$MAX_INSTANCES" \
    --min-instances 0 \
    --timeout 300 \
    --concurrency 80 \
    --set-env-vars "ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")

echo ""
echo -e "${GREEN}🎉 Unified Full-Stack Deployment Complete!${NC}"
echo "======================================================="
echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"
echo ""
echo -e "${BLUE}📋 Access Your Application:${NC}"
echo "🌐 Frontend Web App: $SERVICE_URL"
echo "📋 API Documentation: $SERVICE_URL/docs"
echo "💚 Health Check: $SERVICE_URL/health"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Configure secrets (see CLOUD_RUN_DEPLOYMENT.md)"
echo "2. Test fraud detection with the web interface"
echo "3. Set up monitoring and alerting"
echo ""
echo -e "${YELLOW}💡 To configure email alerts, add these secrets:${NC}"
echo "gcloud secrets create EMAIL_SENDER --data-file=<(echo 'your-email@gmail.com')"
echo "gcloud secrets create EMAIL_PASSWORD --data-file=<(echo 'your-app-password')"
echo "gcloud secrets create EMAIL_RECIPIENTS --data-file=<(echo 'alerts@yourcompany.com')"
echo ""
echo -e "${BLUE}📖 For detailed configuration, see: CLOUD_RUN_DEPLOYMENT.md${NC}"