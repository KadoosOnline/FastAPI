from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Training Center API'
    database_url: str = 'sqlite+aiosqlite:///training.db'
    database_echo: bool = False  # true = print every SQL statement
    # Generate a real one:  python -c "import secrets; print(secrets.token_urlsafe(48))"
    jwt_secret_key: str = Field(default='dev-only-secret-change-me-0123456789abcdef', min_length=32)
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = Field(default=30, gt=0)
    max_page_size: int = Field(default=50, gt=0, le=500)

    # session 11
    upload_dir: Path = Path('uploads')
    max_upload_mb: int = Field(default=10, gt=0, le=100)
    # "a,b,c" in .env -> ['a', 'b', 'c']  (NoDecode: do not parse it as JSON)
    cors_origins: Annotated[list[str], NoDecode] = ['http://localhost:5500']

    @field_validator('cors_origins', mode='before')
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(',') if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
