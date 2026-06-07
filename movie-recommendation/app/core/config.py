import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv


def load_project_env():
    current_dir = Path(__file__).resolve().parent
    
    # Navigate to project root (2 levels up: app/core -> app -> movie-recommendation -> project root)
    project_root = current_dir.parent.parent.parent
    
    env_mode = os.getenv('ENV', 'dev') 
    env_file = project_root / f'.env.{env_mode}'
    
    if not env_file.exists():
        env_file = project_root / '.env'
    
    if env_file.exists():
        load_dotenv(env_file, override=True)
        print(f"[OK] Loaded environment from: {env_file}")
        return env_file
    else:
        print(f"[WARNING] No environment file found at: {env_file}")
        print(f"   Searched in: {project_root}")
        return None


load_project_env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8002, validation_alias="RECOMMENDATION_PORT")
    DEBUG: bool = Field(default=False)
    
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/postgres",
        validation_alias="DB_URL_PYTHON"
    )
    
    ES_HOST: str = Field(default="http://localhost:9200", validation_alias="ES_HOST")
    ES_USERNAME: Optional[str] = Field(default=None, validation_alias="ES_USERNAME")
    ES_PASSWORD: Optional[str] = Field(default=None, validation_alias="ES_PASSWORD")
    ES_URL: Optional[str] = Field(default=None, validation_alias="ES_URL")
    
    HF_TOKEN: Optional[str] = Field(default=None, validation_alias="HF_TOKEN")
    
    backend_service_url: str = Field(
        default="http://localhost:8080",
        validation_alias="BACKEND_URL"
    )
    chatbot_service_url: str = Field(
        default="http://localhost:8001",
        validation_alias="CHATBOT_URL"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def elasticsearch_config(self) -> dict:
        if self.ES_URL:
            return {"hosts": [self.ES_URL]}
        elif self.ES_USERNAME and self.ES_PASSWORD:
            return {
                "hosts": [self.ES_HOST],
                "basic_auth": (self.ES_USERNAME, self.ES_PASSWORD)
            }
        else:
            return {"hosts": [self.ES_HOST]}


settings = Settings()

if __name__ == "__main__":
    print("=" * 60)
    print("RECOMMENDATION SERVICE CONFIGURATION")
    print("=" * 60)
    print(f"Project Root: {BASE_DIR}")
    print(f"Model Directory: {get_model_dir()}")
    print(f"Cache Directory: {get_cache_dir()}")
    print(f"\nService Configuration:")
    print(f"  Host: {settings.HOST}")
    print(f"  Port: {settings.PORT}")
    print(f"  Debug: {settings.DEBUG}")
    print(f"\nDatabase:")
    print(f"  URL: {settings.database_url}")
    print(f"\nElasticsearch:")
    print(f"  Host: {settings.ES_HOST}")
    print(f"  URL: {settings.ES_URL or 'Not set'}")
    print(f"  Username: {settings.ES_USERNAME or 'Not set'}")
    print(f"\nService URLs:")
    print(f"  Backend: {settings.backend_service_url}")
    print(f"  Chatbot: {settings.chatbot_service_url}")
    print(f"\nAPI Keys:")
    print(f"  HF Token: {'Set' if settings.HF_TOKEN else 'Not set'}")
    print("=" * 60)
