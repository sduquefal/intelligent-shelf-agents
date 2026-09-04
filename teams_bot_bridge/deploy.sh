#!/usr/bin/env bash
set -euo pipefail

# Teams Bridge Deployment Script
# Deploys the Teams Bridge service to Google Cloud Run
# Usage: ./deploy.sh
# Environment Variables:
#   - MICROSOFT_APP_ID: Azure Bot app ID
#   - MICROSOFT_APP_PASSWORD: Azure Bot app secret
#   - PROJECT_ID: GCP project ID (default: corp-stro-salesinventory-prod)
#   - REGION: Cloud Run region (default: us-central1)

PROJECT_ID="${PROJECT_ID:-corp-stro-salesinventory-prod}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="teams-ispilot-bridge"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com}"
ALLOW_UNAUTHENTICATED="${ALLOW_UNAUTHENTICATED:-true}"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Required environment variables
if [ -z "${MICROSOFT_APP_ID:-}" ]; then
  echo "ERROR: MICROSOFT_APP_ID environment variable is required"
  exit 1
fi

if [ -z "${MICROSOFT_APP_PASSWORD:-}" ]; then
  echo "ERROR: MICROSOFT_APP_PASSWORD environment variable is required"
  exit 1
fi

cd "$SOURCE_DIR"

echo "============================================================"
echo "Teams Bridge Deployment"
echo "============================================================"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "Service Account: $SERVICE_ACCOUNT"
echo "Allow Unauthenticated: $ALLOW_UNAUTHENTICATED"
echo "============================================================"

if [ "$ALLOW_UNAUTHENTICATED" = "true" ]; then
  GCP_AUTH_FLAG="--allow-unauthenticated"
else
  GCP_AUTH_FLAG="--no-allow-unauthenticated"
fi

echo "Deploying to Cloud Run..."

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --service-account "$SERVICE_ACCOUNT" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --max-instances 100 \
  $GCP_AUTH_FLAG \
  --set-env-vars \
    "MICROSOFT_APP_ID=${MICROSOFT_APP_ID}",\
    "MICROSOFT_APP_PASSWORD=${MICROSOFT_APP_PASSWORD}",\
    "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}",\
    "ISPILOT_API_ENDPOINT=https://ispilot-api-46y2f3tyja-uc.a.run.app/chat",\
    "LOG_LEVEL=info"

echo "============================================================"
echo "Deployment finished!"
echo "============================================================"

# Get the service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --format 'value(status.url)')

echo "Service URL: $SERVICE_URL"
echo "Health endpoint: $SERVICE_URL/health"
echo "Activity endpoint: $SERVICE_URL/api/messages"
echo ""
echo "Next steps:"
echo "1. Update Azure Bot Service messaging endpoint to: $SERVICE_URL/api/messages"
echo "2. Test the service: curl $SERVICE_URL/health"
echo "3. See NEXT_STEPS.md Phase 3 for full deployment validation"
