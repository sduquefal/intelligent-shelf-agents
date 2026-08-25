from functools import cached_property

from google.adk.models.google_llm import Gemini
from google.genai import Client
from google.genai import types
from google.oauth2.credentials import Credentials

from common.gateway_token import get_gateway_token


class GatewayGemini(Gemini):

    @cached_property
    def api_client(self) -> Client:
        api_key = get_gateway_token()

        gateway_url = (
            "https://gateway.falabella.ai/"
            "tenant/ftc/scope/prod/"
            "google/models/chat/"
            "ftc-ispilot-gemini-35-flash-gem"
        )

        return Client(
            vertexai=True,
            project=None,
            location=None,
            credentials=Credentials(token=api_key),
            http_options=types.HttpOptions(
                base_url=gateway_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
            ),
        )