from typing import ClassVar
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:admin@localhost/MovieDatabase"
    # self.model_dir = Path(__file__).resolve().parent.parent.parent / "model-store" check
    model_base : ClassVar[Path] = Path(__file__).parent.parent.parent / "model-store" / "recommendation_models"
    
    class Config:
        env_file = ".env"
        