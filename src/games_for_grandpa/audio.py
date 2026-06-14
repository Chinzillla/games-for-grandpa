from __future__ import annotations

import math
from array import array

import pygame


class SoundBank:
    FREQUENCIES = {
        "click": (330.0, 0.05),
        "success": (660.0, 0.07),
        "point": (440.0, 0.11),
        "complete": (880.0, 0.18),
    }

    def __init__(self) -> None:
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        if pygame.mixer.get_init() is None:
            return
        for name, (frequency, duration) in self.FREQUENCIES.items():
            self.sounds[name] = self._tone(frequency, duration)

    @staticmethod
    def _tone(frequency: float, duration: float) -> pygame.mixer.Sound:
        sample_rate = 44_100
        sample_count = round(sample_rate * duration)
        samples = array("h")
        for index in range(sample_count):
            fade = 1.0 - index / sample_count
            value = math.sin(2 * math.pi * frequency * index / sample_rate)
            samples.append(round(8_000 * fade * value))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

