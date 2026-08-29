# Sprint 3: Staging Validation & Metrics Integration - Detailed Plan

**Status**: Starting  
**Date**: 2026-08-29  
**Duration**: 3-4 weeks  
**Risk**: Will test locally if possible, fallback to remote machine

---

## Overview

Sprint 3 focuses on:
1. ✅ Integrate metrics decorators into agents and API
2. ✅ Deploy to staging environment
3. ✅ Validate with real Intelligent Shelf data
4. ✅ Test agent decision chains under load
5. ✅ Establish performance baseline

**Testing Strategy**:
- **Plan A**: Local testing with SA authentication
- **Plan B**: Commit/push to remote machine if local fails

---

## Phase 1: Local SA Setup & Validation (Week 1)

### Step 1.1: Activate Service Account Locally

**Goal**: Enable local testing against production BigQuery

**Commands**:
```bash
# 1. Set project
$env:GOOGLE_CLOUD_PROJECT = "corp-stro-salesinventory-prod"

# 2. Get SA credentials path
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\sa-tot-osa-key.json"

# 3. Authenticate gcloud
gcloud auth activate-service-account sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com `
  --key-file=$env:GOOGLE_APPLICATION_CREDENTIALS

# 4. Set default project
gcloud config set project corp-stro-salesinventory-prod

# 5. Verify auth
gcloud auth list
gcloud config list
```

**Where to get SA key**:
- Google Cloud Console → Service Accounts → sa-tot-osa
- Click "Keys" tab
- Download JSON key (if not downloaded, create new)
- Save securely (add to .gitignore, never commit)

**Verify It Works**:
```bash
# Should list tables in BigQuery
bq ls --project_id=corp-stro-salesinventory-prod

# Should show reasoning engines
gcloud ai reasoning-engines list `
  --project=corp-stro-salesinventory-prod `
  --region=us-central1
```

**If This Fails** → Jump to "Plan B: Remote Testing" section

---

### Step 1.2: Set Up Local Environment

```bash
# Navigate to root project
cd "c:\Users\sduque\OneDrive - Falabella\Proyectos\2026\is\ispilot\intelligent-shelf-agents"

# Create venv (if not exists)
python -m venv venv
. venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
pip install -r requirements.lock.txt

# Verify imports work
python -c "from agents.coordinator.agent import root_agent; print(f'Agent: {root_agent.name}')"
```

**If This Fails**: Check Python path, missing packages, or venv activation

---

### Step 1.3: Understand Current Code Structure

**Decorator Locations** (ispilot-api):
- `app/utils/observability.py` → `track_vertex_latency()`, `track_cache_operation()`
- `app/utils/metrics.py` → `get_metrics_client()` (Cloud Monitoring client)
- `app/utils/metrics_definitions.py` → Metric schemas

**Agent Files** (root):
- `agents/coordinator/agent.py` ← Main coordinator
- `agents/coordinator/subagents/shelf_analyst/agent.py` ← Analyst
- `agents/coordinator/subagents/store_coach/agent.py` ← Coach

**Services** (root):
- `services/analytics_service.py` ← Query builder
- `services/store_service.py` ← Store data fetcher

**API** (ispilot-api):
- `app/services/vertex_agent_client.py` ← Orchestrates agents
- `app/api/chat.py` ← Chat endpoint

---

## Phase 2: Metrics Integration (Week 1-2)

### Step 2.1: Add Metrics to Coordinator Agent

**File**: `agents/coordinator/agent.py`

**Change**: Wrap agent message handling with latency tracking

```python
# At the top of agent.py
import time
from contextlib import contextmanager

# Add this context manager for agent-level tracking
@contextmanager
def track_agent_operation(agent_name: str):
    """Track agent operation latency."""
    start_time = time.time()
    try:
        yield
    finally:
        latency_ms = (time.time() - start_time) * 1000
        print(f"[METRICS] Agent '{agent_name}' operation took {latency_ms:.2f}ms")
        # Later: Replace with actual metrics.record_agent_latency(...)
```

**Implementation**:
- For now: Log to console (simple, works anywhere)
- Later (in staging): Integrate with Cloud Monitoring

---

### Step 2.2: Add Metrics to Analytics Service

**File**: `services/analytics_service.py`

**Changes**:
1. Track query latency
2. Log operation success/failure
3. Record number of records processed

**Pseudo-code**:
```python
import time

class AnalyticsService:
    def get_latest_daily_summary(self, country: str) -> dict:
        start_time = time.time()
        
        try:
            # ... existing query logic ...
            
            latency_ms = (time.time() - start_time) * 1000
            print(f"[METRICS] get_latest_daily_summary({country}) took {latency_ms:.2f}ms")
            
            return result
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            print(f"[METRICS] get_latest_daily_summary({country}) failed after {latency_ms:.2f}ms: {e}")
            raise
```

---

### Step 2.3: Add Metrics to Store Service

**File**: `services/store_service.py`

**Same pattern as AnalyticsService**:
- Track query start/end
- Log latency
- Record success/failure

---

### Step 2.4: Update VertexAgentClient

**File**: `ispilot-api/app/services/vertex_agent_client.py`

**Changes**:
1. Import tracking utilities
2. Wrap agent invoke call with `track_vertex_latency()`
3. Add error categorization

**Skeleton**:
```python
from app.utils.observability import track_vertex_latency

class VertexAgentClient:
    async def send_message(self, user_id: str, message: str, session_id: str):
        with track_vertex_latency("agent_invoke"):
            # ... existing agent call ...
            response = await self.agent.invoke(message)
            # ...
        return response
```

---

## Phase 3: Local Testing (Week 2)

### Step 3.1: Create Test Script

**File**: `test_local_integration.py` (in root)

```python
#!/usr/bin/env python
"""Local integration test for agents + metrics."""

import os
import asyncio
from agents.coordinator.agent import root_agent
from services.analytics_service import AnalyticsService

async def test_coordinator():
    """Test coordinator agent routing."""
    print("\n=== Test 1: Coordinator Agent ===")
    
    # Test message routing to Analyst
    message = "How is Talca Colin performing?"
    print(f"Message: {message}")
    
    # Note: ADK agents may require async context
    # Exact invocation depends on ADK version
    # response = await root_agent.invoke(message)
    # print(f"Response: {response}")

def test_analytics_service():
    """Test analytics service with real data."""
    print("\n=== Test 2: Analytics Service ===")
    
    service = AnalyticsService()
    
    # Test CL
    result = service.get_latest_daily_summary("CL")
    print(f"CL Result: {result}")
    
    # Test PE
    result = service.get_latest_daily_summary("PE")
    print(f"PE Result: {result}")

async def main():
    """Run all tests."""
    print("[INFO] Starting local integration tests...")
    
    try:
        test_analytics_service()
        # await test_coordinator()  # Uncomment once ADK is understood
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
```

**Run**:
```bash
python test_local_integration.py
```

**Expected Output**:
```
[INFO] Starting local integration tests...

=== Test 2: Analytics Service ===
[METRICS] get_latest_daily_summary(CL) took 1234.56ms
CL Result: {'status': 'success', 'data': {...}}

=== Test 1: Coordinator Agent ===
[METRICS] Agent 'ispilot_coordinator' operation took 5678.90ms
Response: ...
```

**If Tests Pass**:
- ✅ SA auth works
- ✅ BigQuery connectivity OK
- ✅ Agent framework loads
- Proceed to Step 3.2

**If Tests Fail**:
- ❌ SA auth issue → Verify credentials file path
- ❌ BigQuery error → Check project, dataset permissions
- ❌ Agent import error → Check ADK installation, Python path
- Jump to "Plan B: Remote Testing"

---

### Step 3.2: Test with Actual Agent Invocation

**File**: `test_agent_routing.py`

**Goal**: Verify coordinator delegates correctly

```python
"""Test agent routing logic."""

from agents.coordinator.agent import root_agent, shelf_analyst, store_coach

def test_agent_routing():
    """Verify agents are properly configured."""
    
    # Check coordinator
    print(f"Coordinator: {root_agent.name}")
    print(f"Instruction snippet: {root_agent.instruction[:100]}...")
    
    # Check subagents
    print(f"\nSubagents: {[a.name for a in root_agent.sub_agents]}")
    
    # Verify routing keywords are in instruction
    analyst_keywords = ["How is a store", "SNSG", "Performance"]
    for keyword in analyst_keywords:
        if keyword in root_agent.instruction:
            print(f"✓ Analyst keyword found: {keyword}")
        else:
            print(f"✗ Analyst keyword missing: {keyword}")
```

**Run**:
```bash
python test_agent_routing.py
```

---

## Phase 4: Prepare Staging Deployment (Week 2-3)

### Step 4.1: Create Staging Config

**File**: `staging-deployment.yaml` (root)

```yaml
# Staging deployment configuration
project: corp-stro-salesinventory-prod
region: us-central1
environment: staging

# Service configuration
service:
  name: ispilot-api-staging
  image: gcr.io/corp-stro-salesinventory-prod/ispilot-api:staging
  port: 8080
  
  # Environment variables for staging
  env:
    - name: GOOGLE_CLOUD_PROJECT
      value: corp-stro-salesinventory-prod
    - name: VERTEX_ENGINE_ID
      value: "5375474415045705728"
    - name: ENVIRONMENT
      value: staging
    - name: LOG_LEVEL
      value: DEBUG
    - name: ENABLE_METRICS
      value: "true"

  # Staging-specific settings
  memory: 1Gi
  cpu: 1
  timeout: 120  # 2 minutes for agent calls
  
# Service account
service_account:
  email: sa-tot-osa@corp-stro-salesinventory-prod.iam.gserviceaccount.com
  scopes:
    - https://www.googleapis.com/auth/cloud-platform
```

---

### Step 4.2: Build Docker Image

**File**: `Dockerfile` (already exists, verify it's current)

**Build for Staging**:
```bash
cd ispilot-api

# Build image
docker build -t gcr.io/corp-stro-salesinventory-prod/ispilot-api:staging .

# Push to GCP Container Registry
docker push gcr.io/corp-stro-salesinventory-prod/ispilot-api:staging
```

**Or use Cloud Build**:
```bash
gcloud builds submit `
  --tag=gcr.io/corp-stro-salesinventory-prod/ispilot-api:staging `
  --project=corp-stro-salesinventory-prod
```

---

### Step 4.3: Deploy to Staging

**File**: `deploy-staging.sh` (create in root)

```bash
#!/bin/bash
set -e

PROJECT="corp-stro-salesinventory-prod"
REGION="us-central1"
SERVICE_NAME="ispilot-api-staging"
IMAGE="gcr.io/${PROJECT}/ispilot-api:staging"
SA="sa-tot-osa@${PROJECT}.iam.gserviceaccount.com"

echo "[INFO] Deploying $SERVICE_NAME to staging..."

gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE \
  --project=$PROJECT \
  --region=$REGION \
  --service-account=$SA \
  --no-allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT},VERTEX_ENGINE_ID=5375474415045705728,ENVIRONMENT=staging,LOG_LEVEL=DEBUG,ENABLE_METRICS=true" \
  --memory=1Gi \
  --cpu=1 \
  --timeout=120 \
  --wait-for-deployment

echo "[SUCCESS] Deployment complete!"
gcloud run services describe $SERVICE_NAME \
  --project=$PROJECT \
  --region=$REGION \
  --format='value(status.url)'
```

**Run**:
```bash
bash deploy-staging.sh
# Or PowerShell:
cd ispilot-api
. ..\deploy-staging.sh
```

---

## Phase 5: Staging Testing (Week 3)

### Step 5.1: Basic Health Check

```bash
# Get staging URL
$STAGING_URL = "https://ispilot-api-staging-xxxxx.run.app"

# Test health endpoint
curl -X GET "$STAGING_URL/health"

# Should return: {"status": "healthy", ...}
```

---

### Step 5.2: Test Chat Endpoint

**With API Key**:
```bash
$API_KEY = "your-staging-api-key"
$STAGING_URL = "https://ispilot-api-staging-xxxxx.run.app"

curl -X POST "$STAGING_URL/chat" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: $API_KEY" `
  -d '{
    "user_id": "test-user-1",
    "message": "How is Talca Colin performing?",
    "session_id": "test-session-1"
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "session_id": "test-session-1",
  "response": "The Talca Colin store shows...",
  "metadata": {
    "latency_ms": 5234,
    "agents_used": ["shelf_analyst"],
    "timestamp": "2026-08-29T..."
  }
}
```

---

### Step 5.3: Load Testing

**Tool**: Apache Bench or similar

```bash
# Install ab (Apache Bench)
# On Windows: choco install apache-bench
# On Mac: brew install httpd

# 100 requests, 10 concurrent
ab -n 100 -c 10 \
  -H "X-API-Key: $API_KEY" \
  -p payload.json \
  "$STAGING_URL/chat"
```

**payload.json**:
```json
{
  "user_id": "load-test-user",
  "message": "How is Talca Colin performing?",
  "session_id": "load-test-session"
}
```

**Collect Metrics**:
- Requests/second
- Avg latency
- p95, p99 latency
- Error rate

---

### Step 5.4: Chaos Testing

**Scenario 1: BigQuery Timeout**
- Manual: Have DBA throttle BigQuery connections
- Automated: Add deliberate slow query to NSGGateway

**Scenario 2: Firestore Unavailable**
- Disable Firestore API temporarily
- Verify fallback to in-memory sessions works

**Scenario 3: Auth Failures**
- Send invalid API key
- Send expired OAuth token
- Verify proper error responses

---

## Plan B: Remote Testing (If Local Fails)

### When to Use Plan B
- ❌ SA credentials unavailable
- ❌ Network access to BigQuery blocked
- ❌ Python/Docker setup issues
- ❌ Local testing is taking too long

### Steps

1. **Commit and Push All Changes**:
```bash
git add -A
git commit -m "Sprint 3 WIP: Metrics integration and staging deployment config"
git push origin main
```

2. **Test from Remote Machine**:
- SSH into remote machine with SA access
- Clone repo: `git clone <repo>`
- Run tests from there
- Results feed back into code

3. **Document Issues**:
- Update WORK_CHECKPOINT.md with blocker
- Note environment differences
- Plan next steps

---

## Acceptance Criteria (Sprint 3 Complete)

✅ **Code Changes**:
- [ ] Metrics decorators added to coordinator agent
- [ ] Metrics decorators added to analytics/store services
- [ ] VertexAgentClient uses track_vertex_latency()
- [ ] SessionService uses track_cache_operation()
- [ ] All code compiles/imports correctly

✅ **Local Testing**:
- [ ] `test_local_integration.py` runs successfully
- [ ] `test_agent_routing.py` verifies routing
- [ ] Analytics service returns real CL/PE data
- [ ] Agent imports work
- [ ] Metrics logging appears in console

✅ **Staging Deployment**:
- [ ] Docker image builds successfully
- [ ] Image pushed to Container Registry
- [ ] Cloud Run service deployed
- [ ] Health check returns 200 OK
- [ ] Chat endpoint responds with valid JSON

✅ **Staging Validation**:
- [ ] 100+ successful chat requests
- [ ] Latency metrics within budget (p99 < 2000ms)
- [ ] Error rate < 5%
- [ ] All agent routing works (Analyst + Coach paths tested)
- [ ] Load test: 10 concurrent users OK

✅ **Documentation**:
- [ ] Staging deployment runbook created
- [ ] Results logged in WORK_CHECKPOINT.md
- [ ] Performance baseline established
- [ ] Go/No-go decision documented

---

## If You Hit Blockers

**Document Them**:
1. Add to `BLOCKERS.md` file
2. Note time spent
3. Decision made (skip/workaround/escalate)
4. Commit progress

**Example**:
```markdown
# Sprint 3 Blockers

## Blocker 1: SA Key Access
- **Issue**: Cannot locate SA key file
- **Time Spent**: 1 hour
- **Decision**: Proceed to Plan B (remote testing)
- **Status**: ACTIVE

## Blocker 2: ADK Agent Invocation
- **Issue**: Unclear how to async invoke ADK agent
- **Time Spent**: 2 hours
- **Decision**: Create minimal test wrapper
- **Status**: RESOLVED
```

---

## Timeline Estimate

| Phase | Week | Status | Checkpoint |
|-------|------|--------|------------|
| Phase 1: SA Setup | W1 | TODO | SA auth works locally |
| Phase 2: Metrics | W1-2 | TODO | All decorators added |
| Phase 3: Local Test | W2 | TODO | Tests pass with real data |
| Phase 4: Staging Deploy | W2-3 | TODO | Service running in staging |
| Phase 5: Staging Validation | W3 | TODO | Load/chaos tests pass |
| Documentation | W3 | TODO | Runbook + baseline created |

---

## Next Steps (Start Now)

1. **Activate SA locally** (Step 1.1)
   - Try to authenticate to GCP
   - If works → Proceed with local testing
   - If fails → Prepare for Plan B

2. **Create test script** (Step 3.1)
   - Copy `test_local_integration.py` above
   - Run it
   - Debug any failures

3. **Add metrics to code** (Phase 2)
   - One service at a time
   - Test after each change
   - Commit frequently

4. **Report status back** in WORK_CHECKPOINT.md
   - Update progress
   - Document blockers
   - Plan next week

---

## Files to Create/Modify

**Create**:
- [ ] `test_local_integration.py` (root)
- [ ] `test_agent_routing.py` (root)
- [ ] `staging-deployment.yaml` (root)
- [ ] `deploy-staging.sh` (root)
- [ ] `BLOCKERS.md` (root)
- [ ] `SPRINT3_TESTING_RESULTS.md` (root)

**Modify**:
- [ ] `agents/coordinator/agent.py` - Add metrics tracking
- [ ] `services/analytics_service.py` - Add latency logging
- [ ] `services/store_service.py` - Add latency logging
- [ ] `ispilot-api/app/services/vertex_agent_client.py` - Add track_vertex_latency()
- [ ] `ispilot-api/app/services/session_service.py` - Add track_cache_operation()

**Update**:
- [ ] `WORK_CHECKPOINT.md` - Progress & results
- [ ] Root `README.md` - Staging deployment instructions

---

**Ready to Start?** Begin with Step 1.1 (SA Setup). Report back with success/failure.
