from __future__ import annotations

from google.cloud import firestore


class FirestoreSessionStore:
    def __init__(self, project_id: str, collection_name: str = "user_sessions") -> None:
        self.client = firestore.Client(project=project_id)
        self.collection_name = collection_name

    def get_session(self, user_id: str) -> str | None:
        doc = self.client.collection(self.collection_name).document(user_id).get()
        if not doc.exists:
            return None
        return doc.to_dict().get("session_id")

    def save_session(self, user_id: str, session_id: str, timestamp: str | None = None) -> None:
        """Save session with optional timestamp."""
        data = {
            "user_id": user_id,
            "session_id": session_id,
            "status": "active",
        }
        if timestamp:
            data["timestamp"] = timestamp
        
        doc_ref = self.client.collection(self.collection_name).document(user_id)
        doc_ref.set(data)
