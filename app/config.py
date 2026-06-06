from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Application
    DATABASE_URL: str
    REDIS_URL: str
    DOWNLOAD_DIR: str = Field(
        "/data/audio", description="Root directory for downloaded audio files"
    )


settings = Settings()
