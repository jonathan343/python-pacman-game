"""
Main entry point for the Python Pacman game.
"""

from pacman_game.game import Game
from pacman_game.config import GameConfig


def main():
    """Main function to start the game."""
    try:
        # Create game configuration
        config = GameConfig()
        
        # Create and run the game
        game = Game(config)
        print("Starting Python Pacman Game...")
        print("Use arrow keys to move, P to pause, Q to quit")
        game.run()
        
    except Exception as e:
        print(f"Error starting game: {e}")
        print("Make sure you have installed the requirements: pip install -r requirements.txt")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())