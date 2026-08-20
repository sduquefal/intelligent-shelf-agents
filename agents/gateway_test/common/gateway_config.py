# common/gateway_config.py

import litellm

from common.gateway_token import (
    get_gateway_token,
)

litellm.api_key = get_gateway_token()

litellm.api_base = (
    "https://gateway.falabella.ai/"
    "tenant/ftc/scope/prod/"
    "google/models/chat/"
    "ftc-ispilot-gemini-35-flash-oai"
)