"""Resolve the XDG config file and the user-chosen data directory."""

from __future__ import annotations

import json
from pathlib import Path

from cost_tracker.constants import (
    CONFIG_DIRNAME,
    DEFAULT_DATA_FOLDER,
    DEFAULT_DATA_PARENT,
)


def default_config_path() -> Path:
    return Path.home() / ".config" / CONFIG_DIRNAME / "config.json"


def default_data_directory() -> Path:
    return Path.home() / DEFAULT_DATA_PARENT / DEFAULT_DATA_FOLDER


class AppPaths:
    """Keeps the data-folder choice outside the data folder itself."""

    def __init__(self, data_directory: Path, config_path: Path | None = None) -> None:
        self.data_directory = Path(data_directory)
        self.config_path = Path(config_path) if config_path else default_config_path()

    @classmethod
    def load(cls, config_path: Path | None = None) -> AppPaths:
        path = Path(config_path) if config_path else default_config_path()
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
            data_directory = Path(payload["data_directory"])
            return cls(data_directory, path)
        return cls(default_data_directory(), path)

    @property
    def is_configured(self) -> bool:
        return self.config_path.is_file()

    def save(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        payload = {"data_directory": str(self.data_directory)}
        self.config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
