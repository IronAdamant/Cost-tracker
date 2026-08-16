"""Local user accounts with salted PBKDF2 password hashes."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

from cost_tracker.amount_parsing import format_amount_plain, parse_amount
from cost_tracker.constants import PBKDF2_ITERATIONS, USERNAME_PATTERN, USERS_FILENAME


class UserAccountError(ValueError):
    """Raised when a username or password cannot be accepted."""


def hash_password(
    password: str,
    *,
    iterations: int = PBKDF2_ITERATIONS,
    salt: bytes | None = None,
) -> dict[str, Any]:
    if salt is None:
        salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return {
        "algorithm": "pbkdf2_sha256",
        "iterations": iterations,
        "salt_hex": salt.hex(),
        "hash_hex": derived.hex(),
    }


def verify_password(password: str, record: dict[str, Any]) -> bool:
    if record.get("algorithm") != "pbkdf2_sha256":
        return False
    salt = bytes.fromhex(record["salt_hex"])
    expected = bytes.fromhex(record["hash_hex"])
    actual = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        int(record["iterations"]),
    )
    return hmac.compare_digest(expected, actual)


class UserAccountStore:
    def __init__(
        self,
        data_directory: Path,
        *,
        pbkdf2_iterations: int = PBKDF2_ITERATIONS,
    ) -> None:
        self.data_directory = Path(data_directory)
        self.pbkdf2_iterations = pbkdf2_iterations
        self.path = self.data_directory / USERS_FILENAME
        self._payload: dict[str, Any] = {"users": {}}
        self.reload()

    def reload(self) -> None:
        if self.path.is_file():
            self._payload = json.loads(self.path.read_text(encoding="utf-8"))
            self._payload.setdefault("users", {})
        else:
            self._payload = {"users": {}}

    def save(self) -> None:
        self.data_directory.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._payload, indent=2) + "\n", encoding="utf-8")

    @property
    def usernames(self) -> list[str]:
        return sorted(self._payload["users"].keys())

    def has_users(self) -> bool:
        return bool(self._payload["users"])

    def create_user(self, username: str, password: str) -> None:
        name = username.strip()
        if not re.fullmatch(USERNAME_PATTERN, name):
            raise UserAccountError(
                "Username must be 1-32 characters using letters, numbers, or underscore."
            )
        if name in self._payload["users"]:
            raise UserAccountError(f"User {name!r} already exists.")
        password_record = None
        if password != "":
            password_record = hash_password(password, iterations=self.pbkdf2_iterations)
        self._payload["users"][name] = {
            "password": password_record,
            "monthly_target": None,
        }
        self.save()

    def requires_password(self, username: str) -> bool:
        return self._user(username)["password"] is not None

    def verify(self, username: str, password: str) -> bool:
        record = self._user(username)["password"]
        if record is None:
            return True
        return verify_password(password, record)

    def monthly_target(self, username: str) -> Decimal | None:
        raw = self._user(username).get("monthly_target")
        if raw is None or raw == "":
            return None
        return parse_amount(str(raw))

    def set_monthly_target(self, username: str, amount: Decimal | None) -> None:
        user = self._user(username)
        user["monthly_target"] = None if amount is None else format_amount_plain(amount)
        self.save()

    def _user(self, username: str) -> dict[str, Any]:
        try:
            return self._payload["users"][username]
        except KeyError as exc:
            raise UserAccountError(f"Unknown user {username!r}.") from exc
