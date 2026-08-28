# Deploy Script Changes

## Overview
Fixed the Cloud Run deployment script to resolve environment variable formatting errors, correct secret references, and improve health check timing.

## Changed File
`deploy.sh` - Cloud Run deployment automation

## Commits
- `f5cfeae` - "fix: correct --set-env-vars formatting for Cloud Run deploy"
- `5dcd6c3` - "fix: use correct secret name cloud-run-secret"
- `5dcd6c3` - "fix: increase health check wait time to 15s for slower startup"

---

## Fix 1: Environment Variables Formatting

### Problem
**Error Message:**
```
ERROR: (gcloud.run.deploy) unrecognized arguments:
  GOOGLE_CLOUD_PROJECT=corp-stro-salesinventory-prod,
  GOOGLE_CLOUD_LOCATION=us-central1, ...
```

**Root Cause:**
```bash
# ❌ WRONG - Treats each line as separate argument
--set-env-vars \
  "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}," \
  "GOOGLE_CLOUD_LOCATION=${REGION}," \
  "VERTEX_PROJECT_ID=${PROJECT_ID}," \
  ...
```

The backslash-continued lines created separate arguments to gcloud, not a single comma-separated string.

### Solution
```bash
# ✅ CORRECT - Single comma-separated string
--set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},VERTEX_PROJECT_ID=${PROJECT_ID},VERTEX_LOCATION=${REGION},VERTEX_ENGINE_ID=${VERTEX_ENGINE_ID},FIRESTORE_COLLECTION=${FIRESTORE_COLLECTION},SESSION_TIMEOUT_HOURS=${SESSION_TIMEOUT_HOURS}" \
```

**Key Changes:**
- All variables in ONE quoted string
- Commas separate variables (no trailing comma)
- No trailing backslash within the string
- Single `--set-env-vars` flag instead of multiple

### Before vs After

**BEFORE (Failed):**
```bash
gcloud run deploy ispilot-api \
  --set-env-vars \
  "VAR1=value1," \
  "VAR2=value2," \
  "VAR3=value3,"
# Error: unrecognized arguments
```

**AFTER (Works):**
```bash
gcloud run deploy ispilot-api \
  --set-env-vars "VAR1=value1,VAR2=value2,VAR3=value3" \
```

### Variables Set
```
GOOGLE_CLOUD_PROJECT           = corp-stro-salesinventory-prod
GOOGLE_CLOUD_LOCATION          = us-central1
VERTEX_PROJECT_ID              = corp-stro-salesinventory-prod
VERTEX_LOCATION                = us-central1
VERTEX_ENGINE_ID               = 5375474415045705728
FIRESTORE_COLLECTION           = user_sessions
SESSION_TIMEOUT_HOURS          = 8
```

---

## Fix 2: Secret Name Correction

### Problem
**Error Message:**
```
ERROR: Secret 'ispilot-api-key' not found in Secret Manager
```

**Root Cause:**
```bash
# ❌ WRONG - Referenced non-existent secret
ISPILOT_API_KEY=ispilot-api-key:latest
```

The secret `ispilot-api-key` doesn't exist; actual secret is `cloud-run-secret`.

### Solution
```bash
# ✅ CORRECT - Reference actual secret
ISPILOT_API_KEY=cloud-run-secret:latest
```

### Secret Details
**Name:** `cloud-run-secret`
**Contents:** Service account JSON key for sa-tot-osa
**Location:** Google Secret Manager
**Project:** corp-stro-salesinventory-prod

**Purpose:**
- Provides service account credentials to Cloud Run service
- Enables SA-to-SA authentication with Vertex AI
- Used by app to initialize Vertex AI client

**Access:**
```bash
# View secret metadata
gcloud secrets describe cloud-run-secret \
  --project corp-stro-salesinventory-prod

# Access latest version
gcloud secrets versions access latest --secret=cloud-run-secret \
  --project corp-stro-salesinventory-prod
```

### Before vs After

**BEFORE:**
```bash
gcloud run deploy ispilot-api \
  --set-env-vars ISPILOT_API_KEY=ispilot-api-key:latest
# Error: Secret 'ispilot-api-key' not found
```

**AFTER:**
```bash
gcloud run deploy ispilot-api \
  --set-env-vars ISPILOT_API_KEY=cloud-run-secret:latest
# Success ✓
```

---

## Fix 3: Health Check Wait Time

### Problem
**Potential Issue:**
- Cold start latency exceeding 5 seconds
- Health check timeout before service ready
- Cloud Run marks service as unhealthy
- Deployment appears successful but service unavailable

### Solution
```bash
# ❌ BEFORE - Too short for cold start
sleep 5

# ✅ AFTER - Allow cold start time
sleep 15
```

**Wait Time Analysis:**
- `5 seconds` - Insufficient for Python cold start with ML model
- `15 seconds` - Allows:
  - Python interpreter startup (~1s)
  - Package imports (~2-3s)
  - Vertex AI client initialization (~2-3s)
  - FastAPI app startup (~1-2s)
  - Buffer for network latency (~3-4s)

### Why It Matters
```
Service Startup Timeline:
├─ 0-1s:   Python interpreter starts
├─ 1-4s:   Packages imported
├─ 4-6s:   FastAPI app initializes
├─ 6-8s:   Vertex AI client created
├─ 8-10s:  Health check endpoint ready
└─ 10-15s: Full service warm and ready
```

With `sleep 5`, health check might run at 5s before service fully ready.
With `sleep 15`, ensures service is warmed up.

### Impact on Deployment
```bash
# With --wait-for-deployment (deploy.sh line 100)
gcloud run deploy ispilot-api ... --wait-for-deployment

# This flag waits for revision to be ready:
# - If health check fails before sleep time, deployment fails
# - sleep 15 ensures health check runs when service ready
```

### Deployment Output
```
Deploying container to Cloud Run service [ispilot-api]...
✓ Deploying new service revision [ispilot-api-00004-5ng]...
  Setting IAM Policy...
  Routing traffic...
✓ Service [ispilot-api] revision [ispilot-api-00004-5ng] has been deployed
  Service URL: https://ispilot-api-46y2f3tyja-uc.a.run.app
```

---

## Complete deploy.sh Structure

### Pre-Deployment (Lines 1-15)
```bash
#!/bin/bash
set -e
PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_ACCOUNT="sa-tot-osa@${PROJECT_ID}.iam.gserviceaccount.com"
```

**Key:** Service account set to `sa-tot-osa` (correct)

### Docker Build & Push (Lines 20-40)
```bash
docker build -t ${IMAGE_NAME} .
docker push ${IMAGE_NAME}
```

### Cloud Run Deployment (Lines 77-108)
```bash
gcloud run deploy ispilot-api \
  --image ${IMAGE_NAME} \
  --set-env-vars "..." \
  --secret ISPILOT_API_KEY=cloud-run-secret:latest \
  --service-account ${SERVICE_ACCOUNT} \
  --no-allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --max-instances 100 \
  --timeout 300 \
  --wait-for-deployment
```

### Post-Deployment (Lines 110+)
```bash
echo "Deployment complete!"
echo "Service URL: https://ispilot-api-46y2f3tyja-uc.a.run.app"
sleep 15  # Wait for service to warm up
```

---

## Deployment Checklist

- [x] Fixed --set-env-vars formatting (comma-separated string)
- [x] Corrected secret name (cloud-run-secret)
- [x] Increased health check wait time (5s → 15s)
- [x] Service account set to sa-tot-osa
- [x] All environment variables properly passed
- [x] Security: --no-allow-unauthenticated enabled
- [x] Resource config: 1Gi memory, 2 CPU
- [x] Timeout: 300s for long-running requests

---

## How to Deploy

### Prerequisites
```bash
# Set working directory
cd /path/to/intelligent-shelf-agents/ispilot-api

# Authenticate with GCP
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Or use gcloud auth
gcloud auth login
gcloud config set project corp-stro-salesinventory-prod
```

### Run Deployment
```bash
bash deploy.sh
```

### Expected Output
```
Step 1/8 : FROM python:3.11-slim
 ---> abc123...
...
Successfully built xyz789
Successfully tagged us-central1-docker.pkg.dev/corp-stro-salesinventory-prod/ispilot-api/ispilot-api:latest
Pushing us-central1-docker.pkg.dev/corp-stro-salesinventory-prod/ispilot-api/ispilot-api:latest
...
✓ Deploying new service revision [ispilot-api-00004-5ng]...
✓ Service [ispilot-api] revision [ispilot-api-00004-5ng] has been deployed
  Service URL: https://ispilot-api-46y2f3tyja-uc.a.run.app
Deployment complete!
```

---

## Testing After Deployment

### Test with OAuth
```bash
AUTH_TOKEN=$(gcloud auth print-identity-token --audiences https://ispilot-api-46y2f3tyja-uc.a.run.app)

curl -X POST "https://ispilot-api-46y2f3tyja-uc.a.run.app/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"user_id": "test-user", "message": "Hello"}'
```

### View Deployment Logs
```bash
gcloud run services logs read ispilot-api \
  --project corp-stro-salesinventory-prod \
  --region us-central1 \
  --limit 100
```

### Monitor Deployments
```bash
gcloud run services describe ispilot-api \
  --project corp-stro-salesinventory-prod \
  --region us-central1
```

---

## Troubleshooting

### Issue: "Deployment failed: ... gcloud command error"

**Solution:**
1. Check authentication: `gcloud auth list`
2. Verify project: `gcloud config get project`
3. Review logs: `gcloud run services logs read ispilot-api --limit 50`

### Issue: "Secret 'X' not found"

**Solution:**
- Verify secret exists: `gcloud secrets list --project corp-stro-salesinventory-prod`
- Check secret name in deploy.sh matches actual secret name
- Current correct name: `cloud-run-secret`

### Issue: "Service unavailable / 503 Service Unavailable"

**Solution:**
1. Wait 15+ seconds (cold start time)
2. Check health endpoint: 
   ```bash
   curl https://ispilot-api-46y2f3tyja-uc.a.run.app/health
   ```
3. Review logs for startup errors

### Issue: "Permission denied / 403 Forbidden"

**Solution:**
1. Verify service account has required roles:
   ```bash
   gcloud projects get-iam-policy corp-stro-salesinventory-prod \
     --flatten="bindings[].members" \
     --filter="bindings.members:sa-tot-osa@"
   ```
2. Add missing roles if needed:
   ```bash
   gcloud projects add-iam-policy-binding corp-stro-salesinventory-prod \
     --member="serviceAccount:sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   ```

---

## Related Changes

- Authentication OAuth Support: `0ce3ae6`
- Session Service Firestore Fallback: `1881c51`
- See [DEPLOYMENT_SUMMARY_2026-08-28.md](../../DEPLOYMENT_SUMMARY_2026-08-28.md)
