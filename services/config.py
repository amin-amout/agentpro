"""Configuration management for services."""
import os
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Do NOT hard-code endpoint URLs or default models here. Read from environment
    # or per-service config files. Values can be None; the caller must validate.
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


def get_service_config(service_type: str) -> Dict[str, Any]:
    """Get configuration for a specific service.

    Behavior:
    - Load base values from environment via pydantic settings.
    - If a service-specific JSON config exists under `config/`, load and override.
    - Validate that required keys exist (api_url, api_key, model) and raise otherwise.
    """
    config: Dict[str, Any] = {}

    # Use environment / settings values when present
    if settings.LLM_API_URL:
        config["api_url"] = settings.LLM_API_URL
    if settings.LLM_API_KEY:
        config["api_key"] = settings.LLM_API_KEY
    if settings.DEFAULT_MODEL:
        config["model"] = settings.DEFAULT_MODEL
    if settings.TEMPERATURE is not None:
        config["temperature"] = settings.TEMPERATURE
    if settings.MAX_TOKENS is not None:
        config["max_tokens"] = settings.MAX_TOKENS

    # Load service-specific file overrides
    config_dir = Path("config")
    config_file = config_dir / f"{service_type}_config.json"
    if config_file.exists():
        import json
        with open(config_file) as f:
            service_config = json.load(f)
            config.update(service_config)

    # Validate required keys
    missing = [k for k in ("api_url", "api_key", "model") if k not in config or not config[k]]
    if missing:
        raise ValueError(f"Missing required LLM configuration: {', '.join(missing)}")

    return config