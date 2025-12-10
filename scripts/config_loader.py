import json
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
