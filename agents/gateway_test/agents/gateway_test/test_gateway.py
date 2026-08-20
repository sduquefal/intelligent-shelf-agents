# test_gateway.py

import litellm
import litellm

litellm._turn_on_debug()

from common.gateway_token import get_gateway_token

token = get_gateway_token()

response = litellm.completion(
    model="openai/gemini-3.5-flash",
    api_key=token,
    api_base=(
        "https://gateway.falabella.ai/"
        "tenant/ftc/scope/prod/"
        "google/models/chat/"
        "ftc-ispilot-gemini-35-flash-oai"
    ),
    messages=[
        {
            "role": "user",
            "content": "Respond only with HELLO"
        }
    ],
)

print(response)