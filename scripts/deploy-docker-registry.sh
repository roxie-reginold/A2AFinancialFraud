#!/bin/bash
# ADK Financial Fraud Detection System - Docker Registry Deployment
# Manual build with Docker Registry and direct Cloud Run deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🐳 ADK Financial Fraud Detection - Docker Registry Deployment${NC}"
echo "=============================================================="

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

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
echo -e "${GREEN}✅ Docker version: $(docker --version)${NC}"

# Enable required APIs
echo -e "${YELLOW}📋 Enabling required APIs...${NC}"
gcloud services enable containerregistry.googleapis.com run.googleapis.com

# Configure Docker for GCR
echo -e "${YELLOW}🔧 Configuring Docker authentication...${NC}"
gcloud auth configure-docker --quiet

# Set deployment variables
SERVICE_NAME="fraud-detection-docker"
IMAGE_NAME="gcr.io/$PROJECT_ID/fraud-detection"
BUILD_TAG=$(date +%Y%m%d-%H%M%S)
REGION="us-central1"

echo ""
echo -e "${BLUE}📦 Docker Registry Deployment Configuration:${NC}"
echo "Service Name: $SERVICE_NAME"
echo "Docker Image: $IMAGE_NAME:$BUILD_TAG"
echo "Registry: Google Container Registry (GCR)"
echo "Region: $REGION"
echo "Build Method: Local Docker + GCR Push"
echo ""

# Ask for confirmation
read -p "Do you want to proceed with Docker Registry deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

# Build the Docker image locally
echo -e "${YELLOW}🔨 Building Docker image locally...${NC}"
docker build \
    --build-arg BUILD_ID="$BUILD_TAG" \
    --build-arg PROJECT_ID="$PROJECT_ID" \
    -t "$IMAGE_NAME:$BUILD_TAG" \
    -t "$IMAGE_NAME:latest" \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Push to Google Container Registry
echo -e "${YELLOW}📤 Pushing image to Google Container Registry...${NC}"
docker push "$IMAGE_NAME:$BUILD_TAG"
docker push "$IMAGE_NAME:latest"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Image pushed to GCR successfully${NC}"
else
    echo -e "${RED}❌ Failed to push image to GCR${NC}"
    exit 1
fi

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_NAME:$BUILD_TAG" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 4Gi \
    --cpu 2 \
    --max-instances 15 \
    --min-instances 0 \
    --timeout 600 \
    --concurrency 80 \
    --execution-environment gen2 \
    --set-env-vars "ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,BUILD_TAG=$BUILD_TAG" \
    --set-labels "app=fraud-detection,method=docker-registry,version=$BUILD_TAG"

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")

# Test deployment
echo -e "${YELLOW}🔍 Testing deployment...${NC}"
sleep 15
if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠️ Health check failed, but service may still be starting${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Docker Registry Deployment Complete!${NC}"
echo "=============================================="
echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"
echo -e "${GREEN}Docker Image: $IMAGE_NAME:$BUILD_TAG${NC}"
echo ""
echo -e "${BLUE}📋 Access Your Application:${NC}"
echo "🌐 Frontend Web App: $SERVICE_URL"
echo "📋 API Documentation: $SERVICE_URL/docs"
echo "💚 Health Check: $SERVICE_URL/health"
echo "🐳 Container Registry: https://console.cloud.google.com/gcr/images/$PROJECT_ID"
echo ""
echo -e "${BLUE}📊 Deployment Features:${NC}"
echo "✅ Local Docker build for faster iteration"
echo "✅ Google Container Registry storage"
echo "✅ Cloud Run Gen2 execution environment"
echo "✅ Enhanced resource allocation (4Gi RAM)"
echo "✅ Automatic scaling (0-15 instances)"
echo ""
echo -e "${BLUE}📋 Management Commands:${NC}"
echo "View logs: gcloud run services logs read $SERVICE_NAME --region=$REGION"
echo "Update service: gcloud run services update $SERVICE_NAME --region=$REGION"
echo "Delete service: gcloud run services delete $SERVICE_NAME --region=$REGION"
echo ""
echo -e "${CYAN}🐳 Docker Registry deployment complete!${NC}"