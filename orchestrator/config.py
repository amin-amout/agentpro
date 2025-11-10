import os
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # No hard-coded endpoints or models here; read from environment or config files.
    LLM_API_TYPE: Optional[str] = None
    LLM_API_URL: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    DEFAULT_MODEL: Optional[str] = None
    TEMPERATURE: Optional[float] = None
    MAX_TOKENS: Optional[int] = None
    LOCAL_LLM_URL: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()


def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration based on settings. Raises if required values are missing."""
    cfg: Dict[str, Any] = {}
    # Choose provider
    provider = settings.LLM_API_TYPE or "groq"
    if provider == "groq":
        if not settings.LLM_API_URL or not settings.DEFAULT_MODEL or not settings.LLM_API_KEY:
            raise ValueError("Missing required LLM configuration for Groq: LLM_API_URL, DEFAULT_MODEL, LLM_API_KEY")
        cfg.update({
            "api_url": settings.LLM_API_URL,
            "api_key": settings.LLM_API_KEY,
            "model": settings.DEFAULT_MODEL,
        })
    else:
        if not settings.LOCAL_LLM_URL or not settings.DEFAULT_MODEL:
            raise ValueError("Missing required local LLM configuration: LOCAL_LLM_URL, DEFAULT_MODEL")
        cfg.update({
            "api_url": settings.LOCAL_LLM_URL,
            "model": settings.DEFAULT_MODEL,
        })

    if settings.TEMPERATURE is not None:
        cfg["temperature"] = settings.TEMPERATURE
    if settings.MAX_TOKENS is not None:
        cfg["max_tokens"] = settings.MAX_TOKENS

    return cfg