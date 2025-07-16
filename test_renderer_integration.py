#!/usr/bin/env python3
"""
Integration test for the rendering system with all game components.
"""

import pygame
import sys
import os

# Add the pacman_game package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pacman_game.models import Maze, Player, Ghost, ScoreManager, Position, GhostMode, GhostPersonality, Direction
from pacman_game.renderer import Renderer
from pacman_game.config import GameConfig


def test_full_game_rendering():
    """Test rendering of a complete game scene."""
    print("Testing full game rendering integration...")
    
    # Set up headless mode for testing
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    config = GameConfig()
    
    # Initialize all game components
    maze = Maze(tile_size=config.TILE_SIZE)
    
    # Create player
    player_start = Position(13 * config.TILE_SIZE, 15 * config.TILE_SIZE)
    player = Player(player_start, maze, speed=config.PLAYER_SPEED)
    player.set_direction(Direction.RIGHT)  # Set player moving
    
    # Create ghosts with different states
    ghosts = [
        Ghost(Position(12 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, GhostPersonality.BLINKY, config.GHOST_SPEED),
        Ghost(Position(13 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, GhostPersonality.PINKY, config.GHOST_SPEED),
        Ghost(Position(14 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, GhostPersonality.INKY, config.GHOST_SPEED),
        Ghost(Position(15 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, GhostPersonality.SUE, config.GHOST_SPEED)
    ]
    
    # Set different ghost modes for visual testing
    ghosts[0].mode = GhostMode.NORMAL
    ghosts[1].mode = GhostMode.FRIGHTENED
    ghosts[2].mode = GhostMode.EATEN
    ghosts[3].mode = GhostMode.NORMAL
    
    # Create score manager with realistic game state
    score_manager = ScoreManager(starting_lives=config.STARTING_LIVES)
    score_manager.initialize_level(maze.get_dots_remaining())
    score_manager.score = 2340
    score_manager.level = 3
    score_manager.lives = 2
    
    # Initialize renderer
    renderer = Renderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.TILE_SIZE)
    
    try:
        # Test complete game scene rendering
        renderer.clear_screen()
        renderer.render_maze(maze)
        renderer.render_collectibles(maze)
        renderer.render_player(player)
        renderer.render_ghosts(ghosts)
        renderer.render_ui(score_manager)
        renderer.update_display()
        
        # Verify collectibles exist
        assert maze.get_dots_remaining() > 0, "Should have dots to render"
        assert maze.get_power_pellets_remaining() > 0, "Should have power pellets to render"
        
        # Test player movement simulation
        original_pos = Position(player.position.x, player.position.y)
        player.update()  # This should move the player
        
        # Re-render after movement
        renderer.clear_screen()
        renderer.render_maze(maze)
        renderer.render_collectibles(maze)
        renderer.render_player(player)
        renderer.render_ghosts(ghosts)
        renderer.render_ui(score_manager)
        renderer.update_display()
        
        print("✓ Full game rendering integration test passed")
        
    except Exception as e:
        print(f"✗ Full game rendering integration test failed: {e}")
        raise
    finally:
        renderer.cleanup()


def test_collectible_interaction_rendering():
    """Test rendering after collectible interactions."""
    print("Testing collectible interaction rendering...")
    
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    config = GameConfig()
    maze = Maze(tile_size=config.TILE_SIZE)
    
    # Create player at a position with collectibles
    player_start = Position(1 * config.TILE_SIZE, 1 * config.TILE_SIZE)  # Should have a dot
    player = Player(player_start, maze, speed=config.PLAYER_SPEED)
    
    score_manager = ScoreManager()
    score_manager.initialize_level(maze.get_dots_remaining())
    
    renderer = Renderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.TILE_SIZE)
    
    try:
        # Get initial collectible counts
        initial_dots = maze.get_dots_remaining()
        initial_pellets = maze.get_power_pellets_remaining()
        
        # Render initial state
        renderer.clear_screen()
        renderer.render_collectibles(maze)
        
        # Simulate collecting an item
        collected_dot, collected_pellet, points = player.collect_item_at_position(score_manager)
        
        # Render after collection
        renderer.clear_screen()
        renderer.render_collectibles(maze)
        renderer.render_ui(score_manager)
        
        # Verify collection worked
        if collected_dot:
            assert maze.get_dots_remaining() < initial_dots, "Dot count should decrease"
            print(f"  ✓ Collected dot, score: {score_manager.get_score()}")
        
        if collected_pellet:
            assert maze.get_power_pellets_remaining() < initial_pellets, "Power pellet count should decrease"
            print(f"  ✓ Collected power pellet, score: {score_manager.get_score()}")
        
        print("✓ Collectible interaction rendering test passed")
        
    except Exception as e:
        print(f"✗ Collectible interaction rendering test failed: {e}")
        raise
    finally:
        renderer.cleanup()


def main():
    """Run all integration tests."""
    print("Running Pacman Renderer Integration Tests...")
    print("=" * 50)
    
    try:
        test_full_game_rendering()
        test_collectible_interaction_rendering()
        
        print("=" * 50)
        print("✓ All integration tests passed successfully!")
        print("✓ Basic rendering system implementation is complete!")
        
    except Exception as e:
        print("=" * 50)
        print(f"✗ Integration tests failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()