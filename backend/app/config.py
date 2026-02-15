from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str

    # OIDC
    oidc_issuer_url: str = ""
    oidc_audience: str = ""

    # Currency
    base_currency: str = "USD"
    frankfurter_base_url: str = "https://api.frankfurter.app"

    # Scheduler
    scheduler_timezone: str = "UTC"

    # Local auth
    local_auth_enabled: bool = False
    local_auth_secret: str = ""

    # CORS — comma-separated list of allowed origins
    # Default allows the Vite dev server and common local ports
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # App
    app_name: str = "Budget Tracker"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
