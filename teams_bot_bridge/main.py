"""
Teams Bridge for IsPilot - Microsoft 365 Agents SDK

This service bridges Microsoft Teams with the IsPilot API.
It validates Teams activities via Azure Bot Service and routes
messages to the ispilot-api with Google identity tokens.
"""

import json
import logging
import os
from typing import Any, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Teams Bridge for IsPilot",
    description="Bridge between Microsoft Teams and IsPilot API",
    version="1.0.0"
)

# Configuration
MICROSOFT_APP_ID = os.getenv("MICROSOFT_APP_ID", "")
MICROSOFT_APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD", "")
ISPILOT_API_ENDPOINT = os.getenv(
    "ISPILOT_API_ENDPOINT",
    "https://ispilot-api-46y2f3tyja-uc.a.run.app/chat"
)
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "corp-stro-salesinventory-prod")
TARGET_AUDIENCE = "https://ispilot-api-46y2f3tyja-uc.a.run.app"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


class IsPilotBridgeError(Exception):
    """Base exception for bridge errors."""
    pass


class AzureJWTValidator:
    """Validates JWT tokens from Azure Bot Service.
    
    This is a placeholder for Microsoft 365 Agents SDK JWT validation.
    The actual implementation will use the MS 365 SDK once it's available.
    """
    
    @staticmethod
    def validate_jwt(token: str) -> bool:
        """
        Validate JWT token from Azure Bot Service.
        
        Note: This is a simplified implementation.
        In production, use Microsoft 365 Agents SDK for full validation.
        """
        if not token:
            return False
        
        # TODO: Implement full JWT validation with MS 365 SDK
        # For now, we accept any Bearer token
        # This will be replaced with proper Azure AD validation
        logger.debug(f"Validating JWT token (implementation pending)")
        return True


class GoogleIdentityTokenProvider:
    """Generates Google identity tokens for service-to-service authentication."""
    
    @staticmethod
    def get_identity_token() -> str:
        """Get identity token for sa-tot-osa service account."""
        try:
            request = google_requests.Request()
            token = id_token.fetch_id_token(request, TARGET_AUDIENCE)
            logger.debug(f"Generated identity token for {TARGET_AUDIENCE}")
            return token
        except Exception as e:
            logger.error(f"Failed to generate identity token: {e}")
            raise IsPilotBridgeError(f"Cannot generate identity token: {str(e)}")


class IsPilotAPIClient:
    """Client for communicating with IsPilot API."""
    
    def __init__(self, endpoint: str):
        """Initialize client with API endpoint."""
        self.endpoint = endpoint
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def send_message(
        self,
        message: str,
        user_id: str,
        session_id: Optional[str] = None
    ) -> dict[str, Any]:
        """Send message to IsPilot API and get response."""
        try:
            token = GoogleIdentityTokenProvider.get_identity_token()
            
            payload = {
                "user_id": user_id,
                "message": message,
                "session_id": session_id,
            }
            
            logger.info(f"Sending message to IsPilot: user={user_id}, session={session_id}")
            
            response = await self.client.post(
                self.endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }
            )
            
            if response.status_code != 200:
                error_msg = response.text
                logger.error(f"IsPilot API error: {response.status_code} - {error_msg}")
                raise IsPilotBridgeError(f"IsPilot API returned {response.status_code}: {error_msg}")
            
            result = response.json()
            logger.info(f"Received response from IsPilot: {result.get('status', 'unknown')}")
            return result
            
        except IsPilotBridgeError:
            raise
        except Exception as e:
            logger.error(f"Error communicating with IsPilot API: {e}")
            raise IsPilotBridgeError(f"API communication error: {str(e)}")


class TeamsActivityParser:
    """Parses Teams activities and extracts relevant information."""
    
    @staticmethod
    def extract_message(activity: dict[str, Any]) -> str:
        """Extract message text from Teams activity."""
        if not isinstance(activity, dict):
            return ""
        
        # Try direct text field
        text = activity.get("text") or activity.get("message")
        if isinstance(text, str) and text.strip():
            return text.strip()
        
        # Try nested value
        value = activity.get("value")
        if isinstance(value, dict):
            nested_text = value.get("text") or value.get("message")
            if isinstance(nested_text, str) and nested_text.strip():
                return nested_text.strip()
        
        return ""
    
    @staticmethod
    def extract_user_id(activity: dict[str, Any]) -> str:
        """Extract user ID from Teams activity."""
        if not isinstance(activity, dict):
            return "teams-user"
        
        # Try from.id
        from_obj = activity.get("from") or {}
        if isinstance(from_obj, dict):
            # Try nested user.id
            user_obj = from_obj.get("user") or {}
            if isinstance(user_obj, dict):
                user_id = user_obj.get("id")
                if user_id:
                    return str(user_id)
            
            # Try direct id
            user_id = from_obj.get("id")
            if user_id:
                return str(user_id)
        
        # Try user_id directly
        if activity.get("user_id"):
            return str(activity["user_id"])
        
        return "teams-user"
    
    @staticmethod
    def extract_conversation_id(activity: dict[str, Any]) -> str:
        """Extract conversation ID from Teams activity."""
        if not isinstance(activity, dict):
            return ""
        
        conversation = activity.get("conversation") or {}
        if isinstance(conversation, dict):
            conv_id = conversation.get("id")
            if conv_id:
                return str(conv_id)
        
        return ""
    
    @staticmethod
    def extract_activity_id(activity: dict[str, Any]) -> str:
        """Extract activity ID from Teams activity."""
        if not isinstance(activity, dict):
            return ""
        
        activity_id = activity.get("id")
        if activity_id:
            return str(activity_id)
        
        return ""


# Initialize API client
ispilot_client = IsPilotAPIClient(ISPILOT_API_ENDPOINT)


# ============================================================================
# Endpoints
# ============================================================================


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/messages")
async def handle_activity(request: Request) -> dict[str, Any]:
    """
    Handle Teams activities from Azure Bot Service.
    
    This is the main endpoint that Azure Bot Service sends activities to.
    It validates the JWT from Azure, extracts the message, and routes to IsPilot API.
    
    Expected format: Azure Bot Service Activity JSON
    """
    try:
        # Parse request body
        activity = await request.json()
        logger.debug(f"Received activity: {json.dumps(activity, indent=2)}")
        
        # Validate JWT (placeholder - will use MS 365 SDK in production)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if not AzureJWTValidator.validate_jwt(token):
                logger.warning("JWT validation failed")
                raise HTTPException(status_code=401, detail="Invalid JWT")
        else:
            logger.warning("No Bearer token in Authorization header")
            # Allow for now - will enforce in production
        
        # Extract activity information
        activity_type = activity.get("type")
        
        # Only process message activities
        if activity_type != "message":
            logger.info(f"Ignoring non-message activity: {activity_type}")
            return {"status": "ignored", "reason": f"Activity type: {activity_type}"}
        
        # Extract message content
        message = TeamsActivityParser.extract_message(activity)
        if not message:
            logger.warning("No message text found in activity")
            raise HTTPException(status_code=400, detail="No message text found")
        
        # Extract user information
        user_id = TeamsActivityParser.extract_user_id(activity)
        conversation_id = TeamsActivityParser.extract_conversation_id(activity)
        activity_id = TeamsActivityParser.extract_activity_id(activity)
        
        logger.info(f"Processing message from {user_id} in {conversation_id}: '{message[:50]}...'")
        
        # Call IsPilot API
        # TODO: Implement session context persistence using conversation_id
        result = await ispilot_client.send_message(
            message=message,
            user_id=user_id,
            session_id=conversation_id  # Use conversation_id as session_id for now
        )
        
        # Return formatted response
        return {
            "status": "success",
            "reply": result.get("answer", "No answer returned"),
            "session_id": result.get("session_id"),
            "request_id": result.get("request_id"),
            "activity_id": activity_id,
        }
        
    except HTTPException:
        raise
    except IsPilotBridgeError as e:
        logger.error(f"Bridge error: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        raise HTTPException(status_code=400, detail="Request body must be valid JSON")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/activities")
async def handle_activity_alt(request: Request) -> dict[str, Any]:
    """Alternative endpoint for Activities (same as /api/messages)."""
    return await handle_activity(request)


# ============================================================================
# Application startup/shutdown
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Handle application startup."""
    logger.info("Teams Bridge starting up")
    logger.info(f"IsPilot API endpoint: {ISPILOT_API_ENDPOINT}")
    logger.info(f"GCP Project: {GOOGLE_CLOUD_PROJECT}")
    logger.info("Teams Bridge ready to accept activities from Azure Bot Service")


@app.on_event("shutdown")
async def shutdown_event():
    """Handle application shutdown."""
    logger.info("Teams Bridge shutting down")
    await ispilot_client.client.aclose()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Handle application startup."""
    logger.info("="*60)
    logger.info("Teams Bridge for IsPilot Starting")
    logger.info("="*60)
    logger.info(f"Microsoft App ID: {MICROSOFT_APP_ID[:10]}...")
    logger.info(f"IsPilot API: {ISPILOT_API_ENDPOINT}")
    logger.info(f"Google Project: {GOOGLE_CLOUD_PROJECT}")
    logger.info(f"Debug Mode: {DEBUG}")
    logger.info("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    """Handle application shutdown."""
    logger.info("Teams Bridge for IsPilot Shutting Down")
    await ispilot_client.client.aclose()


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )
