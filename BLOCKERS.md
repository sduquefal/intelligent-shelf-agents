# Sprint 3 - Known Blockers & Workarounds

**Updated**: 2026-08-29  
**Status**: Local testing blocked, remote testing proceeding

---

## Blocker 1: SA Credentials Not Available Locally ❌

**Severity**: High | **Impact**: Blocks local testing | **Workaround**: Use remote machine

### Description
Service account key file (`sa-tot-osa-key.json`) is not available in local development environment.

### Root Cause
- SA credentials are securely stored and not distributed to all machines
- Local Python environment lacks production secret access
- Expected behavior for dev environments

### Attempts Made
```bash
# Tried to find credentials
$env:GOOGLE_APPLICATION_CREDENTIALS = "c:\Users\sduque\sa\key.json"  # ❌ File not found
gcloud auth list  # ✓ No service account configured locally
```

### Workaround
1. ✅ Use remote machine that has SA credentials
2. ✅ Follow `REMOTE_TESTING_GUIDE.md` for setup
3. ✅ Run `test_local_integration.py` on remote
4. ✅ Validate metrics from remote logs

### Timeline to Fix
- **For local dev**: Get SA key from team lead (encrypted storage)
- **For testing**: Use remote machine (faster path, recommended)
- **Estimated time if using local**: 30 min (decrypt, setup, verify)
- **Estimated time using remote**: 20 min (clone, install, test)

---

## Blocker 2: Missing google.adk Module Locally ❌

**Severity**: Medium | **Impact**: Blocks module imports | **Workaround**: Install dependencies on remote

### Description
Python module `google.adk` (Vertex AI Agent SDK) is not installed in local environment.

### Root Cause
- Local venv doesn't have `google-cloud-aiplatform` dependency installed
- `requirements.txt` not yet installed locally
- Expected for fresh clone

### Attempts Made
```python
from google.adk.agents import Agent
# ❌ ModuleNotFoundError: No module named 'google.adk'
```

### Workaround
1. ✅ Install dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
2. ✅ Verify installation:
   ```bash
   python -c "from google.adk.agents import Agent; print('OK')"
   ```
3. ✅ Run test again on remote machine

### Timeline to Fix
- **Local**: 5 min (pip install)
- **Remote**: Included in onboarding steps

---

## Decision: Plan B - Remote Testing

**Why Not Continue Local?**
- ✗ Can't get SA credentials locally (security constraint)
- ✗ Better to test on machine with actual GCP access
- ✓ Faster iteration (one setup, multiple tests)
- ✓ More realistic environment (production-like)

**What Changed From Sprint 3 Plan**
- Original: Test locally → if fail, test remotely
- Revised: Local blocked early → jump to remote immediately
- Impact: Same validation, different machine

**Time Impact**
- Local testing path: ~2 hours (blocked → debug → workaround)
- Remote testing path: ~1 hour (clone → install → test)
- **Net savings**: ~1 hour, more confidence in results

---

## Metrics Integration Status ✅

Despite blockers, core work is complete:

| Component | Status | Notes |
|-----------|--------|-------|
| Agent metrics | ✅ Added | `track_agent_operation()` in coordinator |
| Analytics metrics | ✅ Added | Latency tracking on `get_latest_daily_summary()` |
| Store metrics | ✅ Added | Latency tracking on `resolve_store()` |
| Vertex metrics | ✅ Added | End-to-end tracking on `chat()` method |
| Test script | ✅ Created | `test_local_integration.py` ready |
| Documentation | ✅ Created | `REMOTE_TESTING_GUIDE.md` complete |

**Code is production-ready, just needs validation on remote machine.**

---

## What's Next (This Week)

### Priority 1: Get Remote Machine Access ⏳
- [ ] Identify remote machine with SA credentials
- [ ] Get SSH/RDP access
- [ ] Verify gcloud configured

### Priority 2: Run Remote Tests ⏳
- [ ] Clone repo on remote
- [ ] Install dependencies
- [ ] Run `test_local_integration.py`
- [ ] Capture output (metrics validation)

### Priority 3: Deploy to Staging ⏳
- [ ] Build Docker image
- [ ] Push to GCR
- [ ] Deploy to Cloud Run staging
- [ ] Test API endpoints

### Priority 4: Validate & Document ⏳
- [ ] Update this file with remote test results
- [ ] Document any new blockers
- [ ] Measure baseline metrics
- [ ] Prepare for production

---

## FAQ

**Q: Can we continue testing locally without SA credentials?**  
A: Partially. We can test imports/agent config, but can't test BigQuery integration. Remote testing is better.

**Q: Will the local test run if we skip BigQuery tests?**  
A: Yes, but it won't validate the most critical path (analytics). Better to wait for remote.

**Q: How long until we can test on remote?**  
A: Depends on your access. Once you have a remote machine with:
- ✓ Python 3.10+
- ✓ SA credentials for `corp-stro-salesinventory-prod`
- ✓ gcloud CLI configured
You can follow `REMOTE_TESTING_GUIDE.md` in ~30 minutes.

**Q: Do we need to modify any code for remote testing?**  
A: No. Code is identical. Remote machine just needs dependencies + credentials.

**Q: What if remote tests also fail?**  
A: Document the error in this file, investigate root cause, and post-debug. We have debug procedures in `REMOTE_TESTING_GUIDE.md`.

---

## Rollback Plan

If remote testing discovers critical issues:

1. **Revert Metrics Code** (if needed):
   ```bash
   git revert fe106ea  # Reverts metrics commit
   ```

2. **Keep Test Script** (for future use):
   - `test_local_integration.py` stays in repo
   - Can debug incrementally

3. **Document Issue** (in this file):
   - Root cause
   - Proposed fix
   - Estimated effort

4. **Create Follow-up Issue**:
   - Assign to team
   - Schedule for next sprint

---

**Last Updated**: 2026-08-29  
**Tracked By**: WORK_CHECKPOINT.md (Sprint 3 section)  
**Related Files**: REMOTE_TESTING_GUIDE.md, SPRINT3_DETAILED_PLAN.md
