from google.cloud import secretmanager


def get_gateway_token():

    client = secretmanager.SecretManagerServiceClient()

    name = (
        "projects/"
        "corp-stro-salesinventory-prod/"
        "secrets/"
        "genai-gateway-jwt-prod/"
        "versions/latest"
    )

    response = client.access_secret_version(
        request={"name": name}
    )

    return response.payload.data.decode()