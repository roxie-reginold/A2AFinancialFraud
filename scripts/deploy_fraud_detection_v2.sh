#!/bin/bash

# ADK Financial Fraud Detection System v2 - Full Stack Deployment Script
# This script deploys the complete fraud detection system with React frontend and Python backend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="fraud-detection-adkhackathon"
SERVICE_NAME="fraud-detection-v2"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
MEMORY="2Gi"
CPU="2"
MAX_INSTANCES="10"
MIN_INSTANCES="0"
PORT="8080"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE} $1 ${NC}"
    echo -e "${PURPLE}========================================${NC}"
}

# Check if required tools are installed
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI is not installed. Please install it first."
        exit 1
    fi
    print_success "Google Cloud CLI is installed"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    print_success "Node.js is installed"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    print_success "Python 3 is installed"
}

# Authenticate with Google Cloud
authenticate_gcloud() {
    print_header "Google Cloud Authentication"
    
    # Check if already authenticated
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        print_success "Already authenticated with Google Cloud"
    else
        print_status "Authenticating with Google Cloud..."
        gcloud auth login
    fi
    
    # Set project
    print_status "Setting project to $PROJECT_ID"
    gcloud config set project $PROJECT_ID
    
    # Enable required APIs
    print_status "Enabling required Google Cloud APIs..."
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    gcloud services enable aiplatform.googleapis.com
    gcloud services enable pubsub.googleapis.com
    gcloud services enable bigquery.googleapis.com
    
    print_success "Google Cloud setup complete"
}

# Setup environment variables
setup_environment() {
    print_header "Setting Up Environment"
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# ADK Financial Fraud Detection System v2 Configuration
ENVIRONMENT=production
PROJECT_ID=${PROJECT_ID}
REGION=${REGION}

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=${PROJECT_ID}
GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json

# Agent Configuration
ADK_AGENT_MODE=production
ENABLE_MONITORING=true
ENABLE_EMAIL_ALERTS=false

# API Configuration
API_HOST=0.0.0.0
API_PORT=${PORT}
CORS_ORIGINS=*

# Frontend Configuration
REACT_APP_API_URL=/api/v1
REACT_APP_ENVIRONMENT=production

# Pub/Sub Topics
PUBSUB_TOPIC_TRANSACTIONS=transactions-topic
PUBSUB_TOPIC_ALERTS=fraud-alerts
PUBSUB_SUBSCRIPTION_TRANSACTIONS=transactions-sub

# BigQuery Configuration
BIGQUERY_DATASET=fraud_detection
BIGQUERY_TABLE_TRANSACTIONS=fraud_transactions
BIGQUERY_TABLE_ANALYSIS=fraud_analysis
BIGQUERY_TABLE_ALERTS=fraud_alerts

# Model Configuration
ML_MODEL_PATH=/app/models/fraud_detection_model.keras
GEMINI_MODEL=gemini-2.5-pro-preview-05-06
AI_THRESHOLD=0.7

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
EOF
        print_success "Environment file created"
    else
        print_success "Environment file already exists"
    fi
}

# Build React frontend
build_frontend() {
    print_header "Building React Frontend"
    
    cd frontend
    
    # Install dependencies
    print_status "Installing frontend dependencies..."
    npm ci --only=production
    
    # Build React app
    print_status "Building React application for production..."
    npm run build
    
    # Verify build
    if [ ! -d "dist" ]; then
        print_error "Frontend build failed - dist directory not found"
        exit 1
    fi
    
    print_success "Frontend build completed successfully"
    cd ..
}

# Build and push Docker image
build_and_push_image() {
    print_header "Building and Pushing Docker Image"
    
    # Configure Docker for gcloud
    print_status "Configuring Docker authentication..."
    gcloud auth configure-docker
    
    # Build Docker image
    print_status "Building Docker image: $IMAGE_NAME"
    docker build -t $IMAGE_NAME .
    
    # Push to Container Registry
    print_status "Pushing image to Google Container Registry..."
    docker push $IMAGE_NAME
    
    print_success "Docker image built and pushed successfully"
}

# Deploy to Cloud Run
deploy_to_cloud_run() {
    print_header "Deploying to Cloud Run"
    
    print_status "Deploying service: $SERVICE_NAME"
    
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory $MEMORY \
        --cpu $CPU \
        --max-instances $MAX_INSTANCES \
        --min-instances $MIN_INSTANCES \
        --port $PORT \
        --set-env-vars "ENVIRONMENT=production,PROJECT_ID=$PROJECT_ID,REGION=$REGION" \
        --timeout 3600 \
        --concurrency 80
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
    
    print_success "Service deployed successfully!"
    print_success "Service URL: $SERVICE_URL"
}

# Setup Cloud Resources
setup_cloud_resources() {
    print_header "Setting Up Cloud Resources"
    
    # Create Pub/Sub topics
    print_status "Creating Pub/Sub topics..."
    
    # Check if topics exist, create if not
    if ! gcloud pubsub topics describe transactions-topic &>/dev/null; then
        gcloud pubsub topics create transactions-topic
        print_success "Created transactions-topic"
    else
        print_success "transactions-topic already exists"
    fi
    
    if ! gcloud pubsub topics describe fraud-alerts &>/dev/null; then
        gcloud pubsub topics create fraud-alerts
        print_success "Created fraud-alerts topic"
    else
        print_success "fraud-alerts topic already exists"
    fi
    
    # Create subscriptions
    if ! gcloud pubsub subscriptions describe transactions-sub &>/dev/null; then
        gcloud pubsub subscriptions create transactions-sub --topic=transactions-topic
        print_success "Created transactions-sub subscription"
    else
        print_success "transactions-sub subscription already exists"
    fi
    
    # Create BigQuery dataset
    print_status "Setting up BigQuery dataset..."
    if ! bq show ${PROJECT_ID}:fraud_detection &>/dev/null; then
        bq mk --dataset ${PROJECT_ID}:fraud_detection
        print_success "Created BigQuery dataset: fraud_detection"
    else
        print_success "BigQuery dataset already exists"
    fi
    
    # Create BigQuery tables
    print_status "Creating BigQuery tables..."
    
    # Fraud transactions table
    bq mk --table \
        ${PROJECT_ID}:fraud_detection.fraud_transactions \
        transaction_id:STRING,user_id:STRING,amount:FLOAT,currency:STRING,timestamp:TIMESTAMP,merchant:STRING,location:STRING,payment_method:STRING,flagged:BOOLEAN,processed_at:TIMESTAMP
    
    # Analysis results table
    bq mk --table \
        ${PROJECT_ID}:fraud_detection.fraud_analysis \
        analysis_id:STRING,transaction_id:STRING,risk_score:FLOAT,is_fraud:BOOLEAN,analysis_method:STRING,model_confidence:FLOAT,processing_time_ms:INTEGER,analyzed_at:TIMESTAMP
    
    # Alerts table
    bq mk --table \
        ${PROJECT_ID}:fraud_detection.fraud_alerts \
        alert_id:STRING,transaction_id:STRING,risk_score:FLOAT,priority:STRING,analysis_summary:STRING,alert_timestamp:TIMESTAMP,status:STRING
    
    print_success "Cloud resources setup completed"
}

# Test deployment
test_deployment() {
    print_header "Testing Deployment"
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
    
    # Test health endpoint
    print_status "Testing health endpoint..."
    if curl -f "$SERVICE_URL/health" &>/dev/null; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        return 1
    fi
    
    # Test API endpoint
    print_status "Testing API endpoint..."
    if curl -f "$SERVICE_URL/api/v1/health" &>/dev/null; then
        print_success "API health check passed"
    else
        print_error "API health check failed"
        return 1
    fi
    
    # Test frontend
    print_status "Testing frontend..."
    if curl -f "$SERVICE_URL/" &>/dev/null; then
        print_success "Frontend is accessible"
    else
        print_error "Frontend test failed"
        return 1
    fi
    
    print_success "All tests passed!"
}

# Cleanup function
cleanup() {
    print_header "Cleanup (Optional)"
    
    read -p "Do you want to cleanup local Docker images? (y/N): " cleanup_docker
    if [[ $cleanup_docker =~ ^[Yy]$ ]]; then
        print_status "Cleaning up local Docker images..."
        docker rmi $IMAGE_NAME 2>/dev/null || true
        print_success "Local Docker images cleaned up"
    fi
}

# Main deployment function
main() {
    print_header "ADK Financial Fraud Detection System v2 Deployment"
    print_status "Starting full-stack deployment process..."
    
    # Check if we're in the right directory
    if [ ! -f "main.py" ] || [ ! -d "frontend" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Run deployment steps
    check_prerequisites
    authenticate_gcloud
    setup_environment
    setup_cloud_resources
    build_frontend
    build_and_push_image
    deploy_to_cloud_run
    test_deployment
    
    # Get final service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
    
    print_header "Deployment Complete!"
    echo -e "${GREEN}🎉 Your fraud detection system is now live!${NC}"
    echo -e "${CYAN}Frontend URL: ${SERVICE_URL}${NC}"
    echo -e "${CYAN}API URL: ${SERVICE_URL}/api/v1${NC}"
    echo -e "${CYAN}API Docs: ${SERVICE_URL}/docs${NC}"
    echo -e "${CYAN}Health Check: ${SERVICE_URL}/health${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "1. Configure email alerts if needed"
    echo -e "2. Set up monitoring and alerting"
    echo -e "3. Configure custom domain (optional)"
    echo -e "4. Set up CI/CD pipeline (optional)"
    echo ""
    
    cleanup
}

# Run main function
main "$@"