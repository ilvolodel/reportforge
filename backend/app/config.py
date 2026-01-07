"""Application configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql://reportforge:reportforge_password@localhost:5432/reportforge"
    
    # Authentication
    secret_key: str = "your-secret-key-change-in-production"
    magic_link_expiry_minutes: int = 15
    session_expiry_days: int = 30
    
    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = "noreply@example.com"
    smtp_password: str = ""
    smtp_from: str = "ReportForge <noreply@example.com>"
    
    # Application
    app_name: str = "ReportForge"
    app_url: str = "http://localhost:8000"
    debug: bool = False
    environment: str = "development"
    
    # PDF
    pdf_logo_path: str = "/app/frontend/static/assets/logo-infocert.png"
    pdf_brand_color: str = "#0066CC"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
