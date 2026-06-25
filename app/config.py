from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    groq_api_key: str
    github_app_id: str
    github_private_key: str
    github_webhook_secret: str

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()