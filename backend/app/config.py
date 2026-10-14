import re

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from environment variables (or ../.env in development)."""
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
    database_url: str = "postgresql://mind:mind@localhost:5432/mindevidence"
    app_env: str = "development"            # session endpoints only work in "development" until auth exists
    frontend_origin: str = "http://localhost:5500"
    session_secret: str = "change-me"       # reserved for Batch 04
    google_client_id: str = ""
    google_client_secret: str = ""
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    @property
    def sqlalchemy_url(self) -> str:
        return re.sub(r"^postgresql(\+\w+)?://", "postgresql+psycopg://", self.database_url)


settings = Settings()
