import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./blog.db",
    )


settings = Settings()