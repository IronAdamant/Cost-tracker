"""Excel-like monthly cost table with running totals and a monthly target."""

from datetime import date
from decimal import Decimal

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from cost_tracker.amount_parsing import ZERO, format_amount, format_amount_plain, parse_amount
from cost_tracker.constants import APP_NAME
from cost_tracker.csv_monthly_store import CsvMonthlyStore
from cost_tracker.monthly_cost_sheet import month_start, shift_month
from cost_tracker.user_account_store import UserAccountStore

MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


class TrackerWindow(QMainWindow):
    logged_out = Signal()

    def __init__(
        self,
        username: str,
        accounts: UserAccountStore,
        store: CsvMonthlyStore,
        today: date | None = None,
    ) -> None:
        super().__init__()
        self.username = username
        self.accounts = accounts
        self.store = store
        self.today = today or date.today()
        self.sheet = store.load(username, self.today.year, self.today.month)

        self.setWindowTitle(f"{APP_NAME} — {username}")
        self.resize(1100, 620)
        self._build_ui()
        self._reload_table()
        self._refresh_summary()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.addLayout(self._header_row())
        self.table = QTableWidget()
        self.table.cellChanged.connect(self._on_cell_changed)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        layout.addWidget(self.table)
        layout.addLayout(self._table_actions())
        layout.addWidget(self._summary_card())
        self.setCentralWidget(root)

    def _header_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        welcome = QLabel(f"Welcome back, {self.username}")
        welcome.setObjectName("title")
        self.month_label = QLabel()
        self.month_label.setObjectName("monthTitle")
        self.prev_button = QPushButton("Previous month")
        self.next_button = QPushButton("Next month")
        self.prev_button.clicked.connect(lambda: self._shift_month(-1))
        self.next_button.clicked.connect(lambda: self._shift_month(1))
        logout = QPushButton("Log out")
        logout.clicked.connect(self._logout)
        row.addWidget(welcome)
        row.addStretch()
        row.addWidget(self.prev_button)
        row.addWidget(self.month_label)
        row.addWidget(self.next_button)
        row.addWidget(logout)
        return row

    def _table_actions(self) -> QHBoxLayout:
        row = QHBoxLayout()
        add_category = QPushButton("Add category")
        add_category.clicked.connect(self._add_category)
        set_target = QPushButton("Set monthly target")
        set_target.clicked.connect(self._set_target)
        row.addWidget(add_category)
        row.addWidget(set_target)
        row.addStretch()
        self.status_label = QLabel("")
        self.status_label.setObjectName("subtitle")
        row.addWidget(self.status_label)
        return row

    def _summary_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("summaryCard")
        grid = QHBoxLayout(card)
        self.today_label = QLabel()
        self.week_label = QLabel()
        self.month_total_label = QLabel()
        self.year_label = QLabel()
        self.target_label = QLabel()
        for widget in (
            self.today_label,
            self.week_label,
            self.month_total_label,
            self.year_label,
            self.target_label,
        ):
            widget.setWordWrap(True)
            grid.addWidget(widget)
        return card

    def _reload_table(self) -> None:
        self.table.blockSignals(True)
        days = self.sheet.days
        categories = self.sheet.categories
        self.table.clear()
        self.table.setColumnCount(len(days))
        self.table.setRowCount(len(categories) + 1)
        self.table.setHorizontalHeaderLabels([str(day.day) for day in days])
        self.table.setVerticalHeaderLabels([*categories, "Total"])
        for column, day in enumerate(days):
            header = self.table.horizontalHeaderItem(column)
            if header is not None:
                header.setToolTip(day.isoformat())
        for row, category in enumerate(categories):
            for column, day in enumerate(days):
                amount = self.sheet.get(category, day)
                item = QTableWidgetItem(format_amount_plain(amount, blank_if_zero=True))
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                self.table.setItem(row, column, item)
        self._write_totals_row()
        self.table.blockSignals(False)
        self.month_label.setText(f"{MONTH_NAMES[self.sheet.month - 1]} {self.sheet.year}")
        current_month = month_start(self.today.year, self.today.month)
        viewing = month_start(self.sheet.year, self.sheet.month)
        self.next_button.setEnabled(viewing < current_month)

    def _write_totals_row(self) -> None:
        total_row = len(self.sheet.categories)
        for column, day in enumerate(self.sheet.days):
            item = QTableWidgetItem(format_amount_plain(self.sheet.day_total(day)))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(total_row, column, item)

    def _on_cell_changed(self, row: int, column: int) -> None:
        if row >= len(self.sheet.categories):
            return
        item = self.table.item(row, column)
        text = item.text() if item else ""
        category = self.sheet.categories[row]
        day = self.sheet.days[column]
        try:
            amount = parse_amount(text)
        except ValueError:
            self.table.blockSignals(True)
            previous = self.sheet.get(category, day)
            if item is not None:
                item.setText(format_amount_plain(previous, blank_if_zero=True))
            self.table.blockSignals(False)
            QMessageBox.warning(self, "Invalid amount", "Enter a non-negative number.")
            return
        self.sheet.set(category, day, amount)
        self.table.blockSignals(True)
        if item is not None:
            item.setText(format_amount_plain(amount, blank_if_zero=True))
        self._write_totals_row()
        self.table.blockSignals(False)
        self._save_now()
        self._refresh_summary()

    def _shift_month(self, delta: int) -> None:
        self._save_now()
        year, month = shift_month(self.sheet.year, self.sheet.month, delta)
        current = month_start(self.today.year, self.today.month)
        if month_start(year, month) > current:
            return
        self.sheet = self.store.load(self.username, year, month)
        self._reload_table()
        self._refresh_summary()

    def _add_category(self) -> None:
        name, accepted = QInputDialog.getText(self, "Add category", "Category name:")
        if not accepted:
            return
        try:
            self.sheet.add_category(name)
        except ValueError as exc:
            QMessageBox.warning(self, "Could not add category", str(exc))
            return
        self._reload_table()
        self._save_now()
        self._refresh_summary()

    def _set_target(self) -> None:
        current = self.accounts.monthly_target(self.username)
        default = "" if current is None else format_amount_plain(current)
        text, accepted = QInputDialog.getText(
            self,
            "Monthly target",
            "Target amount for a month (blank to clear):",
            text=default,
        )
        if not accepted:
            return
        try:
            amount = None if text.strip() == "" else parse_amount(text)
        except ValueError:
            QMessageBox.warning(self, "Invalid amount", "Enter a non-negative number.")
            return
        self.accounts.set_monthly_target(self.username, amount)
        self._refresh_summary()

    def _refresh_summary(self) -> None:
        today_total = self.store.today_total(self.username, self.today, overlay=self.sheet)
        week_total = self.store.week_total(self.username, self.today, overlay=self.sheet)
        month_total = self.sheet.month_total()
        year_total = self.store.year_total(self.username, self.sheet.year, overlay=self.sheet)
        target = self.accounts.monthly_target(self.username)
        self.today_label.setText(f"Today\n{format_amount(today_total)}")
        self.week_label.setText(f"This week\n{format_amount(week_total)}")
        self.month_total_label.setText(
            f"{MONTH_NAMES[self.sheet.month - 1]} total\n{format_amount(month_total)}"
        )
        self.year_label.setText(f"{self.sheet.year} total\n{format_amount(year_total)}")
        self.target_label.setText(self._target_text(month_total, target))

    def _target_text(self, month_total: Decimal, target: Decimal | None) -> str:
        if target is None:
            return "Monthly target\nNot set"
        remaining = target - month_total
        if remaining >= ZERO:
            return (
                f"Target {format_amount(target)}\n"
                f"{format_amount(remaining)} remaining"
            )
        return (
            f"Target {format_amount(target)}\n"
            f"{format_amount(abs(remaining))} over"
        )

    def _save_now(self) -> None:
        self.store.save(self.username, self.sheet)
        self.status_label.setText("Saved")

    def _logout(self) -> None:
        self._save_now()
        self.logged_out.emit()
        self.close()

    def closeEvent(self, event) -> None:  # noqa: N802
        self._save_now()
        event.accept()
