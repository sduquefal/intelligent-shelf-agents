# Teams Bridge for IsPilot - Microsoft 365 Agents SDK

**Status**: 🆕 New architecture using Microsoft 365 Agents SDK  
**Target Deployment**: Cloud Run service `teams-ispilot-bridge`  
**Complete Setup Guide**: See [../docs/TEAMS_SDK_INTEGRATION.md](../docs/TEAMS_SDK_INTEGRATION.md)

This service bridges Microsoft Teams with the IsPilot API using the **official Microsoft 365 Agents SDK** (Python). It provides native Teams integration, proper JWT validation, and seamless authentication to the backend ispilot-api.

## Quick Links

- **Full Setup**: [../docs/TEAMS_SDK_INTEGRATION.md](../docs/TEAMS_SDK_INTEGRATION.md) - Complete 5-phase implementation guide
- **Architecture Rationale**: [../docs/ARCHITECTURE_RESET_TEAMS_SDK.md](../docs/ARCHITECTURE_RESET_TEAMS_SDK.md) - Why Teams SDK + Teams Bridge
- **API Documentation**: [../ispilot-api/README.md](../ispilot-api/README.md) - ispilot-api endpoint reference
- **Work Checkpoint**: [../WORK_CHECKPOINT.md](../WORK_CHECKPOINT.md) - Current status and remaining tasks

## Architecture

```
Teams User
    ↓
Azure Bot Service (validates Teams JWT)
    ↓
Teams Bridge (Cloud Run - Public)
├─ MS 365 Agents SDK
├─ Validates Azure JWT
├─ Generates Google identity token (sa-tot-osa)
├─ Routes to ispilot-api
├─ Manages session context
    ↓
IsPilot API (Cloud Run - Private)
├─ Validates identity token
├─ Routes to Vertex AI Reasoning Engine
    ↓
Response → Back to Teams
```

## Prerequisites

### Google Cloud Setup (Already in Place ✅)

- **Project**: `corp-stro-salesinventory-prod`
- **Region**: `us-central1`
- **Service Account**: `sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com`
- **ispilot-api**: `https://ispilot-api-46y2f3tyja-uc.a.run.app`

### Azure / Microsoft 365 Setup (✅ COMPLETE - Phase 1)

**Who**: Azure/Teams admin (José Arturo)

**Completed**:
- ✅ Azure AD App Registration: `ftc-ispilot-corp-prod`
- ✅ Microsoft App ID: `53ead9aa-24aa-44e7-b485-81a988e7492f`
- ✅ Object ID: `f85873ef-78e3-4e6e-97dc-48c4f0e95139`
- ✅ Tenant ID: `c4a8886b-f140-478b-ac47-249555c30afd`
- ✅ Client Secret Generated (Secret ID: b8130e5a-3446-49ef-8267-056e21cabec2)
- ✅ Configured in `.env` file

**Next Phase**: Phase 2 (Local Development Setup)
- Start with local Python environment
- Install dependencies
- Test locally before Cloud Run deployment

See [NEXT_STEPS.md](./NEXT_STEPS.md) → "Phase 2" to begin

## Local Development

### 1. Setup

```bash
cd teams_bot_bridge

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment

Edit `.env`:
```bash
# Azure Bot Service credentials (from Phase 1)
MICROSOFT_APP_ID=<your-app-id>
MICROSOFT_APP_PASSWORD=<your-app-password>

# Google Cloud
GOOGLE_CLOUD_PROJECT=corp-stro-salesinventory-prod

# ispilot-api
ISPILOT_API_ENDPOINT=https://ispilot-api-46y2f3tyja-uc.a.run.app/chat

# Local dev
PORT=8080
DEBUG=True
```

### 3. Run Locally

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

Service will be available at: `http://localhost:8080`

### 4. Test Health Endpoint

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "ok"
}
```

## Cloud Run Deployment

### Deploy Command

```bash
PROJECT_ID="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_NAME="teams-ispilot-bridge"
SERVICE_ACCOUNT="sa-tot-osa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --service-account "${SERVICE_ACCOUNT}" \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --set-env-vars \
    MICROSOFT_APP_ID=<APP_ID>,\
    MICROSOFT_APP_PASSWORD=<APP_PASSWORD>,\
    ISPILOT_API_ENDPOINT=https://ispilot-api-46y2f3tyja-uc.a.run.app/chat,\
    GOOGLE_CLOUD_PROJECT=${PROJECT_ID}
```

### Get Service URL

```bash
gcloud run services describe teams-ispilot-bridge \
  --region=us-central1 \
  --project=corp-stro-salesinventory-prod \
  --format='value(status.url)'
```

Use this URL as the **Messaging Endpoint** in Azure Bot Service registration.

## API Endpoints

### GET /health

Health check (no authentication).

```bash
curl https://teams-ispilot-bridge-xxxxxx.run.app/health
```

### POST /api/messages

Handles Teams activities from Azure Bot Service. **Requires valid JWT from Azure Bot Service.**

This is the endpoint configured in Azure Bot Service messaging configuration.

**Headers**: (Added by Azure Bot Service automatically)
```
Authorization: Bearer <JWT-from-Azure>
Content-Type: application/json
```

**Request body**: (Activity JSON from Teams)
```json
{
  "type": "message",
  "from": {"id": "user-id", "name": "User Name"},
  "conversation": {"id": "conversation-id"},
  "text": "How is Talca Colin performing?"
}
```

**Response**: Activity response sent back to Teams.

---

## Testing Sequence

### Step 1: Local Testing
1. Run locally: `uvicorn main:app --reload`
2. Verify health: `curl http://localhost:8080/health`
3. Check logs for startup messages

### Step 2: Cloud Run Testing
1. Deploy to Cloud Run (see deployment command above)
2. Get service URL: `gcloud run services describe teams-ispilot-bridge --region=us-central1 --format='value(status.url)'`
3. Test health: `curl https://<SERVICE-URL>/health`
4. Check logs: `gcloud run logs read teams-ispilot-bridge --region=us-central1 --limit 50`

### Step 3: Azure Bot Service Testing
1. Configure messaging endpoint in Azure Bot Service
2. Use Bot Framework Emulator to test
3. Or test in Teams Web Chat

### Step 4: Teams Testing
1. Publish Teams app (manifest.json configured)
2. Add app to team/group chat
3. Send test message
4. Verify response comes through

See [../docs/TEAMS_SDK_INTEGRATION.md](../docs/TEAMS_SDK_INTEGRATION.md) → "Testing Checklist" for complete validation steps.

## Troubleshooting

### Bridge not receiving messages
- **Check**: Azure Bot messaging endpoint is correctly configured
- **Fix**: Verify Cloud Run service URL in Azure Bot registration
- **Verify**: `gcloud run logs read teams-ispilot-bridge --region=us-central1`

### JWT validation fails
- **Check**: MICROSOFT_APP_ID and MICROSOFT_APP_PASSWORD are correct
- **Fix**: Regenerate credentials in Azure AD if unsure
- **Verify**: Check logs for JWT validation errors

### ispilot-api returns 401
- **Check**: sa-tot-osa has correct Workload Identity permissions
- **Fix**: Verify identity token generation works locally:
  ```bash
  gcloud auth print-identity-token \
    --impersonate-service-account=sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com
  ```
- **Verify**: ispilot-api README for IAM setup

### Message timeouts
- **Check**: ispilot-api is responding (see [../ispilot-api/README.md](../ispilot-api/README.md) smoke test)
- **Fix**: Increase Cloud Run timeout (currently 60s)
- **Verify**: Monitor ispilot-api logs:
  ```bash
  gcloud run logs read ispilot-api --region=us-central1
  ```

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `MICROSOFT_APP_ID` | ✅ | Azure Bot App ID | (none) |
| `MICROSOFT_APP_PASSWORD` | ✅ | Azure Bot App Secret | (none) |
| `ISPILOT_API_ENDPOINT` | ✅ | ispilot-api URL | `https://ispilot-api-46y2f3tyja-uc.a.run.app/chat` |
| `GOOGLE_CLOUD_PROJECT` | ✅ | GCP Project ID | `corp-stro-salesinventory-prod` |
| `PORT` | | Server port | `8080` |
| `DEBUG` | | Enable debug logging | `False` |

## References

- [Microsoft 365 Agents SDK Docs](https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/)
- [Azure Bot Service Docs](https://learn.microsoft.com/en-us/azure/bot-service/)
- [Teams App Manifest Schema](https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema)
- [Google Cloud Identity Tokens](https://cloud.google.com/docs/authentication/get-id-token)

## Implementation Status

See [../WORK_CHECKPOINT.md](../WORK_CHECKPOINT.md) for current implementation status and remaining tasks.
