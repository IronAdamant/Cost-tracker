"""Launch the Cost Tracker desktop app with no login."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from cost_tracker.app_paths import AppPaths
from cost_tracker.app_settings_store import AppSettingsStore
from cost_tracker.constants import APP_NAME
from cost_tracker.csv_monthly_store import CsvMonthlyStore
from cost_tracker.tracker_window import TrackerWindow
from cost_tracker.ui_theme import APP_STYLESHEET


def main(argv: list[str] | None = None) -> int:
    qt_app = QApplication(argv if argv is not None else sys.argv)
    qt_app.setApplicationName(APP_NAME)
    qt_app.setStyle("Fusion")
    qt_app.setStyleSheet(APP_STYLESHEET)

    paths = AppPaths.load()
    if not paths.is_configured:
        paths.save()
    settings = AppSettingsStore(paths.data_directory)
    store = CsvMonthlyStore(paths.data_directory)
    window = TrackerWindow(paths, settings, store)
    window.show()
    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
