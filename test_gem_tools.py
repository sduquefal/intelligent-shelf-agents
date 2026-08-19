from google import genai
from google.genai import types
from google.oauth2.credentials import Credentials

from common.gateway_token import get_gateway_token

from agents.shelf_analyst.tools import resolve_store as real_resolve_store

def resolve_store(query: str, country: str = "CL"):
    try:
        print("\n========== TOOL CALLED ==========")
        print("query =", query)
        print("country =", country)

        result = real_resolve_store(
            query=query,
            country=country,
        )

        print("\n========== RESULT ==========")
        print(result)

        return result

    except Exception as e:
        print("\n========== ERROR ==========")
        print("TYPE:", type(e))
        print("MESSAGE:", e)

        raise

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
    http_options=types.HttpOptions(
        base_url=GATEWAY_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
    ),
)

chat = client.chats.create(
    model=MODEL_NAME,
    config=types.GenerateContentConfig(
    tools=[resolve_store]   
    )
)

response = chat.send_message(
    """
    Use the resolve_store tool.

    Find the store called Talca Colin.

    Do not answer from your own knowledge.
    Use the tool.
    """
)

print(response.text)