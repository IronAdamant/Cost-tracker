from decimal import Decimal

from cost_tracker.app_paths import AppPaths
from cost_tracker.app_settings_store import AppSettingsStore


def test_app_paths_round_trip(tmp_path) -> None:
    config = tmp_path / "config.json"
    data_dir = tmp_path / "data"
    paths = AppPaths(data_dir, config)
    assert paths.is_configured is False
    paths.save()
    loaded = AppPaths.load(config)
    assert loaded.is_configured is True
    assert loaded.data_directory == data_dir


def test_monthly_target_persists_without_login(tmp_path) -> None:
    store = AppSettingsStore(tmp_path)
    assert store.monthly_target() is None
    store.set_monthly_target(Decimal("250.5"))
    assert store.monthly_target() == Decimal("250.50")
    reloaded = AppSettingsStore(tmp_path)
    assert reloaded.monthly_target() == Decimal("250.50")
    store.set_monthly_target(None)
    assert AppSettingsStore(tmp_path).monthly_target() is None
