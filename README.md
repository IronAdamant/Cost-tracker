# Cost Tracker

Local desktop app for tracking daily spending in an Excel-like table. Data stays on your computer as CSV files. Multiple local users are supported; only one person should use the app at a time.

This is version **1.0.0**, a rewrite of the 0.11 pre-release. The older modules mixed UI, CSV paths, and login state across circular imports, so setup, headers, and saves were unreliable. This revision keeps the same product and replaces the internals.

## Features

- Monthly grid: categories as rows, days of the month as columns
- Daily totals in the table, plus today / this week / this month / this year in the summary bar
- Previous and next month (next month stops at the current month)
- Optional monthly target with remaining / over amount
- Local users with optional passwords (salted PBKDF2, not plain SHA-256)
- One CSV file per user per month, rewritten in full on save (no duplicate appends)
- Data folder remembered in `~/.config/cost-tracker/config.json`, so setup is not asked again on every launch

## Run

Python 3.11+ and a desktop session (Qt) are required.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m cost_tracker
```

`python main.py` still works as a launcher.

## Tests

```bash
pytest
```

GUI tests use Qt’s offscreen platform. They skip if PySide6 cannot load (for example when `libEGL` is missing).

## Data layout

After you choose a folder (default `~/Cost Tracker/Cost Tracking Data`):

- `users.json` — usernames, password hashes, monthly targets
- `costs_<user>_YYYY-MM.csv` — one month grid

CSV header row:

```text
Category,2026-08-01,2026-08-02,...
Food,12.50,
Fuel,,
```

Version 0.11 files used several overlapping names and are **not** imported automatically. Copy any values you still need into the new grid, or keep the old files as a backup.

## What 0.11 left unfinished

Those items are implemented here: previous-month navigation, automatic sums, and a monthly target. Login buttons now depend on whether accounts exist, and the data folder is stored outside the data folder so the app can find it next time.
