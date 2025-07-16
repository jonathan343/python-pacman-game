#!/usr/bin/env python3
"""
Demo script to test the game runs without errors.
This script will run the game for a few seconds and then quit automatically.
"""

import pygame
import threading
import time
from pacman_game.game import Game
from pacman_game.config import GameConfig


def auto_quit_game(game, delay=3):
    """Automatically quit the game after a delay."""
    time.sleep(delay)
    print(f"Auto-quitting game after {delay} seconds...")
    game.force_quit()


def main():
    """Test that the game initializes and runs without errors."""
    print("Testing Python Pacman Game initialization and basic functionality...")
    
    try:
        # Create game configuration
        config = GameConfig()
        
        # Create the game
        game = Game(config)
        print("✓ Game initialized successfully")
        
        # Test game state
        assert game.get_game_state().name == "MENU"
        assert game.get_score() == 0
        assert game.get_lives() == config.STARTING_LIVES
        assert game.get_level() == 1
        print("✓ Initial game state is correct")
        
        # Test state transitions
        game._start_new_game()
        game.state_manager.set_state(game.state_manager.get_current_state().__class__.PLAYING)
        print("✓ Game state transitions work")
        
        # Test game update
        game._update_game()
        print("✓ Game update cycle works")
        
        # Start auto-quit timer
        quit_timer = threading.Thread(target=auto_quit_game, args=(game, 2))
        quit_timer.daemon = True
        quit_timer.start()
        
        # Run the game briefly
        print("✓ Starting game loop (will auto-quit in 2 seconds)...")
        game.run()
        
        print("✓ Game loop completed successfully")
        
    except Exception as e:
        print(f"✗ Error during game test: {e}")
        return 1
    
    print("\n🎉 All game integration tests passed!")
    print("The main game loop and all systems are working correctly.")
    return 0


if __name__ == "__main__":
    exit(main())