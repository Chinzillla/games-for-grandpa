from __future__ import annotations

from games_for_grandpa.core import Difficulty, Settings
from games_for_grandpa.persistence import JsonDataStore


def test_missing_file_returns_defaults(tmp_path) -> None:
    store = JsonDataStore(tmp_path / "missing.json")

    saved = store.load()

    assert saved.settings == Settings()
    assert saved.scores == {}


def test_settings_and_scores_round_trip(tmp_path) -> None:
    store = JsonDataStore(tmp_path / "data.json")
    settings = Settings(
        sound_enabled=False,
        ui_scale=1.25,
        difficulties={"target_tap": Difficulty.CHALLENGE},
    )

    store.save(settings, {"target_tap": 10})
    saved = store.load()

    assert saved.settings == settings
    assert saved.scores == {"target_tap": 10}


def test_corrupt_file_recovers_to_defaults(tmp_path) -> None:
    path = tmp_path / "data.json"
    path.write_text("{ definitely not JSON", encoding="utf-8")

    saved = JsonDataStore(path).load()

    assert saved.settings == Settings()
    assert saved.scores == {}


def test_invalid_values_are_ignored(tmp_path) -> None:
    path = tmp_path / "data.json"
    path.write_text(
        """
        {
          "sound_enabled": "yes",
          "ui_scale": 100,
          "difficulties": {"target_tap": "Impossible"},
          "scores": {"target_tap": -2, "other": 4}
        }
        """,
        encoding="utf-8",
    )

    saved = JsonDataStore(path).load()

    assert saved.settings == Settings()
    assert saved.scores == {"other": 4}
