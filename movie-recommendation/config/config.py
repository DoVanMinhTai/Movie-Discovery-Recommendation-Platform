from typing import ClassVar
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:admin@localhost/MovieDatabase"
    model_base : ClassVar[Path] = Path(__file__).parent / "model-store" / "recommendation_models"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )
        