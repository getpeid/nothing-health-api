from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "Nothing Health API"
    debug: bool = False
    api_version: str = "v1"

    # Database
    database_url: str = "postgresql+asyncpg://localhost:5432/nothing_health"

    # OAuth
    oauth_secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 90

    # Rate limits
    rate_limit_per_minute: int = 100
    rate_limit_per_day: int = 10_000

    # CORS
    allowed_origins: list[str] = ["*"]

    model_config = {"env_file": ".env", "env_prefix": "NOTHING_"}


settings = Settings()
