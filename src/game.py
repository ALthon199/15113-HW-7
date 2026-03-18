from __future__ import annotations

import pygame

import config
from entities.player import Player
from level import ExitDoor, Hazard, load_level


class Game:
    """Main game controller managing gameplay state, update logic, and rendering.
    
    The Game class orchestrates the entire game loop:
    1. Handles user input (keyboard events)
    2. Updates game state (players, collision detection, level interactions)
    3. Checks win/loss conditions
    4. Renders everything to screen
    
    Key responsibilities:
    - Managing two players (Fire Boy and Water Girl)
    - Tracking level completion state
    - Coordinating pressure plate activation with gate opening
    - Detecting hazards and enforcing affinity rules
    """
    def __init__(self) -> None:
        """Initialize the game, load the first level, and set up the game window.
        
        Creates the pygame display, initializes both players at their spawn points,
        and prepares all game subsystems.
        """
        pygame.init()

        # Load static level data once, then build runtime objects around it.
        self.level = load_level(config.LEVEL_1_PATH)
        width = self.level.width * config.TILE_SIZE
        height = self.level.height * config.TILE_SIZE
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Fire Boy + Water Girl (MVP)")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.big_font = pygame.font.SysFont("consolas", 40)

        self.players = self._build_players()

        self.running = True
        self.level_complete = False

    def _build_players(self) -> list[Player]:
        """Create and return both player characters with their control schemes.
        
        Returns:
            List containing Water Girl and Fire Boy, each with their spawn position
            and control bindings.
        """
        return [
            Player(
                name="Water Girl",
                affinity="water",
                spawn=self.level.spawn_points["water"],
                controls=config.WATER_CONTROLS,
                color=config.WATER_PLAYER,
            ),
            Player(
                name="Fire Boy",
                affinity="fire",
                spawn=self.level.spawn_points["fire"],
                controls=config.FIRE_CONTROLS,
                color=config.FIRE_PLAYER,
            ),
        ]

    def reset_level(self) -> None:
        """Reset the current level, returning all players to spawn positions.
        
        Soft restart that keeps the game running without reloading assets.
        Called when a player dies or when the user presses R.
        """
        # A reset is a soft restart: keep the window open and restore actor state.
        for player in self.players:
            player.reset()
        self.level_complete = False

    def _player_is_dead(self, player: Player, hazards: list[Hazard]) -> bool:
        """Check if a player has collided with a lethal hazard.
        
        Players die when colliding with hazards that match their weakness:
        - Fire Boy (fire affinity) dies in water, dies in lava
        - Water Girl (water affinity) dies in fire, dies in lava
        
        Args:
            player: The player to check
            hazards: List of hazards in the level
            
        Returns:
            True if player collides with a lethal hazard, False otherwise
        """
        for hazard in hazards:
            if not player.rect.colliderect(hazard.rect):
                continue

            if hazard.kind == "lava":
                return True
            if hazard.kind == "fire" and player.affinity != "fire":
                return True
            if hazard.kind == "water" and player.affinity != "water":
                return True
        return False

    def _update_exit_status(self, player: Player, doors: list[ExitDoor]) -> None:
        """Check if player has reached their matching exit door.
        
        Args:
            player: The player to check
            doors: List of exit doors in the level
        """
        player.reached_exit = any(
            player.rect.colliderect(door.rect) and door.affinity == player.affinity
            for door in doors
        )

    def handle_events(self) -> None:
        """Process all keyboard and window events for this frame.
        
        Handles:
        - Window close requests
        - ESC key to quit
        - R key to restart level
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

    def _handle_keydown(self, key: int) -> None:
        """Process keyboard input for special commands.
        
        Args:
            key: pygame key code pressed
        """
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_r:
            self.reset_level()

    def update(self) -> None:
        """Update all game state for the current frame.
        
        Update order is critical:
        1. Update dynamic objects (moving platforms)
        2. Check pressure plate activations
        3. Update gate states based on plates
        4. Update player positions with collision detection
        5. Check for hazard collisions and deaths
        6. Check exit door collisions
        7. Check win condition
        """
        if self.level_complete:
            return

        # Update order matters: dynamic objects, then players, then state checks.
        self._update_dynamic_objects()
        self._update_pressure_plates()
        self._update_gate_states()
        self._update_players()

        if self._any_player_dead():
            self.reset_level()
            return

        self._update_all_exit_statuses()

        lvl_complete = self._all_players_at_exits()
        self.level_complete = lvl_complete

    def _update_dynamic_objects(self) -> None:
        """Update all moving platforms and other dynamic objects each frame.
        
        Moving platforms update their position based on elapsed time and speed.
        """
        dt = 1.0 / config.FPS
        self.level.update_dynamic_objects(dt)

    def _update_pressure_plates(self) -> None:
        """Detect which pressure plates have players standing on them.
        
        This method checks collision between all players and all pressure plates,
        updating each plate's 'pressed' state. Must be called before _update_gate_states()
        so gates can react to current plate states.
        """
        for plate in self.level.pressure_plates:
            plate.set_pressed(False)
            for player in self.players:
                if player.rect.colliderect(plate.rect):
                    plate.set_pressed(True)
                    break

    def _update_gate_states(self) -> None:
        """Update all gate open/close states based on linked pressure plates.
        
        A gate opens when at least one of its linked pressure plates is pressed.
        Multiple gates can be linked to the same plate, and a plate can link to
        multiple gates (MVP links all plates to all gates).
        
        Must be called after _update_pressure_plates() to use current state.
        """
        for gate in self.level.gates:
            # A gate is open if any plate linked to it is pressed.
            gate_id = gate.gate_id
            is_open = False
            for plate in self.level.pressure_plates:
                if plate.plate_id in self.level.plate_gate_links:
                    if gate_id in self.level.plate_gate_links[plate.plate_id]:
                        if plate.is_pressed:
                            is_open = True
                            break
            gate.set_open(is_open)

    def _get_collision_tiles(self) -> list:
        """Get all solid tiles that should block player movement.
        
        Returns a combined list of collision rectangles:
        - Static wall tiles
        - Moving platform tiles (for standing on)
        - Pressure plate tiles (players stand on them)
        - Closed gate tiles (blocks passage when closed)
        
        Returns:
            List of pygame.Rect objects representing all collision geometry.
        """
        tiles = list(self.level.solid_tiles)
        # Add moving platforms.
        for platform in self.level.dynamic_objects:
            tiles.append(platform.get_rect())
        # Add pressure plates (solid objects to stand on).
        for plate in self.level.pressure_plates:
            tiles.append(plate.get_rect())
        # Add closed gates.
        for gate in self.level.gates:
            if gate.blocks_collision():
                tiles.append(gate.get_rect())
        return tiles

    def _update_players(self) -> None:
        """Update all player positions, handling input and collision detection.
        
        Players move based on currently pressed keys, with collision detection
        against all solid tiles (walls, platforms, plates, gates).
        """
        keys = pygame.key.get_pressed()
        collision_tiles = self._get_collision_tiles()
        for player in self.players:
            player.update(keys, collision_tiles)

    def _any_player_dead(self) -> bool:
        """Check if any player has died from a hazard.
        
        Returns:
            True if at least one player is dead, False otherwise.
        """
        return any(self._player_is_dead(player, self.level.hazards) for player in self.players)

    def _update_all_exit_statuses(self) -> None:
        """Update whether each player is currently at their exit door."""
        for player in self.players:
            self._update_exit_status(player, self.level.doors)

    def _all_players_at_exits(self) -> bool:
        """Check if all players have reached their respective exit doors.
        
        Returns:
            True if both players are at their matching exits, False otherwise.
        """
        return all(player.reached_exit for player in self.players)

    def draw(self) -> None:
        """Render a complete frame to the screen.
        
        Renders in order:
        1. Fill background
        2. Draw level (tiles, hazards, objects, doors)
        3. Draw players
        4. Draw HUD (controls text)
        5. Draw win banner if level complete
        6. Update display
        """
        self.screen.fill(config.BACKGROUND)
        self.level.draw(self.screen)

        for player in self.players:
            player.draw(self.screen)

        self._draw_hud()

        self._draw_win_banner_if_needed()

        pygame.display.flip()

    def _draw_win_banner_if_needed(self) -> None:
        """Draw the level completion banner if the level is finished."""
        if not self.level_complete:
            return

        label = self.big_font.render("Level Complete!", True, config.TEXT)
        x = self.screen.get_width() // 2 - label.get_width() // 2
        self.screen.blit(label, (x, 36))

    def _draw_hud(self) -> None:
        """Draw the heads-up display with control instructions."""
        controls = "Water: A/D + W | Fire: <-/-> + Up | R: Restart | Esc: Quit"
        info = self.font.render(controls, True, config.TEXT)
        self.screen.blit(info, (12, 12))

    def run(self) -> None:
        """Main game loop: update game state and render each frame.
        
        Runs at fixed FPS (frames per second) defined in config.
        Loop continues until running flag is set to False.
        """
        # Main loop: fixed cadence, input handling, simulation, then render.
        while self.running:
            self.clock.tick(config.FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
