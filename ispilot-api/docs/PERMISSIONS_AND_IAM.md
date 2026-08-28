# Permissions & IAM Configuration

## Overview
Complete permissions and IAM setup required for IsPilot API deployment on Google Cloud Run.

---

## Service Account

### Principal
```
sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com
```

### Purpose
- Cloud Run service account (application identity)
- Authenticates API requests to Google Cloud services
- Access control for Vertex AI, Secret Manager, Firestore

### Creation
```bash
PROJECT_ID="corp-stro-salesinventory-prod"

gcloud iam service-accounts create sa-tot-osa \
  --project="${PROJECT_ID}" \
  --display-name="IsPilot API Service Account"
```

**Status:** Already created ✓

---

## Required IAM Roles

### 1. Vertex AI (Required)

**Role:** `roles/aiplatform.user`
**Purpose:** Access Vertex AI Reasoning Engines for chat
**Resource:** Project-level

```bash
gcloud projects add-iam-policy-binding corp-stro-salesinventory-prod \
  --member="serviceAccount:sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

**Permissions Granted:**
- `aiplatform.endpoints.predict` - Invoke reasoning engine
- `aiplatform.endpoints.rawPredict` - Raw predictions
- `aiplatform.models.get` - Retrieve model info
- `aiplatform.models.list` - List available models

**Engine ID:** `5375474415045705728`
**Location:** `us-central1`

---

### 2. Secret Manager (Required)

**Role:** `roles/secretmanager.secretAccessor`
**Purpose:** Retrieve service account credentials from Secret Manager
**Resource:** Project-level

```bash
gcloud projects add-iam-policy-binding corp-stro-salesinventory-prod \
  --member="serviceAccount:sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**Secret:** `cloud-run-secret` (contains service account JSON)

**Permissions Granted:**
- `secretmanager.secrets.get` - Read secret metadata
- `secretmanager.versions.access` - Access secret contents
- `secretmanager.versions.list` - List secret versions

---

### 3. Cloud Firestore (Required when Firestore enabled)

**Role:** `roles/datastore.user`
**Purpose:** Read/write user sessions to Firestore
**Resource:** Database or project-level
**Collection:** `user_sessions`

```bash
gcloud projects add-iam-policy-binding corp-stro-salesinventory-prod \
  --member="serviceAccount:sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

**Permissions Granted:**
- `datastore.databases.get` - Access database
- `datastore.entities.create` - Create session documents
- `datastore.entities.list` - Query sessions
- `datastore.entities.update` - Update sessions
- `datastore.entities.delete` - Delete expired sessions

**Status:** ⏳ Deferred (in-memory fallback active)
**Enable when ready:**
```bash
gcloud services enable firestore.googleapis.com \
  --project corp-stro-salesinventory-prod
```

---

### 4. Logging (Recommended)

**Role:** `roles/logging.logWriter`
**Purpose:** Write application logs to Cloud Logging
**Resource:** Project-level

```bash
gcloud projects add-iam-policy-binding corp-stro-salesinventory-prod \
  --member="serviceAccount:sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

**Permissions Granted:**
- `logging.logEntries.create` - Write log entries

**Status:** ✓ Recommended (already configured)

---

### 5. Monitoring (Recommended)

**Role:** `roles/monitoring.metricWriter`
**Purpose:** Write custom metrics to Cloud Monitoring
**Resource:** Project-level

```bash
gcloud projects add-iam-policy-binding corp-stro-salesinventory-prod \
  --member="serviceAccount:sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com" \
  --role="roles/monitoring.metricWriter"
```

**Permissions Granted:**
- `monitoring.timeSeries.create` - Write metrics

**Status:** ✓ Recommended (optional)

---

## Cloud Run Configuration

### Deployment Settings
```bash
gcloud run deploy ispilot-api \
  --service-account sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com \
  --no-allow-unauthenticated \
  ...
```

### Access Control
```
┌─────────────────────────────────────────┐
│ Client (User/System)                    │
├─────────────────────────────────────────┤
│ Requires: OAuth Bearer Token or API Key │
├─────────────────────────────────────────┤
│         ↓ (Auth Check)                  │
├─────────────────────────────────────────┤
│ Cloud Run Service (ispilot-api)         │
│ Identity: sa-tot-osa                    │
├─────────────────────────────────────────┤
│         ↓ (Service uses SA creds)       │
├─────────────────────────────────────────┤
│ Google Cloud APIs:                      │
│ • Vertex AI (reasoning engine)          │
│ • Secret Manager (credentials)          │
│ • Firestore (sessions - optional)       │
│ • Cloud Logging (logs)                  │
└─────────────────────────────────────────┘
```

---

## Secret Manager Configuration

### Secret: `cloud-run-secret`

**Contents:**
```json
{
  "type": "service_account",
  "project_id": "corp-stro-salesinventory-prod",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

**Access in Deploy:**
```bash
--secret ISPILOT_API_KEY=cloud-run-secret:latest
```

**Access in Application:**
```python
import google.auth
credentials, project = google.auth.default()
# OR
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
response = client.access_secret_version(request={
    "name": "projects/390358249123/secrets/cloud-run-secret/versions/latest"
})
secret_json = response.payload.data.decode("UTF-8")
```

---

## Current IAM State

### Verify Service Account Roles

```bash
# List all roles assigned to service account
gcloud projects get-iam-policy corp-stro-salesinventory-prod \
  --flatten="bindings[].members" \
  --filter="bindings.members:sa-tot-osa@" \
  --format="table(bindings.role)"

# Output should include:
# - roles/aiplatform.user
# - roles/secretmanager.secretAccessor
# - roles/datastore.user (if Firestore enabled)
# - roles/logging.logWriter
# - roles/monitoring.metricWriter (optional)
```

### Verify Service Account Usage

```bash
# Check service account details
gcloud iam service-accounts describe \
  sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com \
  --project corp-stro-salesinventory-prod

# Check key information
gcloud iam service-accounts keys list \
  --iam-account=sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com \
  --project corp-stro-salesinventory-prod
```

---

## Permission Dependencies

### Startup Flow
```
App Start
├─ Read GOOGLE_APPLICATION_CREDENTIALS
│  └─ Use service account key file
│
├─ Initialize Vertex AI Client
│  └─ Requires: roles/aiplatform.user
│     ✗ Error if missing: "Permission denied on resource"
│
├─ Access Secret from Secret Manager
│  └─ Requires: roles/secretmanager.secretAccessor
│     ✗ Error if missing: "Not authorized to perform"
│
├─ Initialize Firestore (if enabled)
│  └─ Requires: roles/datastore.user
│     ✗ Error if missing: "Permission denied on resource"
│     ✓ Graceful fallback to in-memory if missing
│
└─ Start logging
   └─ Requires: roles/logging.logWriter (recommended)
      ⚠ Warning if missing: Logs not persisted to Cloud Logging
```

---

## Troubleshooting Permissions

### Error: "Permission denied on resource"

**Diagnosis:**
```bash
# Check current roles
gcloud projects get-iam-policy corp-stro-salesinventory-prod \
  --flatten="bindings[].members" \
  --filter="bindings.members:sa-tot-osa@" \
  --format=json | jq '.[] | .bindings[] | select(.members[] | contains("sa-tot-osa")) | .role'
```

**Solution:**
Add missing role:
```bash
gcloud projects add-iam-policy-binding corp-stro-salesinventory-prod \
  --member="serviceAccount:sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"  # Replace with needed role
```

---

### Error: "Service account not found"

**Diagnosis:**
```bash
gcloud iam service-accounts describe \
  sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com \
  --project corp-stro-salesinventory-prod
```

**Solution:**
Create service account:
```bash
gcloud iam service-accounts create sa-tot-osa \
  --project corp-stro-salesinventory-prod \
  --display-name="IsPilot API Service Account"
```

---

### Error: "Secret not found"

**Diagnosis:**
```bash
gcloud secrets describe cloud-run-secret \
  --project corp-stro-salesinventory-prod
```

**Solution:**
Create secret with service account key:
```bash
gcloud iam service-accounts keys create - \
  --iam-account=sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com \
  | gcloud secrets create cloud-run-secret \
    --project corp-stro-salesinventory-prod \
    --replication-policy="user-managed" \
    --locations="us-central1" \
    --data-file=-
```

---

## Security Best Practices

### 1. Principle of Least Privilege
- ✓ Service account has minimal required roles
- ✗ Avoid adding Editor or Owner roles
- ✓ Use specific roles (e.g., `aiplatform.user` not `aiplatform.admin`)

### 2. Secret Management
- ✓ Service account key stored in Secret Manager
- ✓ Not in environment variables or code
- ✓ Automatic rotation recommended

### 3. Authentication
- ✓ Cloud Run requires authentication (--no-allow-unauthenticated)
- ✓ OAuth Bearer tokens for production
- ✓ API keys only for development/testing

### 4. Auditing
- ✓ Cloud Audit Logs track permission usage
- ✓ Monitor failed authentication attempts
- ✓ Set up alerts for suspicious activity

---

## Deployment Checklist

- [ ] Service account `sa-tot-osa` created
- [ ] Role `roles/aiplatform.user` assigned
- [ ] Role `roles/secretmanager.secretAccessor` assigned
- [ ] Secret `cloud-run-secret` created with service account key
- [ ] Cloud Run deployment configured with --no-allow-unauthenticated
- [ ] Deploy script uses correct service account
- [ ] Firestore API enabled (optional, for persistent sessions)
- [ ] Role `roles/datastore.user` assigned (if Firestore enabled)
- [ ] Monitoring configured (optional)

---

## Quick Setup Script

```bash
#!/bin/bash
set -e

PROJECT_ID="corp-stro-salesinventory-prod"
SERVICE_ACCOUNT_EMAIL="sa-tot-osa@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Setting up permissions for IsPilot API..."

# Create service account (if not exists)
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT_EMAIL}" --project="${PROJECT_ID}" &>/dev/null; then
  echo "Creating service account..."
  gcloud iam service-accounts create sa-tot-osa \
    --project="${PROJECT_ID}" \
    --display-name="IsPilot API Service Account"
fi

# Assign required roles
echo "Assigning IAM roles..."

for ROLE in \
  "roles/aiplatform.user" \
  "roles/secretmanager.secretAccessor" \
  "roles/logging.logWriter" \
  "roles/monitoring.metricWriter"
do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="${ROLE}" \
    --quiet
  echo "✓ Assigned ${ROLE}"
done

# Create secret (if not exists)
if ! gcloud secrets describe cloud-run-secret --project="${PROJECT_ID}" &>/dev/null; then
  echo "Creating secret..."
  gcloud iam service-accounts keys create - \
    --iam-account="${SERVICE_ACCOUNT_EMAIL}" \
    | gcloud secrets create cloud-run-secret \
      --project="${PROJECT_ID}" \
      --replication-policy="user-managed" \
      --locations="us-central1" \
      --data-file=-
  echo "✓ Created secret cloud-run-secret"
fi

echo "✓ All permissions configured!"
```

---

## Related Documentation

- [DEPLOYMENT_SUMMARY_2026-08-28.md](../../DEPLOYMENT_SUMMARY_2026-08-28.md)
- [DEPLOY_SCRIPT_CHANGES.md](./DEPLOY_SCRIPT_CHANGES.md)
- [AUTHENTICATION_CHANGES.md](./AUTHENTICATION_CHANGES.md)
