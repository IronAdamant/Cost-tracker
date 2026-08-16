from datetime import date
from decimal import Decimal

from cost_tracker.constants import DEFAULT_CATEGORIES
from cost_tracker.csv_monthly_store import CsvMonthlyStore
from cost_tracker.monthly_cost_sheet import MonthlyCostSheet


def test_csv_round_trip_keeps_categories_and_amounts(tmp_path) -> None:
    store = CsvMonthlyStore(tmp_path)
    sheet = MonthlyCostSheet(2026, 8)
    sheet.set("Food", date(2026, 8, 16), "12.50")
    sheet.add_category("Pets")
    sheet.set("Pets", date(2026, 8, 1), "4")
    store.save("sam", sheet)

    loaded = store.load("sam", 2026, 8)
    assert loaded.get("Food", date(2026, 8, 16)) == Decimal("12.50")
    assert loaded.get("Pets", date(2026, 8, 1)) == Decimal("4.00")
    for category in DEFAULT_CATEGORIES:
        assert category in loaded.categories


def test_year_and_week_totals_span_months(tmp_path) -> None:
    store = CsvMonthlyStore(tmp_path)
    july = MonthlyCostSheet(2026, 7)
    august = MonthlyCostSheet(2026, 8)
    july.set("Food", date(2026, 7, 31), "10")
    august.set("Food", date(2026, 8, 1), "5")
    august.set("Fuel", date(2026, 8, 16), "20")
    store.save("sam", july)
    store.save("sam", august)

    assert store.year_total("sam", 2026) == Decimal("35.00")
    january = MonthlyCostSheet(2026, 1)
    february = MonthlyCostSheet(2026, 2)
    january.set("Food", date(2026, 1, 31), "10")
    february.set("Food", date(2026, 2, 1), "5")
    store.save("sam", january)
    store.save("sam", february)
    # 1 Feb 2026 is a Sunday; that week starts Monday 26 Jan.
    assert store.week_total("sam", date(2026, 2, 1)) == Decimal("15.00")


def test_overlay_sheet_is_used_before_disk_save(tmp_path) -> None:
    store = CsvMonthlyStore(tmp_path)
    disk = MonthlyCostSheet(2026, 8)
    disk.set("Food", date(2026, 8, 16), "1")
    store.save("sam", disk)

    overlay = store.load("sam", 2026, 8)
    overlay.set("Food", date(2026, 8, 16), "9")
    assert store.today_total("sam", date(2026, 8, 16), overlay=overlay) == Decimal("9.00")
    assert store.year_total("sam", 2026, overlay=overlay) == Decimal("9.00")


def test_missing_month_file_returns_empty_defaults(tmp_path) -> None:
    store = CsvMonthlyStore(tmp_path)
    sheet = store.load("sam", 2026, 1)
    assert sheet.month_total() == Decimal("0.00")
    assert sheet.categories == list(DEFAULT_CATEGORIES)
