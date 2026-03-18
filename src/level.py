from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pygame

import config
from entities.dynamic_object import DynamicObject
from entities.moving_platform import MovingPlatform
from entities.pressure_plate import PressurePlate
from entities.gate import Gate


@dataclass
class Hazard:
    """Represents a hazard tile in the level.
    
    Hazards are environmental obstacles that damage or kill players based on
    their affinity. For example, fire kills water players, water kills fire players.
    
    Attributes:
        rect: The spatial bounds of this hazard
        kind: Type of hazard ('fire', 'water', or 'lava')
    """
    rect: pygame.Rect
    kind: str


@dataclass
class ExitDoor:
    """Represents an exit door (goal) in the level.
    
    Each player must reach their matching exit door to complete the level.
    Fire Boy reaches the fire exit (E), Water Girl reaches the water exit (e).
    
    Attributes:
        rect: The spatial bounds of this exit door
        affinity: Player type that can use this exit ('fire' or 'water')
    """
    rect: pygame.Rect
    affinity: str


@dataclass
class Level:
    """Complete representation of a game level.
    
    Contains all static and dynamic objects, hazards, exits, and interconnections
    between game elements. The Level class handles rendering of all level components.
    
    Attributes:
        width: Level width in tiles
        height: Level height in tiles
        solid_tiles: List of solid wall rectangles (collision tiles)
        hazards: List of hazardous areas (fire, water, lava)
        doors: List of exit doors (goals for each player)
        spawn_points: Starting positions for each player ('fire' and 'water')
        dynamic_objects: Moving entities (e.g., moving platforms)
        pressure_plates: Plates that activate when stood upon
        gates: Doors that open/close based on pressure plate states
        gems: Collectible items (future expansion)
        plate_gate_links: Maps pressure plate IDs to the gate IDs they control
    """
    width: int
    height: int
    solid_tiles: list[pygame.Rect]
    hazards: list[Hazard]
    doors: list[ExitDoor]
    spawn_points: dict[str, tuple[int, int]]
    dynamic_objects: list[DynamicObject] = field(default_factory=list)
    pressure_plates: list[PressurePlate] = field(default_factory=list)
    gates: list[Gate] = field(default_factory=list)
    gems: list[Gem] = field(default_factory=list)
    plate_gate_links: dict[int, list[int]] = field(default_factory=dict)  # plate_id -> [gate_ids]

    def draw(self, screen: pygame.Surface) -> None:
        """Render the entire level to the screen in proper layer order.
        
        Renders in this order: solid tiles, hazards, dynamic objects, exit doors.
        This ensures hazards and doors remain visible over base tiles.
        
        Args:
            screen: The pygame Surface to draw the level on.
        """
        # Draw in layers so hazards and doors remain visible over base tiles.
        self._draw_solid_tiles(screen)
        self._draw_hazards(screen)
        self._draw_dynamic_objects(screen)
        self._draw_doors(screen)

    def _draw_solid_tiles(self, screen: pygame.Surface) -> None:
        for tile in self.solid_tiles:
            pygame.draw.rect(screen, config.WALL, tile)

    def _draw_hazards(self, screen: pygame.Surface) -> None:
        hazard_colors = {
            "fire": config.FIRE_TILE,
            "water": config.WATER_TILE,
            "lava": config.LAVA_TILE,
        }
        for hazard in self.hazards:
            pygame.draw.rect(screen, hazard_colors[hazard.kind], hazard.rect)

    def _draw_dynamic_objects(self, screen: pygame.Surface) -> None:
        for obj in self.dynamic_objects:
            obj.draw(screen)
        for plate in self.pressure_plates:
            plate.draw(screen)
        for gate in self.gates:
            gate.draw(screen)
        for gem in self.gems:
            gem.draw(screen)

    def _draw_doors(self, screen: pygame.Surface) -> None:
        for door in self.doors:
            color = config.FIRE_DOOR if door.affinity == "fire" else config.WATER_DOOR
            # Draw goal destination with solid color and border
            pygame.draw.rect(screen, color, door.rect)
            pygame.draw.rect(screen, (255, 255, 255), door.rect, width=3)  # White border for visibility
            
            # Draw label to identify which player's exit
            if hasattr(screen, 'get_flags'):
                small_font = pygame.font.SysFont("monospace", 12, bold=True)
                label = "E♦" if door.affinity == "fire" else "E♦"
                text = small_font.render(label, True, (0, 0, 0))
                text_rect = text.get_rect(center=door.rect.center)
                screen.blit(text, text_rect)

    def update_dynamic_objects(self, dt: float) -> None:
        """Update all dynamic objects (moving platforms, etc.) each frame.
        
        Args:
            dt: Delta time (elapsed seconds since last frame).
        """
        for obj in self.dynamic_objects:
            obj.update(dt)


def _tile_position(row_idx: int, col_idx: int) -> tuple[int, int]:
    """Convert grid cell indices to pixel coordinates.
    
    Args:
        row_idx: Row index (0 = top)
        col_idx: Column index (0 = left)
        
    Returns:
        Tuple of (x, y) pixel coordinates for top-left of tile
    """
    return col_idx * config.TILE_SIZE, row_idx * config.TILE_SIZE


def _spawn_position(x: int, y: int) -> tuple[int, int]:
    """Adjust spawn position with a small inset from tile boundary.
    
    This prevents players from clipping through tile edges at spawn time.
    
    Args:
        x: Base x position (left edge of tile)
        y: Base y position (top edge of tile)
        
    Returns:
        Adjusted (x, y) position for player spawning
    """
    # Small inset keeps players from clipping the tile boundary at spawn.
    return x + 8, y + 4


def _parse_symbol(
    symbol: str,
    tile_rect: pygame.Rect,
    spawn_point: tuple[int, int],
    solid_tiles: list[pygame.Rect],
    hazards: list[Hazard],
    doors: list[ExitDoor],
    spawn_points: dict[str, tuple[int, int]],
    dynamic_objects: list[DynamicObject],
    pressure_plates: list[PressurePlate],
    gates: list[Gate],
) -> None:
    """Parse a single level symbol and add corresponding game object.
    
    Converts ASCII characters from the level map into game objects:
    - '#' = solid wall tile
    - 'f', 'w', 'l' = fire/water/lava hazards
    - 'E', 'e' = fire/water exit doors
    - 'F', 'W' = fire/water spawn points
    - 'M' = moving platform
    - 'P' = pressure plate
    - 'G' = gate
    
    Args:
        symbol: Single character from level map
        tile_rect: Bounding box for this tile location
        spawn_point: Adjusted position for player spawning
        solid_tiles: List to add solid tiles to
        hazards: List to add hazards to
        doors: List to add exit doors to
        spawn_points: Dict to add spawn positions to
        dynamic_objects: List to add moving platforms to
        pressure_plates: List to add pressure plates to
        gates: List to add gates to
    """
    # Keep map-to-object translation centralized for easy symbol extension.
    if symbol == "#":
        solid_tiles.append(tile_rect)
    elif symbol == "f":
        hazards.append(Hazard(tile_rect, "fire"))
    elif symbol == "w":
        hazards.append(Hazard(tile_rect, "water"))
    elif symbol == "l":
        hazards.append(Hazard(tile_rect, "lava"))
    elif symbol == "E":
        doors.append(ExitDoor(tile_rect, "fire"))
    elif symbol == "e":
        doors.append(ExitDoor(tile_rect, "water"))
    elif symbol == "F":
        spawn_points["fire"] = spawn_point
    elif symbol == "W":
        spawn_points["water"] = spawn_point
    elif symbol == "M":
        # Moving platform: moves horizontally between two tiles.
        platform = MovingPlatform(
            start_x=tile_rect.x,
            start_y=tile_rect.y,
            width=config.TILE_SIZE,
            height=config.TILE_SIZE // 3,
            end_x=tile_rect.x + config.TILE_SIZE * 2,
            end_y=tile_rect.y,
            speed=2.0,
        )
        dynamic_objects.append(platform)
    elif symbol == "P":
        # Pressure plate: thin plate at this position.
        plate = PressurePlate(tile_rect.x, tile_rect.y + config.TILE_SIZE - 12)
        plate.plate_id = len(pressure_plates)
        pressure_plates.append(plate)
    elif symbol == "G":
        # Gate: blocks passage when closed.
        gate = Gate(tile_rect.x, tile_rect.y)
        gate.gate_id = len(gates)
        gates.append(gate)


def load_level(path: Path) -> Level:
    """Load and parse a complete level from an ASCII map file.
    
    The level file is an ASCII grid where each character maps to a game object.
    Each character position represents one tile. Returns a fully initialized Level
    with all static and dynamic objects positioned.
    
    Args:
        path: Path to the level file
        
    Returns:
        Complete Level object with all entities initialized and positioned
        
    Raises:
        ValueError: If level file is empty or rows have different lengths
    """
    # The level file is an ASCII grid where each character maps to a game object.
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError("Level file is empty")

    height = len(lines)
    width = len(lines[0])

    solid_tiles: list[pygame.Rect] = []
    hazards: list[Hazard] = []
    doors: list[ExitDoor] = []
    spawn_points: dict[str, tuple[int, int]] = {}
    dynamic_objects: list[DynamicObject] = []
    pressure_plates: list[PressurePlate] = []
    gates: list[Gate] = []

    for row_idx, line in enumerate(lines):
        if len(line) != width:
            raise ValueError("All level rows must be the same length")

        for col_idx, symbol in enumerate(line):
            x, y = _tile_position(row_idx, col_idx)
            tile_rect = pygame.Rect(x, y, config.TILE_SIZE, config.TILE_SIZE)
            _parse_symbol(
                symbol=symbol,
                tile_rect=tile_rect,
                spawn_point=_spawn_position(x, y),
                solid_tiles=solid_tiles,
                hazards=hazards,
                doors=doors,
                spawn_points=spawn_points,
                dynamic_objects=dynamic_objects,
                pressure_plates=pressure_plates,
                gates=gates,
            )

    if "fire" not in spawn_points or "water" not in spawn_points:
        raise ValueError("Level must include both F and W spawn symbols")

    # For MVP, link all plates to all gates (first plate opens all gates).
    plate_gate_links: dict[int, list[int]] = {}
    for plate in pressure_plates:
        plate_gate_links[plate.plate_id] = [gate.gate_id for gate in gates]

    return Level(
        width=width,
        height=height,
        solid_tiles=solid_tiles,
        hazards=hazards,
        doors=doors,
        spawn_points=spawn_points,
        dynamic_objects=dynamic_objects,
        pressure_plates=pressure_plates,
        gates=gates,
        plate_gate_links=plate_gate_links,
    )
