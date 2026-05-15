from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # These must be supplied via environment variables or a .env file.
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"
    DOWNLOAD_DIR: str = "/data/audio"

    class Config:
        env_file = ".env"


settings = Settings()
