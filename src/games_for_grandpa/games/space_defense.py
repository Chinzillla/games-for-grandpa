from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

ENEMY_ROWS = 3
ENEMY_COLUMNS = 7
ENEMY_COUNT = ENEMY_ROWS * ENEMY_COLUMNS


class SpaceState(Enum):
    PLAYING = "playing"
    COMPLETE = "complete"
    GAME_OVER = "game_over"


@dataclass(slots=True)
class Enemy:
    x: float
    y: float
    kind: int
    alive: bool = True


@dataclass(slots=True)
class Bullet:
    x: float
    y: float


class SpaceDefenseModel:
    def __init__(self) -> None:
        self.player_x = 640.0
        self.enemies: list[Enemy] = []
        self.bullets: list[Bullet] = []
        self.direction = 1
        self.shoot_timer = 0.0
        self.score = 0
        self.state = SpaceState.PLAYING
        self.reset()

    def reset(self) -> None:
        self.player_x = 640.0
        # DSA: A list stores active enemies because each frame scans a small fixed group.
        self.enemies = [
            Enemy(280 + column * 105, 120 + row * 70, row)
            for row in range(ENEMY_ROWS)
            for column in range(ENEMY_COLUMNS)
        ]
        self.bullets = []
        self.direction = 1
        self.shoot_timer = 0.0
        self.score = 0
        self.state = SpaceState.PLAYING

    def move_player(self, x: float) -> None:
        self.player_x = max(110.0, min(1170.0, x))

    def update(self, dt: float) -> None:
        if self.state is not SpaceState.PLAYING:
            return
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.bullets.append(Bullet(self.player_x, 590.0))
            self.shoot_timer = 0.45

        for bullet in self.bullets:
            bullet.y -= 620.0 * dt
        self.bullets = [bullet for bullet in self.bullets if bullet.y > 40]

        alive = [enemy for enemy in self.enemies if enemy.alive]
        if not alive:
            self.state = SpaceState.COMPLETE
            return

        left = min(enemy.x for enemy in alive)
        right = max(enemy.x for enemy in alive)
        if (right > 1165 and self.direction > 0) or (left < 115 and self.direction < 0):
            self.direction *= -1
            for enemy in alive:
                enemy.y += 28
        for enemy in alive:
            enemy.x += self.direction * 85.0 * dt
            if enemy.y >= 540:
                self.state = SpaceState.GAME_OVER

        self._handle_collisions()
        if all(not enemy.alive for enemy in self.enemies):
            self.state = SpaceState.COMPLETE

    def _handle_collisions(self) -> None:
        for bullet in self.bullets:
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                if abs(bullet.x - enemy.x) <= 32 and abs(bullet.y - enemy.y) <= 26:
                    enemy.alive = False
                    bullet.y = -100
                    self.score += 1
                    break
