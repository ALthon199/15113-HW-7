# Fire Boy + Water Girl Clone (Pygame)

This repository contains a local co-op puzzle-platformer MVP inspired by Fireboy and Watergirl.

Current status: MVP foundation implemented.

## What Is Implemented

- Two playable characters with separate controls
- Tile-based level loading from a text map
- Platform collision + gravity + jumping
- Hazard rules:
  - Fire Boy is safe in fire, dies in water and lava
  - Water Girl is safe in water, dies in fire and lava
- Exit-door win condition requiring both players
- Restart flow (`R`) and quit flow (`Esc`)

## Tech Stack

- Python 3.10+
- Pygame 2.6.1

## Quick Start

1. Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Run the game.

```powershell
python -m src.main
```

## Controls

- Water Girl: `A` (left), `D` (right), `W` (jump)
- Fire Boy: `Left Arrow` (left), `Right Arrow` (right), `Up Arrow` (jump)
- Restart level: `R`
- Quit: `Esc`

## Level Map Symbols

The level in `assets/levels/level1.txt` uses these symbols:

- `#`: solid wall/platform
- `.`: empty space
- `W`: Water Girl spawn
- `F`: Fire Boy spawn
- `w`: water hazard
- `f`: fire hazard
- `l`: lava hazard (kills both)
- `e`: Water Girl exit door
- `E`: Fire Boy exit door

## Project Structure

```text
assets/
	levels/
		level1.txt
src/
	entities/
		player.py
	config.py
	game.py
	level.py
	main.py
requirements.txt
README.md
```

## High-Level Implementation Plan

1. MVP foundation (done): dual characters, physics, hazards, one level, and win condition.
2. **Dynamic obstacles (done)**: moving platforms, pressure plates/gates, basic puzzle mechanics.
3. **Visual enhancements (done)**: labels and indicators (W/F/P/G/arrows) on all game objects for clarity.
4. Add more puzzle mechanics: multi-level progression, switch chains, elevators.
5. Improve feel: coyote time, jump buffering, better acceleration, and animation states.
6. Add game flow: menu, level select, death/win transitions, and multi-level progression.
7. Add content pipeline: more levels and optional support for Tiled JSON maps.
8. Add polish: sprite art, sound effects, music, particles, and camera effects.
9. Add quality checks: lightweight tests for level parsing and collision edge cases.

## Current Level Design

**Level 1** (Puzzle MVP):

- Two moving platforms (M) to cross gaps.
- Two pressure plates (P) that toggle gates.
- Two gates (G) blocking certain passages.
- Hazards: fire (f), water (w), lava (l) — each blocks a specific affinity.
- Goal: Both players reach their exits (e/E) by navigating the puzzle.

**Solvable via**: Walking and platform jumping, stepping on pressure plates to open gates, avoiding hazards based on character type.

## Object Sprites & Indicators

All objects are rendered with **distinguishing labels and colors**:

- **Water Girl (W)**: Light blue box with white "W" label
- **Fire Boy (F)**: Light orange box with white "F" label
- **Moving Platform (M)**: Gray platform with direction arrow (→/←)
- **Pressure Plate (P)**: Brown when idle, gold when pressed, with "P" label
- **Gate (G)**: Dark red, shows "G◇" when open or "G✕" when closed
- **Hazards**: Color-coded (red fire, blue water, orange lava) with letter labels
- **Exit Doors**: Cyan for water (e), orange for fire (E), shown as outline boxes

See [SPRITE_DESIGN.md](SPRITE_DESIGN.md) for full visual reference.

## Development Notes

- Gameplay code is intentionally simple for rapid iteration.
- The level loader validates map shape and required spawn points.
- New levels can be added by creating new map files and loading them in `src/game.py`.

## Troubleshooting

- If `pygame` fails to install, upgrade pip first:

```powershell
python -m pip install --upgrade pip
```

- If controls do not work, make sure the game window is focused.
- If PowerShell blocks activation scripts, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
