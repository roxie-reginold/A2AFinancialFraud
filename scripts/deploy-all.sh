#!/bin/bash
# ADK Financial Fraud Detection System - Complete Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 ADK Financial Fraud Detection - Complete Deployment${NC}"
echo "================================================================"

# Check if we're in the right directory
if [ ! -f "Dockerfile.backend" ] || [ ! -f "Dockerfile.frontend" ]; then
    echo -e "${RED}❌ Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "${BLUE}📋 This will deploy both services:${NC}"
echo "1. Backend API service (Python FastAPI + ML agents)"
echo "2. Frontend web app (React + Nginx)"
echo ""

read -p "Deploy complete application? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}🔧 Step 1: Deploying Backend Service...${NC}"
echo "============================================="
./scripts/deploy-backend.sh

echo ""
echo -e "${YELLOW}🌐 Step 2: Deploying Frontend Service...${NC}"
echo "=============================================="
./scripts/deploy-frontend.sh

# Get final URLs
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
REGION="us-central1"
BACKEND_URL=$(gcloud run services describe "fraud-detection-backend" --region="$REGION" --format="value(status.url)")
FRONTEND_URL=$(gcloud run services describe "fraud-detection-frontend" --region="$REGION" --format="value(status.url)")

echo ""
echo -e "${GREEN}🎉 COMPLETE DEPLOYMENT SUCCESSFUL!${NC}"
echo "================================================================"
echo ""
echo -e "${BLUE}📱 Your Fraud Detection System is Live:${NC}"
echo -e "${GREEN}🌐 Application: $FRONTEND_URL${NC}"
echo ""
echo -e "${BLUE}📋 Service Architecture:${NC}"
echo "Frontend (React): $FRONTEND_URL"
echo "Backend (API):    $BACKEND_URL"
echo ""
echo -e "${BLUE}📋 API Endpoints:${NC}"
echo "🔌 API Base:     $BACKEND_URL/api/v1"
echo "📖 Documentation: $BACKEND_URL/docs"
echo "💚 Health Check: $BACKEND_URL/health"
echo ""
echo -e "${BLUE}📋 Features Deployed:${NC}"
echo "✅ Real-time fraud detection with ML agents"
echo "✅ Email alerting system for high-risk transactions"
echo "✅ Interactive web dashboard"
echo "✅ RESTful API for integrations"
echo "✅ Auto-scaling Cloud Run services"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Test your application: $FRONTEND_URL"
echo "2. Configure email settings in environment variables"
echo "3. Set up monitoring and alerting"
echo "4. Configure custom domain (optional)"
echo ""
echo -e "${PURPLE}🚀 Deployment complete! Your fraud detection system is ready.${NC}"