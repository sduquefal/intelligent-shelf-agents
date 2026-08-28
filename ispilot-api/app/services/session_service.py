from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from app.config.settings import settings
from app.db.firestore_client import FirestoreSessionStore
from app.services.vertex_client import VertexAgentClient


class InMemorySessionStore:
    """Simple in-memory store used for tests and local fallbacks."""

    def __init__(self, store: dict[str, dict[str, str]]) -> None:
        self.store = store

    def get_session(self, user_id: str) -> str | None:
        data = self.store.get(user_id)
        if not data:
            return None
        return data.get("session_id")

    def get_session_data(self, user_id: str) -> dict[str, str] | None:
        return self.store.get(user_id)

    def save_session(self, user_id: str, session_id: str, timestamp: str | None = None) -> None:
        self.store[user_id] = {
            "user_id": user_id,
            "session_id": session_id,
            "status": "active",
        }
        if timestamp is not None:
            self.store[user_id]["timestamp"] = timestamp


class SessionService:
    """Service for managing user sessions with timeout/expiration logic."""

    def __init__(
        self,
        firestore_store: FirestoreSessionStore | InMemorySessionStore | None = None,
        vertex_client: VertexAgentClient | None = None,
        session_timeout_hours: int = 8,
        store: dict[str, dict[str, str]] | None = None,
    ) -> None:
        if store is not None:
            self.firestore_store = InMemorySessionStore(store)
        elif firestore_store is not None:
            self.firestore_store = firestore_store
        else:
            # Try to use Firestore, fall back to in-memory if API is disabled
            try:
                self.firestore_store = FirestoreSessionStore(
                    project_id=settings.project_id,
                    collection_name=settings.firestore_collection,
                )
            except Exception as e:
                self.logger = logging.getLogger(__name__)
                self.logger.warning(
                    f"Firestore initialization failed, using in-memory store: {str(e)}"
                )
                self.firestore_store = InMemorySessionStore({})
        self.vertex_client = vertex_client or VertexAgentClient()
        self.session_timeout_hours = session_timeout_hours
        self.logger = logging.getLogger(__name__)

    def create(self, user_id: str) -> str:
        """Create a new session via Vertex and store session_id in Firestore."""
        session_id = self.vertex_client.create_session(user_id=user_id)
        self._save_session(user_id=user_id, session_id=session_id)
        self.logger.info(
            f"Session created for user {user_id}",
            extra={"user_id": user_id, "session_id": session_id},
        )
        return session_id

    def get(self, user_id: str) -> str | None:
        """
        Get existing session for user. Returns None if no active session exists.
        Checks session expiration.
        """
        session_id = self.firestore_store.get_session(user_id=user_id)
        if session_id:
            if self._is_session_valid(user_id=user_id):
                return session_id
            self.logger.info(
                f"Session expired for user {user_id}",
                extra={"user_id": user_id},
            )
            return None
        return None

    def exists(self, user_id: str) -> bool:
        """Check if a valid session exists for the user."""
        return self.get(user_id=user_id) is not None

    def get_current(self, user_id: str) -> str | None:
        """Return the active session id for a user, if any."""
        return self.get(user_id=user_id)

    def get_or_create(self, user_id: str, session_id: str | None = None) -> str:
        """Get existing session or create a new one."""
        if session_id is not None:
            self._save_session(user_id=user_id, session_id=session_id)
            return session_id

        existing_session = self.get(user_id=user_id)
        if existing_session:
            return existing_session
        return self.create(user_id=user_id)

    def _save_session(self, user_id: str, session_id: str) -> None:
        """Save session with timestamp."""
        timestamp = datetime.now(timezone.utc).isoformat()
        self.firestore_store.save_session(
            user_id=user_id,
            session_id=session_id,
            timestamp=timestamp,
        )

    def _is_session_valid(self, user_id: str) -> bool:
        """Check if session is still valid (not expired)."""
        data = getattr(self.firestore_store, "get_session_data", None)
        if callable(data):
            payload = data(user_id=user_id)
        else:
            doc = self.firestore_store.client.collection(
                settings.firestore_collection
            ).document(user_id).get()
            if not doc.exists:
                return False
            payload = doc.to_dict()

        if not payload:
            return False

        timestamp_str = payload.get("timestamp")
        if not timestamp_str:
            return False

        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            now = datetime.now(timezone.utc)
            expiration = timestamp + timedelta(hours=self.session_timeout_hours)
            return now < expiration
        except (ValueError, TypeError):
            return False
