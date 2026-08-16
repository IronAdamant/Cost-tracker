from decimal import Decimal

import pytest

from cost_tracker.app_paths import AppPaths
from cost_tracker.user_account_store import UserAccountError, UserAccountStore


def test_app_paths_round_trip(tmp_path) -> None:
    config = tmp_path / "config.json"
    data_dir = tmp_path / "data"
    paths = AppPaths(data_dir, config)
    assert paths.is_configured is False
    paths.save()
    loaded = AppPaths.load(config)
    assert loaded.is_configured is True
    assert loaded.data_directory == data_dir


def test_user_create_verify_and_target(tmp_path) -> None:
    store = UserAccountStore(tmp_path, pbkdf2_iterations=1_000)
    store.create_user("sam", "secret")
    store.create_user("open_account", "")
    assert store.has_users()
    assert store.usernames == ["open_account", "sam"]
    assert store.requires_password("sam") is True
    assert store.verify("sam", "secret") is True
    assert store.verify("sam", "nope") is False
    assert store.requires_password("open_account") is False
    assert store.verify("open_account", "") is True
    store.set_monthly_target("sam", Decimal("250.5"))
    assert store.monthly_target("sam") == Decimal("250.50")
    reloaded = UserAccountStore(tmp_path, pbkdf2_iterations=1_000)
    assert reloaded.verify("sam", "secret") is True
    assert reloaded.monthly_target("sam") == Decimal("250.50")


def test_invalid_or_duplicate_usernames(tmp_path) -> None:
    store = UserAccountStore(tmp_path, pbkdf2_iterations=1_000)
    with pytest.raises(UserAccountError):
        store.create_user("bad name", "x")
    store.create_user("sam", "x")
    with pytest.raises(UserAccountError):
        store.create_user("sam", "y")
