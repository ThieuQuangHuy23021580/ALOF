from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    groq_api_key: str = Field(
        validation_alias="GROQ_API_KEY_1"
    )

    model_name: str = Field(
        default="openai/gpt-oss-120b",
        validation_alias="MODEL_NAME"
    )

    temperature: float = Field(
        default=0.3,
        validation_alias="TEMPERATURE"
    )

    max_output_tokens: int = Field(
        default=2048,
        validation_alias="MAX_OUTPUT_TOKENS"
    )

    history_limit: int = Field(
        default=6,
        validation_alias="HISTORY_LIMIT"
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()