"""Local settings only. This test project does not use login or passwords."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from cost_tracker.amount_parsing import format_amount_plain, parse_amount
from cost_tracker.constants import SETTINGS_FILENAME


class AppSettingsStore:
    def __init__(self, data_directory: Path) -> None:
        self.data_directory = Path(data_directory)
        self.path = self.data_directory / SETTINGS_FILENAME
        self._payload: dict[str, Any] = {"monthly_target": None}
        self.reload()

    def reload(self) -> None:
        if self.path.is_file():
            self._payload = json.loads(self.path.read_text(encoding="utf-8"))
            self._payload.setdefault("monthly_target", None)
        else:
            self._payload = {"monthly_target": None}

    def save(self) -> None:
        self.data_directory.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._payload, indent=2) + "\n", encoding="utf-8")

    def monthly_target(self) -> Decimal | None:
        raw = self._payload.get("monthly_target")
        if raw is None or raw == "":
            return None
        return parse_amount(str(raw))

    def set_monthly_target(self, amount: Decimal | None) -> None:
        self._payload["monthly_target"] = None if amount is None else format_amount_plain(amount)
        self.save()
