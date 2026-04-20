from typing import ClassVar
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:admin@localhost/MovieDatabase"
    es_host: str = "http://localhost:9200"
    es_username: str = "elastic"
    es_password: str = "changeme"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
