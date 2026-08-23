from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"

    database_url: str = "sqlite:///./weblog.db"
    secret_key: str
    algorithm: str = "HS256"

    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from_email: str = "no-reply@weblog.local"
    app_base_url: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
