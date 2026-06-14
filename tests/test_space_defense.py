from __future__ import annotations

from games_for_grandpa.games.space_defense import Bullet, SpaceDefenseModel, SpaceState


def test_space_defense_auto_shoots() -> None:
    model = SpaceDefenseModel()

    model.update(0.5)

    assert model.bullets


def test_bullet_can_destroy_enemy() -> None:
    model = SpaceDefenseModel()
    enemy = model.enemies[0]
    model.bullets.clear()
    model.bullets.append(Bullet(enemy.x, enemy.y))

    model._handle_collisions()

    assert not enemy.alive
    assert model.score == 1


def test_all_enemies_destroyed_completes_game() -> None:
    model = SpaceDefenseModel()
    for enemy in model.enemies:
        enemy.alive = False

    model.update(0.1)

    assert model.state is SpaceState.COMPLETE
