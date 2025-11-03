"""Game loop and scene management for the TDS project."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Protocol

import pygame


class Scene(Protocol):
    """Interface that every scene must implement."""

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Process incoming events for this scene."""

    def update(self, dt: float) -> None:
        """Update scene state using the elapsed time in seconds."""

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the scene onto the provided surface."""


@dataclass
class SceneConfig:
    """Metadata for scenes to simplify registration and switching."""

    name: str
    factory: type["BaseScene"]


class BaseScene:
    """Common base class that provides access to the game controller."""

    def __init__(self, game: "Game") -> None:
        self.game = game

    def handle_events(self, events: list[pygame.event.Event]) -> None:  # pragma: no cover - protocol
        raise NotImplementedError

    def update(self, dt: float) -> None:  # pragma: no cover - protocol
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:  # pragma: no cover - protocol
        raise NotImplementedError


class MenuScene(BaseScene):
    """Simple menu scene that switches to gameplay when any key is pressed."""

    FONT_COLOR = (255, 255, 255)
    BACKGROUND_COLOR = (30, 30, 30)

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.font = pygame.font.Font(None, 48)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.game.change_scene("play")

    def update(self, dt: float) -> None:  # noqa: ARG002 - unused by design
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.BACKGROUND_COLOR)
        text = self.font.render("Press any key to play", True, self.FONT_COLOR)
        rect = text.get_rect(center=surface.get_rect().center)
        surface.blit(text, rect)


class PlayScene(BaseScene):
    """Minimal gameplay scene that returns to the menu with ESC."""

    PLAYER_COLOR = (200, 60, 80)
    BACKGROUND_COLOR = (10, 40, 60)

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.player_pos = pygame.Vector2(game.width / 2, game.height / 2)
        self.speed = 200  # pixels per second

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.change_scene("menu")

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            movement.y += 1

        if movement.length_squared() > 0:
            movement = movement.normalize() * self.speed * dt
            self.player_pos += movement

        self.player_pos.x = max(0, min(self.player_pos.x, self.game.width))
        self.player_pos.y = max(0, min(self.player_pos.y, self.game.height))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.BACKGROUND_COLOR)
        pygame.draw.circle(surface, self.PLAYER_COLOR, self.player_pos, 20)


class Game:
    """Main game controller responsible for running the loop and scenes."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        fps: int = 60,
        title: str = "Top-Down Shooter",
    ) -> None:
        pygame.init()
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.width = width
        self.height = height
        self.running = False

        self.scenes: Dict[str, SceneConfig] = {}
        self.current_scene: Optional[BaseScene] = None

        # Register default scenes and make the menu the starting point.
        self.register_scene("menu", MenuScene)
        self.register_scene("play", PlayScene)
        self.change_scene("menu")

    def register_scene(self, name: str, factory: type[BaseScene]) -> None:
        """Register a new scene that can be activated later."""

        normalized = name.strip()
        if not normalized:
            raise ValueError("Scene name cannot be empty")
        self.scenes[normalized] = SceneConfig(name=normalized, factory=factory)

    def change_scene(self, name: str) -> None:
        """Switch the currently active scene."""

        if name not in self.scenes:
            raise ValueError(f"Scene '{name}' is not registered")
        self.current_scene = self.scenes[name].factory(self)

    def handle_events(self) -> None:
        """Process events and forward them to the active scene."""

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
        if self.current_scene is not None:
            self.current_scene.handle_events(events)

    def update(self, dt: float) -> None:
        """Update the active scene with the elapsed delta time."""

        if self.current_scene is not None:
            self.current_scene.update(dt)

    def draw(self) -> None:
        """Render the active scene and update the display."""

        if self.current_scene is not None:
            self.current_scene.draw(self.screen)
        pygame.display.flip()

    def run(self) -> None:
        """Start the main loop until the user closes the window."""

        self.running = True
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()


__all__ = ["Game", "MenuScene", "PlayScene", "Scene", "BaseScene"]
