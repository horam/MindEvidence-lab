from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
    database_url: str = "postgresql+psycopg://mind:mind@localhost:5432/mindevidence"
    session_secret: str = "change-me"
    google_client_id: str = ""
    google_client_secret: str = ""
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    frontend_origin: str = "http://localhost:5500"


settings = Settings()
