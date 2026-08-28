# IsPilot API

This service exposes IsPilot through a simple REST interface for enterprise channels such as Copilot Studio and Teams.

## Local development

### Quick start (using shared service account)

```bash
./run.sh
```

This will automatically use the shared service account key at `../../sa/key.json` and set up the environment.

### Manual setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# The shared service account key is at ../../sa/key.json
# It's automatically detected by run.sh and deploy.sh
# Or set it manually:
export GOOGLE_APPLICATION_CREDENTIALS="../../../sa/key.json"
export GOOGLE_CLOUD_PROJECT="corp-stro-salesinventory-prod"
export GOOGLE_CLOUD_LOCATION="us-central1"
export VERTEX_PROJECT_ID="corp-stro-salesinventory-prod"
export VERTEX_LOCATION="us-central1"
export VERTEX_ENGINE_ID="5375474415045705728"
export ISPILOT_API_KEY="your-test-api-key"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## Service Account

This project uses a shared service account key located at:
```
../../sa/key.json  (relative to ispilot-api/)
```

This key is automatically loaded by:
- `run.sh` (local development)
- `deploy.sh` (Cloud Run deployment)

If the file is not found, you can override with `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

## Environment Variables

See `.env.example` for all available configuration options:

- `GOOGLE_APPLICATION_CREDENTIALS`: Path to GCP service account JSON
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `GOOGLE_CLOUD_LOCATION`: GCP region
- `VERTEX_PROJECT_ID`: Vertex AI project ID
- `VERTEX_LOCATION`: Vertex AI location
- `VERTEX_ENGINE_ID`: Reasoning Engine ID
- `ISPILOT_API_KEY`: API key for authentication
- `SESSION_TIMEOUT_HOURS`: Session expiration timeout (default: 8)

## Authentication

All endpoints (except `/health`) require authentication via one of:

### Option 1: OAuth Bearer Token (Recommended for Cloud Run)

```bash
AUTH_TOKEN=$(gcloud auth print-identity-token --audiences https://ispilot-api-46y2f3tyja-uc.a.run.app)

curl -X POST https://ispilot-api-46y2f3tyja-uc.a.run.app/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{
    "user_id": "sebastian",
    "message": "How is Talca Colin performing?"
  }'
```

### Option 2: API Key Header (Local development)

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "user_id": "sebastian",
    "message": "How is Talca Colin performing?"
  }'
```

Optional headers (both methods):
- `X-User-ID`: Explicitly set user ID (otherwise extracted from request body)
- `X-Request-ID`: Custom request ID (auto-generated if not provided)

## Session Handling

Sessions are automatically managed per user:

1. **Automatic session creation**: If user doesn't have an active session, one is created on first request
2. **Session reuse**: Existing valid sessions are reused across requests
3. **Session expiration**: Sessions expire after `SESSION_TIMEOUT_HOURS` (default: 8 hours)
4. **Explicit session ID**: You can provide a `session_id` in the request to use a specific session

### Storage Backends

Sessions are stored using one of:

- **Primary (Recommended)**: Cloud Firestore for persistent, distributed storage
  - Enable with: `gcloud services enable firestore.googleapis.com --project corp-stro-salesinventory-prod`
  - Persists sessions across service restarts
  - Enables multi-instance deployments

- **Fallback (Auto-used if Firestore unavailable)**: In-memory session store
  - Works immediately without enabling Firestore API
  - Sessions only persist during service runtime
  - Sufficient for development and testing
  - Automatically detected and used if Firestore initialization fails

Example with explicit session:

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "user_id": "sebastian",
    "message": "Continue from previous context",
    "session_id": "existing-session-id"
  }'
```

## Health

```bash
curl http://localhost:8080/health
```

Response:

```json
{
  "status": "healthy",
  "timestamp": "2026-08-27T10:30:45.123456"
}
```

## Chat

Default session behavior with automatic creation:

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "user_id": "sebastian",
    "message": "How is Talca Colin performing?"
  }'
```

### Response Contract

All chat responses include:

```json
{
  "answer": "Response from IsPilot...",
  "session_id": "session-uuid",
  "request_id": "request-uuid",
  "timestamp": "2026-08-27T10:30:45.123456",
  "status": "ok"
}
```

### Error Response Contract

Error responses follow this format:

```json
{
  "error_code": "ERROR_CODE",
  "error_message": "Human-readable error message",
  "request_id": "request-uuid"
}
```

Common error codes:
- `MISSING_API_KEY`: X-API-Key header not provided
- `INVALID_API_KEY`: X-API-Key value is invalid
- `VALIDATION_ERROR`: Request validation failed
- `INTERNAL_ERROR`: Server-side error

## Deployment to Cloud Run

### Automated Deployment Script

```bash
chmod +x deploy.sh
./deploy.sh
```

The `deploy.sh` script handles:
1. Building the Docker image with multi-stage optimization
2. Pushing to Artifact Registry (us-central1-docker.pkg.dev)
3. Deploying to Cloud Run with proper resource configuration
4. Setting environment variables and secrets
5. Configuring service account (sa-ispilot-api)
6. Health check verification

### Manual Deployment

If you need to deploy manually:

```bash
# 1. Set configuration
export PROJECT_ID="corp-stro-salesinventory-prod"
export REGION="us-central1"
export SERVICE_NAME="ispilot-api"
export REPOSITORY="ispilot-api"

# 2. Build image
docker build -t us-central1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:latest .

# 3. Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# 4. Push to Artifact Registry
docker push us-central1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:latest

# 5. Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --project ${PROJECT_ID} \
  --region ${REGION} \
  --image us-central1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:latest \
  --platform managed \
  --no-allow-unauthenticated \
  --service-account sa-ispilot-api@${PROJECT_ID}.iam.gserviceaccount.com \
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

### Cloud Build CI/CD

The service includes a `cloudbuild.yaml` for automated CI/CD. Each push to main triggers:

1. **Build**: Docker image build with optimized multi-stage compilation
2. **Push**: Image pushed to Artifact Registry
3. **Deploy**: Deployment to Cloud Run via gke-deploy
4. **Verify**: Service verification and health check

See [Cloud Build Configuration](#cloud-build-configuration) below for details.

### Configuration

#### Environment Variables

All environment variables are documented in `.env.example`:

```bash
# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_PROJECT=corp-stro-salesinventory-prod
GOOGLE_CLOUD_LOCATION=us-central1

# Vertex AI Configuration
VERTEX_PROJECT_ID=corp-stro-salesinventory-prod
VERTEX_LOCATION=us-central1
VERTEX_ENGINE_ID=5375474415045705728

# IsPilot API Configuration
FIRESTORE_COLLECTION=user_sessions
SESSION_TIMEOUT_HOURS=8
ISPILOT_API_KEY=your-api-key
```

#### Secrets Management

The API key is stored securely in Google Cloud Secret Manager:

```bash
# Create the secret
echo -n "your-secure-api-key" | gcloud secrets create ispilot-api-key \
  --project=corp-stro-salesinventory-prod \
  --replication-policy="automatic" \
  --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding ispilot-api-key \
  --project=corp-stro-salesinventory-prod \
  --member=serviceAccount:sa-ispilot-api@corp-stro-salesinventory-prod.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

See `secrets.yaml` for complete secret configuration details.

#### Service Account

The service runs as `sa-ispilot-api@corp-stro-salesinventory-prod.iam.gserviceaccount.com` with required roles:

- `roles/aiplatform.user` - Access to Vertex AI Reasoning Engine
- `roles/datastore.user` - Access to Firestore sessions
- `roles/secretmanager.secretAccessor` - Access to API key secret
- `roles/logging.logWriter` - Write logs to Cloud Logging
- `roles/monitoring.metricWriter` - Write metrics to Cloud Monitoring

### Cloud Build Configuration

The `cloudbuild.yaml` defines the CI/CD pipeline:

```bash
# Manually trigger a build
gcloud builds submit \
  --project=corp-stro-salesinventory-prod \
  --config=cloudbuild.yaml \
  --region=us-central1
```

### Infrastructure as Code

The `deploy.yaml` Kubernetes manifest defines the Cloud Run service with:

- CPU/Memory: 2 CPU (limit) / 1 CPU (request), 1GB (limit) / 512MB (request)
- Concurrency: 100 requests per instance
- Timeout: 300 seconds (5 minutes)
- Health checks: Liveness (30s interval) and Readiness (5s interval)
- Environment variables and secrets (see Configuration section)

## Local Development

### Quick Start

```bash
chmod +x run.sh
./run.sh
```

The `run.sh` script:
1. Creates Python virtual environment
2. Installs dependencies from requirements.txt
3. Loads environment from .env
4. Starts uvicorn with auto-reload

### Manual Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export GOOGLE_CLOUD_PROJECT="corp-stro-salesinventory-prod"
export GOOGLE_CLOUD_LOCATION="us-central1"
export VERTEX_PROJECT_ID="corp-stro-salesinventory-prod"
export VERTEX_LOCATION="us-central1"
export VERTEX_ENGINE_ID="5375474415045705728"
export ISPILOT_API_KEY="your-test-api-key"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_health.py

# Run with verbose output
pytest -v
```

## Troubleshooting

### Authentication Issues

- **"Not authenticated with gcloud"**: Run `gcloud auth login`
- **"Permission denied" errors**: Verify service account has required IAM roles
- **"Secret not found"**: Ensure `ispilot-api-key` secret exists in Secret Manager

### Health Check Failures

- Service may need time to start (first deployment can take 30-60 seconds)
- Verify Cloud Run resource limits are sufficient
- Check Cloud Run service logs: `gcloud run services logs read ispilot-api --region us-central1`

### Cold Start Performance

- Multi-stage Docker build optimizes image size for faster cold starts
- Consider enabling Cloud Run's min instances if cold starts impact users

## Architecture Notes

- The service hides all Vertex-specific request details behind `VertexAgentClient`
- Sessions are managed in Firestore with automatic expiration
- All requests include structured JSON logging with request IDs
- API key validation is enforced via middleware
- Authentication failures are logged for security auditing
- Vertex API calls include automatic retry with exponential backoff

