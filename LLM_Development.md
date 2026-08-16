# Cost Tracker — development log

## Project overview

Local PySide6 cost tracker. Version 1.0 rewrites the 0.11 pre-release: same product (Excel-like table, CSV, local users, passwords), new package layout, tests, and the features that were still listed as pending.

## Active context

- Focus: 1.0 rewrite landed on `cursor/modernize-cost-tracker-b21d`.
- Decision: remember the data folder in XDG config, not in a JSON file inside the data folder (that was why 0.11 kept re-running setup).
- Decision: one CSV per user per month, full rewrite on save; categories as rows, ISO dates as columns.
- Decision: PBKDF2-SHA256 with salt; optional blank password; do not delete accounts after failed logins.
- Blockers: none for the rewrite. Old 0.11 CSV/JSON files are not auto-migrated.

## Session log

- 2026-08-16: [REWRITE] Replaced Common/CostCell/CSVManagement/UserManagement/main with the `cost_tracker` package. Implemented previous-month navigation, daily/weekly/monthly/yearly sums, monthly target, login-button states, and pytest coverage (domain + offscreen Qt).

## Rules

- Keep domain logic (sheet, CSV, accounts, paths) importable without Qt so tests stay headless except for window smoke tests.
- Do not store the chosen data directory only inside that directory.
- Prefer rewriting a month CSV over appending rows.
