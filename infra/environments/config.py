from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class AppConfig(BaseSettings):
    """
    Base configuration model for the Assistant API.
    Values can be overridden by environment variables (e.g., ENVIRONMENT=prod).
    """

    environment: Literal["dev", "staging", "prod"] = "dev"

    # Database Settings
    postgres_uri: str = "postgresql://admin:password@localhost:5432/assistant_db"

    # Object Storage (MinIO/S3) Settings
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "admin"
    s3_secret_key: str = "password123"
    s3_bucket: str = "mf-evidence"

    # Redis Settings
    redis_url: str = "redis://localhost:6379/0"

    # Model Settings
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"  # Can be pointed to Groq or generic OpenAI endpoint

    @property
    def policy_version(self) -> str:
        import datetime

        return f"{datetime.date.today().strftime('%Y-%m-%d')}.1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Global config instance
config = AppConfig()
