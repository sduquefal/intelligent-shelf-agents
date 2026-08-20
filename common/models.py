from common.gateway_gemini import GatewayGemini

def get_default_model():
    return GatewayGemini(
        model="ftc-ispilot-gemini-35-flash-gem"
    )