#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_NAME="teams-ispilot-bridge"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com}"
ALLOW_UNAUTHENTICATED="${ALLOW_UNAUTHENTICATED:-false}"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SOURCE_DIR"

echo "Deploying ${SERVICE_NAME} to Cloud Run in ${REGION} (${PROJECT_ID}) with runtime service account ${SERVICE_ACCOUNT}..."

echo "This mirrors the IsPilot pattern: service account is bound to the service, and public access remains disabled by default."

echo "If this fails with iam.serviceaccounts.actAs, the active gcloud identity must be granted permission on that service account or must impersonate it."

if [ "$ALLOW_UNAUTHENTICATED" = "true" ]; then
  GCP_AUTH_FLAG="--allow-unauthenticated"
else
  GCP_AUTH_FLAG="--no-allow-unauthenticated"
fi

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --service-account "$SERVICE_ACCOUNT" \
  $GCP_AUTH_FLAG

echo "Deployment finished."
