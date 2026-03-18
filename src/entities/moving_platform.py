"""Moving platform that oscillates between two positions."""
from __future__ import annotations

import pygame

import config
from .dynamic_object import DynamicObject


class MovingPlatform(DynamicObject):
    """A platform that moves between two fixed points in a continuous loop."""

    def __init__(
        self,
        start_x: int,
        start_y: int,
        width: int,
        height: int,
        end_x: int,
        end_y: int,
        speed: float = 2.0,
    ) -> None:
        super().__init__(start_x, start_y, width, height)
        self.start_pos = pygame.Vector2(start_x, start_y)
        self.end_pos = pygame.Vector2(end_x, end_y)
        self.current_pos = pygame.Vector2(self.start_pos)
        self.speed = speed
        self.moving_to_end = True

    def update(self, dt: float) -> None:
        """Move towards target, reverse direction when endpoint reached."""
        target = self.end_pos if self.moving_to_end else self.start_pos
        direction = target - self.current_pos

        # Stop if we've reached the target (within 1 pixel).
        if direction.length() < 1.0:
            self.moving_to_end = not self.moving_to_end
            return

        # Move towards target.
        direction_normalized = direction.normalize()
        step = direction_normalized * self.speed
        self.current_pos += step

        # Clamp to exact endpoint to avoid overshooting.
        if (target - self.current_pos).length() < self.speed:
            self.current_pos = target.copy()

        # Update rect position.
        self.rect.x = int(self.current_pos.x)
        self.rect.y = int(self.current_pos.y)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw platform as a tinted rectangle."""
        pygame.draw.rect(screen, config.PLATFORM_COLOR, self.rect)
        # Draw border to emphasize it's movable.
        pygame.draw.rect(screen, config.PLATFORM_BORDER, self.rect, width=2)
        
        # Draw arrow or "M" label to show it's a moving platform.
        if hasattr(screen, 'get_flags'):
            small_font = pygame.font.SysFont("monospace", 14, bold=True)
            # Show direction indicator based on which way we're moving.
            arrow = "→" if self.moving_to_end else "←"
            text = small_font.render(arrow, True, (255, 255, 255))
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)
