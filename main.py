"""Minimal pygame loop demonstrating the wave manager, HUD, and configurator CLI."""

from __future__ import annotations

import argparse
import random
from typing import Dict, List

import pygame

from src.economy.player_stats import PlayerStats
from src.ui.hud import HUD
from src.waves.wave_manager import WaveManager

WIDTH, HEIGHT = 960, 540
BACKGROUND_COLOR = (25, 25, 35)
ENEMY_RADIUS = 16

ENEMY_DEFINITIONS: Dict[str, Dict[str, object]] = {
    "grunt": {"color": (70, 200, 70), "speed": 90.0, "reward": 5},
    "runner": {"color": (200, 200, 70), "speed": 130.0, "reward": 7},
    "tank": {"color": (220, 80, 80), "speed": 60.0, "reward": 12},
}

WAVES = [
    [("grunt", 0.0), ("grunt", 1.2), ("runner", 2.5)],
    [("grunt", 0.0), ("tank", 0.8), ("grunt", 1.6), ("runner", 2.4)],
    [("tank", 0.0), ("tank", 1.5), ("runner", 2.0), ("runner", 2.8)],
]


class Enemy:
    def __init__(self, enemy_type: str) -> None:
        definition = ENEMY_DEFINITIONS[enemy_type]
        self.enemy_type = enemy_type
        self.color = definition["color"]  # type: ignore[assignment]
        self.speed = float(definition["speed"])  # type: ignore[arg-type]
        self.reward = int(definition["reward"])  # type: ignore[arg-type]
        self.x = -ENEMY_RADIUS
        self.y = random.randint(200, HEIGHT - 50)

    def update(self, delta: float) -> None:
        self.x += self.speed * delta

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), ENEMY_RADIUS)

    def is_out_of_bounds(self) -> bool:
        return self.x - ENEMY_RADIUS > WIDTH

    def hit_test(self, position: pygame.Vector2) -> bool:
        return pygame.Vector2(self.x, self.y).distance_to(position) <= ENEMY_RADIUS


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Tower Defense Sandbox")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.stats = PlayerStats(money=250, lives=20)
        self.enemies: List[Enemy] = []
        self.wave_manager = WaveManager(WAVES, self.spawn_enemy)
        self.hud = HUD(self.stats, self.wave_manager)

    def spawn_enemy(self, enemy_type: str) -> None:
        self.enemies.append(Enemy(enemy_type))

    def run(self) -> None:
        running = True
        while running:
            delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.hud.wants_to_start_wave(event):
                    if self.wave_manager.start_next_wave():
                        self.stats.start_wave(self.wave_manager.current_wave_number)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_enemy_click(pygame.Vector2(event.pos))

            self.wave_manager.update(delta)
            self.update_enemies(delta)
            self.render()

        pygame.quit()

    def handle_enemy_click(self, position: pygame.Vector2) -> None:
        for enemy in list(self.enemies):
            if enemy.hit_test(position):
                self.enemies.remove(enemy)
                self.stats.register_enemy_kill(enemy.reward)
                break

    def update_enemies(self, delta: float) -> None:
        for enemy in list(self.enemies):
            enemy.update(delta)
            if enemy.is_out_of_bounds():
                self.enemies.remove(enemy)
                self.stats.lose_life(1)

    def render(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.hud.draw(self.screen)
        pygame.display.flip()


def run_game() -> None:
    Game().run()


def run_configurator() -> None:
    from tds.menu import main as menu_main

    menu_main()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tower Defense Sandbox entry point")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--mode",
        choices=("game", "configurator"),
        default="game",
        help="Run the realtime demo or launch the configurator CLI (default: game)",
    )
    mode_group.add_argument(
        "--configurator",
        action="store_true",
        help="Shortcut to launch the configurator CLI",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.configurator or getattr(args, "mode", "game") == "configurator":
        run_configurator()
    else:
        run_game()


if __name__ == "__main__":
    main()