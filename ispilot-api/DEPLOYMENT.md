# IsPilot API Deployment Guide

> **📋 See Also:** [Deployment Summary (Aug 28, 2026)](../DEPLOYMENT_SUMMARY_2026-08-28.md) for detailed changelog, all fixes applied, and current status.

This guide provides step-by-step instructions for deploying the IsPilot API to Google Cloud Run.

## Prerequisites

### Required Tools

- Docker (version 20.10+)
- gcloud CLI (version 500+)
- bash or PowerShell
- Git

### Required Google Cloud Resources

- **Project**: `corp-stro-salesinventory-prod`
- **Service Account**: `sa-ispilot-api@corp-stro-salesinventory-prod.iam.gserviceaccount.com`
- **Artifact Registry**: `ispilot-api` in `us-central1-docker.pkg.dev`
- **Secret Manager**: `ispilot-api-key` secret
- **Firestore Database**: For user session storage
- **Vertex AI**: Reasoning Engine with ID `5375474415045705728`

### Required IAM Roles

The service account must have:

```bash
- roles/aiplatform.user
- roles/datastore.user
- roles/secretmanager.secretAccessor
- roles/logging.logWriter
- roles/monitoring.metricWriter
```

## Setup: One-Time Configuration

### Step 1: Create Service Account (if needed)

```bash
PROJECT_ID="corp-stro-salesinventory-prod"

gcloud iam service-accounts create sa-ispilot-api \
  --project="${PROJECT_ID}" \
  --display-name="IsPilot API Service Account"
```

### Step 2: Grant IAM Roles

```bash
PROJECT_ID="corp-stro-salesinventory-prod"
SERVICE_ACCOUNT="sa-ispilot-api@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant required roles
for role in \
  "roles/aiplatform.user" \
  "roles/datastore.user" \
  "roles/secretmanager.secretAccessor" \
  "roles/logging.logWriter" \
  "roles/monitoring.metricWriter"
do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="${role}"
done
```

### Step 3: Create API Key Secret

```bash
PROJECT_ID="corp-stro-salesinventory-prod"
SERVICE_ACCOUNT="sa-ispilot-api@${PROJECT_ID}.iam.gserviceaccount.com"

# Generate a secure random API key
API_KEY=$(openssl rand -hex 16)

# Create the secret
echo -n "${API_KEY}" | gcloud secrets create ispilot-api-key \
  --project="${PROJECT_ID}" \
  --replication-policy="automatic" \
  --data-file=-

# Grant the service account access to the secret
gcloud secrets add-iam-policy-binding ispilot-api-key \
  --project="${PROJECT_ID}" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role=roles/secretmanager.secretAccessor

echo "Created secret 'ispilot-api-key': ${API_KEY}"
```

### Step 4: Create Artifact Registry Repository (if needed)

```bash
PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
REPOSITORY="ispilot-api"

gcloud artifacts repositories create "${REPOSITORY}" \
  --project="${PROJECT_ID}" \
  --location="${REGION}" \
  --repository-format=docker
```

## Deployment: Quick Start

### Automated Deployment

```bash
# 1. Navigate to project root
cd /path/to/ispilot-api

# 2. Ensure script is executable
chmod +x deploy.sh

# 3. Run deployment script
./deploy.sh
```

The script will:
1. Build Docker image
2. Configure Docker authentication
3. Push image to Artifact Registry
4. Deploy to Cloud Run
5. Verify deployment
6. Output service URL

### Manual Deployment

If you need finer control:

```bash
PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_NAME="ispilot-api"
REPOSITORY="ispilot-api"

# 1. Build Docker image
docker build -t us-central1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:latest .

# 2. Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# 3. Push image
docker push us-central1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:latest

# 4. Deploy to Cloud Run
gcloud run deploy "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --image "us-central1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:latest" \
  --platform managed \
  --no-allow-unauthenticated \
  --service-account "sa-ispilot-api@${PROJECT_ID}.iam.gserviceaccount.com" \
  --memory 1Gi \
  --cpu 2 \
  --concurrency 100 \
  --timeout 300 \
  --set-env-vars \
    "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}," \
    "GOOGLE_CLOUD_LOCATION=${REGION}," \
    "VERTEX_PROJECT_ID=${PROJECT_ID}," \
    "VERTEX_LOCATION=${REGION}," \
    "VERTEX_ENGINE_ID=5375474415045705728," \
    "FIRESTORE_COLLECTION=user_sessions," \
    "SESSION_TIMEOUT_HOURS=8" \
  --update-secrets \
    "ISPILOT_API_KEY=ispilot-api-key:latest"
```

## Verification

### Get Service URL

```bash
PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_NAME="ispilot-api"

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --format='value(status.url)')

echo "Service URL: ${SERVICE_URL}"
```

### Test Health Endpoint

```bash
curl "${SERVICE_URL}/health"

# Expected response:
# {"status": "healthy", "timestamp": "2026-08-27T10:30:45.123456Z"}
```

### Test Chat Endpoint

```bash
API_KEY=$(gcloud secrets versions access latest --secret=ispilot-api-key --project=corp-stro-salesinventory-prod)

curl -X POST "${SERVICE_URL}/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "user_id": "test-user",
    "message": "What is the inventory status?"
  }'
```

### Check Service Status

```bash
PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_NAME="ispilot-api"

gcloud run services describe "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}"
```

### View Logs

```bash
PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_NAME="ispilot-api"

# Recent logs
gcloud run services logs read "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --limit 50

# Real-time logs
gcloud run services logs read "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --limit 10 \
  --follow
```

## CI/CD: Cloud Build Automation

The service uses Cloud Build for automated CI/CD. Each push to the main branch triggers a build pipeline.

### Trigger Manual Build

```bash
gcloud builds submit \
  --project=corp-stro-salesinventory-prod \
  --config=cloudbuild.yaml \
  --region=us-central1
```

### View Build History

```bash
gcloud builds list \
  --project=corp-stro-salesinventory-prod \
  --limit=10
```

### View Build Logs

```bash
BUILD_ID="your-build-id"
gcloud builds log "${BUILD_ID}" \
  --project=corp-stro-salesinventory-prod \
  --stream
```

## Rollback: Revert to Previous Deployment

### Get Previous Revision

```bash
PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_NAME="ispilot-api"

gcloud run revisions list \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --service="${SERVICE_NAME}"
```

### Deploy Previous Revision

```bash
PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_NAME="ispilot-api"
REVISION_ID="ispilot-api-xxxxx"

gcloud run services update-traffic "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --to-revisions "${REVISION_ID}=100"
```

## Troubleshooting

### "Docker push failed"

```bash
# Verify Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# Check Docker daemon is running
docker ps
```

### "Permission denied" on Cloud Run deployment

```bash
# Verify service account has required roles
gcloud projects get-iam-policy corp-stro-salesinventory-prod \
  --flatten="bindings[].members" \
  --filter="bindings.members:sa-ispilot-api*"
```

### "Secret not found"

```bash
# List available secrets
gcloud secrets list --project=corp-stro-salesinventory-prod

# Verify secret has the right accessor
gcloud secrets get-iam-policy ispilot-api-key \
  --project=corp-stro-salesinventory-prod
```

### Health check fails immediately after deployment

1. Service needs time to start (30-60 seconds for first deployment)
2. Check service logs: `gcloud run services logs read ispilot-api --limit 50`
3. Verify all environment variables are set correctly
4. Verify Secret Manager secret is accessible

### Cold start performance

- Multi-stage Docker build reduces image size
- Consider enabling minimum instances:
  ```bash
  gcloud run services update ispilot-api \
    --project=corp-stro-salesinventory-prod \
    --region=us-central1 \
    --min-instances=1
  ```

## Monitoring

### View Metrics

```bash
PROJECT_ID="corp-stro-salesinventory-prod"
SERVICE_NAME="ispilot-api"

# View in Cloud Console
echo "https://console.cloud.google.com/run/detail/us-central1/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"
```

### Set Up Alerts

Use Cloud Monitoring to create alerts for:
- High error rates
- High latency (>1s)
- Service unavailability

## Security

### API Key Rotation

```bash
PROJECT_ID="corp-stro-salesinventory-prod"

# Generate new key
NEW_API_KEY=$(openssl rand -hex 16)

# Create new secret version
echo -n "${NEW_API_KEY}" | gcloud secrets versions add ispilot-api-key \
  --data-file=- \
  --project="${PROJECT_ID}"

# Cloud Run automatically uses the latest version (no redeployment needed)
echo "New API key: ${NEW_API_KEY}"
```

### Service Account Key Management

Service account keys are NOT used for Cloud Run authentication. Instead, Cloud Run uses Workload Identity Federation for secure authentication.

## Next Steps

1. Monitor service logs and metrics
2. Set up alerts for high error rates
3. Implement API rate limiting (if needed)
4. Set up automated backups for Firestore sessions
5. Configure custom domain (if needed)
