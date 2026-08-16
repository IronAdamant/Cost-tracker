# Cost Tracker — project documentation

Updated: 2026-08-16  
Purpose: Inventory of the 1.0 rewrite. This is a test project with **no login**.

## Purpose

Desktop cost tracker (PySide6) with monthly CSV sheets, running totals, and an optional monthly target. It does not create users, store passwords, or prompt for credentials.

## All files

| Path | Purpose | Justification | Dependencies / data flow |
| --- | --- | --- | --- |
| `README.md` | How to run, test, and where files live | Root overview | None |
| `LLM_Development.md` | Session log and active decisions | Root history log | None |
| `COMPLETE_PROJECT_DOCUMENTATION.md` | This inventory | Root file map | None |
| `pyproject.toml` | Package metadata, dependencies, pytest config | Install and test entry | setuptools |
| `requirements.txt` | Runtime pin helper for `pip install -r` | Same dependency as pyproject | PySide6 |
| `.gitignore` | Ignore bytecode, venvs, build artifacts | Keep the repo source-only | None |
| `main.py` | `python main.py` launcher | Compatibility with the old start command | `cost_tracker.__main__` |
| `cost_tracker/__init__.py` | Package version | Importable package | None |
| `cost_tracker/__main__.py` | QApplication, opens the tracker with no login | Process entry | Qt, paths, settings, tracker |
| `cost_tracker/constants.py` | App name, default categories, sheet id | Shared literals | None |
| `cost_tracker/amount_parsing.py` | Decimal parse/format | Money helpers used by sheet, CSV, UI | decimal |
| `cost_tracker/app_paths.py` | XDG config + data directory | Avoids storing the folder path *inside* the folder | json, pathlib |
| `cost_tracker/app_settings_store.py` | Monthly target in `settings.json` | Local settings without accounts | json, amount_parsing |
| `cost_tracker/monthly_cost_sheet.py` | In-memory month grid and totals | Domain model with no Qt or disk | amount_parsing, calendar |
| `cost_tracker/csv_monthly_store.py` | Load/save monthly CSV, year/week/day totals | Persistence; overlay argument uses unsaved sheet | csv, monthly_cost_sheet |
| `cost_tracker/ui_theme.py` | Fusion stylesheet | Visual defaults for windows | None |
| `cost_tracker/tracker_window.py` | Table, month nav, summary, target, folder picker | Only window; no login | csv store, settings, sheet |
| `tests/test_monthly_cost_sheet.py` | Amount parsing and grid totals | Domain tests without Qt | pytest |
| `tests/test_csv_monthly_store.py` | CSV round-trip and range totals | Persistence tests | pytest, tmp_path |
| `tests/test_settings_and_paths.py` | Config + settings JSON | Path/settings tests | pytest, tmp_path |
| `tests/test_qt_windows.py` | Table save smoke test | Offscreen Qt; skipped without libEGL | PySide6 |

## Removed files (0.11 and login layer)

| Path | Reason |
| --- | --- |
| `README` | Replaced by `README.md` |
| `Common.py` | Global path mutation and circular imports |
| `CostCell.py` | Duplicate table logic and unfinished handlers |
| `CSVManagement.py` | Append-based saves and conflicting filenames |
| `UserManagement.py` | Unsalted SHA-256 login |
| `cost_tracker/user_account_store.py` | Test project does not use login |
| `cost_tracker/create_user_dialog.py` | No credentials |
| `cost_tracker/start_window.py` | No user selection |

## Data files (not in git)

| Path | Purpose |
| --- | --- |
| `~/.config/cost-tracker/config.json` | Remembers `data_directory` |
| `<data_directory>/settings.json` | Monthly target |
| `<data_directory>/costs_local_YYYY-MM.csv` | Month grid |

## New vs removed this revision

New: `cost_tracker/` package, tests, packaging, root markdown docs.  
Removed: 0.11 modules plus the 1.0 login/password UI.
