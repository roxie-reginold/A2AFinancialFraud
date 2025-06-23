# Cloud Run Deployment Guide
## ADK Financial Fraud Detection System - Unified Full-Stack Deployment

This guide covers deploying the complete fraud detection system (React frontend + Python backend) to Google Cloud Run in a single container for production use.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **APIs Enabled:**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   ```

3. **Authentication:**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

## Environment Configuration

### Required Environment Variables

Create these secrets in Google Secret Manager:

```bash
# Email configuration
gcloud secrets create EMAIL_SENDER --data-file=<(echo "your-email@gmail.com")
gcloud secrets create EMAIL_PASSWORD --data-file=<(echo "your-app-password")
gcloud secrets create EMAIL_RECIPIENTS --data-file=<(echo "alerts@yourcompany.com")

# Google API Key
gcloud secrets create GOOGLE_API_KEY --data-file=<(echo "your-gemini-api-key")
```

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

1. **Setup Cloud Build trigger:**
   ```bash
   gcloud builds triggers create github \
     --repo-name=your-repo \
     --repo-owner=your-username \
     --branch-pattern="^main$" \
     --build-config=cloudbuild.yaml
   ```

2. **Manual build and deploy:**
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

### Method 2: Direct gcloud Deployment

1. **Build and deploy in one step:**
   ```bash
   gcloud run deploy fraud-detection \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --memory 2Gi \
     --cpu 2 \
     --max-instances 10 \
     --set-env-vars ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT
   ```

### Method 3: Container Registry

1. **Build and push image:**
   ```bash
   # Build
   docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/fraud-detection .
   
   # Push
   docker push gcr.io/$GOOGLE_CLOUD_PROJECT/fraud-detection
   
   # Deploy
   gcloud run deploy fraud-detection \
     --image gcr.io/$GOOGLE_CLOUD_PROJECT/fraud-detection \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Production Configuration

### Resource Limits
```yaml
Memory: 2Gi
CPU: 2
Max Instances: 10
Min Instances: 0 (scales to zero)
Timeout: 300s
Concurrency: 80
```

### Environment Variables
```bash
ENVIRONMENT=production
GOOGLE_CLOUD_PROJECT=your-project-id
PORT=8080 (set automatically by Cloud Run)
```

### Secret Management
Attach secrets to Cloud Run service:

```bash
gcloud run services update fraud-detection \
  --region us-central1 \
  --set-secrets EMAIL_SENDER=EMAIL_SENDER:latest \
  --set-secrets EMAIL_PASSWORD=EMAIL_PASSWORD:latest \
  --set-secrets EMAIL_RECIPIENTS=EMAIL_RECIPIENTS:latest \
  --set-secrets GOOGLE_API_KEY=GOOGLE_API_KEY:latest
```

## Custom Domain (Optional)

1. **Map custom domain:**
   ```bash
   gcloud run domain-mappings create \
     --service fraud-detection \
     --domain fraud.yourcompany.com \
     --region us-central1
   ```

2. **Configure DNS:**
   - Add CNAME record pointing to `ghs.googlehosted.com`

## Monitoring and Logging

### Cloud Logging
Logs are automatically sent to Cloud Logging. View them:
```bash
gcloud logs read "resource.type=cloud_run_revision" --limit 50
```

### Health Checks
Service includes built-in health check at `/health`:
```bash
curl https://your-service-url/health
```

### Metrics
- CPU utilization
- Memory usage
- Request count
- Request latency

## Security

### IAM Permissions
Grant necessary permissions:
```bash
# For Cloud Run service account
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member="serviceAccount:fraud-detection@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member="serviceAccount:fraud-detection@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### VPC Integration (Optional)
For additional security, deploy to VPC:
```bash
gcloud run services update fraud-detection \
  --region us-central1 \
  --vpc-connector your-vpc-connector
```

## Testing Deployment

1. **Health Check:**
   ```bash
   curl https://your-service-url/health
   ```

2. **API Documentation:**
   ```bash
   curl https://your-service-url/docs
   ```

3. **Test Transaction Analysis:**
   ```bash
   curl -X POST https://your-service-url/api/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{
       "transaction_id": "test_001",
       "amount": 15000,
       "merchant": "Test Merchant"
     }'
   ```

## Scaling Configuration

### Auto-scaling
Cloud Run automatically scales based on:
- Request volume
- CPU utilization
- Memory usage

### Manual Scaling
```bash
# Set minimum instances (keep warm)
gcloud run services update fraud-detection \
  --region us-central1 \
  --min-instances 1

# Set maximum instances
gcloud run services update fraud-detection \
  --region us-central1 \
  --max-instances 50
```

## Cost Optimization

1. **Scale to Zero:** Default configuration allows scaling to zero when no traffic
2. **Right-sizing:** Start with 2Gi memory, 2 CPU and adjust based on usage
3. **Regional Deployment:** Deploy in region closest to your users
4. **Request Timeout:** Set appropriate timeout (default 300s)

## Troubleshooting

### Common Issues

1. **Cold Starts:**
   - Set min-instances > 0 for critical services
   - Optimize container startup time

2. **Memory Issues:**
   - Increase memory allocation
   - Check for memory leaks in logs

3. **Timeout Issues:**
   - Increase request timeout
   - Optimize slow operations

### Debug Commands
```bash
# View service details
gcloud run services describe fraud-detection --region us-central1

# View recent logs
gcloud logs tail "resource.type=cloud_run_revision"

# Check service status
gcloud run services list
```

## Production Checklist

- [ ] Enable required GCP APIs
- [ ] Configure secrets in Secret Manager
- [ ] Set up monitoring and alerting
- [ ] Configure custom domain (if needed)
- [ ] Set up CI/CD pipeline
- [ ] Test email notifications
- [ ] Configure scaling parameters
- [ ] Set up VPC (if required)
- [ ] Document incident response procedures

## Support

For deployment issues:
1. Check Cloud Run logs in Google Cloud Console
2. Verify all required APIs are enabled
3. Ensure service account has proper permissions
4. Test locally with `docker run` first