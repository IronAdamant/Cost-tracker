# Cost Tracker

Test-project desktop app for tracking daily spending in an Excel-like table. Data stays on disk as CSV files.

**This is a test project. There is no login.** Do not enter usernames, passwords, or real account credentials. The app opens the cost grid directly.

This is version **1.0.0**, a rewrite of the 0.11 pre-release.

## Features

- Opens straight to the monthly grid (categories as rows, days as columns)
- Daily totals in the table, plus today / this week / this month / this year
- Previous and next month (next month stops at the current month)
- Optional monthly target with remaining / over amount
- One CSV file per month, rewritten in full on save
- Data folder remembered in `~/.config/cost-tracker/config.json`

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

Default folder: `~/Cost Tracker/Cost Tracking Data`

- `settings.json` — monthly target only (no accounts)
- `costs_local_YYYY-MM.csv` — one month grid

CSV header row:

```text
Category,2026-08-01,2026-08-02,...
Food,12.50,
Fuel,,
```

Version 0.11 files are **not** imported automatically.
