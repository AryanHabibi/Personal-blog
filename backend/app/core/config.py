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


settings = Settings()