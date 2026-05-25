from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Drug Classification API"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    allowed_origins: list[str] = Field(default_factory=lambda: ["*"])

    max_file_size_mb: int = 10
    upload_field_name: str = "file"

    request_timeout_seconds: float = 8.0
    max_concurrent_rxnav_calls: int = 10

    rxnav_base_url: str = "https://rxnav.nlm.nih.gov/REST"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache

def get_settings() -> Settings:
    return Settings()
