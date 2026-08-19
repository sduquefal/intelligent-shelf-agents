import common.gateway_config

from google.adk.models.lite_llm import LiteLlm


def get_default_model():
    return LiteLlm(
        model="openai/gemini-3.5-flash"
    )