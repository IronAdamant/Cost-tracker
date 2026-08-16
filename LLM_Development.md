# Cost Tracker — development log

## Project overview

Local PySide6 cost tracker. Version 1.0 rewrites the 0.11 pre-release. This is a **test project with no login**.

## Active context

- Focus: 1.0 rewrite on `cursor/modernize-cost-tracker-b21d`, merging to `main`.
- Decision: remember the data folder in XDG config, not inside the data folder.
- Decision: one CSV per month (`costs_local_YYYY-MM.csv`), full rewrite on save.
- Decision: **no usernames, passwords, or account prompts.** Monthly target lives in `settings.json`.
- Blockers: none. Old 0.11 CSV/JSON files are not auto-migrated.

## Session log

- 2026-08-16: [REWRITE] Replaced Common/CostCell/CSVManagement/UserManagement with the `cost_tracker` package. Implemented previous-month navigation, sums, and monthly target.
- 2026-08-16: [AUTH] Removed login, password hashing, and user selection. App opens the grid directly.

## Rules

- Keep domain logic (sheet, CSV, settings, paths) importable without Qt.
- Do not add login or credential storage.
- Do not store the chosen data directory only inside that directory.
- Prefer rewriting a month CSV over appending rows.
