"""CASA configuration — India MSME Secured Loan LOS."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CASA"
    bank_name: str = "CASA Finance India"
    country: str = "India"
    currency: str = "INR"
    currency_symbol: str = "₹"
    log_level: str = "INFO"
    api_host: str = "http://localhost:8000"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_default_model: str = "claude-sonnet-4-6"
    llm_fast_model: str = "claude-haiku-4-5-20251001"

    database_url: str = "sqlite:///./casa.db"
    upload_dir: str = "./uploads"

    # India-specific thresholds
    ltv_max_pct: float = 60.0          # Max LTV for secured MSME loans
    dscr_min: float = 1.25             # Minimum DSCR for approval
    cibil_min_score: int = 650         # Minimum CIBIL score
    max_loan_amount: float = 100_000_000  # ₹10 Cr max loan
    msme_turnover_limit: float = 250_000_000  # ₹25 Cr MSME classification

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
os.makedirs(settings.upload_dir, exist_ok=True)
