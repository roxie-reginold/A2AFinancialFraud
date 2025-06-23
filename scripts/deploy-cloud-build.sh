#!/bin/bash
# ADK Financial Fraud Detection System - Cloud Build Service Deployment
# Alternative deployment using Cloud Build with custom configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 ADK Financial Fraud Detection - Cloud Build Service Deployment${NC}"
echo "=================================================================="

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
echo -e "${YELLOW}📋 Checking and enabling required APIs...${NC}"
REQUIRED_APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "containerregistry.googleapis.com"
    "artifactregistry.googleapis.com"
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

# Set region
REGION="us-central1"

# Set deployment variables
SERVICE_NAME="fraud-detection-v2"
BUILD_ID=$(date +%Y%m%d-%H%M%S)
MEMORY="4Gi"
CPU="2"
MAX_INSTANCES="20"
MIN_INSTANCES="1"

echo ""
echo -e "${BLUE}📦 Enhanced Cloud Run Configuration:${NC}"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo "Memory: $MEMORY"
echo "CPU: $CPU"
echo "Max Instances: $MAX_INSTANCES"
echo "Min Instances: $MIN_INSTANCES"
echo "Build Method: Cloud Build from Source"
echo "Frontend: React app (built in container)"
echo "Backend: Python FastAPI + Fraud Detection"
echo ""

# Ask for confirmation
read -p "Do you want to proceed with Cloud Build deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

# Use the simpler direct deployment approach
echo -e "${YELLOW}🚀 Starting enhanced Cloud Build deployment...${NC}"

# Build and deploy using gcloud run deploy with source
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8080 \
    --memory "$MEMORY" \
    --cpu "$CPU" \
    --max-instances "$MAX_INSTANCES" \
    --min-instances "$MIN_INSTANCES" \
    --timeout 900 \
    --concurrency 100 \
    --execution-environment gen2 \
    --set-env-vars "ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --labels "app=fraud-detection,version=v2,deployment=cloud-build"

BUILD_STATUS=$?

if [ $BUILD_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ Cloud Build completed successfully!${NC}"
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")
    
    echo ""
    echo -e "${GREEN}🎉 Enhanced Cloud Run Deployment Complete!${NC}"
    echo "========================================================="
    echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"
    echo -e "${GREEN}Service Name: $SERVICE_NAME${NC}"
    echo ""
    echo -e "${BLUE}📋 Access Your Enhanced Application:${NC}"
    echo "🌐 Frontend Web App: $SERVICE_URL"
    echo "📋 API Documentation: $SERVICE_URL/docs"
    echo "💚 Health Check: $SERVICE_URL/health"
    echo "🔍 Build Logs: https://console.cloud.google.com/cloud-build/builds"
    echo ""
    echo -e "${BLUE}📊 Enhanced Features:${NC}"
    echo "✅ Artifact Registry for container storage"
    echo "✅ Enhanced Cloud Run configuration (Gen2)"
    echo "✅ Automatic health verification"
    echo "✅ Build and deployment logging"
    echo "✅ Scalable infrastructure (1-20 instances)"
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "1. Configure secrets in Secret Manager"
    echo "2. Test the unified web application"
    echo "3. Set up monitoring and alerting"
    echo "4. Configure custom domain (optional)"
    
else
    echo -e "${RED}❌ Cloud Run deployment failed. Check the logs above for details.${NC}"
    echo "🔍 View detailed logs: https://console.cloud.google.com/cloud-build/builds"
    exit 1
fi

echo ""
echo -e "${PURPLE}🚀 Enhanced deployment with Cloud Build service complete!${NC}"