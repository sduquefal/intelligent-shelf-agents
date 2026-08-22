from google.cloud import secretmanager
import os


def get_gateway_token() -> str:
    return os.environ["AI_GW_API_KEY"]

# def get_gateway_token() -> str:
#     client = secretmanager.SecretManagerServiceClient()

    # name = (
    #     "projects/"
    #     "corp-stro-salesinventory-prod/"
    #     "secrets/"
    #     "genai-gateway-jwt-prod/"
    #     "versions/latest"
    # )

    # response = client.access_secret_version(
    #     request={"name": name}
    # )

    # return response.payload.data.decode()