#!/usr/bin/env python3
"""
Unit tests for the basic rendering system.
"""

import pygame
import sys
import os

# Add the pacman_game package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pacman_game.models import Maze, Player, Ghost, ScoreManager, Position, GhostMode
from pacman_game.renderer import Renderer
from pacman_game.config import GameConfig


def test_renderer_initialization():
    """Test that the renderer initializes correctly."""
    print("Testing renderer initialization...")
    
    # Set up headless mode for testing
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    config = GameConfig()
    renderer = Renderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.TILE_SIZE)
    
    # Check that renderer has required attributes
    assert hasattr(renderer, 'screen')
    assert hasattr(renderer, 'font')
    assert hasattr(renderer, 'tile_size')
    assert renderer.tile_size == config.TILE_SIZE
    assert renderer.screen_width == config.SCREEN_WIDTH
    assert renderer.screen_height == config.SCREEN_HEIGHT
    
    # Test color constants
    assert renderer.BLACK == (0, 0, 0)
    assert renderer.WHITE == (255, 255, 255)
    assert renderer.YELLOW == (255, 255, 0)
    
    # Test ghost colors mapping
    assert "red" in renderer.ghost_colors
    assert "pink" in renderer.ghost_colors
    assert "cyan" in renderer.ghost_colors
    assert "orange" in renderer.ghost_colors
    
    renderer.cleanup()
    print("✓ Renderer initialization test passed")


def test_maze_rendering():
    """Test maze rendering functionality."""
    print("Testing maze rendering...")
    
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    config = GameConfig()
    renderer = Renderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.TILE_SIZE)
    maze = Maze(tile_size=config.TILE_SIZE)
    
    # Test that render_maze doesn't crash
    try:
        renderer.clear_screen()
        renderer.render_maze(maze)
        print("✓ Maze rendering test passed")
    except Exception as e:
        print(f"✗ Maze rendering test failed: {e}")
        raise
    finally:
        renderer.cleanup()


def test_collectibles_rendering():
    """Test collectibles rendering functionality."""
    print("Testing collectibles rendering...")
    
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    config = GameConfig()
    renderer = Renderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.TILE_SIZE)
    maze = Maze(tile_size=config.TILE_SIZE)
    
    # Test that render_collectibles doesn't crash
    try:
        renderer.clear_screen()
        renderer.render_collectibles(maze)
        
        # Verify maze has collectibles to render
        assert len(maze.dots) > 0, "Maze should have dots"
        assert len(maze.power_pellets) > 0, "Maze should have power pellets"
        
        print("✓ Collectibles rendering test passed")
    except Exception as e:
        print(f"✗ Collectibles rendering test failed: {e}")
        raise
    finally:
        renderer.cleanup()


def test_player_rendering():
    """Test player rendering functionality."""
    print("Testing player rendering...")
    
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    config = GameConfig()
    renderer = Renderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.TILE_SIZE)
    maze = Maze(tile_size=config.TILE_SIZE)
    
    # Create player
    player_start = Position(13 * config.TILE_SIZE, 15 * config.TILE_SIZE)
    player = Player(player_start, maze, speed=config.PLAYER_SPEED)
    
    # Test that render_player doesn't crash
    try:
        renderer.clear_screen()
        renderer.render_player(player)
        print("✓ Player rendering test passed")
    except Exception as e:
        print(f"✗ Player rendering test failed: {e}")
        raise
    finally:
        renderer.cleanup()


def test_ghost_rendering():
    """Test ghost rendering functionality."""
    print("Testing ghost rendering...")
    
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    config = GameConfig()
    renderer = Renderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.TILE_SIZE)
    maze = Maze(tile_size=config.TILE_SIZE)
    
    # Create ghosts with different colors and modes
    ghosts = [
        Ghost(Position(12 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, "red", config.GHOST_SPEED),
        Ghost(Position(13 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, "pink", config.GHOST_SPEED),
        Ghost(Position(14 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, "cyan", config.GHOST_SPEED),
        Ghost(Position(15 * config.TILE_SIZE, 9 * config.TILE_SIZE), maze, "orange", config.GHOST_SPEED)
    ]
    
    # Set different modes for testing
    ghosts[1].mode = GhostMode.FRIGHTENED
    ghosts[2].mode = GhostMode.EATEN
    
    # Test that render_ghost and render_ghosts don't crash
    try:
        renderer.clear_screen()
        
        # Test individual ghost rendering
        renderer.render_ghost(ghosts[0])
        
        # Test multiple ghosts rendering
        renderer.render_ghosts(ghosts)
        
        print("✓ Ghost rendering test passed")
    except Exception as e:
        print(f"✗ Ghost rendering test failed: {e}")
        raise
    finally:
        renderer.cleanup()


def test_ui_rendering():
    """Test UI rendering functionality."""
    print("Testing UI rendering...")
    
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    config = GameConfig()
    renderer = Renderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.TILE_SIZE)
    
    # Create score manager with test data
    score_manager = ScoreManager(starting_lives=config.STARTING_LIVES)
    score_manager.score = 1250
    score_manager.level = 2
    score_manager.initialize_level(100)
    
    # Test that render_ui doesn't crash
    try:
        renderer.clear_screen()
        renderer.render_ui(score_manager)
        print("✓ UI rendering test passed")
    except Exception as e:
        print(f"✗ UI rendering test failed: {e}")
        raise
    finally:
        renderer.cleanup()


def test_screen_rendering():
    """Test different screen rendering functionality."""
    print("Testing screen rendering...")
    
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    config = GameConfig()
    renderer = Renderer(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.TILE_SIZE)
    
    # Test that screen rendering methods don't crash
    try:
        # Test start screen
        renderer.render_start_screen()
        
        # Test game over screen
        renderer.render_game_over_screen(1500)
        
        # Test pause screen
        renderer.render_pause_screen()
        
        print("✓ Screen rendering test passed")
    except Exception as e:
        print(f"✗ Screen rendering test failed: {e}")
        raise
    finally:
        renderer.cleanup()


def main():
    """Run all renderer tests."""
    print("Running Pacman Renderer Unit Tests...")
    print("=" * 50)
    
    try:
        test_renderer_initialization()
        test_maze_rendering()
        test_collectibles_rendering()
        test_player_rendering()
        test_ghost_rendering()
        test_ui_rendering()
        test_screen_rendering()
        
        print("=" * 50)
        print("✓ All renderer tests passed successfully!")
        
    except Exception as e:
        print("=" * 50)
        print(f"✗ Tests failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()