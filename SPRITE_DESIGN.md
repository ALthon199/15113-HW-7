"""
SPRITE DESIGN GUIDE - Fire Boy + Water Girl MVP
=================================================

Visual Reference for ASCII/Simple Box Rendering
All sprites use simple colored rectangles or text symbols for MVP.

## PLAYERS

Water Girl (moving, 32x40):
░░░░
░WW░ ← Blue outline box with "WW" label
░░░░
Color: (120, 182, 255) - Light Blue

Fire Boy (moving, 32x40):
░░░░
░FB░ ← Orange outline box with "FB" label
░░░░
Color: (255, 156, 110) - Light Orange

## STATIC HAZARDS

Fire Zone (48x48):
████
██f██ ← Red box with "f" label
████
Color: (224, 91, 63) - Red-Orange

Water Zone (48x48):
████
██w██ ← Blue box with "w" label
████
Color: (68, 136, 224) - Blue

Lava Zone (48x48):
████
██l██ ← Yellow/orange box with "l" label
████
Color: (245, 156, 66) - Orange

Wall/Solid (48x48):
████
████ ← Gray block
████
Color: (70, 86, 112) - Dark Gray

## EXIT DOORS

Water Girl Exit (48x48):
┌──┐
│ee│ ← Blue outline door with "e" label
└──┘
Color: (106, 170, 255) - Cyan

Fire Boy Exit (48x48):
┌──┐
│EE│ ← Orange outline door with "E" label
└──┘
Color: (255, 120, 95) - Orange

## DYNAMIC OBSTACLES

Moving Platform (48x16):
┌──────┐
│ M→ │ ← Gray platform with direction arrow
└──────┘
Color: (130, 130, 140) - Light Gray
Border: (180, 180, 190) - Lighter Gray
Note: Renders with border to show it's special

Pressure Plate (48x12, thin):
┌────────┐
│ P │ ← When PRESSED, highlights in gold
└────────┘
IDLE: (150, 140, 120) - Brown
PRESSED: (200, 180, 80) - Gold

Gate (48x48):
===== (OPEN - semi-transparent/thin lines)
═════ BLOCKED! (CLOSED - thick solid block)
=====
CLOSED: (100, 50, 50) - Dark Red
OPEN: Same color but rendered with alpha/thin border
Border: (150, 100, 100) - Reddish

# LAYOUT REFERENCE (Single screen 48-pixel tiles)

20 tiles wide × 12 tiles high = 960×576 pixels

Sample puzzle layout (see level1.txt):
┌────────────────────────────────────────┐
│ Border of walls ( # ) │
│ W = Water Girl spawn │
│ F = Fire Boy spawn │
│ e = Water Girl exit │
│ E = Fire Boy exit │
│ M = Moving platform (oscillates) │
│ P = Pressure plate (toggles gates) │
│ G = Gate (blocks, opens when P activated)
│ f w l = Fire/Water/Lava hazards │
└────────────────────────────────────────┘

# RENDERING STRATEGY

MVP uses pygame.draw.rect() for all objects. Future sprite system:

1. Load sprite sheets for each object type
2. Use rotation/flip for direction facing
3. Animate moving platforms with frame offsets
4. Animate pressure plate press/release with depth effect
