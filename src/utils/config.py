import yaml
from pathlib import Path

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_configs() -> dict:
    base = Path("configs")
    return {
        "pipeline": load_yaml(str(base / "pipeline.yaml")),
        "sources": load_yaml(str(base / "sources.yaml")),
        "models": load_yaml(str(base / "models.yaml")),
        "scoring": load_yaml(str(base / "scoring.yaml")),
        "signals": load_yaml(str(base / "signals.yaml")),
    }
