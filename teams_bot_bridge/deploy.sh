#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_NAME="teams-ispilot-bridge"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SOURCE_DIR"

echo "Deploying ${SERVICE_NAME} to Cloud Run in ${REGION} (${PROJECT_ID})..."

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --allow-unauthenticated

echo "Deployment finished."
