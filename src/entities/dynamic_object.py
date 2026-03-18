"""Base class for game objects with state and animation."""
from __future__ import annotations

from abc import ABC, abstractmethod

import pygame


class DynamicObject(ABC):
    """Base class for objects that update and draw each frame.
    
    This abstract class serves as the foundation for all game objects that move,
    change state, or need to be rendered each frame (e.g., moving platforms,
    pressure plates, gates). Subclasses must implement update() and draw().
    """

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Initialize a dynamic object with position and dimensions.
        
        Args:
            x: Horizontal pixel position (left edge)
            y: Vertical pixel position (top edge)
            width: Width in pixels
            height: Height in pixels
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update state each frame based on elapsed time.
        
        Args:
            dt: Delta time (elapsed time since last frame) in seconds.
               Use this to ensure frame-rate-independent movement.
        """
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Render this object to the screen.
        
        Args:
            screen: The pygame Surface to draw on (the game window).
        """
        pass

    def get_rect(self) -> pygame.Rect:
        """Return the bounding rectangle for collision detection.
        
        Returns:
            pygame.Rect: The object's collision bounding box.
        """
        return self.rect
