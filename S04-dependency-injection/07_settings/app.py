"""Settings from environment variables with pydantic-settings.

A secret key, a database URL, the list of allowed origins... must not be
written in the code. They come from the ENVIRONMENT (or a `.env` file that is
never committed to Git).

    class Settings(BaseSettings):
        app_name: str = 'Training Center API'
        debug: bool = False

`Settings()` reads APP_NAME and DEBUG from the environment, converts them to
the right types, and fails loudly at start-up if a required value is missing.

`@lru_cache` makes `get_settings()` build the object only once; as a
dependency it can be replaced in tests (session 13).

    copy .env.example .env         (Windows)
    cp .env.example .env           (Linux / macOS)
    python app.py
"""

from functools import lru_cache
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    app_name: str = 'Training Center API'
    debug: bool = False
    admin_email: str = 'admin@kadoos.ir'
    max_page_size: int = Field(default=50, gt=0, le=500)
    secret_key: str = Field(min_length=16)  # required: no default


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
app = FastAPI()


@app.get('/info')
def info(settings: SettingsDep) -> dict:
    # Never return the secret itself!
    return {
        'app_name': settings.app_name,
        'debug': settings.debug,
        'max_page_size': settings.max_page_size,
        'secret_key_length': len(settings.secret_key),
    }


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
