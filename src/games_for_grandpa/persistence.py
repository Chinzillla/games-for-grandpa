from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from games_for_grandpa.core import Difficulty, Settings


@dataclass(slots=True)
class SavedData:
    settings: Settings
    scores: dict[str, int]


class JsonDataStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or self.default_path()

    @staticmethod
    def default_path() -> Path:
        local_app_data = os.environ.get("LOCALAPPDATA")
        base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        return base / "GamesForGrandpa" / "player-data.json"

    def load(self) -> SavedData:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("Saved data must be a JSON object")
            return SavedData(
                settings=self._settings_from(raw),
                scores=self._scores_from(raw.get("scores", {})),
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return SavedData(settings=Settings(), scores={})

    def save(self, settings: Settings, scores: dict[str, int]) -> None:
        payload = {
            "sound_enabled": settings.sound_enabled,
            "ui_scale": settings.ui_scale,
            "difficulties": {
                game_id: difficulty.value
                for game_id, difficulty in settings.difficulties.items()
            },
            "scores": scores,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self.path)

    @staticmethod
    def _settings_from(raw: dict[object, object]) -> Settings:
        sound_enabled = raw.get("sound_enabled", True)
        ui_scale = raw.get("ui_scale", 1.0)
        if not isinstance(sound_enabled, bool):
            sound_enabled = True
        if not isinstance(ui_scale, int | float) or not 0.75 <= float(ui_scale) <= 1.5:
            ui_scale = 1.0

        difficulties: dict[str, Difficulty] = {}
        raw_difficulties = raw.get("difficulties", {})
        if isinstance(raw_difficulties, dict):
            by_value = {difficulty.value: difficulty for difficulty in Difficulty}
            for game_id, value in raw_difficulties.items():
                if isinstance(game_id, str) and isinstance(value, str) and value in by_value:
                    difficulties[game_id] = by_value[value]
        return Settings(
            sound_enabled=sound_enabled,
            ui_scale=float(ui_scale),
            difficulties=difficulties,
        )

    @staticmethod
    def _scores_from(raw: object) -> dict[str, int]:
        if not isinstance(raw, dict):
            return {}
        return {
            game_id: score
            for game_id, score in raw.items()
            if isinstance(game_id, str)
            and isinstance(score, int)
            and not isinstance(score, bool)
            and score >= 0
        }
