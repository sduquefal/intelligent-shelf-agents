# ISPilot API - Quick Reference Guide

**Status:** 🟢 LIVE IN PRODUCTION | **Service URL:** https://ispilot-api-46y2f3tyja-uc.a.run.app

---

## ⚡ Quick Deploy

```bash
cd c:/Users/sduque/OneDrive\ -\ Falabella/Proyectos/2026/is/ispilot/intelligent-shelf-agents/ispilot-api
bash deploy.sh
```

**Expected Output:** Service URL + "Deployment complete!" ✓

---

## 🔐 Get Auth Token

```bash
gcloud auth print-identity-token \
  --audiences https://ispilot-api-46y2f3tyja-uc.a.run.app
```

---

## 🧪 Test API

### Health Check
```bash
curl https://ispilot-api-46y2f3tyja-uc.a.run.app/health
```
**Expected:** `{"status": "healthy", "timestamp": "..."}`

### Chat Query
```bash
AUTH_TOKEN=$(gcloud auth print-identity-token \
  --audiences https://ispilot-api-46y2f3tyja-uc.a.run.app)

curl -X POST https://ispilot-api-46y2f3tyja-uc.a.run.app/chat \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "message": "How is Talca Colin performing?"
  }'
```
**Expected:** JSON response with `answer`, `session_id`, `status: "ok"`

---

## 📋 View Logs

```bash
gcloud run services logs read ispilot-api \
  --project corp-stro-salesinventory-prod \
  --region us-central1 \
  --limit 50
```

---

## 🔍 Check Service Status

```bash
gcloud run services describe ispilot-api \
  --project corp-stro-salesinventory-prod \
  --region us-central1 \
  --format="table(status.url,status.revision,serviceAccountEmail)"
```

---

## 🛠️ Local Development

### Setup
```bash
cd ispilot-api
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Run Local
```bash
./run.sh
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Test Local
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{
    "user_id": "test",
    "message": "Hello"
  }'
```

---

## 📊 Configuration Reference

### Production (Cloud Run)
| Variable | Value |
|----------|-------|
| Project | `corp-stro-salesinventory-prod` |
| Region | `us-central1` |
| Service Account | `sa-tot-osa` |
| Memory | 1Gi |
| CPU | 2 |
| Vertex Engine ID | `5375474415045705728` |

### Keys
| Key | Status | Usage |
|-----|--------|-------|
| Service Account (sa-tot-osa) | ✅ Active | Cloud Run identity |
| Cloud Run Secret | ✅ Configured | Credentials storage |
| API Key | ✅ Available | Local dev only |

---

## ❌ Troubleshooting Checklist

| Issue | Check | Fix |
|-------|-------|-----|
| Auth fails | Is gcloud authenticated? | `gcloud auth list` |
| Health check fails | Is service started? | Check logs: `gcloud run services logs read...` |
| Deployment fails | Is docker installed? | `docker --version` |
| Vertex error | Is engine ID correct? | Engine ID: `5375474415045705728` |
| Session fails | Is Firestore available? | Falls back to in-memory (OK for dev) |

---

## 🔐 Authentication Methods

### Production (OAuth Bearer Token) ✅
```bash
AUTH_TOKEN=$(gcloud auth print-identity-token --audiences https://ispilot-api-46y2f3tyja-uc.a.run.app)
curl -H "Authorization: Bearer $AUTH_TOKEN" https://ispilot-api-46y2f3tyja-uc.a.run.app/chat
```

### Development (API Key) ⚠️
```bash
curl -H "X-API-Key: test-key" http://localhost:8080/chat
```

---

## 📁 Important Files

| File | Purpose | Location |
|------|---------|----------|
| `deploy.sh` | Deployment automation | `ispilot-api/` |
| `Dockerfile` | Container build | `ispilot-api/` |
| `app/main.py` | FastAPI entry point | `ispilot-api/app/` |
| `app/services/vertex_client.py` | Vertex integration ✅ | `ispilot-api/app/services/` |
| `requirements.txt` | Python dependencies | `ispilot-api/` |
| `.env.example` | Config template | `ispilot-api/` |

---

## 🎯 Common Tasks

### Task: Redeploy Latest Code
```bash
git pull
cd ispilot-api
bash deploy.sh
```
⏱️ Time: ~10-15 minutes

### Task: Check Service Health
```bash
curl https://ispilot-api-46y2f3tyja-uc.a.run.app/health
```
Expected: `{"status": "healthy"}`

### Task: View Last 20 Logs
```bash
gcloud run services logs read ispilot-api \
  --project corp-stro-salesinventory-prod \
  --region us-central1 \
  --limit 20
```

### Task: Test Chat Endpoint
```bash
AUTH_TOKEN=$(gcloud auth print-identity-token --audiences https://ispilot-api-46y2f3tyja-uc.a.run.app)
curl -X POST https://ispilot-api-46y2f3tyja-uc.a.run.app/chat \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"Hello ISPilot"}'
```

### Task: Enable Firestore (Optional)
```bash
gcloud services enable firestore.googleapis.com \
  --project corp-stro-salesinventory-prod
```
Note: Service works fine without this (uses in-memory fallback)

---

## 📞 Key Resources

- **API Status:** [API_STATUS_2026-08-28.md](API_STATUS_2026-08-28.md)
- **Full Guide:** [INTELLIGENT_SHELF_AGENTS_GUIDE.md](INTELLIGENT_SHELF_AGENTS_GUIDE.md)
- **Deployment Details:** [ispilot-api/DEPLOYMENT.md](ispilot-api/DEPLOYMENT.md)
- **Architecture:** [docs/ISPilot-Enterprise-Architecture-And-Vertex-Agent-Engine-Guide.md](docs/ISPilot-Enterprise-Architecture-And-Vertex-Agent-Engine-Guide.md)

---

## ✅ Deployment Checklist

Before deploying:
- [ ] Code committed to git
- [ ] `requirements.txt` updated if needed
- [ ] Environment variables reviewed
- [ ] Service account correct (`sa-tot-osa`)
- [ ] gcloud authenticated

After deploying:
- [ ] Health check passes
- [ ] Chat endpoint responds
- [ ] Logs show no errors
- [ ] Session management working

---

**Last Updated:** August 28, 2026  
**Status:** 🟢 PRODUCTION READY
