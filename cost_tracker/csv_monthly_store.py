"""Load and save one CSV file per user per calendar month."""

from __future__ import annotations

import csv
import re
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from cost_tracker.amount_parsing import ZERO, format_amount_plain, parse_amount
from cost_tracker.constants import CSV_PREFIX, DEFAULT_CATEGORIES
from cost_tracker.monthly_cost_sheet import MonthlyCostSheet

MONTH_FILE_PATTERN = re.compile(rf"^{CSV_PREFIX}_(.+)_(\d{{4}})-(\d{{2}})$")


class CsvMonthlyStore:
    def __init__(self, data_directory: Path) -> None:
        self.data_directory = Path(data_directory)

    def path_for(self, username: str, year: int, month: int) -> Path:
        return self.data_directory / f"{CSV_PREFIX}_{username}_{year:04d}-{month:02d}.csv"

    def load(self, username: str, year: int, month: int) -> MonthlyCostSheet:
        path = self.path_for(username, year, month)
        if not path.is_file():
            return MonthlyCostSheet(year, month)
        with path.open("r", newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        if not rows:
            return MonthlyCostSheet(year, month)
        header, *body = rows
        day_columns = self._parse_day_columns(header[1:], year, month)
        sheet = MonthlyCostSheet(year, month, categories=[])
        for row in body:
            if not row or not row[0].strip():
                continue
            category = row[0].strip()
            if category.lower() == "total":
                continue
            sheet.register_category(category)
            for index, day in enumerate(day_columns):
                if day is None or index + 1 >= len(row):
                    continue
                cell = row[index + 1].strip()
                if cell:
                    sheet.set(category, day, parse_amount(cell))
        if not sheet.categories:
            return MonthlyCostSheet(year, month)
        sheet.ensure_categories(DEFAULT_CATEGORIES)
        return sheet

    def save(self, username: str, sheet: MonthlyCostSheet) -> Path:
        path = self.path_for(username, sheet.year, sheet.month)
        path.parent.mkdir(parents=True, exist_ok=True)
        days = sheet.days
        header = ["Category"] + [day.isoformat() for day in days]
        rows: list[list[str]] = [header]
        for category in sheet.categories:
            row = [category]
            for day in days:
                amount = sheet.get(category, day)
                row.append(format_amount_plain(amount, blank_if_zero=True))
            rows.append(row)
        temporary = path.with_suffix(".csv.tmp")
        with temporary.open("w", newline="", encoding="utf-8") as handle:
            csv.writer(handle).writerows(rows)
        temporary.replace(path)
        return path

    def available_months(self, username: str) -> list[tuple[int, int]]:
        months: list[tuple[int, int]] = []
        for path in self.data_directory.glob(f"{CSV_PREFIX}_{username}_*.csv"):
            match = MONTH_FILE_PATTERN.match(path.stem)
            if not match:
                continue
            if match.group(1) != username:
                continue
            months.append((int(match.group(2)), int(match.group(3))))
        return sorted(months)

    def year_total(
        self,
        username: str,
        year: int,
        overlay: MonthlyCostSheet | None = None,
    ) -> Decimal:
        total = ZERO
        months = self.available_months(username)
        used_overlay = False
        for file_year, month in months:
            if file_year != year:
                continue
            if overlay is not None and overlay.year == file_year and overlay.month == month:
                total += overlay.month_total()
                used_overlay = True
            else:
                total += self.load(username, file_year, month).month_total()
        if overlay is not None and overlay.year == year and not used_overlay:
            total += overlay.month_total()
        return total

    def range_total(
        self,
        username: str,
        start: date,
        end: date,
        overlay: MonthlyCostSheet | None = None,
    ) -> Decimal:
        if end < start:
            return ZERO
        total = ZERO
        cursor = date(start.year, start.month, 1)
        last = date(end.year, end.month, 1)
        while cursor <= last:
            if (
                overlay is not None
                and overlay.year == cursor.year
                and overlay.month == cursor.month
            ):
                sheet = overlay
            else:
                sheet = self.load(username, cursor.year, cursor.month)
            total += sheet.total_between(start, end)
            if cursor.month == 12:
                cursor = date(cursor.year + 1, 1, 1)
            else:
                cursor = date(cursor.year, cursor.month + 1, 1)
        return total

    def today_total(
        self,
        username: str,
        today: date | None = None,
        overlay: MonthlyCostSheet | None = None,
    ) -> Decimal:
        day = today or date.today()
        if overlay is not None and overlay.year == day.year and overlay.month == day.month:
            return overlay.day_total(day)
        return self.load(username, day.year, day.month).day_total(day)

    def week_total(
        self,
        username: str,
        today: date | None = None,
        overlay: MonthlyCostSheet | None = None,
    ) -> Decimal:
        day = today or date.today()
        start = day - timedelta(days=day.weekday())
        end = start + timedelta(days=6)
        return self.range_total(username, start, end, overlay=overlay)

    def _parse_day_columns(
        self,
        raw_headers: list[str],
        year: int,
        month: int,
    ) -> list[date | None]:
        parsed: list[date | None] = []
        for header in raw_headers:
            try:
                day = date.fromisoformat(header.strip())
            except ValueError:
                parsed.append(None)
                continue
            if day.year == year and day.month == month:
                parsed.append(day)
            else:
                parsed.append(None)
        return parsed
