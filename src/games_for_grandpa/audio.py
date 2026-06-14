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
        self.sounds["gunshot"] = self._gunshot()
        self.sounds["quack"] = self._quack()

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

    @staticmethod
    def _gunshot() -> pygame.mixer.Sound:
        sample_rate = 44_100
        sample_count = round(sample_rate * 0.18)
        samples = array("h")
        seed = 32_417
        for index in range(sample_count):
            seed = (1_103_515_245 * seed + 12_345) & 0x7FFFFFFF
            noise = (seed / 0x7FFFFFFF) * 2.0 - 1.0
            fade = max(0.0, 1.0 - index / sample_count) ** 3
            thump = math.sin(2 * math.pi * 90 * index / sample_rate)
            samples.append(round((noise * 15_000 + thump * 7_000) * fade))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    @staticmethod
    def _quack() -> pygame.mixer.Sound:
        sample_rate = 44_100
        sample_count = round(sample_rate * 0.24)
        samples = array("h")
        for index in range(sample_count):
            time = index / sample_rate
            envelope = min(1.0, time / 0.035) * max(0.0, 1.0 - time / 0.24)
            wobble = math.sin(2 * math.pi * 18 * time)
            tone = math.sin(2 * math.pi * (330 + 90 * wobble) * time)
            harmonic = math.sin(2 * math.pi * (165 + 40 * wobble) * time)
            samples.append(round(9_000 * envelope * (0.75 * tone + 0.25 * harmonic)))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()
