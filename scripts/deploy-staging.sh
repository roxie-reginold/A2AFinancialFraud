#!/bin/bash
# ADK Financial Fraud Detection System - Staging Environment Deployment
# Deploy to staging environment for testing before production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${MAGENTA}🧪 ADK Financial Fraud Detection - Staging Environment Deployment${NC}"
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

# Enable required APIs
echo -e "${YELLOW}📋 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# Set staging deployment variables
SERVICE_NAME="fraud-detection-staging"
REGION="us-central1"
MEMORY="2Gi"
CPU="1"
MAX_INSTANCES="5"
MIN_INSTANCES="0"
ENV="staging"

echo ""
echo -e "${BLUE}📦 Staging Environment Configuration:${NC}"
echo "Service Name: $SERVICE_NAME"
echo "Environment: $ENV"
echo "Region: $REGION"
echo "Memory: $MEMORY"
echo "CPU: $CPU"
echo "Max Instances: $MAX_INSTANCES (limited for staging)"
echo "Min Instances: $MIN_INSTANCES (scales to zero)"
echo "Purpose: Testing and validation"
echo ""

# Ask for confirmation
read -p "Do you want to proceed with staging deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Staging deployment cancelled.${NC}"
    exit 0
fi

# Create staging-specific environment variables
echo -e "${YELLOW}🔧 Configuring staging environment...${NC}"
STAGING_ENV_VARS="ENVIRONMENT=staging"
STAGING_ENV_VARS="$STAGING_ENV_VARS,GOOGLE_CLOUD_PROJECT=$PROJECT_ID"
STAGING_ENV_VARS="$STAGING_ENV_VARS,ENABLE_EMAIL_ALERTS=false"
STAGING_ENV_VARS="$STAGING_ENV_VARS,HIGH_RISK_THRESHOLD=0.7"
STAGING_ENV_VARS="$STAGING_ENV_VARS,MEDIUM_RISK_THRESHOLD=0.4"

# Deploy to Cloud Run with staging configuration
echo -e "${YELLOW}🚀 Deploying to staging environment...${NC}"
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8080 \
    --memory "$MEMORY" \
    --cpu "$CPU" \
    --max-instances "$MAX_INSTANCES" \
    --min-instances "$MIN_INSTANCES" \
    --timeout 300 \
    --concurrency 50 \
    --execution-environment gen2 \
    --set-env-vars "$STAGING_ENV_VARS" \
    --set-labels "environment=staging,app=fraud-detection,purpose=testing" \
    --tag staging

# Get service URLs
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")
STAGING_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.traffic[0].url)")

# Test the staging deployment
echo -e "${YELLOW}🔍 Testing staging deployment...${NC}"
sleep 20

# Health check
if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Staging health check passed${NC}"
else
    echo -e "${YELLOW}⚠️ Staging health check failed${NC}"
fi

# API documentation check
if curl -f "$SERVICE_URL/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API documentation accessible${NC}"
else
    echo -e "${YELLOW}⚠️ API documentation check failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Staging Environment Deployment Complete!${NC}"
echo "================================================"
echo -e "${GREEN}Staging URL: $SERVICE_URL${NC}"
echo ""
echo -e "${BLUE}📋 Staging Environment Access:${NC}"
echo "🧪 Frontend Web App: $SERVICE_URL"
echo "📋 API Documentation: $SERVICE_URL/docs"
echo "💚 Health Check: $SERVICE_URL/health"
echo "🏷️  Staging Tag: $STAGING_URL"
echo ""
echo -e "${BLUE}📊 Staging Configuration:${NC}"
echo "✅ Reduced resource allocation for cost efficiency"
echo "✅ Email alerts disabled for testing"
echo "✅ Lower risk thresholds for more test cases"
echo "✅ Limited scaling for controlled testing"
echo "✅ Tagged deployment for easy identification"
echo ""
echo -e "${BLUE}📋 Testing Checklist:${NC}"
echo "□ Test frontend interface functionality"
echo "□ Verify API endpoints work correctly"
echo "□ Test transaction analysis with sample data"
echo "□ Validate agent workflow visualization"
echo "□ Check error handling and edge cases"
echo "□ Performance testing with concurrent requests"
echo ""
echo -e "${BLUE}📋 Promotion to Production:${NC}"
echo "After testing, promote to production with:"
echo "gcloud run services update-traffic $SERVICE_NAME --region=$REGION --to-latest"
echo ""
echo -e "${YELLOW}💡 Staging Environment Notes:${NC}"
echo "• This is a testing environment with limited resources"
echo "• Email alerts are disabled to prevent spam during testing"
echo "• Use this environment to validate changes before production"
echo "• Monitor logs: gcloud run services logs read $SERVICE_NAME --region=$REGION"
echo ""
echo -e "${MAGENTA}🧪 Staging environment ready for testing!${NC}"