# Teams Cloud Run bridge for IsPilot

This service is a minimal bridge between Microsoft Teams and the validated IsPilot API.

## Purpose

- receive a message from Teams
- call the IsPilot Cloud Run API
- return the answer to Teams

## Required runtime

This service should run in Cloud Run using the correct Google service account identity.

Do not rely on a personal `gcloud` session to impersonate another account.

## Environment variables

```bash
ISPILOT_URL=https://ispilot-api-46y2f3tyja-uc.a.run.app/chat
TARGET_AUDIENCE=https://ispilot-api-46y2f3tyja-uc.a.run.app
PORT=8080
```

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8080
```

## Cloud Run deployment

```bash
gcloud run deploy teams-ispilot-bridge \
  --source . \
  --region us-central1 \
  --project corp-stro-salesinventory-prod \
  --allow-unauthenticated
```

## Teams request example

```json
{
  "text": "How is Talca Colin performing?",
  "user_id": "sebastian"
}
```

## Response example

```json
{
  "reply": "Talca Colín is performing at 95.16% SNSG, with 0.67% Bodega and 4.17% Quiebre.",
  "session_id": "5411387247947677696",
  "status": "ok"
}
```
