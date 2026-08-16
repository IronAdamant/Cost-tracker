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
from cost_tracker.csv_monthly_store import CsvMonthlyStore
from cost_tracker.start_window import StartWindow
from cost_tracker.tracker_window import TrackerWindow
from cost_tracker.user_account_store import UserAccountStore


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_existing_users_button_only_after_accounts_exist(qapp, tmp_path) -> None:
    paths = AppPaths(tmp_path / "data", tmp_path / "config.json")
    accounts = UserAccountStore(paths.data_directory, pbkdf2_iterations=1_000)
    window = StartWindow(paths, accounts)
    assert window.existing_button.isHidden() is True
    assert window.create_button.text() == "Create user"
    accounts.create_user("sam", "secret")
    window.accounts = accounts
    window._refresh_home()
    assert window.existing_button.isHidden() is False
    assert window.create_button.text() == "Create another user"
    window.close()


def test_tracker_edit_writes_csv(qapp, tmp_path) -> None:
    accounts = UserAccountStore(tmp_path, pbkdf2_iterations=1_000)
    accounts.create_user("sam", "secret")
    store = CsvMonthlyStore(tmp_path)
    window = TrackerWindow("sam", accounts, store, today=date(2026, 8, 16))
    food_row = window.sheet.categories.index("Food")
    day_column = 15  # 16 August
    window.table.item(food_row, day_column).setText("11.25")
    saved = store.load("sam", 2026, 8)
    assert saved.get("Food", date(2026, 8, 16)) == Decimal("11.25")
    assert "11.25" in window.today_label.text()
    window.close()
