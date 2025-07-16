"""
Main Game class that coordinates all systems and implements the game loop.
"""

import pygame
import sys
from typing import List, Optional

from .models import (
    Position, Direction, GameState, GhostMode, 
    Maze, Player, Ghost, ScoreManager
)
from .renderer import Renderer
from .input_handler import InputHandler
from .game_state_manager import GameStateManager
from .config import GameConfig


class Game:
    """Main game controller that orchestrates all game systems."""
    
    def __init__(self, config: Optional[GameConfig] = None):
        """Initialize the game with all systems.
        
        Args:
            config: Optional game configuration, uses default if None
        """
        self.config = config or GameConfig()
        self.running = False
        self.clock = pygame.time.Clock()
        
        # Initialize Pygame
        pygame.init()
        
        # Initialize core systems
        self.renderer = Renderer(
            self.config.SCREEN_WIDTH, 
            self.config.SCREEN_HEIGHT, 
            self.config.TILE_SIZE
        )
        self.input_handler = InputHandler()
        self.state_manager = GameStateManager(self.renderer.screen, self.config)
        
        # Initialize game objects
        self.maze = Maze(self.config.TILE_SIZE)
        self.score_manager = ScoreManager(self.config.STARTING_LIVES)
        
        # Initialize player at starting position (center-left of maze)
        player_start_x = 13 * self.config.TILE_SIZE  # Grid position 13
        player_start_y = 15 * self.config.TILE_SIZE  # Grid position 15
        self.player = Player(
            Position(player_start_x, player_start_y), 
            self.maze, 
            self.config.PLAYER_SPEED
        )
        
        # Initialize ghosts at different starting positions
        self.ghosts: List[Ghost] = []
        ghost_configs = [
            {"color": "red", "x": 13, "y": 9},
            {"color": "pink", "x": 14, "y": 9},
            {"color": "cyan", "x": 13, "y": 10},
            {"color": "orange", "x": 14, "y": 10}
        ]
        
        for ghost_config in ghost_configs:
            ghost_x = ghost_config["x"] * self.config.TILE_SIZE
            ghost_y = ghost_config["y"] * self.config.TILE_SIZE
            ghost = Ghost(
                Position(ghost_x, ghost_y),
                self.maze,
                ghost_config["color"],
                self.config.GHOST_SPEED
            )
            self.ghosts.append(ghost)
        
        # Power pellet effect tracking
        self.power_pellet_timer = 0
        self.power_pellet_active = False
        
        # Game state callbacks
        self._setup_state_callbacks()
        
        # Initialize score manager with maze dot count
        self.score_manager.initialize_level(self.maze.get_dots_remaining())
    
    def _setup_state_callbacks(self) -> None:
        """Set up callbacks for state manager."""
        self.state_manager.set_callbacks(
            on_start_game=self._start_new_game,
            on_restart_game=self._restart_game,
            on_quit_game=self._quit_game
        )
    
    def run(self) -> None:
        """Main game loop with 60 FPS timing."""
        self.running = True
        
        try:
            while self.running:
                # Handle events
                events = pygame.event.get()
                self._handle_events(events)
                
                # Update game state
                if self.state_manager.should_update_game():
                    self._update_game()
                
                # Render frame
                self._render_frame()
                
                # Control frame rate (60 FPS)
                self.clock.tick(self.config.FPS)
                
        except KeyboardInterrupt:
            print("Game interrupted by user")
        except Exception as e:
            print(f"Game error: {e}")
            raise
        finally:
            self._cleanup()
    
    def _handle_events(self, events: list) -> None:
        """Handle input events and system events.
        
        Args:
            events: List of pygame events
        """
        for event in events:
            # Skip invalid events
            if event is None or not hasattr(event, 'type'):
                continue
                
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # Let state manager handle state-specific input
            self.state_manager.handle_input(event)
        
        # Update input handler with events
        self.input_handler.update(events, self.state_manager.get_current_state())
        
        # Handle gameplay input if in playing state
        if self.state_manager.can_handle_game_input():
            self._handle_gameplay_input()
    
    def _handle_gameplay_input(self) -> None:
        """Handle input during active gameplay."""
        input_state = self.input_handler.handle_game_input()
        
        # Handle player movement
        if input_state["new_direction"] != Direction.NONE:
            self.player.set_direction(input_state["new_direction"])
        
        # Handle pause
        if input_state["pause_pressed"]:
            self.state_manager.set_state(GameState.PAUSED)
        
        # Handle quit
        if input_state["quit_pressed"]:
            self.running = False
    
    def _update_game(self) -> None:
        """Update all game objects and systems."""
        # Update player
        self.player.update()
        
        # Handle collectible collection
        self._handle_collectibles()
        
        # Update power pellet effect
        self._update_power_pellet_effect()
        
        # Update ghosts
        for ghost in self.ghosts:
            ghost.update(self.player.position)
        
        # Handle ghost collisions
        self._handle_ghost_collisions()
        
        # Check for level completion
        if self.score_manager.is_level_complete():
            self._handle_level_complete()
        
        # Check for game over
        if self.score_manager.is_game_over():
            self._handle_game_over()
    
    def _handle_collectibles(self) -> None:
        """Handle player collecting dots and power pellets."""
        collected_dot, collected_power_pellet, points = self.player.collect_item_at_position(
            self.score_manager
        )
        
        if collected_power_pellet:
            self._activate_power_pellet()
    
    def _activate_power_pellet(self) -> None:
        """Activate power pellet effect on all ghosts."""
        self.power_pellet_active = True
        self.power_pellet_timer = self.config.POWER_PELLET_DURATION
        
        # Set all ghosts to frightened mode
        for ghost in self.ghosts:
            if ghost.mode != GhostMode.EATEN:
                ghost.set_mode(GhostMode.FRIGHTENED, self.config.POWER_PELLET_DURATION)
    
    def _update_power_pellet_effect(self) -> None:
        """Update power pellet timer and effects."""
        if self.power_pellet_active:
            self.power_pellet_timer -= 1
            if self.power_pellet_timer <= 0:
                self.power_pellet_active = False
                # Reset ghost multiplier when power pellet effect ends
                self.score_manager.reset_ghost_multiplier()
    
    def _handle_ghost_collisions(self) -> None:
        """Handle collisions between player and ghosts."""
        for ghost in self.ghosts:
            if self.player.check_collision_with_ghost(ghost):
                life_lost, points_earned = self.player.handle_ghost_collision(
                    ghost, self.score_manager
                )
                
                if life_lost:
                    self._handle_life_lost()
                    break  # Only handle one collision per frame
    
    def _handle_life_lost(self) -> None:
        """Handle player losing a life."""
        # Reset positions
        self.player.reset_position()
        for ghost in self.ghosts:
            ghost.reset_position()
        
        # Reset power pellet effect
        self.power_pellet_active = False
        self.power_pellet_timer = 0
    
    def _handle_level_complete(self) -> None:
        """Handle level completion."""
        # For now, just reset the maze and advance level
        self.maze.reset_collectibles()
        self.score_manager.start_new_level(self.maze.get_dots_remaining())
        
        # Reset positions
        self.player.reset_position()
        for ghost in self.ghosts:
            ghost.reset_position()
        
        # Reset power pellet effect
        self.power_pellet_active = False
        self.power_pellet_timer = 0
    
    def _handle_game_over(self) -> None:
        """Handle game over state."""
        self.state_manager.set_game_over_data(
            self.score_manager.get_score(),
            self.score_manager.get_level()
        )
        self.state_manager.set_state(GameState.GAME_OVER)
    
    def _render_frame(self) -> None:
        """Render the current frame."""
        # Update animations first
        self.renderer.update_animations()
        
        # Clear screen
        self.renderer.clear_screen()
        
        # Render game if in playing or paused state
        if self.state_manager.should_render_game():
            # Render maze
            self.renderer.render_maze(self.maze)
            
            # Render collectibles
            self.renderer.render_collectibles(self.maze)
            
            # Render player
            self.renderer.render_player(self.player)
            
            # Render ghosts
            self.renderer.render_ghosts(self.ghosts)
            
            # Render UI
            self.renderer.render_ui(self.score_manager)
        
        # Render state-specific screens
        self.state_manager.render()
        
        # Update display
        self.renderer.update_display()
    
    def _start_new_game(self) -> None:
        """Start a new game."""
        self._reset_game()
    
    def _restart_game(self) -> None:
        """Restart the current game."""
        self._reset_game()
    
    def _reset_game(self) -> None:
        """Reset all game state for a new game."""
        # Reset score manager
        self.score_manager.reset_game()
        self.score_manager.initialize_level(self.maze.get_dots_remaining())
        
        # Reset maze
        self.maze.reset_collectibles()
        
        # Reset player
        self.player.reset_position()
        
        # Reset ghosts
        for ghost in self.ghosts:
            ghost.reset_position()
            ghost.set_mode(GhostMode.NORMAL)
        
        # Reset power pellet effect
        self.power_pellet_active = False
        self.power_pellet_timer = 0
    
    def _quit_game(self) -> None:
        """Quit the game."""
        self.running = False
    
    def _cleanup(self) -> None:
        """Clean up resources and quit pygame."""
        self.renderer.cleanup()
        pygame.quit()
    
    def get_fps(self) -> float:
        """Get the current FPS for debugging.
        
        Returns:
            Current frames per second
        """
        return self.clock.get_fps()
    
    def is_running(self) -> bool:
        """Check if the game is currently running.
        
        Returns:
            True if game is running, False otherwise
        """
        return self.running
    
    def get_game_state(self) -> GameState:
        """Get the current game state.
        
        Returns:
            Current GameState enum value
        """
        return self.state_manager.get_current_state()
    
    def get_score(self) -> int:
        """Get the current score.
        
        Returns:
            Current score value
        """
        return self.score_manager.get_score()
    
    def get_lives(self) -> int:
        """Get the current number of lives.
        
        Returns:
            Number of lives remaining
        """
        return self.score_manager.get_lives()
    
    def get_level(self) -> int:
        """Get the current level.
        
        Returns:
            Current level number
        """
        return self.score_manager.get_level()
    
    def force_quit(self) -> None:
        """Force quit the game (for testing)."""
        self.running = False