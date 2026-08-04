import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./blog.db",
    )

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "",
    )

    ALGORITHM: str = os.getenv(
        "ALGORITHM",
        "HS256",
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "60",
        )
    )

    ADMIN_USERNAME: str = os.getenv(
        "ADMIN_USERNAME",
        "admin",
    )

    ADMIN_EMAIL: str = os.getenv(
        "ADMIN_EMAIL",
        "admin@example.com",
    )

    ADMIN_PASSWORD: str = os.getenv(
        "ADMIN_PASSWORD",
        "Admin123!",
    )

    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://127.0.0.1:5500,http://localhost:5500,"
            "http://127.0.0.1:3000,http://localhost:3000",
        ).split(",")
        if origin.strip()
    ]


settings = Settings()

if not settings.SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set. Add a SECRET_KEY value to your "
        ".env file before starting the API — without it, JWTs "
        "would be signed with an empty key."
    )