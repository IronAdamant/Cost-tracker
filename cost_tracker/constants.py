"""Shared names and default categories for the cost tracker."""

APP_NAME = "Cost Tracker"
APP_VERSION = "1.0.0"
CONFIG_DIRNAME = "cost-tracker"
DEFAULT_DATA_PARENT = "Cost Tracker"
DEFAULT_DATA_FOLDER = "Cost Tracking Data"
USERS_FILENAME = "users.json"
CSV_PREFIX = "costs"
DEFAULT_CATEGORIES = (
    "Food",
    "Fuel",
    "Bills",
    "Investments",
    "Miscellaneous",
)
USERNAME_PATTERN = r"^[A-Za-z0-9_]{1,32}$"
PBKDF2_ITERATIONS = 200_000
