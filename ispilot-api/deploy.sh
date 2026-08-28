#!/usr/bin/env bash
set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${PROJECT_ID:-corp-stro-salesinventory-prod}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-ispilot-api}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-sa-tot-osa@${PROJECT_ID}.iam.gserviceaccount.com}"

# Set service account credentials (sa-tot-osa key for authentication)
SA_KEY_PATH="${GOOGLE_APPLICATION_CREDENTIALS:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/sa/key.json}"
export GOOGLE_APPLICATION_CREDENTIALS="$SA_KEY_PATH"
REPOSITORY="${REPOSITORY:-ispilot-api}"
IMAGE_NAME="${SERVICE_NAME}:latest"
ARTIFACT_REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}"
IMAGE="${ARTIFACT_REGISTRY}/${IMAGE_NAME}"

echo -e "${YELLOW}=== IsPilot API Deployment ===${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"
echo "Service Account: $SERVICE_ACCOUNT"
echo "Artifact Registry: $ARTIFACT_REGISTRY"
echo ""

# Verify gcloud is authenticated
echo -e "${YELLOW}Verifying gcloud authentication...${NC}"
if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo -e "${RED}Error: Service account key not found at $GOOGLE_APPLICATION_CREDENTIALS${NC}"
    echo "Please ensure the key file exists or set GOOGLE_APPLICATION_CREDENTIALS environment variable"
    exit 1
fi

if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}Authenticating with service account key...${NC}"
    gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
fi
echo -e "${GREEN}✓ Authenticated (GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS)${NC}"
echo ""

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t "$IMAGE" .
echo -e "${GREEN}✓ Image built${NC}"
echo ""

# Configure Docker to push to Artifact Registry
echo -e "${YELLOW}Configuring Docker authentication for Artifact Registry...${NC}"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
echo -e "${GREEN}✓ Docker configured${NC}"
echo ""

# Push image to Artifact Registry
echo -e "${YELLOW}Pushing image to Artifact Registry...${NC}"
docker push "$IMAGE"
echo -e "${GREEN}✓ Image pushed to $IMAGE${NC}"
echo ""

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy "$SERVICE_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --image "$IMAGE" \
  --platform managed \
  --no-allow-unauthenticated \
  --service-account sa-tot-osa@${PROJECT_ID}.iam.gserviceaccount.com \
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

echo -e "${GREEN}✓ Deployment completed${NC}"
echo ""

# Verify deployment
echo -e "${YELLOW}Verifying deployment...${NC}"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --format='value(status.url)')

if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}Error: Could not retrieve service URL${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Service URL: $SERVICE_URL${NC}"
echo ""

# Health check
echo -e "${YELLOW}Checking service health...${NC}"
sleep 5  # Give service time to start

if curl -s "${SERVICE_URL}/health" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠ Health check did not respond immediately. Service may still be starting.${NC}"
fi

echo ""
echo -e "${GREEN}=== Deployment Summary ===${NC}"
echo "Service: $SERVICE_NAME"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "URL: $SERVICE_URL"
echo ""
echo "To test the deployment:"
echo "  curl -X POST \"${SERVICE_URL}/chat\" \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -H \"X-API-Key: your-api-key\" \\"
echo "    -d '{\"user_id\": \"test-user\", \"message\": \"Hello\"}'"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
