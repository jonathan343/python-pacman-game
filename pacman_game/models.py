"""
Core data models and enums for the Pacman game.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List, Set, Optional
import random
import math


@dataclass
class Position:
    """Represents a position in the game world with pixel coordinates."""
    x: float
    y: float
    
    def to_grid(self, tile_size: int = 20) -> Tuple[int, int]:
        """Convert pixel position to grid coordinates.
        
        Args:
            tile_size: Size of each tile in pixels (default: 20)
            
        Returns:
            Tuple of (grid_x, grid_y) coordinates
        """
        return (int(self.x // tile_size), int(self.y // tile_size))
    
    def from_grid(self, grid_x: int, grid_y: int, tile_size: int = 20) -> 'Position':
        """Create a Position from grid coordinates.
        
        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            tile_size: Size of each tile in pixels (default: 20)
            
        Returns:
            New Position instance
        """
        return Position(grid_x * tile_size, grid_y * tile_size)
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate Euclidean distance to another position.
        
        Args:
            other: Another Position instance
            
        Returns:
            Distance as a float
        """
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def __add__(self, other: 'Position') -> 'Position':
        """Add two positions together."""
        return Position(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Position') -> 'Position':
        """Subtract one position from another."""
        return Position(self.x - other.x, self.y - other.y)


class Direction(Enum):
    """Enum representing movement directions with coordinate deltas."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)
    
    @property
    def dx(self) -> int:
        """Get the X coordinate delta for this direction."""
        return self.value[0]
    
    @property
    def dy(self) -> int:
        """Get the Y coordinate delta for this direction."""
        return self.value[1]
    
    def opposite(self) -> 'Direction':
        """Get the opposite direction.
        
        Returns:
            The opposite Direction enum value
        """
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
            Direction.NONE: Direction.NONE
        }
        return opposites[self]
    
    def is_horizontal(self) -> bool:
        """Check if this direction is horizontal (LEFT or RIGHT)."""
        return self in (Direction.LEFT, Direction.RIGHT)
    
    def is_vertical(self) -> bool:
        """Check if this direction is vertical (UP or DOWN)."""
        return self in (Direction.UP, Direction.DOWN)


class GameState(Enum):
    """Enum representing different game states."""
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    PAUSED = "paused"
    LEVEL_COMPLETE = "level_complete"
    
    def is_active_gameplay(self) -> bool:
        """Check if this state represents active gameplay."""
        return self == GameState.PLAYING
    
    def allows_input(self) -> bool:
        """Check if this state allows player input."""
        return self in (GameState.PLAYING, GameState.MENU)


class GhostMode(Enum):
    """Enum representing different ghost AI modes."""
    NORMAL = "normal"
    FRIGHTENED = "frightened"
    EATEN = "eaten"
    SCATTER = "scatter"
    IN_HOUSE = "in_house"
    EXITING_HOUSE = "exiting_house"
    
    def is_vulnerable(self) -> bool:
        """Check if ghost is vulnerable to being eaten."""
        return self == GhostMode.FRIGHTENED
    
    def is_dangerous(self) -> bool:
        """Check if ghost is dangerous to the player."""
        return self in (GhostMode.NORMAL, GhostMode.SCATTER)


class GhostPersonality(Enum):
    """Enum representing different ghost AI personalities."""
    BLINKY = "blinky"  # Aggressive chaser - directly targets player
    PINKY = "pinky"    # Ambusher - targets ahead of player
    INKY = "inky"      # Flanker - uses complex targeting based on Blinky and player
    SUE = "sue"        # Patrol - switches between chase and scatter frequently
    
    def get_color(self) -> str:
        """Get the default color for this ghost personality."""
        colors = {
            GhostPersonality.BLINKY: "red",
            GhostPersonality.PINKY: "pink", 
            GhostPersonality.INKY: "cyan",
            GhostPersonality.SUE: "orange"
        }
        return colors[self]


class Maze:
    """Represents the game maze with collision detection and navigation methods."""
    
    # Classic Pacman maze layout (simplified version)
    # 0 = path, 1 = wall, 2 = dot, 3 = power pellet, 4 = tunnel
    DEFAULT_LAYOUT = [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
        [1,3,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,3,1],
        [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
        [1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
        [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
        [1,1,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,1,1],
        [0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0],
        [1,1,1,1,1,1,2,1,1,0,1,1,0,0,0,0,1,1,0,1,1,2,1,1,1,1,1,1],
        [4,0,0,0,0,0,2,0,0,0,1,0,0,0,0,0,0,1,0,0,0,2,0,0,0,0,0,4],
        [1,1,1,1,1,1,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,1,1,1,1,1,1],
        [0,0,0,0,0,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,0,0,0,0,0],
        [1,1,1,1,1,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,1,1,1,1,1],
        [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
        [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
        [1,3,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,3,1],
        [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
        [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
        [1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
        [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ]
    
    def __init__(self, tile_size: int = 20):
        """Initialize the maze with default layout.
        
        Args:
            tile_size: Size of each tile in pixels
        """
        self.tile_size = tile_size
        self.layout = [row[:] for row in self.DEFAULT_LAYOUT]  # Deep copy
        self.width = len(self.layout[0])
        self.height = len(self.layout)
        self.dots: Set[Tuple[int, int]] = set()
        self.power_pellets: Set[Tuple[int, int]] = set()
        self._load_collectibles()
    
    def _load_collectibles(self) -> None:
        """Load dots and power pellets from the maze layout."""
        self.dots.clear()
        self.power_pellets.clear()
        
        for y in range(self.height):
            for x in range(self.width):
                if self.layout[y][x] == 2:  # Dot
                    self.dots.add((x, y))
                elif self.layout[y][x] == 3:  # Power pellet
                    self.power_pellets.add((x, y))
    
    def is_wall(self, grid_x: int, grid_y: int) -> bool:
        """Check if the given grid position is a wall.
        
        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            
        Returns:
            True if position is a wall, False otherwise
        """
        if not self._is_valid_position(grid_x, grid_y):
            return True  # Out of bounds is considered a wall
        return self.layout[grid_y][grid_x] == 1
    
    def is_tunnel(self, grid_x: int, grid_y: int) -> bool:
        """Check if the given grid position is a tunnel.
        
        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            
        Returns:
            True if position is a tunnel, False otherwise
        """
        if not self._is_valid_position(grid_x, grid_y):
            return False
        return self.layout[grid_y][grid_x] == 4
    
    def _is_valid_position(self, grid_x: int, grid_y: int) -> bool:
        """Check if grid coordinates are within maze bounds.
        
        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            
        Returns:
            True if position is within bounds, False otherwise
        """
        return 0 <= grid_x < self.width and 0 <= grid_y < self.height
    
    def get_valid_moves(self, position: Position) -> List[Direction]:
        """Get list of valid movement directions from a position.
        
        Args:
            position: Current position
            
        Returns:
            List of valid Direction enums
        """
        grid_x, grid_y = position.to_grid(self.tile_size)
        valid_moves = []
        
        for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            new_x = grid_x + direction.dx
            new_y = grid_y + direction.dy
            
            # Handle tunnel wrapping
            if self.is_tunnel(grid_x, grid_y) and direction.is_horizontal():
                valid_moves.append(direction)
            elif not self.is_wall(new_x, new_y):
                valid_moves.append(direction)
        
        return valid_moves
    
    def can_move(self, position: Position, direction: Direction) -> bool:
        """Check if movement in a direction is valid from a position.
        
        Args:
            position: Current position
            direction: Direction to move
            
        Returns:
            True if movement is valid, False otherwise
        """
        grid_x, grid_y = position.to_grid(self.tile_size)
        new_x = grid_x + direction.dx
        new_y = grid_y + direction.dy
        
        # Handle tunnel wrapping
        if self.is_tunnel(grid_x, grid_y) and direction.is_horizontal():
            return True
        
        return not self.is_wall(new_x, new_y)
    
    def wrap_position(self, position: Position) -> Position:
        """Handle tunnel wrapping for positions.
        
        Args:
            position: Current position
            
        Returns:
            Wrapped position if in tunnel, otherwise original position
        """
        grid_x, grid_y = position.to_grid(self.tile_size)
        
        # Check for horizontal tunnel wrapping
        if grid_x < 0:
            # Wrap to right side
            return Position((self.width - 1) * self.tile_size, position.y)
        elif grid_x >= self.width:
            # Wrap to left side
            return Position(0, position.y)
        
        return position
    
    def has_dot(self, grid_x: int, grid_y: int) -> bool:
        """Check if there's a dot at the given grid position.
        
        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            
        Returns:
            True if there's a dot, False otherwise
        """
        return (grid_x, grid_y) in self.dots
    
    def has_power_pellet(self, grid_x: int, grid_y: int) -> bool:
        """Check if there's a power pellet at the given grid position.
        
        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            
        Returns:
            True if there's a power pellet, False otherwise
        """
        return (grid_x, grid_y) in self.power_pellets
    
    def remove_dot(self, grid_x: int, grid_y: int) -> bool:
        """Remove a dot from the maze.
        
        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            
        Returns:
            True if dot was removed, False if no dot was there
        """
        if (grid_x, grid_y) in self.dots:
            self.dots.remove((grid_x, grid_y))
            return True
        return False
    
    def remove_power_pellet(self, grid_x: int, grid_y: int) -> bool:
        """Remove a power pellet from the maze.
        
        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            
        Returns:
            True if power pellet was removed, False if none was there
        """
        if (grid_x, grid_y) in self.power_pellets:
            self.power_pellets.remove((grid_x, grid_y))
            return True
        return False
    
    def get_dots_remaining(self) -> int:
        """Get the number of dots remaining in the maze.
        
        Returns:
            Number of dots left to collect
        """
        return len(self.dots)
    
    def get_power_pellets_remaining(self) -> int:
        """Get the number of power pellets remaining in the maze.
        
        Returns:
            Number of power pellets left to collect
        """
        return len(self.power_pellets)
    
    def reset_collectibles(self) -> None:
        """Reset all collectibles to their original positions."""
        self._load_collectibles()
    
    def get_pixel_position(self, grid_x: int, grid_y: int) -> Position:
        """Convert grid coordinates to pixel position.
        
        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            
        Returns:
            Position in pixel coordinates
        """
        return Position(grid_x * self.tile_size, grid_y * self.tile_size)


class ScoreManager:
    """Manages game scoring, level progression, and collectible tracking."""
    
    # Point values for different collectibles
    DOT_POINTS = 10
    POWER_PELLET_POINTS = 50
    GHOST_BASE_POINTS = 200
    
    def __init__(self, starting_lives: int = 3):
        """Initialize the score manager.
        
        Args:
            starting_lives: Number of lives to start with
        """
        self.score = 0
        self.level = 1
        self.lives = starting_lives
        self.starting_lives = starting_lives
        self.ghost_eat_multiplier = 1  # Multiplier for consecutive ghost eating
        self.total_dots_in_level = 0
        self.dots_collected_in_level = 0
        self.ghosts_eaten_in_power_mode = 0  # Track consecutive ghost eating
        self.game_over = False
        
    def reset_game(self) -> None:
        """Reset all scoring data for a new game."""
        self.score = 0
        self.level = 1
        self.lives = self.starting_lives
        self.ghost_eat_multiplier = 1
        self.total_dots_in_level = 0
        self.dots_collected_in_level = 0
        self.ghosts_eaten_in_power_mode = 0
        self.game_over = False
    
    def start_new_level(self, total_dots: int) -> None:
        """Start a new level with the given number of dots.
        
        Args:
            total_dots: Total number of dots in the new level
        """
        self.level += 1
        self.total_dots_in_level = total_dots
        self.dots_collected_in_level = 0
        self.ghost_eat_multiplier = 1
    
    def initialize_level(self, total_dots: int) -> None:
        """Initialize the current level with dot count.
        
        Args:
            total_dots: Total number of dots in the level
        """
        self.total_dots_in_level = total_dots
        self.dots_collected_in_level = 0
    
    def collect_dot(self) -> int:
        """Handle dot collection and return points earned.
        
        Returns:
            Points earned from collecting the dot
        """
        self.score += self.DOT_POINTS
        self.dots_collected_in_level += 1
        return self.DOT_POINTS
    
    def collect_power_pellet(self) -> int:
        """Handle power pellet collection and return points earned.
        
        Returns:
            Points earned from collecting the power pellet
        """
        self.score += self.POWER_PELLET_POINTS
        self.ghosts_eaten_in_power_mode = 0  # Reset consecutive ghost counter
        return self.POWER_PELLET_POINTS
    
    def eat_ghost(self) -> int:
        """Handle ghost eating and return points earned.
        
        Returns:
            Points earned from eating the ghost
        """
        # Calculate points based on consecutive ghosts eaten: 200, 400, 800, 1600
        # Cap at 1600 points (multiplier of 8)
        multiplier = min(2 ** self.ghosts_eaten_in_power_mode, 8)  # Cap at 8x multiplier
        points = self.GHOST_BASE_POINTS * multiplier
        self.score += points
        self.ghosts_eaten_in_power_mode += 1
        return points
    
    def lose_life(self) -> bool:
        """Handle losing a life.
        
        Returns:
            True if game over (no lives left), False otherwise
        """
        self.lives -= 1
        self.ghost_eat_multiplier = 1  # Reset multiplier on life loss
        self.ghosts_eaten_in_power_mode = 0  # Reset ghost eating counter
        
        if self.lives <= 0:
            self.game_over = True
            return True
        return False
    
    def is_game_over(self) -> bool:
        """Check if the game is over.
        
        Returns:
            True if game is over, False otherwise
        """
        return self.game_over or self.lives <= 0
    
    def gain_life(self) -> None:
        """Add an extra life (for bonus points, etc.)."""
        self.lives += 1
    
    def is_level_complete(self) -> bool:
        """Check if the current level is complete.
        
        Returns:
            True if all dots have been collected, False otherwise
        """
        return self.dots_collected_in_level >= self.total_dots_in_level
    
    def get_score(self) -> int:
        """Get the current score.
        
        Returns:
            Current score value
        """
        return self.score
    
    def get_level(self) -> int:
        """Get the current level.
        
        Returns:
            Current level number
        """
        return self.level
    
    def get_lives(self) -> int:
        """Get the current number of lives.
        
        Returns:
            Number of lives remaining
        """
        return self.lives
    
    def get_dots_remaining(self) -> int:
        """Get the number of dots remaining in the current level.
        
        Returns:
            Number of dots left to collect
        """
        return max(0, self.total_dots_in_level - self.dots_collected_in_level)
    
    def get_level_progress(self) -> float:
        """Get the completion percentage of the current level.
        
        Returns:
            Percentage of dots collected (0.0 to 1.0)
        """
        if self.total_dots_in_level == 0:
            return 1.0
        return self.dots_collected_in_level / self.total_dots_in_level
    
    def add_bonus_points(self, points: int) -> None:
        """Add bonus points to the score.
        
        Args:
            points: Number of bonus points to add
        """
        self.score += points
    
    def reset_ghost_multiplier(self) -> None:
        """Reset the ghost eating multiplier (when power pellet effect ends)."""
        self.ghost_eat_multiplier = 1
        self.ghosts_eaten_in_power_mode = 0


class Player:
    """Represents the player (Pacman) with movement, collision detection, and animation."""
    
    def __init__(self, start_position: Position, maze: Maze, speed: int = 2):
        """Initialize the player.
        
        Args:
            start_position: Starting position in pixel coordinates
            maze: Reference to the game maze
            speed: Movement speed in pixels per frame
        """
        self.position = Position(start_position.x, start_position.y)
        self.start_position = Position(start_position.x, start_position.y)
        self.maze = maze
        self.speed = speed
        
        # Movement state
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE
        
        # Animation state
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8  # frames per animation frame
        
        # Movement smoothing
        self.target_position = Position(start_position.x, start_position.y)
        self.is_moving = False
    
    def update(self) -> None:
        """Update player state including movement and animation."""
        self._handle_direction_change()
        self._update_movement()
        self._update_animation()
    
    def set_direction(self, new_direction: Direction) -> None:
        """Queue a new movement direction.
        
        Args:
            new_direction: Direction to move in
        """
        self.next_direction = new_direction
    
    def _handle_direction_change(self) -> None:
        """Handle queued direction changes when possible."""
        if self.next_direction == Direction.NONE:
            return
        
        # Check if we can change direction immediately
        if self._can_change_direction():
            self.direction = self.next_direction
            self.next_direction = Direction.NONE
            self._align_to_grid()
    
    def _can_change_direction(self) -> bool:
        """Check if the player can change to the queued direction.
        
        Returns:
            True if direction change is possible, False otherwise
        """
        if self.next_direction == Direction.NONE:
            return False
        
        # Allow immediate direction change if not moving
        if self.direction == Direction.NONE:
            return self.maze.can_move(self.position, self.next_direction)
        
        # Allow opposite direction change immediately
        if self.next_direction == self.direction.opposite():
            return True
        
        # For perpendicular direction changes, check if we're aligned to grid
        if self._is_aligned_to_grid():
            return self.maze.can_move(self.position, self.next_direction)
        
        return False
    
    def _is_aligned_to_grid(self) -> bool:
        """Check if the player is aligned to the grid.
        
        Returns:
            True if aligned to grid, False otherwise
        """
        tile_size = self.maze.tile_size
        return (self.position.x % tile_size == 0 and 
                self.position.y % tile_size == 0)
    
    def _align_to_grid(self) -> None:
        """Align the player position to the nearest grid intersection."""
        tile_size = self.maze.tile_size
        grid_x = round(self.position.x / tile_size)
        grid_y = round(self.position.y / tile_size)
        self.position.x = grid_x * tile_size
        self.position.y = grid_y * tile_size
        self.target_position = Position(self.position.x, self.position.y)
    
    def _update_movement(self) -> None:
        """Update player movement based on current direction."""
        if self.direction == Direction.NONE:
            self.is_moving = False
            return
        
        # Calculate next position
        next_x = self.position.x + (self.direction.dx * self.speed)
        next_y = self.position.y + (self.direction.dy * self.speed)
        next_position = Position(next_x, next_y)
        
        # Check for collision
        if self._would_collide(next_position):
            # Stop at the current position if we hit a wall
            self.direction = Direction.NONE
            self.is_moving = False
            self._align_to_grid()
            return
        
        # Update position
        self.position = next_position
        self.is_moving = True
        
        # Handle tunnel wrapping
        self.position = self.maze.wrap_position(self.position)
    
    def _would_collide(self, position: Position) -> bool:
        """Check if moving to a position would cause a collision.
        
        Args:
            position: Position to check
            
        Returns:
            True if collision would occur, False otherwise
        """
        # Get the grid position we're moving into
        grid_x, grid_y = position.to_grid(self.maze.tile_size)
        
        # Check if we're moving through a tunnel (allow movement beyond boundaries)
        current_grid_x, current_grid_y = self.position.to_grid(self.maze.tile_size)
        if self.maze.is_tunnel(current_grid_x, current_grid_y):
            return False
        
        # Check for wall collision
        if self.maze.is_wall(grid_x, grid_y):
            return True
        
        return False
    
    def _update_animation(self) -> None:
        """Update animation frame based on movement state."""
        if not self.is_moving:
            return
        
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4  # 4 animation frames
    
    def get_grid_position(self) -> Tuple[int, int]:
        """Get the current grid position of the player.
        
        Returns:
            Tuple of (grid_x, grid_y) coordinates
        """
        return self.position.to_grid(self.maze.tile_size)
    
    def collect_item_at_position(self, score_manager: Optional['ScoreManager'] = None) -> Tuple[bool, bool, int]:
        """Check and collect items at the current position.
        
        Args:
            score_manager: Optional ScoreManager instance to update scores
        
        Returns:
            Tuple of (collected_dot, collected_power_pellet, points_earned)
        """
        grid_x, grid_y = self.get_grid_position()
        collected_dot = False
        collected_power_pellet = False
        points_earned = 0
        
        # Check for dot collection
        if self.maze.has_dot(grid_x, grid_y):
            if self.maze.remove_dot(grid_x, grid_y):
                collected_dot = True
                if score_manager:
                    points_earned += score_manager.collect_dot()
                else:
                    points_earned += ScoreManager.DOT_POINTS
        
        # Check for power pellet collection
        if self.maze.has_power_pellet(grid_x, grid_y):
            if self.maze.remove_power_pellet(grid_x, grid_y):
                collected_power_pellet = True
                if score_manager:
                    points_earned += score_manager.collect_power_pellet()
                else:
                    points_earned += ScoreManager.POWER_PELLET_POINTS
        
        return collected_dot, collected_power_pellet, points_earned
    
    def reset_position(self) -> None:
        """Reset player to starting position."""
        self.position = Position(self.start_position.x, self.start_position.y)
        self.target_position = Position(self.start_position.x, self.start_position.y)
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE
        self.is_moving = False
        self.animation_frame = 0
        self.animation_timer = 0
    
    def get_center_position(self) -> Position:
        """Get the center position of the player for collision detection.
        
        Returns:
            Center position of the player
        """
        half_tile = self.maze.tile_size // 2
        return Position(self.position.x + half_tile, self.position.y + half_tile)
    
    def is_at_intersection(self) -> bool:
        """Check if the player is at a grid intersection.
        
        Returns:
            True if at intersection, False otherwise
        """
        return self._is_aligned_to_grid()
    
    def get_valid_directions(self) -> List[Direction]:
        """Get list of valid movement directions from current position.
        
        Returns:
            List of valid Direction enums
        """
        return self.maze.get_valid_moves(self.position)
    
    def check_collision_with_ghost(self, ghost: 'Ghost') -> bool:
        """Check if the player is colliding with a ghost.
        
        Args:
            ghost: Ghost instance to check collision with
            
        Returns:
            True if collision detected, False otherwise
        """
        # Use center positions for more accurate collision detection
        player_center = self.get_center_position()
        ghost_center = ghost.get_center_position()
        
        # Calculate distance between centers
        distance = player_center.distance_to(ghost_center)
        
        # Collision threshold (roughly half a tile size)
        collision_threshold = self.maze.tile_size * 0.6
        
        return distance < collision_threshold
    
    def handle_ghost_collision(self, ghost: 'Ghost', score_manager: 'ScoreManager') -> Tuple[bool, int]:
        """Handle collision with a ghost.
        
        Args:
            ghost: Ghost that was collided with
            score_manager: Score manager to update
            
        Returns:
            Tuple of (life_lost, points_earned)
        """
        if ghost.mode == GhostMode.FRIGHTENED:
            # Player eats the ghost
            points_earned = score_manager.eat_ghost()
            ghost.set_mode(GhostMode.EATEN, duration=180)  # 3 seconds at 60 FPS
            return False, points_earned
        elif ghost.mode == GhostMode.NORMAL:
            # Ghost catches player - lose a life
            game_over = score_manager.lose_life()
            return True, 0
        else:
            # Ghost is eaten or in other state - no collision effect
            return False, 0


class Ghost:
    """Represents a ghost with enhanced AI behavior, movement, and mode management."""
    
    def __init__(self, start_position: Position, maze: Maze, personality: GhostPersonality = GhostPersonality.BLINKY, 
                 speed: int = 2, ghost_house_position: Optional[Position] = None):
        """Initialize the ghost.
        
        Args:
            start_position: Starting position in pixel coordinates
            maze: Reference to the game maze
            personality: Ghost AI personality type
            speed: Movement speed in pixels per frame
            ghost_house_position: Position inside the ghost house (defaults to start_position)
        """
        self.position = Position(start_position.x, start_position.y)
        self.start_position = Position(start_position.x, start_position.y)
        self.ghost_house_position = ghost_house_position or Position(start_position.x, start_position.y)
        self.maze = maze
        self.personality = personality
        self.color = personality.get_color()
        self.speed = speed
        
        # AI and movement state
        self.mode = GhostMode.IN_HOUSE if ghost_house_position else GhostMode.NORMAL
        self.direction = Direction.UP  # Default starting direction
        self.target_position = Position(start_position.x, start_position.y)
        
        # Mode timing and transitions
        self.frightened_timer = 0
        self.eaten_timer = 0
        self.mode_change_timer = 0
        self.scatter_timer = 0
        self.house_exit_timer = 0
        
        # AI behavior state
        self.last_direction_change = 0
        self.direction_change_cooldown = 10  # frames between direction changes
        self.scatter_mode_active = False
        self.dots_eaten_before_exit = 0  # For house exit timing
        
        # Scatter mode corner targets for each personality
        self.scatter_targets = {
            GhostPersonality.BLINKY: Position(25 * maze.tile_size, 0),  # Top right
            GhostPersonality.PINKY: Position(2 * maze.tile_size, 0),   # Top left  
            GhostPersonality.INKY: Position(25 * maze.tile_size, 20 * maze.tile_size),  # Bottom right
            GhostPersonality.SUE: Position(2 * maze.tile_size, 20 * maze.tile_size)    # Bottom left
        }
        
        # Animation state
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 12  # frames per animation frame
        
        # Global mode timing (shared across all ghosts)
        self.global_mode_timer = 0
        self.mode_sequence = [
            (420, GhostMode.SCATTER),  # 7 seconds scatter
            (1200, GhostMode.NORMAL),  # 20 seconds chase
            (420, GhostMode.SCATTER),  # 7 seconds scatter
            (1200, GhostMode.NORMAL),  # 20 seconds chase
            (300, GhostMode.SCATTER),  # 5 seconds scatter
            (1200, GhostMode.NORMAL),  # 20 seconds chase
            (300, GhostMode.SCATTER),  # 5 seconds scatter
            (-1, GhostMode.NORMAL)     # Infinite chase
        ]
        self.current_mode_index = 0
    
    def update(self, player_position: Position, other_ghosts: Optional[List['Ghost']] = None, 
               dots_eaten: int = 0) -> None:
        """Update ghost state including AI, movement, and animation.
        
        Args:
            player_position: Current position of the player for AI targeting
            other_ghosts: List of other ghosts for complex AI behaviors
            dots_eaten: Total dots eaten (for house exit timing)
        """
        self._update_global_mode_timer()
        self._update_mode_timers()
        self._update_house_mechanics(dots_eaten)
        self._update_ai_target(player_position, other_ghosts or [])
        self._update_movement()
        self._update_animation()
    
    def set_mode(self, new_mode: GhostMode, duration: int = 0) -> None:
        """Set the ghost's mode.
        
        Args:
            new_mode: New mode to set
            duration: Duration in frames for timed modes (frightened, eaten)
        """
        old_mode = self.mode
        self.mode = new_mode
        
        if new_mode == GhostMode.FRIGHTENED:
            self.frightened_timer = duration
            # Reverse direction when becoming frightened (unless already frightened)
            if old_mode != GhostMode.FRIGHTENED:
                self.direction = self.direction.opposite()
        elif new_mode == GhostMode.EATEN:
            self.eaten_timer = duration
            # Set target to ghost house for respawn
            self.target_position = Position(self.ghost_house_position.x, self.ghost_house_position.y)
        elif new_mode == GhostMode.NORMAL:
            self.frightened_timer = 0
            self.eaten_timer = 0
        elif new_mode == GhostMode.IN_HOUSE:
            # Reset to house position
            self.position = Position(self.ghost_house_position.x, self.ghost_house_position.y)
            self.house_exit_timer = self._get_house_exit_delay()
        elif new_mode == GhostMode.EXITING_HOUSE:
            # Target the house exit
            self.target_position = Position(self.start_position.x, self.start_position.y)
    
    def _update_mode_timers(self) -> None:
        """Update mode-specific timers and handle mode transitions."""
        if self.mode == GhostMode.FRIGHTENED and self.frightened_timer > 0:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.set_mode(GhostMode.NORMAL)
        
        elif self.mode == GhostMode.EATEN and self.eaten_timer > 0:
            self.eaten_timer -= 1
            if self.eaten_timer <= 0:
                # Return to normal mode when respawn timer expires
                self.set_mode(GhostMode.NORMAL)
                self.position = Position(self.start_position.x, self.start_position.y)
    
    def _update_global_mode_timer(self) -> None:
        """Update the global mode timer and handle scatter/chase transitions."""
        if self.mode in (GhostMode.FRIGHTENED, GhostMode.EATEN, GhostMode.IN_HOUSE, GhostMode.EXITING_HOUSE):
            return  # Don't update global timer during special modes
        
        self.global_mode_timer += 1
        
        # Check if we need to transition to next mode in sequence
        if self.current_mode_index < len(self.mode_sequence):
            duration, target_mode = self.mode_sequence[self.current_mode_index]
            
            if duration > 0 and self.global_mode_timer >= duration:
                # Move to next mode in sequence
                self.current_mode_index += 1
                self.global_mode_timer = 0
                
                # Set the new mode if we haven't reached the end
                if self.current_mode_index < len(self.mode_sequence):
                    _, next_mode = self.mode_sequence[self.current_mode_index]
                    if next_mode != self.mode:  # Only change if different
                        self.set_mode(next_mode)
    
    def _update_house_mechanics(self, dots_eaten: int) -> None:
        """Update ghost house mechanics and exit timing.
        
        Args:
            dots_eaten: Total number of dots eaten in the game
        """
        if self.mode == GhostMode.IN_HOUSE:
            # Check if it's time to exit the house
            exit_threshold = self._get_dot_threshold_for_exit()
            if dots_eaten >= exit_threshold or self.house_exit_timer <= 0:
                self.set_mode(GhostMode.EXITING_HOUSE)
            else:
                self.house_exit_timer -= 1
        
        elif self.mode == GhostMode.EXITING_HOUSE:
            # Check if we've reached the exit position
            if self.position.distance_to(self.start_position) < self.maze.tile_size:
                self.set_mode(GhostMode.NORMAL)
    
    def _get_house_exit_delay(self) -> int:
        """Get the delay before this ghost can exit the house.
        
        Returns:
            Delay in frames before ghost can exit
        """
        delays = {
            GhostPersonality.BLINKY: 0,    # Exits immediately
            GhostPersonality.PINKY: 0,     # Exits immediately  
            GhostPersonality.INKY: 180,   # 3 seconds
            GhostPersonality.SUE: 360     # 6 seconds
        }
        return delays.get(self.personality, 0)
    
    def _get_dot_threshold_for_exit(self) -> int:
        """Get the number of dots that must be eaten before this ghost exits.
        
        Returns:
            Number of dots required for exit
        """
        thresholds = {
            GhostPersonality.BLINKY: 0,   # Exits immediately
            GhostPersonality.PINKY: 0,    # Exits immediately
            GhostPersonality.INKY: 30,    # After 30 dots
            GhostPersonality.SUE: 60      # After 60 dots
        }
        return thresholds.get(self.personality, 0)
    
    def _update_ai_target(self, player_position: Position, other_ghosts: List['Ghost']) -> None:
        """Update the ghost's target position based on current mode and AI personality.
        
        Args:
            player_position: Current position of the player
            other_ghosts: List of other ghosts for complex AI behaviors
        """
        if self.mode == GhostMode.NORMAL:
            self._calculate_chase_target(player_position, other_ghosts)
        elif self.mode == GhostMode.SCATTER:
            self._calculate_scatter_target()
        elif self.mode == GhostMode.FRIGHTENED:
            self._calculate_flee_target(player_position)
        elif self.mode == GhostMode.EATEN:
            # Return to ghost house
            self.target_position = Position(self.ghost_house_position.x, self.ghost_house_position.y)
        elif self.mode == GhostMode.IN_HOUSE:
            # Move around inside the house
            self._calculate_house_patrol_target()
        elif self.mode == GhostMode.EXITING_HOUSE:
            # Target the house exit
            self.target_position = Position(self.start_position.x, self.start_position.y)
    
    def _calculate_chase_target(self, player_position: Position, other_ghosts: List['Ghost']) -> None:
        """Calculate target position for chase mode based on ghost personality.
        
        Args:
            player_position: Current position of the player
            other_ghosts: List of other ghosts for complex AI behaviors
        """
        if self.personality == GhostPersonality.BLINKY:
            # Blinky: Direct chase - target player position
            self.target_position = Position(player_position.x, player_position.y)
        
        elif self.personality == GhostPersonality.PINKY:
            # Pinky: Ambush - target 4 tiles ahead of player
            # Note: In original Pacman, this had a bug with UP direction, but we'll implement it correctly
            player_grid_x, player_grid_y = player_position.to_grid(self.maze.tile_size)
            # Get player's current direction (we'll assume UP for now, this should come from player object)
            target_x = player_grid_x * self.maze.tile_size
            target_y = (player_grid_y - 4) * self.maze.tile_size  # 4 tiles ahead (assuming UP)
            
            # Clamp to maze boundaries
            target_x = max(0, min(target_x, (self.maze.width - 1) * self.maze.tile_size))
            target_y = max(0, min(target_y, (self.maze.height - 1) * self.maze.tile_size))
            
            self.target_position = Position(target_x, target_y)
        
        elif self.personality == GhostPersonality.INKY:
            # Inky: Flanking - complex targeting based on Blinky's position and player
            blinky = None
            for ghost in other_ghosts:
                if ghost.personality == GhostPersonality.BLINKY:
                    blinky = ghost
                    break
            
            if blinky:
                # Vector from Blinky to 2 tiles ahead of player
                player_grid_x, player_grid_y = player_position.to_grid(self.maze.tile_size)
                ahead_x = player_grid_x * self.maze.tile_size
                ahead_y = (player_grid_y - 2) * self.maze.tile_size  # 2 tiles ahead
                
                # Double the vector from Blinky to that point
                dx = ahead_x - blinky.position.x
                dy = ahead_y - blinky.position.y
                
                target_x = blinky.position.x + (dx * 2)
                target_y = blinky.position.y + (dy * 2)
                
                # Clamp to maze boundaries
                target_x = max(0, min(target_x, (self.maze.width - 1) * self.maze.tile_size))
                target_y = max(0, min(target_y, (self.maze.height - 1) * self.maze.tile_size))
                
                self.target_position = Position(target_x, target_y)
            else:
                # Fallback to direct chase if Blinky not found
                self.target_position = Position(player_position.x, player_position.y)
        
        elif self.personality == GhostPersonality.SUE:
            # Sue: Patrol - chase if far from player, scatter if close
            distance_to_player = self.position.distance_to(player_position)
            if distance_to_player > 8 * self.maze.tile_size:  # More than 8 tiles away
                # Chase mode
                self.target_position = Position(player_position.x, player_position.y)
            else:
                # Scatter to corner
                self._calculate_scatter_target()
    
    def _calculate_scatter_target(self) -> None:
        """Calculate target position for scatter mode - go to assigned corner."""
        self.target_position = Position(
            self.scatter_targets[self.personality].x,
            self.scatter_targets[self.personality].y
        )
    
    def _calculate_house_patrol_target(self) -> None:
        """Calculate target for patrolling inside the ghost house."""
        # Simple up-down movement in the house
        house_center_x = self.ghost_house_position.x
        house_top_y = self.ghost_house_position.y - self.maze.tile_size
        house_bottom_y = self.ghost_house_position.y + self.maze.tile_size
        
        # Alternate between top and bottom of house
        if abs(self.position.y - house_top_y) < abs(self.position.y - house_bottom_y):
            self.target_position = Position(house_center_x, house_bottom_y)
        else:
            self.target_position = Position(house_center_x, house_top_y)
    
    def _calculate_flee_target(self, player_position: Position) -> None:
        """Calculate a target position to flee from the player.
        
        Args:
            player_position: Current position of the player
        """
        # Calculate vector away from player
        dx = self.position.x - player_position.x
        dy = self.position.y - player_position.y
        
        # Normalize and extend the flee vector
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            # Extend the flee vector to create a target far from player
            flee_distance = 200  # pixels
            target_x = self.position.x + (dx / distance) * flee_distance
            target_y = self.position.y + (dy / distance) * flee_distance
            
            # Clamp to maze boundaries
            max_x = (self.maze.width - 1) * self.maze.tile_size
            max_y = (self.maze.height - 1) * self.maze.tile_size
            target_x = max(0, min(target_x, max_x))
            target_y = max(0, min(target_y, max_y))
            
            self.target_position = Position(target_x, target_y)
        else:
            # If at same position as player, pick a random corner
            corners = [
                Position(0, 0),
                Position((self.maze.width - 1) * self.maze.tile_size, 0),
                Position(0, (self.maze.height - 1) * self.maze.tile_size),
                Position((self.maze.width - 1) * self.maze.tile_size, 
                        (self.maze.height - 1) * self.maze.tile_size)
            ]
            self.target_position = random.choice(corners)
    
    def _update_movement(self) -> None:
        """Update ghost movement based on AI target and collision detection."""
        # Only change direction at intersections or when blocked
        if self._should_change_direction():
            new_direction = self._choose_best_direction()
            if new_direction != Direction.NONE:
                self.direction = new_direction
                self.last_direction_change = 0
        
        # Move in current direction
        self._move_in_direction()
        
        # Handle tunnel wrapping
        self.position = self.maze.wrap_position(self.position)
        
        # Update direction change cooldown
        self.last_direction_change += 1
    
    def _should_change_direction(self) -> bool:
        """Determine if the ghost should consider changing direction.
        
        Returns:
            True if direction change should be considered, False otherwise
        """
        # Always change direction if blocked
        if not self.maze.can_move(self.position, self.direction):
            return True
        
        # Change direction at intersections (but not too frequently)
        if (self._is_at_intersection() and 
            self.last_direction_change >= self.direction_change_cooldown):
            return True
        
        return False
    
    def _is_at_intersection(self) -> bool:
        """Check if the ghost is at a grid intersection.
        
        Returns:
            True if at intersection, False otherwise
        """
        tile_size = self.maze.tile_size
        return (self.position.x % tile_size == 0 and 
                self.position.y % tile_size == 0)
    
    def _choose_best_direction(self) -> Direction:
        """Choose the best direction to move toward the target.
        
        Returns:
            Best Direction to move, or NONE if no valid moves
        """
        valid_moves = self.maze.get_valid_moves(self.position)
        
        if not valid_moves:
            return Direction.NONE
        
        # Remove opposite direction to prevent immediate reversals (unless it's the only option)
        if len(valid_moves) > 1:
            opposite = self.direction.opposite()
            if opposite in valid_moves:
                valid_moves.remove(opposite)
        
        # In frightened mode, add some randomness to movement
        if self.mode == GhostMode.FRIGHTENED:
            if random.random() < 0.3:  # 30% chance of random movement
                return random.choice(valid_moves)
        
        # Choose direction that gets closest to target
        best_direction = Direction.NONE
        best_distance = float('inf')
        
        for direction in valid_moves:
            # Calculate position after moving in this direction (use speed, not tile_size)
            next_x = self.position.x + (direction.dx * self.speed)
            next_y = self.position.y + (direction.dy * self.speed)
            next_pos = Position(next_x, next_y)
            
            # Calculate distance to target
            distance = next_pos.distance_to(self.target_position)
            
            if distance < best_distance:
                best_distance = distance
                best_direction = direction
        
        return best_direction
    
    def _move_in_direction(self) -> None:
        """Move the ghost in its current direction."""
        if self.direction == Direction.NONE:
            return
        
        # Calculate next position
        next_x = self.position.x + (self.direction.dx * self.speed)
        next_y = self.position.y + (self.direction.dy * self.speed)
        next_position = Position(next_x, next_y)
        
        # Check for collision
        if self._would_collide(next_position):
            # Stop and try to find new direction
            self.direction = Direction.NONE
            return
        
        # Update position
        self.position = next_position
    
    def _would_collide(self, position: Position) -> bool:
        """Check if moving to a position would cause a collision.
        
        Args:
            position: Position to check
            
        Returns:
            True if collision would occur, False otherwise
        """
        # Get the grid position we're moving into
        grid_x, grid_y = position.to_grid(self.maze.tile_size)
        
        # Check if we're moving through a tunnel (allow movement beyond boundaries)
        current_grid_x, current_grid_y = self.position.to_grid(self.maze.tile_size)
        if self.maze.is_tunnel(current_grid_x, current_grid_y):
            return False
        
        # Check for wall collision
        if self.maze.is_wall(grid_x, grid_y):
            return True
        
        return False
    
    def _update_animation(self) -> None:
        """Update animation frame based on movement and mode."""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            
            # Different animation speeds for different modes
            if self.mode == GhostMode.FRIGHTENED:
                self.animation_frame = (self.animation_frame + 1) % 2  # 2 frames for frightened
            else:
                self.animation_frame = (self.animation_frame + 1) % 4  # 4 frames for normal
    
    def get_grid_position(self) -> Tuple[int, int]:
        """Get the current grid position of the ghost.
        
        Returns:
            Tuple of (grid_x, grid_y) coordinates
        """
        return self.position.to_grid(self.maze.tile_size)
    
    def get_center_position(self) -> Position:
        """Get the center position of the ghost for collision detection.
        
        Returns:
            Center position of the ghost
        """
        half_tile = self.maze.tile_size // 2
        return Position(self.position.x + half_tile, self.position.y + half_tile)
    
    def reset_position(self) -> None:
        """Reset ghost to starting position and normal mode."""
        self.position = Position(self.start_position.x, self.start_position.y)
        self.target_position = Position(self.start_position.x, self.start_position.y)
        self.set_mode(GhostMode.NORMAL)
        self.direction = Direction.UP
        self.last_direction_change = 0
        self.animation_frame = 0
        self.animation_timer = 0
    
    def is_vulnerable(self) -> bool:
        """Check if the ghost is vulnerable to being eaten.
        
        Returns:
            True if ghost can be eaten, False otherwise
        """
        return self.mode.is_vulnerable()
    
    def is_dangerous(self) -> bool:
        """Check if the ghost is dangerous to the player.
        
        Returns:
            True if ghost can harm the player, False otherwise
        """
        return self.mode.is_dangerous()
    
    def get_distance_to_player(self, player_position: Position) -> float:
        """Calculate distance to the player.
        
        Args:
            player_position: Current position of the player
            
        Returns:
            Distance to player as a float
        """
        return self.position.distance_to(player_position)
    
    def collides_with_player(self, player_position: Position, collision_radius: float = 10.0) -> bool:
        """Check if the ghost collides with the player.
        
        Args:
            player_position: Current position of the player
            collision_radius: Collision detection radius in pixels
            
        Returns:
            True if collision detected, False otherwise
        """
        distance = self.get_distance_to_player(player_position)
        return distance <= collision_radius


class PowerPelletManager:
    """Manages power pellet effects and ghost interactions."""
    
    # Power pellet effect duration in frames (10 seconds at 60 FPS)
    POWER_PELLET_DURATION = 600
    
    def __init__(self):
        """Initialize the power pellet manager."""
        self.is_active = False
        self.timer = 0
        self.affected_ghosts: List[Ghost] = []
    
    def activate_power_mode(self, ghosts: List[Ghost]) -> None:
        """Activate power pellet mode and set all ghosts to frightened.
        
        Args:
            ghosts: List of ghost instances to affect
        """
        self.is_active = True
        self.timer = self.POWER_PELLET_DURATION
        self.affected_ghosts = ghosts.copy()
        
        # Set all ghosts to frightened mode
        for ghost in self.affected_ghosts:
            if ghost.mode != GhostMode.EATEN:  # Don't affect already eaten ghosts
                ghost.set_mode(GhostMode.FRIGHTENED, duration=self.POWER_PELLET_DURATION)
    
    def update(self) -> bool:
        """Update power pellet timer and handle mode transitions.
        
        Returns:
            True if power mode is still active, False if it ended
        """
        if not self.is_active:
            return False
        
        self.timer -= 1
        
        # Check if power mode should end
        if self.timer <= 0:
            self._deactivate_power_mode()
            return False
        
        return True
    
    def _deactivate_power_mode(self) -> None:
        """Deactivate power pellet mode and return ghosts to normal."""
        self.is_active = False
        self.timer = 0
        
        # Return all non-eaten ghosts to normal mode
        for ghost in self.affected_ghosts:
            if ghost.mode == GhostMode.FRIGHTENED:
                ghost.set_mode(GhostMode.NORMAL)
        
        self.affected_ghosts.clear()
    
    def eat_ghost(self, ghost: Ghost, score_manager: ScoreManager) -> int:
        """Handle ghost eating during power mode.
        
        Args:
            ghost: The ghost being eaten
            score_manager: Score manager to update points
            
        Returns:
            Points earned from eating the ghost
        """
        if not self.is_active or not ghost.is_vulnerable():
            return 0
        
        # Set ghost to eaten mode (3 seconds respawn time at 60 FPS)
        ghost.set_mode(GhostMode.EATEN, duration=180)
        
        # Award points through score manager
        points = score_manager.eat_ghost()
        
        return points
    
    def get_remaining_time(self) -> int:
        """Get remaining power pellet time in frames.
        
        Returns:
            Remaining time in frames, 0 if not active
        """
        return self.timer if self.is_active else 0
    
    def get_remaining_seconds(self) -> float:
        """Get remaining power pellet time in seconds.
        
        Returns:
            Remaining time in seconds, 0.0 if not active
        """
        return (self.timer / 60.0) if self.is_active else 0.0
    
    def is_power_mode_active(self) -> bool:
        """Check if power pellet mode is currently active.
        
        Returns:
            True if power mode is active, False otherwise
        """
        return self.is_active
    
    def force_deactivate(self) -> None:
        """Force deactivate power mode (for game resets, etc.)."""
        if self.is_active:
            self._deactivate_power_mode()
    
    def check_ghost_collision(self, player_position: Position, ghosts: List[Ghost], 
                            score_manager: ScoreManager, collision_radius: float = 10.0) -> Tuple[bool, int]:
        """Check for collisions between player and ghosts, handle eating/death.
        
        Args:
            player_position: Current player position
            ghosts: List of all ghosts
            score_manager: Score manager for point tracking
            collision_radius: Collision detection radius
            
        Returns:
            Tuple of (player_died, points_earned)
        """
        points_earned = 0
        player_died = False
        
        for ghost in ghosts:
            if ghost.collides_with_player(player_position, collision_radius):
                if ghost.is_vulnerable() and self.is_active:
                    # Player eats ghost
                    points_earned = self.eat_ghost(ghost, score_manager)
                    break  # Only process one ghost eating per frame
                elif ghost.is_dangerous():
                    # Ghost kills player
                    player_died = True
                    break  # No need to check other ghosts
        
        return player_died, points_earned


class CollisionManager:
    """Manages collision detection and handling between game entities."""
    
    def __init__(self, collision_radius: float = 12.0):
        """Initialize the collision manager.
        
        Args:
            collision_radius: Collision detection radius in pixels
        """
        self.collision_radius = collision_radius
        self.life_lost_this_frame = False
        self.respawn_timer = 0
        self.respawn_duration = 120  # 2 seconds at 60 FPS
    
    def check_player_ghost_collisions(self, player: Player, ghosts: List[Ghost], 
                                    score_manager: ScoreManager) -> Tuple[bool, int, bool]:
        """Check for collisions between player and all ghosts.
        
        Args:
            player: Player instance
            ghosts: List of ghost instances
            score_manager: Score manager for point tracking
            
        Returns:
            Tuple of (life_lost, points_earned, game_over)
        """
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            return False, 0, False
        
        points_earned = 0
        life_lost = False
        game_over = False
        
        player_center = player.get_center_position()
        
        for ghost in ghosts:
            if self._check_collision(player_center, ghost.get_center_position()):
                if ghost.mode == GhostMode.FRIGHTENED:
                    # Player eats ghost
                    points_earned += score_manager.eat_ghost()
                    ghost.set_mode(GhostMode.EATEN, duration=180)  # 3 seconds respawn
                    break  # Only one ghost can be eaten per frame
                    
                elif ghost.mode == GhostMode.NORMAL:
                    # Ghost catches player
                    life_lost = True
                    game_over = score_manager.lose_life()
                    self._handle_life_loss(player, ghosts)
                    break  # Stop checking other ghosts
        
        return life_lost, points_earned, game_over
    
    def _check_collision(self, pos1: Position, pos2: Position) -> bool:
        """Check if two positions are within collision distance.
        
        Args:
            pos1: First position
            pos2: Second position
            
        Returns:
            True if collision detected, False otherwise
        """
        distance = pos1.distance_to(pos2)
        return distance <= self.collision_radius
    
    def _handle_life_loss(self, player: Player, ghosts: List[Ghost]) -> None:
        """Handle the aftermath of losing a life.
        
        Args:
            player: Player instance to reset
            ghosts: List of ghosts to reset
        """
        # Reset player position
        player.reset_position()
        
        # Reset all ghosts to their starting positions and normal mode
        for ghost in ghosts:
            ghost.reset_position()
        
        # Set respawn timer to prevent immediate collision after respawn
        self.respawn_timer = self.respawn_duration
        self.life_lost_this_frame = True
    
    def is_respawning(self) -> bool:
        """Check if entities are currently in respawn state.
        
        Returns:
            True if in respawn state, False otherwise
        """
        return self.respawn_timer > 0
    
    def get_respawn_time_remaining(self) -> int:
        """Get remaining respawn time in frames.
        
        Returns:
            Remaining respawn time in frames
        """
        return max(0, self.respawn_timer)
    
    def reset(self) -> None:
        """Reset collision manager state."""
        self.life_lost_this_frame = False
        self.respawn_timer = 0
    
    def was_life_lost_this_frame(self) -> bool:
        """Check if a life was lost in the current frame.
        
        Returns:
            True if life was lost this frame, False otherwise
        """
        result = self.life_lost_this_frame
        self.life_lost_this_frame = False  # Reset flag after checking
        return result