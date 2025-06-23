#!/bin/bash
# ADK Financial Fraud Detection System - Complete Deployment Script
# Version: 2.0.0
# Description: End-to-end deployment script for the financial fraud detection system on Google Cloud Run

set -eo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REGION="us-central1"
BACKEND_SERVICE="fraud-detection-backend"
FRONTEND_SERVICE="fraud-detection-frontend"
PROJECT_ID=""

# Function to print section headers
section() {
    echo -e "\n${PURPLE}### $1 ###${NC}"
    echo -e "${PURPLE}##################################${NC}"
}

# Function to check command existence
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}❌ Error: $1 could not be found. Please install it and try again.${NC}"
        exit 1
    fi
}

# Function to validate GCP authentication
validate_gcp_auth() {
    if ! gcloud auth list --filter=status:ACTIVE --format='value(account)' &>/dev/null; then
        echo -e "${RED}❌ Not authenticated with Google Cloud. Please run 'gcloud auth login' first.${NC}"
        exit 1
    fi

    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ No Google Cloud project set. Run: gcloud config set project YOUR_PROJECT_ID${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Authenticated as: $(gcloud config get-value account)${NC}"
    echo -e "${GREEN}✓ Project: $PROJECT_ID${NC}"
}

# Function to enable required GCP APIs
enable_required_apis() {
    section "Enabling Required GCP APIs"
    
    local REQUIRED_APIS=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "artifactregistry.googleapis.com"
        "cloudresourcemanager.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
    )

    for api in "${REQUIRED_APIS[@]}"; do
        echo -e "${YELLOW}Enabling $api...${NC}"
        gcloud services enable "$api" --project="$PROJECT_ID" --quiet || {
            echo -e "${RED}❌ Failed to enable $api${NC}"
            return 1
        }
    done
    
    echo -e "${GREEN}✓ All required APIs enabled${NC}"
}

# Function to deploy a service
deploy_service() {
    local service_type=$1
    local script_path="./scripts/deploy-${service_type}.sh"
    
    if [ ! -f "$script_path" ]; then
        echo -e "${RED}❌ Deployment script not found: $script_path${NC}"
        return 1
    fi
    
    # Convert first character to uppercase for display
    local display_type=$(echo "$service_type" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}')
    echo -e "\n${YELLOW}🔧 Deploying $display_type Service...${NC}"
    echo "============================================="
    
    if bash "$script_path"; then
        echo -e "\n${GREEN}✓ $display_type service deployed successfully!${NC}"
        return 0
    else
        echo -e "\n${RED}❌ $display_type service deployment failed${NC}"
        return 1
    fi
}

# Function to get service URL
get_service_url() {
    local service=$1
    local url
    
    echo -e "\n${YELLOW}🔍 Getting $service URL...${NC}"
    url=$(gcloud run services describe "$service" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format="value(status.url)" 2>/dev/null || echo "")
    
    if [ -z "$url" ]; then
        echo -e "${RED}❌ Failed to get URL for $service${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ $service URL: $url${NC}"
    echo "$url"
    return 0
}

# Function to clean up temporary files
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up temporary files...${NC}"
    rm -f cloudbuild-*.yaml
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Main execution
main() {
    echo -e "${PURPLE}🚀 ADK Financial Fraud Detection - Complete Deployment${NC}"
    echo "================================================================"

    # Check if we're in the right directory
    if [ ! -f "Dockerfile.backend" ] || [ ! -f "Dockerfile.frontend" ]; then
        echo -e "${RED}❌ Please run this script from the project root directory${NC}"
        exit 1
    fi

    # Check for required commands
    check_command "gcloud"
    check_command "docker"

    # Validate GCP authentication
    validate_gcp_auth

    # Show deployment plan
    echo -e "${BLUE}📋 Deployment Plan:${NC}"
    echo "1. Enable required GCP APIs"
    echo "2. Deploy Backend Service (FastAPI + ML Agents)"
    echo "3. Deploy Frontend Service (React + Nginx)"
    echo ""

    read -p "Proceed with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deployment cancelled.${NC}"
        exit 0
    fi

    # Enable required GCP APIs
    if ! enable_required_apis; then
        echo -e "${RED}❌ Failed to enable required APIs${NC}"
        exit 1
    fi

    # Deploy backend
    if ! deploy_service "backend"; then
        cleanup
        exit 1
    fi

    # Deploy frontend
    if ! deploy_service "frontend"; then
        cleanup
        exit 1
    fi

    # Get service URLs
    BACKEND_URL=$(get_service_url "$BACKEND_SERVICE")
    FRONTEND_URL=$(get_service_url "$FRONTEND_SERVICE")

    # Clean up
    cleanup

    # Show success message
    echo -e "\n${GREEN}🎉 COMPLETE DEPLOYMENT SUCCESSFUL!${NC}"
    echo "================================================================"
    
    echo -e "\n${BLUE}📱 Your Fraud Detection System is Live:${NC}"
    echo -e "${GREEN}🌐 Application: $FRONTEND_URL${NC}"
    
    echo -e "\n${BLUE}📋 Service Architecture:${NC}"
    echo "Frontend (React): $FRONTEND_URL"
    echo "Backend (API):    $BACKEND_URL"
    
    echo -e "\n${BLUE}📋 API Endpoints:${NC}"
    echo "🔌 API Base:     $BACKEND_URL/api/v1"
    echo "📖 Documentation: $BACKEND_URL/docs"
    echo "💚 Health Check: $BACKEND_URL/health"
    
    echo -e "\n${BLUE}📋 Features Deployed:${NC}"
    echo "✅ Real-time fraud detection with ML agents"
    echo "✅ Email alerting system for high-risk transactions"
    echo "✅ Interactive web dashboard"
    echo "✅ RESTful API for integrations"
    echo "✅ Auto-scaling Cloud Run services"
    
    echo -e "\n${BLUE}📋 Next Steps:${NC}"
    echo "1. Test your application: $FRONTEND_URL"
    echo "2. Configure email settings in environment variables"
    echo "3. Set up monitoring and alerting in Google Cloud Console"
    echo "4. Configure custom domain (optional)"
    echo -e "\n${CYAN}💡 Tip: Run 'gcloud run services update-traffic' to manage traffic splitting between revisions${NC}"
    
    echo -e "\n${PURPLE}🚀 Deployment complete! Your fraud detection system is ready.${NC}"
}

# Run main function
main "$@"

exit 0