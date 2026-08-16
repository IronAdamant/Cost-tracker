"""In-memory month grid: categories as rows, calendar days as columns."""

from __future__ import annotations

from calendar import monthrange
from datetime import date
from decimal import Decimal

from cost_tracker.amount_parsing import ZERO, parse_amount
from cost_tracker.constants import DEFAULT_CATEGORIES


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    index = year * 12 + (month - 1) + delta
    return index // 12, index % 12 + 1


def month_start(year: int, month: int) -> date:
    return date(year, month, 1)


class MonthlyCostSheet:
    def __init__(
        self,
        year: int,
        month: int,
        categories: list[str] | None = None,
    ) -> None:
        if not 1 <= month <= 12:
            raise ValueError(f"Invalid month: {month}")
        self.year = year
        self.month = month
        names = list(DEFAULT_CATEGORIES) if categories is None else list(categories)
        self.categories: list[str] = []
        self._amounts: dict[str, dict[date, Decimal]] = {}
        for name in names:
            self.register_category(name)

    @property
    def days(self) -> list[date]:
        _, last_day = monthrange(self.year, self.month)
        return [date(self.year, self.month, day) for day in range(1, last_day + 1)]

    def get(self, category: str, day: date) -> Decimal:
        return self._amounts.get(category, {}).get(day, ZERO)

    def set(self, category: str, day: date, value: Decimal | str) -> Decimal:
        if category not in self._amounts:
            raise KeyError(f"Unknown category {category!r}")
        if day.year != self.year or day.month != self.month:
            raise ValueError("Date is outside this sheet's month")
        amount = value if isinstance(value, Decimal) else parse_amount(str(value))
        if amount == ZERO:
            self._amounts[category].pop(day, None)
        else:
            self._amounts[category][day] = amount
        return amount

    def register_category(self, name: str) -> str:
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("Category name is empty")
        if cleaned in self._amounts:
            return cleaned
        self.categories.append(cleaned)
        self._amounts[cleaned] = {}
        return cleaned

    def add_category(self, name: str) -> str:
        cleaned = name.strip()
        if cleaned in self._amounts:
            raise ValueError(f"Category {cleaned!r} already exists")
        return self.register_category(cleaned)

    def ensure_categories(self, names: list[str] | tuple[str, ...]) -> None:
        for name in names:
            self.register_category(name)

    def day_total(self, day: date) -> Decimal:
        return sum((self.get(category, day) for category in self.categories), ZERO)

    def month_total(self) -> Decimal:
        return sum((self.day_total(day) for day in self.days), ZERO)

    def total_between(self, start: date, end: date) -> Decimal:
        total = ZERO
        for day in self.days:
            if start <= day <= end:
                total += self.day_total(day)
        return total
