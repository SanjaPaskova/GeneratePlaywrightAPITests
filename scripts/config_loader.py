import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from config.json.

    Returns a dict with keys like:
    - swagger_url
    - api_key
    - llm_provider
    - model
    - fallback_to_schema
    """
    cfg_path = path or CONFIG_PATH
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found at {cfg_path}")

    with open(cfg_path, "r") as f:
        return json.load(f)


def get_swagger_url(path: Optional[Path] = None) -> str:
    """Convenience accessor for the Swagger/OpenAPI URL."""
    cfg = load_config(path)
    url = cfg.get("swagger_url")
    if not url:
        raise KeyError("'swagger_url' not set in config.json")
    return url


# Centralized, typed configuration for the app
@dataclass
class AppConfig:
    swagger_url: str
    llm_provider: str = "none"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    model: str = "gpt-4o"
    fallback_to_schema: bool = True
    use_ai_for_tests: bool = False


def load_app_config(path: Optional[Path] = None) -> AppConfig:
    """Load configuration and return a typed AppConfig instance with safe defaults."""
    raw = load_config(path)
    if not raw.get("swagger_url"):
        raise KeyError("'swagger_url' not set in config.json")

    return AppConfig(
        swagger_url=raw.get("swagger_url"),
        llm_provider=raw.get("llm_provider", "none"),
        openai_api_key=raw.get("openai_api_key"),
        anthropic_api_key=raw.get("anthropic_api_key"),
        model=raw.get("model", "gpt-4o"),
        fallback_to_schema=raw.get("fallback_to_schema", True),
        use_ai_for_tests=raw.get("use_ai_for_tests", False),
    )
