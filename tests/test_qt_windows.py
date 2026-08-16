import os
from datetime import date
from decimal import Decimal

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtWidgets import QApplication
except ImportError as exc:
    pytest.skip(f"PySide6 Qt widgets unavailable: {exc}", allow_module_level=True)

from cost_tracker.app_paths import AppPaths
from cost_tracker.app_settings_store import AppSettingsStore
from cost_tracker.csv_monthly_store import CsvMonthlyStore
from cost_tracker.tracker_window import TrackerWindow


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_tracker_edit_writes_csv(qapp, tmp_path) -> None:
    paths = AppPaths(tmp_path, tmp_path / "config.json")
    settings = AppSettingsStore(tmp_path)
    store = CsvMonthlyStore(tmp_path)
    window = TrackerWindow(paths, settings, store, today=date(2026, 8, 16), sheet_id="local")
    food_row = window.sheet.categories.index("Food")
    day_column = 15  # 16 August
    window.table.item(food_row, day_column).setText("11.25")
    saved = store.load("local", 2026, 8)
    assert saved.get("Food", date(2026, 8, 16)) == Decimal("11.25")
    assert "11.25" in window.today_label.text()
    window.close()
