from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Training Center API'
    database_url: str = 'sqlite:///training.db'
    database_echo: bool = False  # true = print every SQL statement
    # Generate a real one:  python -c "import secrets; print(secrets.token_urlsafe(48))"
    jwt_secret_key: str = Field(default='dev-only-secret-change-me-0123456789abcdef', min_length=32)
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = Field(default=30, gt=0)
    max_page_size: int = Field(default=50, gt=0, le=500)


@lru_cache
def get_settings() -> Settings:
    return Settings()
