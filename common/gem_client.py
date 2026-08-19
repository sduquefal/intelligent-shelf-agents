from google import genai
from google.genai import types
from google.oauth2.credentials import Credentials

from common.gateway_token import get_gateway_token

API_KEY = get_gateway_token()

GATEWAY_URL = (
    "https://gateway.falabella.ai/"
    "tenant/ftc/scope/prod/"
    "google/models/chat/"
    "ftc-ispilot-gemini-35-flash-gem"
)

MODEL_NAME = "ftc-ispilot-gemini-35-flash-gem"

client = genai.Client(
    vertexai=True,
    project=None,
    location=None,
    credentials=Credentials(token=API_KEY),
    http_options=types.HttpOptions(
        base_url=GATEWAY_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
    ),
)