#!/bin/bash
# ADK Financial Fraud Detection System - Frontend Cloud Run Deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 ADK Financial Fraud Detection - Frontend Deployment${NC}"
echo "============================================================="

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

# Set deployment variables
REGION="us-central1"
SERVICE_NAME="fraud-detection-frontend"
BACKEND_SERVICE="fraud-detection-backend"
MEMORY="512Mi"
CPU="1"
MAX_INSTANCES="5"
MIN_INSTANCES="1"

# Get backend URL (required for frontend to work)
echo -e "${YELLOW}📋 Getting backend service URL...${NC}"
BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" --region="$REGION" --format="value(status.url)" 2>/dev/null)

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}❌ Backend service not found. Deploy backend first with: ./scripts/deploy-backend.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend URL: $BACKEND_URL${NC}"

echo ""
echo -e "${BLUE}📦 Frontend Configuration:${NC}"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo "Memory: $MEMORY"
echo "CPU: $CPU"
echo "Max Instances: $MAX_INSTANCES"
echo "Min Instances: $MIN_INSTANCES"
echo "Backend URL: $BACKEND_URL"
echo ""

# Ask for confirmation
read -p "Deploy frontend service? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

echo -e "${YELLOW}🚀 Deploying frontend service...${NC}"

# Create temporary cloudbuild.yaml for frontend
cat > cloudbuild-frontend.yaml << EOF
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-f', 'Dockerfile.frontend', '-t', 'gcr.io/$PROJECT_ID/$SERVICE_NAME', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/$SERVICE_NAME']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - '$SERVICE_NAME'
      - '--image=gcr.io/$PROJECT_ID/$SERVICE_NAME'
      - '--region=$REGION'
      - '--allow-unauthenticated'
      - '--port=8080'
      - '--memory=$MEMORY'
      - '--cpu=$CPU'
      - '--max-instances=$MAX_INSTANCES'
      - '--min-instances=$MIN_INSTANCES'
      - '--timeout=300'
      - '--concurrency=100'
      - '--execution-environment=gen2'
      - '--set-env-vars=BACKEND_URL=$BACKEND_URL'
      - '--labels=app=fraud-detection,component=frontend,version=v2'
images:
  - 'gcr.io/$PROJECT_ID/$SERVICE_NAME'
substitutions:
  _SERVICE_NAME: '$SERVICE_NAME'
  _REGION: '$REGION'
  _MEMORY: '$MEMORY'
  _CPU: '$CPU'
  _MAX_INSTANCES: '$MAX_INSTANCES'
  _MIN_INSTANCES: '$MIN_INSTANCES'
  _BACKEND_URL: '$BACKEND_URL'
EOF

# Deploy using Cloud Build
gcloud builds submit --config=cloudbuild-frontend.yaml .

DEPLOY_STATUS=$?

if [ $DEPLOY_STATUS -eq 0 ]; then
    # Get service URL
    FRONTEND_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")
    
    echo ""
    echo -e "${GREEN}🎉 Frontend Deployment Complete!${NC}"
    echo "=================================="
    echo -e "${GREEN}Frontend URL: $FRONTEND_URL${NC}"
    echo ""
    echo -e "${BLUE}📋 Application Access:${NC}"
    echo "🌐 Web App: $FRONTEND_URL"
    echo "💚 Health: $FRONTEND_URL/health"
    echo ""
    echo -e "${BLUE}📋 Connected Services:${NC}"
    echo "🔌 Backend API: $BACKEND_URL"
    echo "📖 API Docs: $BACKEND_URL/docs"
    echo ""
    echo -e "${BLUE}📋 Complete Application:${NC}"
    echo "✅ Frontend: $FRONTEND_URL"
    echo "✅ Backend: $BACKEND_URL"
    echo "✅ Services Connected: Yes"
    
    # Clean up temporary file
    rm -f cloudbuild-frontend.yaml
    
else
    echo -e "${RED}❌ Frontend deployment failed.${NC}"
    rm -f cloudbuild-frontend.yaml
    exit 1
fi

echo ""
echo -e "${PURPLE}✅ Frontend deployment complete!${NC}"