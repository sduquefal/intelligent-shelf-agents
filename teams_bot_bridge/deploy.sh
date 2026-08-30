#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_NAME="teams-ispilot-bridge"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com}"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SOURCE_DIR"

echo "Deploying ${SERVICE_NAME} to Cloud Run in ${REGION} (${PROJECT_ID}) with runtime service account ${SERVICE_ACCOUNT}..."

echo "If this fails with iam.serviceaccounts.actAs, the active gcloud identity must be granted permission on that service account or must impersonate it."

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --service-account "$SERVICE_ACCOUNT" \
  --allow-unauthenticated

echo "Deployment finished."
