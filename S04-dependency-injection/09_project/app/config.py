"""Settings read from the environment / the .env file."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Training Center API'
    # Temporary protection for write operations. Session 10 replaces it with JWT.
    admin_api_key: str = Field(default='dev-admin-key', min_length=8)
    max_page_size: int = Field(default=50, gt=0, le=500)


@lru_cache
def get_settings() -> Settings:
    return Settings()
