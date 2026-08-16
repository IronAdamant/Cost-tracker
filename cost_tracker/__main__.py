"""Launch the Cost Tracker desktop app."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from cost_tracker.app_paths import AppPaths
from cost_tracker.constants import APP_NAME
from cost_tracker.csv_monthly_store import CsvMonthlyStore
from cost_tracker.start_window import StartWindow
from cost_tracker.tracker_window import TrackerWindow
from cost_tracker.ui_theme import APP_STYLESHEET
from cost_tracker.user_account_store import UserAccountStore


def main(argv: list[str] | None = None) -> int:
    qt_app = QApplication(argv if argv is not None else sys.argv)
    qt_app.setApplicationName(APP_NAME)
    qt_app.setStyle("Fusion")
    qt_app.setStyleSheet(APP_STYLESHEET)

    paths = AppPaths.load()
    accounts = UserAccountStore(paths.data_directory)
    start = StartWindow(paths, accounts)
    open_windows: list[TrackerWindow] = []

    def open_tracker(username: str) -> None:
        current_paths = start.paths
        current_accounts = UserAccountStore(current_paths.data_directory)
        store = CsvMonthlyStore(current_paths.data_directory)
        window = TrackerWindow(username, current_accounts, store)
        window.logged_out.connect(start.show)
        window.show()
        start.hide()
        open_windows.append(window)

    start.user_authenticated.connect(open_tracker)
    start.show()
    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
