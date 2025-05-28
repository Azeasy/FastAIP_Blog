from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ENV: str = "DEV"
    TEST_DATABASE_URL: str | None = None
    POSTGRES_PORT: str = "5432"
    POSTGRES_HOST: str = "localhost"

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_CACHE_EXPIRE: int = 300  # 300 seconds = 5 minutes

    model_config = ConfigDict(
        env_file=".env",
        extra="allow"
    )


settings = Settings()
