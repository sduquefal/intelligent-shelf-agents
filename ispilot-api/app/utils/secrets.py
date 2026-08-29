"""Secret Manager integration for sensitive configuration."""

from __future__ import annotations

import logging
import os
from functools import lru_cache

try:
    from google.cloud import secretmanager
    GOOGLE_CLOUD_SECRETMANAGER_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_SECRETMANAGER_AVAILABLE = False


logger = logging.getLogger(__name__)


@lru_cache(maxsize=128)
def get_secret(
    secret_id: str,
    project_id: str,
    version_id: str = "latest",
) -> str:
    """
    Retrieve a secret from Google Secret Manager.
    
    Falls back to environment variable if Secret Manager is unavailable.
    
    Args:
        secret_id: Secret identifier (e.g., "ispilot-api-key")
        project_id: GCP project ID
        version_id: Secret version (default: "latest")
    
    Returns:
        Secret value as string
    
    Raises:
        ValueError: If secret not found and no environment variable exists
    """
    # Try to get from environment variable first (dev/local override)
    env_var = secret_id.upper().replace("-", "_")
    if os.getenv(env_var):
        return os.getenv(env_var)

    # Try Secret Manager if available
    if not GOOGLE_CLOUD_SECRETMANAGER_AVAILABLE:
        logger.warning(
            f"Secret Manager not available. Fallback to environment variable: {env_var}"
        )
        if value := os.getenv(env_var):
            return value
        raise ValueError(f"Secret '{secret_id}' not found in environment or Secret Manager")

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
        logger.info(f"Retrieved secret '{secret_id}' from Secret Manager")
        return secret_value
    except Exception as e:
        logger.warning(
            f"Failed to retrieve secret '{secret_id}' from Secret Manager: {e}. "
            f"Falling back to environment variable: {env_var}"
        )
        if value := os.getenv(env_var):
            return value
        raise ValueError(f"Secret '{secret_id}' not found in Secret Manager or environment")


def load_secrets_from_manager(
    project_id: str,
    secret_ids: list[str],
) -> dict[str, str]:
    """
    Load multiple secrets from Secret Manager.
    
    Args:
        project_id: GCP project ID
        secret_ids: List of secret identifiers
    
    Returns:
        Dictionary mapping secret_id to secret value
    """
    secrets = {}
    for secret_id in secret_ids:
        try:
            secrets[secret_id] = get_secret(secret_id, project_id)
        except ValueError as e:
            logger.error(f"Failed to load secret '{secret_id}': {e}")
            raise

    return secrets


def get_api_key(project_id: str) -> str:
    """Get API key from Secret Manager or environment."""
    # First check direct environment variable
    if api_key := os.getenv("ISPILOT_API_KEY"):
        return api_key

    # Try Secret Manager
    try:
        return get_secret("ispilot-api-key", project_id)
    except ValueError:
        logger.warning("No API key configured. API will require OAuth Bearer token")
        return ""
