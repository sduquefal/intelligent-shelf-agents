import os

from pydantic import BaseModel


class Settings(BaseModel):
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "corp-stro-salesinventory-prod")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    vertex_project_id: str = os.getenv(
        "VERTEX_PROJECT_ID",
        os.getenv("GOOGLE_CLOUD_PROJECT", "corp-stro-salesinventory-prod"),
    )
    vertex_location: str = os.getenv("VERTEX_LOCATION", os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
    vertex_engine_id: str = os.getenv("VERTEX_ENGINE_ID", "5375474415045705728")
    firestore_collection: str = os.getenv("FIRESTORE_COLLECTION", "user_sessions")
    api_key: str | None = os.getenv("ISPILOT_API_KEY")
    session_timeout_hours: int = int(os.getenv("SESSION_TIMEOUT_HOURS", "8"))


settings = Settings()
