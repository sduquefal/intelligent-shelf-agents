from __future__ import annotations

import os


class AuthService:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("ISPILOT_API_KEY")
        if not self.api_key:
            raise ValueError("ISPILOT_API_KEY is required")

    def validate(self, provided_key: str) -> bool:
        if provided_key != self.api_key:
            raise ValueError("Invalid API key")
        return True
