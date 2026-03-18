from __future__ import annotations

import pygame

import config


class Player:
    def __init__(
        self,
        name: str,
        affinity: str,
        spawn: tuple[int, int],
        controls: dict[str, int],
        color: tuple[int, int, int],
    ) -> None:
        self.name = name
        self.affinity = affinity
        self.spawn = pygame.Vector2(spawn)
        self.controls = controls
        self.color = color
        self.rect = pygame.Rect(spawn[0], spawn[1], config.PLAYER_WIDTH, config.PLAYER_HEIGHT)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.reached_exit = False

    def reset(self) -> None:
        self.rect.topleft = (int(self.spawn.x), int(self.spawn.y))
        self.velocity.xy = (0, 0)
        self.on_ground = False
        self.reached_exit = False

    def update(self, keys: pygame.key.ScancodeWrapper, solid_tiles: list[pygame.Rect]) -> None:
        # Input and physics are split to keep each step easy to tune.
        self._apply_horizontal_input(keys)
        self._apply_jump_input(keys)
        self._apply_gravity()
        self._move_and_collide(solid_tiles)

    def _apply_horizontal_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        move_axis = 0
        if keys[self.controls["left"]]:
            move_axis -= 1
        if keys[self.controls["right"]]:
            move_axis += 1
        self.velocity.x = move_axis * config.MOVE_SPEED

    def _apply_jump_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        # Jump is allowed only from grounded state in this MVP.
        if keys[self.controls["jump"]] and self.on_ground:
            self.velocity.y = -config.JUMP_VELOCITY
            self.on_ground = False

    def _apply_gravity(self) -> None:
        self.velocity.y = min(self.velocity.y + config.GRAVITY, config.MAX_FALL_SPEED)

    def _move_and_collide(self, solid_tiles: list[pygame.Rect]) -> None:
        # Resolve X and Y separately to keep collision responses predictable.
        self.rect.x += int(self.velocity.x)
        for tile in solid_tiles:
            if self.rect.colliderect(tile):
                if self.velocity.x > 0:
                    self.rect.right = tile.left
                elif self.velocity.x < 0:
                    self.rect.left = tile.right

        self.rect.y += int(self.velocity.y)
        self.on_ground = False
        for tile in solid_tiles:
            if self.rect.colliderect(tile):
                if self.velocity.y > 0:
                    self.rect.bottom = tile.top
                    self.velocity.y = 0
                    self.on_ground = True
                elif self.velocity.y < 0:
                    self.rect.top = tile.bottom
                    self.velocity.y = 0

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        # Draw border for depth.
        pygame.draw.rect(screen, (255, 255, 255), self.rect, width=2, border_radius=8)
        
        # Draw player initial or name label.
        if hasattr(screen, 'get_flags'):
            tiny_font = pygame.font.SysFont("monospace", 10, bold=True)
            label = "W" if self.affinity == "water" else "F"
            text = tiny_font.render(label, True, (50, 50, 50))
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)
