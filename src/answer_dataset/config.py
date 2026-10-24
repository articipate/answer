"""Application configuration."""

import json
from pathlib import Path
from typing import Any, Dict

from platformdirs import user_config_dir, user_data_dir

APP_NAME = "Answer"
ORG_NAME = "Articipate"

CONFIG_DIR = Path(user_config_dir(APP_NAME, ORG_NAME))
DATA_DIR = Path(user_data_dir(APP_NAME, ORG_NAME))
CACHE_DIR = DATA_DIR / "cache"
CHECKPOINT_DIR = DATA_DIR / "checkpoints"

for d in [CONFIG_DIR, DATA_DIR, CACHE_DIR, CHECKPOINT_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class Config:
    def __init__(self):
        self.config_file = CONFIG_DIR / "config.json"
        self.data: Dict[str, Any] = self._load()
    
    def _load(self) -> Dict[str, Any]:
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}
    
    def save(self):
        self.config_file.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        self.data[key] = value
        self.save()


config = Config()
