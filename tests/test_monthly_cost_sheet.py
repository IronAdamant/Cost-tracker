from datetime import date
from decimal import Decimal

import pytest

from cost_tracker.amount_parsing import format_amount, format_amount_plain, parse_amount
from cost_tracker.monthly_cost_sheet import MonthlyCostSheet, shift_month


def test_parse_amount_accepts_blank_and_currency_noise() -> None:
    assert parse_amount("") == Decimal("0.00")
    assert parse_amount("  $12.5 ") == Decimal("12.50")
    assert parse_amount("1,234.5") == Decimal("1234.50")


def test_parse_amount_rejects_invalid_and_negative() -> None:
    with pytest.raises(ValueError):
        parse_amount("nope")
    with pytest.raises(ValueError):
        parse_amount("-1")


def test_format_amount_variants() -> None:
    assert format_amount(Decimal("12.5")) == "12.50"
    assert format_amount(Decimal("0"), blank_if_zero=True) == ""
    assert format_amount_plain(Decimal("12.5")) == "12.50"


def test_shift_month_wraps_year() -> None:
    assert shift_month(2026, 1, -1) == (2025, 12)
    assert shift_month(2026, 12, 1) == (2027, 1)


def test_sheet_totals_and_custom_category() -> None:
    sheet = MonthlyCostSheet(2026, 8)
    food_day = date(2026, 8, 16)
    sheet.set("Food", food_day, "10.25")
    sheet.set("Fuel", date(2026, 8, 17), "20")
    sheet.add_category("Pets")
    sheet.set("Pets", food_day, "3.75")
    assert sheet.day_total(food_day) == Decimal("14.00")
    assert sheet.month_total() == Decimal("34.00")
    assert sheet.total_between(date(2026, 8, 16), date(2026, 8, 16)) == Decimal("14.00")


def test_sheet_rejects_dates_outside_month() -> None:
    sheet = MonthlyCostSheet(2026, 8)
    with pytest.raises(ValueError):
        sheet.set("Food", date(2026, 7, 31), "1")
