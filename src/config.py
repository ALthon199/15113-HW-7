from pathlib import Path

import pygame

# Display and timing
FPS = 60
TILE_SIZE = 48

# Player physics
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 40
MOVE_SPEED = 4.0
GRAVITY = 0.55
JUMP_VELOCITY = 11.5
MAX_FALL_SPEED = 14.0

# Colors (R, G, B)
BACKGROUND = (18, 24, 38)
TEXT = (240, 244, 252)
WALL = (70, 86, 112)
FIRE_TILE = (224, 91, 63)
WATER_TILE = (68, 136, 224)
LAVA_TILE = (245, 156, 66)
FIRE_DOOR = (255, 120, 95)
WATER_DOOR = (106, 170, 255)
FIRE_PLAYER = (255, 156, 110)
WATER_PLAYER = (120, 182, 255)

# Obstacles and interactive objects
PLATFORM_COLOR = (130, 130, 140)
PLATFORM_BORDER = (180, 180, 190)
PLATE_IDLE = (150, 140, 120)
PLATE_PRESSED = (200, 180, 80)
PLATE_BORDER = (120, 110, 80)
GATE_CLOSED = (100, 50, 50)
GATE_OPEN = (100, 50, 50)
GATE_BORDER = (150, 100, 100)
SPIKE_COLOR = (200, 200, 200)

# Controls
WATER_CONTROLS = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "jump": pygame.K_w,
}

FIRE_CONTROLS = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "jump": pygame.K_UP,
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEVEL_1_PATH = PROJECT_ROOT / "assets" / "levels" / "level1.txt"
