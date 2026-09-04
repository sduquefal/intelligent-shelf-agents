# ⚠️ DEPRECATED - Old Power Automate Architecture

**Status**: Do NOT use. Historical reference only.

This file documents the **old Power Automate + Copilot Studio** architecture that has been deprecated and replaced.

---

## Why This Was Deprecated

The old approach attempted to use **Power Automate** as a bridge between Teams and IsPilot API:

- ❌ Token type mismatch (Microsoft Bearer ≠ Google identity tokens)
- ❌ Cross-cloud authentication complexity (Azure ↔ GCP)
- ❌ No native Teams protocol handling
- ❌ Missing session context management
- ❌ Limited to Power Automate quotas and constraints

See [../docs/ARCHITECTURE_RESET_TEAMS_SDK.md](../docs/ARCHITECTURE_RESET_TEAMS_SDK.md) for complete analysis.

---

## Current Architecture (Use This Instead)

The project has been reset to use:

1. **Microsoft 365 Agents SDK** (instead of Power Automate)
2. **Teams Bridge** service (instead of direct Copilot Studio)
3. **Azure Bot Service** (instead of Power Automate flows)

---

## Documentation References

For current implementation, refer to:

| Purpose | File |
|---------|------|
| Quick Start & Architecture | [README.md](./README.md) |
| 5-Phase Implementation Plan | [NEXT_STEPS.md](./NEXT_STEPS.md) |
| Complete Setup Guide | [../docs/TEAMS_SDK_INTEGRATION.md](../docs/TEAMS_SDK_INTEGRATION.md) |
| Architecture Decision Rationale | [../docs/ARCHITECTURE_RESET_TEAMS_SDK.md](../docs/ARCHITECTURE_RESET_TEAMS_SDK.md) |
| API Documentation | [../ispilot-api/README.md](../ispilot-api/README.md) |
| Project Status | [../WORK_CHECKPOINT.md](../WORK_CHECKPOINT.md) |

---

## Key Differences

| Aspect | Old Approach | New Approach |
|--------|-------------|-------------|
| Technology | Power Automate | MS 365 Agents SDK + FastAPI |
| Integration | Direct Copilot Studio | Azure Bot Service → Teams Bridge |
| Authentication | Manual in Power Automate | Built-in Azure JWT + Google identity tokens |
| Session Context | Limited | Full session persistence via conversation_id |
| Scalability | Power Automate quotas | Cloud Run auto-scaling |
| Deployment | Power Automate cloud | Cloud Run + Dockerfile |
| Testing | Manual in Power Automate | Local uvicorn + cloud integration tests |

---

## For Historical Reference

**Old files that have been replaced**:
- ~~app.py~~ → main.py (MS 365 SDK implementation)
- ~~COPILOT_STUDIO_SETUP.md~~ → README.md + NEXT_STEPS.md
- ~~MIGRATION_GUIDE.md~~ → DEPRECATED.md (this file)
- ~~power-automate-flow-template.json~~ (removed)

---

## Need to Understand the Old Approach?

This file keeps the deprecated approach documented for historical reference. If you need to:

- **Understand why we changed**: See [../docs/ARCHITECTURE_RESET_TEAMS_SDK.md](../docs/ARCHITECTURE_RESET_TEAMS_SDK.md)
- **See rollback options**: Documented in architecture file above
- **Reference old patterns**: Search git history for Power Automate branch

---

**Last Updated**: 2026-09-01  
**Deprecated Since**: 2026-09-01  
**Migration Status**: ✅ Complete - All new development uses Teams SDK approach
