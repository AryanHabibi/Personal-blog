from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env lives next to this file: api/app/.env
ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")

    # Database. Postgres by default; override with sqlite:///./app.db for a
    # zero-setup local fallback.
    database_url: str = "postgresql+psycopg://weblog:weblog@localhost:5432/weblog"

    # Single admin account (no DB row) - credentials come from .env
    admin_username: str
    admin_password: str

    # JWT
    jwt_secret: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Email verification
    app_base_url: str = "http://localhost:8000"
    email_backend: str = "console"  # "console" logs the link | "smtp" sends it
    email_from: str = "no-reply@weblog.local"
    verification_token_ttl_hours: int = 24
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_tls: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
