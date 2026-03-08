import os
import json
from pathlib import Path
from typing import Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from dotenv import load_dotenv

current_file = Path(__file__).resolve()
env_path = None
for parent in current_file.parents:
    check_path = parent / ".env"
    if check_path.exists():
        env_path = check_path
        break

if env_path:
    load_dotenv(env_path)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    hf_token: str = Field(default="", validation_alias="HF_TOKEN")

    model_path_raw: str = Field(default="model-store/chatbot_models", validation_alias="MODEL_PATH")
    
    es_host: str = Field(default="http://localhost:9200", validation_alias="ES_HOST")
    recommendation_service_url: str = Field(default="http://localhost:8080")
    embed_model_name: str = Field(default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", validation_alias="EMBED_MODEL_NAME")

    repo_id: str = Field(default="hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF")
    llm_model_name: str = Field(default="llama-3.2-3b-instruct-q4_k_m.gguf", validation_alias="LLM_MODEL_NAME")

    intent_anchors: Dict[str, List[str]] = Field(default_factory=dict)
    genre_map: Dict[str, str] = Field(default_factory=dict)

    @property
    def model_path(self) -> str:
        p = Path(self.model_path_raw)
        if not p.is_absolute():
            full_path = (BASE_DIR / p).resolve()
        else:
            full_path = p.resolve()
        
        if not full_path.exists():
            print(f"Warning: Model folder not found at {full_path}")
        return str(full_path)

    @field_validator("intent_anchors", "genre_map", mode="before")
    @classmethod
    def parse_json_strings(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v

    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

if __name__ == "__main__":
    print(f"Project Root: {BASE_DIR}")
    print(f"Final Model Path: {settings.model_path}")