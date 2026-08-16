"""Backward-compatible launcher for `python main.py`."""

from cost_tracker.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
