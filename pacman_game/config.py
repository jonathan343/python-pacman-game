"""
Game configuration module containing constants and settings.
"""

from dataclasses import dataclass
from enum import Enum


@dataclass
class GameConfig:
    """Main game configuration with all constants and settings."""
    
    # Screen dimensions
    SCREEN_WIDTH: int = 800
    SCREEN_HEIGHT: int = 900
    TILE_SIZE: int = 20
    
    # Game performance
    FPS: int = 60
    
    # Character speeds (pixels per frame)
    PLAYER_SPEED: int = 2
    GHOST_SPEED: int = 2
    
    # Game mechanics
    POWER_PELLET_DURATION: int = 600  # frames (10 seconds at 60 FPS)
    STARTING_LIVES: int = 3
    
    # Scoring
    DOT_POINTS: int = 10
    POWER_PELLET_POINTS: int = 50
    GHOST_BASE_POINTS: int = 200  # First ghost eaten
    
    # Colors (RGB tuples)
    BLACK: tuple = (0, 0, 0)
    WHITE: tuple = (255, 255, 255)
    YELLOW: tuple = (255, 255, 0)
    BLUE: tuple = (0, 0, 255)
    RED: tuple = (255, 0, 0)
    PINK: tuple = (255, 184, 255)
    CYAN: tuple = (0, 255, 255)
    ORANGE: tuple = (255, 184, 82)
    
    # UI positioning
    SCORE_X: int = 10
    SCORE_Y: int = 10
    LIVES_X: int = 10
    LIVES_Y: int = 40
    LEVEL_X: int = 10
    LEVEL_Y: int = 70


class Direction(Enum):
    """Direction enumeration with coordinate deltas."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)


class GameState(Enum):
    """Game state enumeration for state management."""
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    PAUSED = "paused"


class GhostMode(Enum):
    """Ghost AI mode enumeration."""
    CHASE = "chase"
    SCATTER = "scatter"
    FRIGHTENED = "frightened"
    EATEN = "eaten"


# Global configuration instance
CONFIG = GameConfig()