"""
config.py
---------
Single source of truth for paths, seeds, features, and model parameters.
Loads from config.yaml at project root.
"""
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def load_config() -> dict:
    """Load YAML config and resolve relative paths against project root."""
    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)

    # Resolve paths
    cfg["paths"]["raw_data"] = PROJECT_ROOT / cfg["paths"]["raw_data"]
    cfg["paths"]["outputs"] = PROJECT_ROOT / cfg["paths"]["outputs"]
    cfg["paths"]["outputs"].mkdir(parents=True, exist_ok=True)

    return cfg


CONFIG = load_config()
