#!/usr/bin/env python3
"""
Demo script to test the basic rendering system.
"""

import pygame
import sys
import os

# Add the pacman_game package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pacman_game.models import Maze, Player, Ghost, ScoreManager, Position, GhostMode, GhostPersonality
from pacman_game.renderer import Renderer
from pacman_game.config import GameConfig


def main():
    """Run a basic rendering demo."""
    print("Starting Pacman Renderer Demo...")
    
    # Initialize game components
    config = GameConfig()
    maze = Maze(tile_size=config.TILE_SIZE)
    
    # Create player at starting position
    player_start = Position(13 * config.TILE_SIZE, 15 * config.TILE_SIZE)  # Center-ish position
    player = Player(player_start, maze, speed=config.PLAYER_SPEED)
    
    # Create some ghosts
    ghosts = [
        Ghost(Position(12 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, GhostPersonality.BLINKY, config.GHOST_SPEED),
        Ghost(Position(13 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, GhostPersonality.PINKY, config.GHOST_SPEED),
        Ghost(Position(14 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, GhostPersonality.INKY, config.GHOST_SPEED),
        Ghost(Position(15 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, GhostPersonality.SUE, config.GHOST_SPEED)
    ]
    
    # Set one ghost to frightened mode for testing
    ghosts[1].mode = GhostMode.FRIGHTENED
    
    # Create score manager
    score_manager = ScoreManager(starting_lives=config.STARTING_LIVES)
    score_manager.initialize_level(maze.get_dots_remaining())
    score_manager.score = 1250  # Set some demo score
    score_manager.level = 2
    
    # Initialize renderer
    renderer = Renderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.TILE_SIZE)
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    print("Demo running. Press ESC to exit, SPACE to toggle game over screen.")
    show_game_over = False
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    show_game_over = not show_game_over
        
        # Clear screen
        renderer.clear_screen()
        
        if not show_game_over:
            # Render game elements
            renderer.render_maze(maze)
            renderer.render_collectibles(maze)
            renderer.render_player(player)
            renderer.render_ghosts(ghosts)
            renderer.render_ui(score_manager)
        else:
            # Show game over screen
            renderer.render_game_over_screen(score_manager.get_score())
        
        # Update display
        renderer.update_display()
        
        # Control frame rate
        clock.tick(config.FPS)
    
    # Cleanup
    renderer.cleanup()
    print("Demo completed successfully!")


if __name__ == "__main__":
    main()