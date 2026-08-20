import subprocess


def get_gateway_token() -> str:
    return subprocess.check_output(
        [
            "gcloud",
            "secrets",
            "versions",
            "access",
            "latest",
            "--secret=genai-gateway-jwt-prod",
            "--project=corp-stro-salesinventory-prod",
        ],
        text=True,
    ).strip()