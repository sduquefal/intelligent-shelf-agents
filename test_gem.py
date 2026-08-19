from google import genai
from google.genai import types as genai_types
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

credentials = Credentials(token=API_KEY)

client = genai.Client(
    vertexai=True,
    project=None,
    location=None,
    credentials=credentials,
    http_options=genai_types.HttpOptions(
        base_url=GATEWAY_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
    ),
)

response = client.models.generate_content(
    model=MODEL_NAME,
    contents="Hola"
)

print(response.text)

chat = client.chats.create(
    model=MODEL_NAME
)

r1 = chat.send_message(
    "Mi nombre es Sebastián. Recuérdalo."
)

print("Turno 1:")
print(r1.text)

r2 = chat.send_message(
    "¿Cómo me llamo?"
)

print("Turno 2:")
print(r2.text)