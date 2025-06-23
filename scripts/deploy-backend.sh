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
COMMIT_SHA="$(git rev-parse --short HEAD)"
SHORT_SHA="${COMMIT_SHA:0:7}"

# Enable additional required APIs
ADDITIONAL_APIS=(
    "secretmanager.googleapis.com"
    "sqladmin.googleapis.com"
    "vpcaccess.googleapis.com"
    "servicenetworking.googleapis.com"
    "cloudkms.googleapis.com"
)

echo -e "${YELLOW}📋 Enabling additional required APIs...${NC}"
for api in "${ADDITIONAL_APIS[@]}"; do
    gcloud services enable "$api" --project="$PROJECT_ID" --quiet || echo -e "${YELLOW}⚠️  Failed to enable $api, continuing anyway...${NC}"
done

# Create VPC connector if it doesn't exist
VPC_CONNECTOR="fraud-detection-connector"
if ! gcloud compute networks vpc-access connectors describe "$VPC_CONNECTOR" --region="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    echo -e "${YELLOW}🔧 Creating VPC connector...${NC}"
    gcloud compute networks vpc-access connectors create "$VPC_CONNECTOR" \
        --region="$REGION" \
        --subnet=default \
        --min-instances=2 \
        --max-instances=10 \
        --machine-type=e2-micro \
        --project="$PROJECT_ID" || echo -e "${YELLOW}⚠️  Failed to create VPC connector, continuing anyway...${NC}
else
    echo -e "${GREEN}✅ VPC connector already exists${NC}"
fi

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
  # Build the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    id: 'build'
    args: ['build', 
           '-f', 'Dockerfile.backend', 
           '--build-arg', 'COMMIT_SHA=$COMMIT_SHA',
           '-t', 'gcr.io/$PROJECT_ID/$SERVICE_NAME:$COMMIT_SHA', 
           '-t', 'gcr.io/$PROJECT_ID/$SERVICE_NAME:latest',
           '.']
    
  # Push the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    id: 'push'
    args: ['push', 'gcr.io/$PROJECT_ID/$SERVICE_NAME:$COMMIT_SHA']
    
  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    id: 'deploy'
    args:
      - 'run'
      - 'deploy'
      - '$SERVICE_NAME'
      - '--image=gcr.io/$PROJECT_ID/$SERVICE_NAME:$COMMIT_SHA'
      - '--region=$REGION'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--port=8080'
      - '--memory=$MEMORY'
      - '--cpu=$CPU'
      - '--max-instances=$MAX_INSTANCES'
      - '--min-instances=$MIN_INSTANCES'
      - '--timeout=300s'
      - '--concurrency=80'
      - '--ingress=all'
      - '--vpc-connector=projects/$PROJECT_ID/locations/$REGION/connectors/fraud-detection-connector'
      - '--vpc-egress=all-traffic'
      - '--set-env-vars=ENVIRONMENT=production,PYTHONUNBUFFERED=1,GCP_PROJECT=$PROJECT_ID,REGION=$REGION'
      - '--revision-suffix=$SHORT_SHA'
      - '--no-cpu-throttling'
      - '--session-affinity'
      - '--labels=app=fraud-detection,component=backend,environment=production,managed-by=cloud-build,commit-sha=$SHORT_SHA'
      - '--format=json'
    timeout: 1200s
    
  # Get the service URL
  - name: 'gcr.io/cloud-builders/gcloud'
    id: 'get-url'
    args: ['run', 'services', 'describe', '$SERVICE_NAME', '--region=$REGION', '--platform=managed', '--format=value(status.url)']
    waitFor: ['deploy']

# Store the built images
images:
  - 'gcr.io/$PROJECT_ID/$SERVICE_NAME:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/$SERVICE_NAME:latest'

# Store the service URL as a build variable
availableSecrets:
  secretManager:
  - versionName: projects/$PROJECT_ID/secrets/SERVICE_URL/versions/latest
    env: 'SERVICE_URL'

# Store build artifacts
artifacts:
  objects:
    location: 'gs://$PROJECT_ID-cloudbuild-logs/backend/'
    paths: ['**/*']

# Timeout for the entire build
timeout: 1800s

# Machine type for the build
options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY

# Substitutions for the build
substitutions:
  _SERVICE_NAME: '$SERVICE_NAME'
  _REGION: '$REGION'
  _MEMORY: '$MEMORY'
  _CPU: '$CPU'
  _MAX_INSTANCES: '$MAX_INSTANCES'
  _MIN_INSTANCES: '$MIN_INSTANCES'
  _COMMIT_SHA: '$COMMIT_SHA'
  _SHORT_SHA: '$SHORT_SHA'
EOF

# Deploy using Cloud Build
echo -e "${YELLOW}🚀 Deploying backend service using Cloud Build...${NC}"

# Submit the build to Cloud Build
gcloud builds submit \
  --config=cloudbuild-backend.yaml \
  --project=$PROJECT_ID \
  --substitutions=_SERVICE_NAME=$SERVICE_NAME,_REGION=$REGION,_MEMORY=$MEMORY,_CPU=$CPU,_MAX_INSTANCES=$MAX_INSTANCES,_MIN_INSTANCES=$MIN_INSTANCES,_COMMIT_SHA=$COMMIT_SHA,_SHORT_SHA=$SHORT_SHA \
  --async

# Wait for the service to be ready
echo -e "\n${YELLOW}⏳ Waiting for the service to be ready...${NC}"

# Maximum number of attempts to check service status
MAX_ATTEMPTS=30
ATTEMPT=1
SERVICE_URL=""

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo -n "."
    
    # Try to get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
        --region=$REGION \
        --platform=managed \
        --format='value(status.url)' 2>/dev/null)
    
    # If we got a URL, the service is ready
    if [ -n "$SERVICE_URL" ]; then
        echo -e "\n\n${GREEN}✅ Service is ready!${NC}"
        break
    fi
    
    # If we've reached max attempts, exit with an error
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo -e "\n\n${RED}❌ Timed out waiting for service to be ready.${NC}"
        echo -e "${YELLOW}   Check the Cloud Run console for more details:${NC}"
        echo -e "   https://console.cloud.google.com/run?project=$PROJECT_ID"
        exit 1
    fi
    
    # Wait before trying again
    sleep 10
    ATTEMPT=$((ATTEMPT + 1))
done

# Display service information
echo -e "\n${BLUE}🌐 Service Information:${NC}"
echo -e "   Name: ${GREEN}$SERVICE_NAME${NC}"
echo -e "   URL: ${GREEN}$SERVICE_URL${NC}"
echo -e "   Region: ${GREEN}$REGION${NC}"
echo -e "   Memory: ${GREEN}$MEMORY${NC}"
echo -e "   CPU: ${GREEN}$CPU${NC}"
echo -e "   Min Instances: ${GREEN}$MIN_INSTANCES${NC}"
echo -e "   Max Instances: ${GREEN}$MAX_INSTANCES${NC}"

# Test the health check endpoint
echo -e "\n${YELLOW}🧪 Testing health check endpoint...${NC}"
HEALTH_CHECK_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health" 2>/dev/null || echo "000")

if [ "$HEALTH_CHECK_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Health check returned status code: $HEALTH_CHECK_RESPONSE${NC}"
    echo -e "${YELLOW}   The service might still be starting up.${NC}"
fi

# Display useful links
echo -e "\n${BLUE}🔗 Useful Links:${NC}"
echo -e "   Service Overview: ${BLUE}https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME?project=$PROJECT_ID${NC}"
echo -e "   Logs: ${BLUE}https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/logs?project=$PROJECT_ID${NC}"
echo -e "   Metrics: ${BLUE}https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/metrics?project=$PROJECT_ID${NC}"
echo -e "   Revisions: ${BLUE}https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/revisions?project=$PROJECT_ID${NC}"

echo -e "\n${GREEN}🚀 Deployment completed successfully!${NC}"
echo -e "${YELLOW}   The service might take a few minutes to be fully available.${NC}"

# Clean up
rm -f cloudbuild-backend.yaml

exit 0

echo ""
echo -e "${PURPLE}✅ Backend deployment complete!${NC}"