from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

ENEMY_ROWS = 3
ENEMY_COLUMNS = 7
ENEMY_COUNT = ENEMY_ROWS * ENEMY_COLUMNS
PLAYER_LIVES = 3


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


@dataclass(slots=True)
class EnemyBolt:
    x: float
    y: float


@dataclass(slots=True)
class Shield:
    x: float
    y: float
    health: int = 5


class SpaceDefenseModel:
    def __init__(self, *, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.player_x = 640.0
        self.enemies: list[Enemy] = []
        self.bullets: list[Bullet] = []
        self.enemy_bolts: list[EnemyBolt] = []
        self.shields: list[Shield] = []
        self.direction = 1
        self.shoot_timer = 0.0
        self.enemy_shot_timer = 0.0
        self.score = 0
        self.lives = PLAYER_LIVES
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
        self.enemy_bolts = []
        self.shields = [Shield(330 + index * 205, 505) for index in range(4)]
        self.direction = 1
        self.shoot_timer = 0.0
        self.enemy_shot_timer = 0.9
        self.score = 0
        self.lives = PLAYER_LIVES
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
        self.enemy_shot_timer -= dt

        for bullet in self.bullets:
            bullet.y -= 620.0 * dt
        self.bullets = [bullet for bullet in self.bullets if bullet.y > 40]
        for bolt in self.enemy_bolts:
            bolt.y += 320.0 * dt
        self.enemy_bolts = [bolt for bolt in self.enemy_bolts if bolt.y < 690]

        alive = [enemy for enemy in self.enemies if enemy.alive]
        if not alive:
            self.state = SpaceState.COMPLETE
            return

        if self.enemy_shot_timer <= 0:
            self._spawn_enemy_bolt()
            self.enemy_shot_timer = max(0.35, 1.1 - self.score * 0.025)

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
            for shield in self.shields:
                if (
                    shield.health > 0
                    and abs(bullet.x - shield.x) <= 55
                    and abs(bullet.y - shield.y) <= 30
                ):
                    shield.health -= 1
                    bullet.y = -100
                    break
            if bullet.y < 0:
                continue
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                if abs(bullet.x - enemy.x) <= 32 and abs(bullet.y - enemy.y) <= 26:
                    enemy.alive = False
                    bullet.y = -100
                    self.score += 1
                    break
        for bolt in self.enemy_bolts:
            for shield in self.shields:
                if (
                    shield.health > 0
                    and abs(bolt.x - shield.x) <= 58
                    and abs(bolt.y - shield.y) <= 34
                ):
                    shield.health -= 1
                    bolt.y = 999
                    break
            if bolt.y > 690:
                continue
            if abs(bolt.x - self.player_x) <= 44 and 600 <= bolt.y <= 680:
                bolt.y = 999
                self.lives -= 1
                if self.lives <= 0:
                    self.state = SpaceState.GAME_OVER
        self.enemy_bolts = [bolt for bolt in self.enemy_bolts if bolt.y < 690]
        self.shields = [shield for shield in self.shields if shield.health > 0]

    def _spawn_enemy_bolt(self) -> None:
        # DSA: A dict keeps the lowest living enemy in each column, so only front ships fire.
        front_by_column: dict[int, Enemy] = {}
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            column = round((enemy.x - 280) / 105)
            current = front_by_column.get(column)
            if current is None or enemy.y > current.y:
                front_by_column[column] = enemy
        if front_by_column:
            shooter = self.rng.choice(list(front_by_column.values()))
            self.enemy_bolts.append(EnemyBolt(shooter.x, shooter.y + 26))
