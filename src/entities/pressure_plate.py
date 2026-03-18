"""Pressure plate that detects player standing on it."""
from __future__ import annotations

import pygame

import config
from .dynamic_object import DynamicObject


class PressurePlate(DynamicObject):
    """A plate that activates when a player stands on it.
    
    Pressure plates are solid surfaces that players can stand on. When a player
    collides with a plate, it activates (becomes 'pressed') and can trigger
    linked gates to open. The plate visually changes color when pressed.
    
    Attributes:
        is_pressed: True when a player is currently standing on this plate.
        plate_id: Unique identifier used to link this plate to gates.
    """

    def __init__(self, x: int, y: int, width: int = 48, height: int = 12) -> None:
        """Initialize a pressure plate.
        
        Args:
            x: Left edge pixel position
            y: Top edge pixel position
            width: Width in pixels (default 48, typically one tile width)
            height: Height in pixels (default 12, thin plate to sit below feet)
        """
        # Thin plate (smaller height) to sit below players' feet.
        super().__init__(x, y, width, height)
        self.is_pressed = False
        self.plate_id = None

    def update(self, dt: float) -> None:
        """Pressure plates don't move; state updated externally by game logic."""
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """Draw plate, highlighting if currently pressed."""
        color = config.PLATE_PRESSED if self.is_pressed else config.PLATE_IDLE
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, config.PLATE_BORDER, self.rect, width=1)
        
        # Draw "P" label to identify as pressure plate.
        if hasattr(screen, 'get_flags'):
            # Simple text label (uses pygame font)
            small_font = pygame.font.SysFont("monospace", 12, bold=True)
            text = small_font.render("P", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)

    def set_pressed(self, pressed: bool) -> None:
        """Set whether this plate is currently being stepped on by a player.
        
        This method updates the plate's state and may trigger visual feedback.
        Called by the game each frame after collision detection.
        
        Args:
            pressed: True if a player is standing on this plate, False otherwise.
        """
        self.is_pressed = pressed
