"""CASA configuration — loads from .env file."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CASA"
    bank_name: str = "Community First Bank"
    log_level: str = "INFO"
    api_host: str = "http://localhost:8000"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_default_model: str = "claude-sonnet-4-20250514"
    llm_fast_model: str = "claude-haiku-4-5-20251001"

    database_url: str = "sqlite:///./casa.db"
    upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
os.makedirs(settings.upload_dir, exist_ok=True)
