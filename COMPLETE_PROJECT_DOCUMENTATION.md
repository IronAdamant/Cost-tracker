# Cost Tracker — project documentation

Updated: 2026-08-16  
Purpose: Inventory of the 1.0 rewrite so later changes can land in the right module instead of growing another catch-all file.

## Purpose

Desktop cost tracker (PySide6) with local multi-user login, monthly CSV sheets, running totals, and an optional monthly target.

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
| `cost_tracker/__main__.py` | QApplication, wires start → tracker windows | Process entry | Qt, paths, accounts, windows |
| `cost_tracker/constants.py` | App name, default categories, username rules | Shared literals | None |
| `cost_tracker/amount_parsing.py` | Decimal parse/format | Money helpers used by sheet, CSV, UI | decimal |
| `cost_tracker/app_paths.py` | XDG config + data directory | Avoids storing the folder path *inside* the folder | json, pathlib |
| `cost_tracker/user_account_store.py` | Create/verify users, monthly target | Auth + per-user settings in `users.json` | hashlib, json, amount_parsing |
| `cost_tracker/monthly_cost_sheet.py` | In-memory month grid and totals | Domain model with no Qt or disk | amount_parsing, calendar |
| `cost_tracker/csv_monthly_store.py` | Load/save monthly CSV, year/week/day totals | Persistence; overlay argument uses unsaved sheet | csv, monthly_cost_sheet |
| `cost_tracker/ui_theme.py` | Fusion stylesheet | Visual defaults for windows | None |
| `cost_tracker/create_user_dialog.py` | Username/password form | Isolated dialog | PySide6 |
| `cost_tracker/start_window.py` | Folder choice, create user, existing users | Fixes 0.11 login-button bugs | paths, accounts, create_user_dialog |
| `cost_tracker/tracker_window.py` | Table, month nav, summary, target | Main working screen | csv store, accounts, sheet |
| `tests/test_monthly_cost_sheet.py` | Amount parsing and grid totals | Domain tests without Qt | pytest |
| `tests/test_csv_monthly_store.py` | CSV round-trip and range totals | Persistence tests | pytest, tmp_path |
| `tests/test_accounts_and_paths.py` | Config + user JSON | Auth/path tests | pytest, tmp_path |
| `tests/test_qt_windows.py` | Start-button visibility and table save | Offscreen Qt smoke tests | PySide6 |

## Removed files (0.11)

| Path | Reason |
| --- | --- |
| `README` | Replaced by `README.md` |
| `Common.py` | Global path mutation and circular imports |
| `CostCell.py` | Duplicate table logic and unfinished handlers |
| `CSVManagement.py` | Append-based saves and conflicting filenames |
| `UserManagement.py` | Unsalted SHA-256, broken create-user signatures |

Git history still contains the 0.11 sources.

## Data files (not in git)

| Path | Purpose |
| --- | --- |
| `~/.config/cost-tracker/config.json` | Remembers `data_directory` |
| `<data_directory>/users.json` | Users, hashes, targets |
| `<data_directory>/costs_<user>_YYYY-MM.csv` | Month grid |

## New vs removed this revision

New: `cost_tracker/` package, tests, packaging, root markdown docs.  
Removed: the five 0.11 Python/README files listed above.
