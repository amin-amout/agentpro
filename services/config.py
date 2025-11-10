"""Configuration management for services."""
import os
from typing import Dict, Any
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_API_TYPE: str = "groq"
    LLM_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    LLM_API_KEY: str = ""
    DEFAULT_MODEL: str = "openai/gpt-oss-safeguard-20b"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    LOCAL_LLM_URL: str = "http://localhost:8000/v1/chat/completions"

    class Config:
        env_file = ".env"

settings = Settings()

def get_service_config(service_type: str) -> Dict[str, Any]:
    """Get configuration for a specific service."""
    # Base configuration from environment
    config = {
        "api_url": settings.LLM_API_URL,
        "api_key": settings.LLM_API_KEY,
        "model": settings.DEFAULT_MODEL,
    }
    
    # Check for service-specific config file
    config_dir = Path("config")
    config_file = config_dir / f"{service_type}_config.json"
    
    if config_file.exists():
        import json
        with open(config_file) as f:
            service_config = json.load(f)
            config.update(service_config)
    
    return config