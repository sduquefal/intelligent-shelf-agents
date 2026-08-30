import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException, Request
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

app = FastAPI(title="Teams Cloud Run bridge for IsPilot")

ISPILOT_URL = os.getenv("ISPILOT_URL", "https://ispilot-api-46y2f3tyja-uc.a.run.app/chat")
TARGET_AUDIENCE = os.getenv("TARGET_AUDIENCE", "https://ispilot-api-46y2f3tyja-uc.a.run.app")


def get_identity_token() -> str:
    """Use the runtime identity already attached to the Cloud Run service."""
    request = google_requests.Request()
    return id_token.fetch_id_token(request, TARGET_AUDIENCE)


def extract_message(payload: dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        return ""

    direct_text = payload.get("text") or payload.get("message")
    if isinstance(direct_text, str) and direct_text.strip():
        return direct_text.strip()

    nested_value = payload.get("value")
    if isinstance(nested_value, dict):
        nested_text = nested_value.get("text") or nested_value.get("message")
        if isinstance(nested_text, str) and nested_text.strip():
            return nested_text.strip()

    return ""


def extract_user_id(payload: dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        return "teams-user"

    user_block = payload.get("from") or {}
    if isinstance(user_block, dict):
        user_id = user_block.get("user", {}).get("id") or user_block.get("id")
        if user_id:
            return str(user_id)

    if payload.get("user_id"):
        return str(payload["user_id"])

    return "teams-user"


def call_ispilot(message: str, user_id: str) -> dict[str, Any]:
    token = get_identity_token()

    body = {
        "user_id": user_id,
        "message": message,
        "session_id": None,
    }

    response = requests.post(
        ISPILOT_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json=body,
        timeout=60,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = response.text
        raise HTTPException(status_code=response.status_code, detail=f"IsPilot API error: {detail}") from exc

    payload = response.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail="Invalid response from IsPilot API")

    return payload


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/teams/message")
async def teams_message(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception as exc:  # pragma: no cover - defensive handling
        raise HTTPException(status_code=400, detail="Request body must be valid JSON") from exc

    message = extract_message(payload)
    if not message:
        raise HTTPException(status_code=400, detail="No message text found in payload")

    user_id = extract_user_id(payload)
    result = call_ispilot(message=message, user_id=user_id)

    return {
        "reply": result.get("answer", "No answer returned"),
        "session_id": result.get("session_id"),
        "status": result.get("status", "unknown"),
        "request_id": result.get("request_id"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")), reload=False)
