from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from app.config.settings import settings

logger = logging.getLogger(__name__)


class VertexAgentClient:
    def __init__(self, max_retries: int = 3) -> None:
        self.project_id = settings.vertex_project_id
        self.location = settings.vertex_location
        self.engine_id = settings.vertex_engine_id
        self.endpoint = (
            f"https://{self.location}-aiplatform.googleapis.com/v1/"
            f"projects/{self.project_id}/locations/{self.location}/"
            f"reasoningEngines/{self.engine_id}:query"
        )
        self.max_retries = max_retries

    def _token(self) -> str:
        """Get valid Google Cloud authentication token."""
        credentials_input = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_input:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not configured for Vertex access")
        
        try:
            # Handle both file path and JSON string (from Cloud Run --set-secrets)
            if credentials_input.startswith("{"):
                # JSON string from environment variable
                creds_dict = json.loads(credentials_input)
                credentials = service_account.Credentials.from_service_account_info(creds_dict)
            else:
                # File path
                credentials = service_account.Credentials.from_service_account_file(credentials_input)
            
            # Refresh credentials to get valid token
            credentials.refresh(Request())
            return credentials.token
        except Exception as exc:
            logger.error(
                "Authentication failed",
                extra={"error": str(exc), "credentials_input": credentials_input[:50] if credentials_input else None},
            )
            raise ValueError(f"Failed to authenticate with Vertex: {exc}") from exc

    def _request_with_retry(
        self,
        payload: dict[str, Any],
        timeout: int,
        operation: str,
    ) -> dict[str, Any]:
        """Execute request with exponential backoff retry logic."""
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Vertex API request: {operation}",
                    extra={
                        "operation": operation,
                        "attempt": attempt + 1,
                        "max_retries": self.max_retries,
                        "payload_size": len(json.dumps(payload)),
                    },
                )
                response = requests.post(
                    self.endpoint,
                    headers={
                        "Authorization": f"Bearer {self._token()}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=timeout,
                )
                response.raise_for_status()
                data = response.json()
                logger.info(
                    f"Vertex API success: {operation}",
                    extra={
                        "operation": operation,
                        "response_size": len(response.text),
                    },
                )
                return data
            except requests.exceptions.Timeout as exc:
                last_error = exc
                logger.warning(
                    f"Vertex API timeout (attempt {attempt + 1}/{self.max_retries}): {operation}",
                    extra={"operation": operation, "attempt": attempt + 1},
                )
            except requests.exceptions.RequestException as exc:
                last_error = exc
                if response.status_code >= 500:
                    logger.warning(
                        f"Vertex API server error (attempt {attempt + 1}/{self.max_retries}): {operation}",
                        extra={"operation": operation, "attempt": attempt + 1, "status": response.status_code},
                    )
                else:
                    logger.error(
                        f"Vertex API client error: {operation}",
                        extra={"operation": operation, "status": response.status_code, "detail": str(exc)},
                    )
                    raise

            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.info(
                    f"Retrying Vertex API request after {wait_time}s",
                    extra={"operation": operation, "wait_time": wait_time},
                )
                time.sleep(wait_time)

        logger.error(
            f"Vertex API failed after {self.max_retries} retries: {operation}",
            extra={"operation": operation, "error": str(last_error)},
        )
        raise ValueError(f"Vertex API call failed ({operation}): {last_error}")

    def create_session(self, user_id: str) -> str:
        """Create a new session via Vertex with retry logic."""
        payload = {
            "classMethod": "create_session",
            "input": {"user_id": user_id},
        }
        data = self._request_with_retry(
            payload=payload,
            timeout=120,
            operation="create_session",
        )
        session_id = data.get("output", {}).get("id")
        if not session_id:
            raise ValueError("Vertex session creation did not return a session id")
        return session_id

    def stream_query(self, user_id: str, session_id: str, message: str) -> dict[str, Any]:
        """Execute stream query with retry logic."""
        payload = {
            "classMethod": "stream_query",
            "input": {
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
            },
        }
        return self._request_with_retry(
            payload=payload,
            timeout=180,
            operation="stream_query",
        )

    def _extract_text(self, payload: dict[str, Any]) -> str:
        output = payload.get("output", [])
        if not isinstance(output, list):
            return json.dumps(payload)

        for item in output:
            content = item.get("content", {})
            parts = content.get("parts", [])
            for part in parts:
                if "text" in part:
                    return part["text"]
        return json.dumps(payload)

    def chat(self, user_id: str, message: str, session_id: str | None = None) -> tuple[str, str]:
        effective_session = session_id or self.create_session(user_id)
        result = self.stream_query(user_id=user_id, session_id=effective_session, message=message)
        answer = self._extract_text(result)
        return answer, effective_session
