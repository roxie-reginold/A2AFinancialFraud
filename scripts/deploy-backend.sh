#!/bin/bash
# ADK Financial Fraud Detection System - Backend Cloud Run Deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 ADK Financial Fraud Detection - Backend Deployment${NC}"
echo "============================================================"

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
echo -e "${YELLOW}📋 Enabling required APIs...${NC}"
REQUIRED_APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "artifactregistry.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    gcloud services enable "$api" --quiet
done

# Set deployment variables
REGION="us-central1"
SERVICE_NAME="fraud-detection-backend"
MEMORY="2Gi"
CPU="2"
MAX_INSTANCES="10"
MIN_INSTANCES="1"

echo ""
echo -e "${BLUE}📦 Backend Configuration:${NC}"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo "Memory: $MEMORY"
echo "CPU: $CPU"
echo "Max Instances: $MAX_INSTANCES"
echo "Min Instances: $MIN_INSTANCES"
echo ""

# Ask for confirmation
read -p "Deploy backend service? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

echo -e "${YELLOW}🚀 Deploying backend service...${NC}"

# Create temporary cloudbuild.yaml for backend
cat > cloudbuild-backend.yaml << EOF
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-f', 'Dockerfile.backend', '-t', 'gcr.io/$PROJECT_ID/\${_SERVICE_NAME}', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/\${_SERVICE_NAME}']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - '\${_SERVICE_NAME}'
      - '--image=gcr.io/$PROJECT_ID/\${_SERVICE_NAME}'
      - '--region=\${_REGION}'
      - '--allow-unauthenticated'
      - '--port=8080'
      - '--memory=\${_MEMORY}'
      - '--cpu=\${_CPU}'
      - '--max-instances=\${_MAX_INSTANCES}'
      - '--min-instances=\${_MIN_INSTANCES}'
      - '--timeout=900'
      - '--concurrency=50'
      - '--execution-environment=gen2'
      - '--set-env-vars=ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=$PROJECT_ID'
      - '--labels=app=fraud-detection,component=backend,version=v2'
images:
  - 'gcr.io/$PROJECT_ID/\${_SERVICE_NAME}'
substitutions:
  _SERVICE_NAME: '$SERVICE_NAME'
  _REGION: '$REGION'
  _MEMORY: '$MEMORY'
  _CPU: '$CPU'
  _MAX_INSTANCES: '$MAX_INSTANCES'
  _MIN_INSTANCES: '$MIN_INSTANCES'
EOF

# Deploy using Cloud Build
gcloud builds submit --config=cloudbuild-backend.yaml .

DEPLOY_STATUS=$?

if [ $DEPLOY_STATUS -eq 0 ]; then
    # Get service URL
    BACKEND_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")
    
    echo ""
    echo -e "${GREEN}🎉 Backend Deployment Complete!${NC}"
    echo "================================="
    echo -e "${GREEN}Backend URL: $BACKEND_URL${NC}"
    echo ""
    echo -e "${BLUE}📋 Backend Endpoints:${NC}"
    echo "🔌 API: $BACKEND_URL/api/v1"
    echo "📖 Docs: $BACKEND_URL/docs"
    echo "💚 Health: $BACKEND_URL/health"
    echo ""
    echo -e "${YELLOW}📝 Save this URL for frontend deployment:${NC}"
    echo "$BACKEND_URL"
    
    # Clean up temporary file
    rm -f cloudbuild-backend.yaml
    
else
    echo -e "${RED}❌ Backend deployment failed.${NC}"
    rm -f cloudbuild-backend.yaml
    exit 1
fi

echo ""
echo -e "${PURPLE}✅ Backend deployment complete!${NC}"