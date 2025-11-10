import os
from typing import Dict, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_API_TYPE: str = "groq"
    LLM_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    LLM_API_KEY: str = ""
    DEFAULT_MODEL: str = "openai/gpt-oss-safeguard-20b"  # Updated to use an available model
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    LOCAL_LLM_URL: str = "http://localhost:8000/v1/chat/completions"

    class Config:
        env_file = ".env"

settings = Settings()

def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration based on settings."""
    if settings.LLM_API_TYPE == "groq":
        return {
            "api_url": settings.LLM_API_URL,
            "api_key": settings.LLM_API_KEY,
            "model": settings.DEFAULT_MODEL,
        }
    else:
        return {
            "api_url": settings.LOCAL_LLM_URL,
            "model": settings.DEFAULT_MODEL,
        }