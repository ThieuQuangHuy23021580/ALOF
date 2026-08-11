from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(
        default="Adaptive Learning Multi-Agent API",
        validation_alias="APP_NAME",
    )

    app_version: str = Field(
        default="1.0.0",
        validation_alias="APP_VERSION",
    )

    debug: bool = Field(
        default=True,
        validation_alias="DEBUG",
    )

    host: str = Field(
        default="127.0.0.1",
        validation_alias="HOST",
    )

    port: int = Field(
        default=8000,
        validation_alias="PORT",
    )

    database_url: str = Field(
        validation_alias="DATABASE_URL",
    )

    allowed_origins: str = Field(
        default="*",
        validation_alias="ALLOWED_ORIGINS",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()