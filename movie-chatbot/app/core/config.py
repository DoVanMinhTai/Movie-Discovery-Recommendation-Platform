import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    chatbot_port: int = Field(default=8001, validation_alias="CHATBOT_PORT")
    host: str = Field(default="0.0.0.0")
    debug: bool = Field(default=False)
    
    hf_token: str = Field(default="", validation_alias="HF_TOKEN")
    groq_api_key: str = Field(default="", validation_alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama3-70b-8192", validation_alias="GROQ_MODEL")
    groq_project_id: Optional[str] = Field(default=None, validation_alias="GROQ_PROJECT_ID")
    
    es_host: str = Field(default="http://localhost:9200", validation_alias="ES_HOST")
    es_username: Optional[str] = Field(default=None, validation_alias="ES_USERNAME")
    es_password: Optional[str] = Field(default=None, validation_alias="ES_PASSWORD")
    es_url: Optional[str] = Field(default=None, validation_alias="ES_URL")
    
    recommendation_service_url: str = Field(
        default="http://localhost:8002", 
        validation_alias="RECO_URL"
    )
    backend_service_url: str = Field(
        default="http://localhost:8080",
        validation_alias="BACKEND_URL"
    )
    
    embed_model_name: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        validation_alias="EMBED_MODEL_NAME"
    )
    repo_id: str = Field(
        default="hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF",
        validation_alias="REPO_ID"
    )
    llm_model_name: str = Field(
        default="llama-3.2-3b-instruct-q4_k_m.gguf",
        validation_alias="LLM_MODEL_NAME"
    )
    
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def elasticsearch_config(self) -> dict:
        """Get Elasticsearch configuration as dict"""
        if self.es_url:
            return {"hosts": [self.es_url]}
        elif self.es_username and self.es_password:
            return {
                "hosts": [self.es_host],
                "basic_auth": (self.es_username, self.es_password)
            }
        else:
            return {"hosts": [self.es_host]}
    
    def get_groq_config(self) -> dict:
        """Get Groq API configuration"""
        config = {
            "api_key": self.groq_api_key,
            "model": self.groq_model
        }
        if self.groq_project_id:
            config["project_id"] = self.groq_project_id
        return config


settings = Settings()

if __name__ == "__main__":
    print("=" * 60)
    print("CHATBOT SERVICE CONFIGURATION")
    print("=" * 60)
    print(f"Project Root: {BASE_DIR}")
    print(f"Model Directory: {get_model_dir()}")
    print(f"Cache Directory: {get_cache_dir()}")
    print(f"\nService Configuration:")
    print(f"  Port: {settings.chatbot_port}")
    print(f"  Host: {settings.host}")
    print(f"\nElasticsearch:")
    print(f"  Host: {settings.es_host}")
    print(f"  URL: {settings.es_url or 'Not set'}")
    print(f"\nService URLs:")
    print(f"  Recommendation: {settings.recommendation_service_url}")
    print(f"  Backend: {settings.backend_service_url}")
    print(f"\nAPI Keys:")
    print(f"  HF Token: {'Set' if settings.hf_token else 'Not set'}")
    print(f"  Groq API Key: {'Set' if settings.groq_api_key else 'Not set'}")
    print(f"  Groq Model: {settings.groq_model}")
    print(f"\nModel Configuration:")
    print(f"  Embed Model: {settings.embed_model_name}")
    print(f"  LLM Model: {settings.llm_model_name}")
    print(f"  Repo ID: {settings.repo_id}")
    print("=" * 60)
