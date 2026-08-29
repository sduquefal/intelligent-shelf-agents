import os

from pydantic import BaseModel


class Settings(BaseModel):
    # Google Cloud configuration
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "corp-stro-salesinventory-prod")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Vertex AI configuration
    vertex_project_id: str = os.getenv(
        "VERTEX_PROJECT_ID",
        os.getenv("GOOGLE_CLOUD_PROJECT", "corp-stro-salesinventory-prod"),
    )
    vertex_location: str = os.getenv("VERTEX_LOCATION", os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
    vertex_engine_id: str = os.getenv("VERTEX_ENGINE_ID", "5375474415045705728")
    
    # Firestore configuration
    firestore_collection: str = os.getenv("FIRESTORE_COLLECTION", "user_sessions")
    session_timeout_hours: int = int(os.getenv("SESSION_TIMEOUT_HOURS", "8"))
    
    # API Key configuration
    api_key: str | None = os.getenv("ISPILOT_API_KEY")
    
    # Cloud Logging configuration
    enable_cloud_logging: bool = os.getenv("ENABLE_CLOUD_LOGGING", "true").lower() == "true"
    
    # Application configuration
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()
