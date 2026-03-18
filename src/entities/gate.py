"""Gate that can be opened/closed by pressure plates."""
from __future__ import annotations

import pygame

import config
from .dynamic_object import DynamicObject


class Gate(DynamicObject):
    """A barrier that can be opened by linked pressure plates.
    
    Gates block player movement when closed, and become passable when opened
    by pressure plate activation. Multiple gates can be linked to the same
    pressure plate, and each gate maintains its own open/closed state.
    
    Attributes:
        is_open: True if gate is open (passable), False if closed (blocks movement)
        gate_id: Unique identifier used to link this gate to pressure plates
    """

    def __init__(self, x: int, y: int, width: int = 48, height: int = 48) -> None:
        """Initialize a gate.
        
        Args:
            x: Left edge pixel position
            y: Top edge pixel position
            width: Width in pixels (default 48, one tile width)
            height: Height in pixels (default 48, one tile height)
        """
        super().__init__(x, y, width, height)
        self.is_open = False
        self.gate_id = None

    def update(self, dt: float) -> None:
        """Gates don't animate; they toggle on/off via set_open()."""
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """Draw gate, showing open or closed state visually.
        
        Args:
            screen: The pygame Surface to draw the gate on
        """
        if self.is_open:
            # Open: thin outline or semi-transparent.
            color = config.GATE_OPEN
            border_width = 1
        else:
            # Closed: solid barrier.
            color = config.GATE_CLOSED
            border_width = 0

        pygame.draw.rect(screen, color, self.rect, width=border_width)
        pygame.draw.rect(screen, config.GATE_BORDER, self.rect, width=2)
        
        # Draw "G" label and open/closed indicator.
        if hasattr(screen, 'get_flags'):
            small_font = pygame.font.SysFont("monospace", 12, bold=True)
            status = "G◇" if self.is_open else "G✕"  # Diamond for open, X for closed
            text = small_font.render(status, True, (255, 255, 255))
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)

    def set_open(self, open_state: bool) -> None:
        """Set gate open/closed state.
        
        Called each frame by the game to update gate state based on
        pressure plate activation.
        
        Args:
            open_state: True to open gate (passable), False to close (blocking)
        """
        self.is_open = open_state

    def blocks_collision(self) -> bool:
        """Return True if this gate should block player collision.
        
        Returns:
            True when gate is closed (blocking), False when open (passable)
        """
        return not self.is_open
