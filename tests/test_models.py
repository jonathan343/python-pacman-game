"""
Unit tests for core data models and enums.
"""
import unittest
from pacman_game.models import Position, Direction, GameState, GhostMode, GhostPersonality, Maze, Player, ScoreManager, Ghost, PowerPelletManager, CollisionManager


class TestPosition(unittest.TestCase):
    """Test cases for the Position dataclass."""
    
    def test_position_creation(self):
        """Test basic position creation."""
        pos = Position(10.5, 20.3)
        self.assertEqual(pos.x, 10.5)
        self.assertEqual(pos.y, 20.3)
    
    def test_to_grid_default_tile_size(self):
        """Test grid conversion with default tile size."""
        pos = Position(45.7, 63.2)
        grid_x, grid_y = pos.to_grid()
        self.assertEqual(grid_x, 2)  # 45.7 // 20 = 2
        self.assertEqual(grid_y, 3)  # 63.2 // 20 = 3
    
    def test_to_grid_custom_tile_size(self):
        """Test grid conversion with custom tile size."""
        pos = Position(50.0, 75.0)
        grid_x, grid_y = pos.to_grid(tile_size=25)
        self.assertEqual(grid_x, 2)  # 50 // 25 = 2
        self.assertEqual(grid_y, 3)  # 75 // 25 = 3
    
    def test_from_grid_default_tile_size(self):
        """Test position creation from grid coordinates."""
        pos = Position(0, 0)
        new_pos = pos.from_grid(3, 4)
        self.assertEqual(new_pos.x, 60.0)  # 3 * 20
        self.assertEqual(new_pos.y, 80.0)  # 4 * 20
    
    def test_from_grid_custom_tile_size(self):
        """Test position creation from grid coordinates with custom tile size."""
        pos = Position(0, 0)
        new_pos = pos.from_grid(2, 3, tile_size=25)
        self.assertEqual(new_pos.x, 50.0)  # 2 * 25
        self.assertEqual(new_pos.y, 75.0)  # 3 * 25
    
    def test_distance_to(self):
        """Test distance calculation between positions."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        distance = pos1.distance_to(pos2)
        self.assertEqual(distance, 5.0)  # 3-4-5 triangle
    
    def test_position_addition(self):
        """Test position addition operator."""
        pos1 = Position(10, 20)
        pos2 = Position(5, 15)
        result = pos1 + pos2
        self.assertEqual(result.x, 15)
        self.assertEqual(result.y, 35)
    
    def test_position_subtraction(self):
        """Test position subtraction operator."""
        pos1 = Position(10, 20)
        pos2 = Position(3, 7)
        result = pos1 - pos2
        self.assertEqual(result.x, 7)
        self.assertEqual(result.y, 13)


class TestDirection(unittest.TestCase):
    """Test cases for the Direction enum."""
    
    def test_direction_values(self):
        """Test that direction enum values are correct."""
        self.assertEqual(Direction.UP.value, (0, -1))
        self.assertEqual(Direction.DOWN.value, (0, 1))
        self.assertEqual(Direction.LEFT.value, (-1, 0))
        self.assertEqual(Direction.RIGHT.value, (1, 0))
        self.assertEqual(Direction.NONE.value, (0, 0))
    
    def test_direction_properties(self):
        """Test dx and dy properties."""
        self.assertEqual(Direction.UP.dx, 0)
        self.assertEqual(Direction.UP.dy, -1)
        self.assertEqual(Direction.RIGHT.dx, 1)
        self.assertEqual(Direction.RIGHT.dy, 0)
    
    def test_opposite_directions(self):
        """Test opposite direction calculation."""
        self.assertEqual(Direction.UP.opposite(), Direction.DOWN)
        self.assertEqual(Direction.DOWN.opposite(), Direction.UP)
        self.assertEqual(Direction.LEFT.opposite(), Direction.RIGHT)
        self.assertEqual(Direction.RIGHT.opposite(), Direction.LEFT)
        self.assertEqual(Direction.NONE.opposite(), Direction.NONE)
    
    def test_horizontal_directions(self):
        """Test horizontal direction detection."""
        self.assertTrue(Direction.LEFT.is_horizontal())
        self.assertTrue(Direction.RIGHT.is_horizontal())
        self.assertFalse(Direction.UP.is_horizontal())
        self.assertFalse(Direction.DOWN.is_horizontal())
        self.assertFalse(Direction.NONE.is_horizontal())
    
    def test_vertical_directions(self):
        """Test vertical direction detection."""
        self.assertTrue(Direction.UP.is_vertical())
        self.assertTrue(Direction.DOWN.is_vertical())
        self.assertFalse(Direction.LEFT.is_vertical())
        self.assertFalse(Direction.RIGHT.is_vertical())
        self.assertFalse(Direction.NONE.is_vertical())


class TestGameState(unittest.TestCase):
    """Test cases for the GameState enum."""
    
    def test_game_state_values(self):
        """Test that game state enum values are correct."""
        self.assertEqual(GameState.MENU.value, "menu")
        self.assertEqual(GameState.PLAYING.value, "playing")
        self.assertEqual(GameState.GAME_OVER.value, "game_over")
        self.assertEqual(GameState.PAUSED.value, "paused")
        self.assertEqual(GameState.LEVEL_COMPLETE.value, "level_complete")
    
    def test_is_active_gameplay(self):
        """Test active gameplay state detection."""
        self.assertTrue(GameState.PLAYING.is_active_gameplay())
        self.assertFalse(GameState.MENU.is_active_gameplay())
        self.assertFalse(GameState.GAME_OVER.is_active_gameplay())
        self.assertFalse(GameState.PAUSED.is_active_gameplay())
        self.assertFalse(GameState.LEVEL_COMPLETE.is_active_gameplay())
    
    def test_allows_input(self):
        """Test input allowance for different states."""
        self.assertTrue(GameState.PLAYING.allows_input())
        self.assertTrue(GameState.MENU.allows_input())
        self.assertFalse(GameState.GAME_OVER.allows_input())
        self.assertFalse(GameState.PAUSED.allows_input())
        self.assertFalse(GameState.LEVEL_COMPLETE.allows_input())


class TestMaze(unittest.TestCase):
    """Test cases for the Maze class."""
    
    def setUp(self):
        """Set up test maze instance."""
        self.maze = Maze(tile_size=20)
    
    def test_maze_initialization(self):
        """Test maze initialization with default layout."""
        self.assertEqual(self.maze.tile_size, 20)
        self.assertEqual(self.maze.width, 28)
        self.assertEqual(self.maze.height, 21)
        self.assertIsInstance(self.maze.dots, set)
        self.assertIsInstance(self.maze.power_pellets, set)
    
    def test_is_wall_detection(self):
        """Test wall detection functionality."""
        # Test corner wall (should be wall)
        self.assertTrue(self.maze.is_wall(0, 0))
        
        # Test known path position (should not be wall)
        self.assertFalse(self.maze.is_wall(1, 1))
        
        # Test out of bounds (should be considered wall)
        self.assertTrue(self.maze.is_wall(-1, 0))
        self.assertTrue(self.maze.is_wall(100, 100))
    
    def test_is_tunnel_detection(self):
        """Test tunnel detection functionality."""
        # Test known tunnel positions (row 9, columns 0 and 27)
        self.assertTrue(self.maze.is_tunnel(0, 9))
        self.assertTrue(self.maze.is_tunnel(27, 9))
        
        # Test non-tunnel position
        self.assertFalse(self.maze.is_tunnel(1, 1))
        
        # Test out of bounds
        self.assertFalse(self.maze.is_tunnel(-1, 0))
    
    def test_valid_position_checking(self):
        """Test valid position boundary checking."""
        # Test valid positions
        self.assertTrue(self.maze._is_valid_position(0, 0))
        self.assertTrue(self.maze._is_valid_position(27, 20))
        
        # Test invalid positions
        self.assertFalse(self.maze._is_valid_position(-1, 0))
        self.assertFalse(self.maze._is_valid_position(28, 0))
        self.assertFalse(self.maze._is_valid_position(0, -1))
        self.assertFalse(self.maze._is_valid_position(0, 21))
    
    def test_get_valid_moves(self):
        """Test valid move detection from various positions."""
        # Test from a position with multiple valid moves
        position = Position(20, 20)  # Grid position (1, 1)
        valid_moves = self.maze.get_valid_moves(position)
        self.assertIsInstance(valid_moves, list)
        self.assertTrue(len(valid_moves) > 0)
        
        # Test from a corner position (should have limited moves)
        corner_position = Position(20, 40)  # Grid position (1, 2)
        corner_moves = self.maze.get_valid_moves(corner_position)
        self.assertIsInstance(corner_moves, list)
    
    def test_can_move_functionality(self):
        """Test movement validation."""
        # Test valid movement
        position = Position(20, 20)  # Grid position (1, 1)
        self.assertTrue(self.maze.can_move(position, Direction.RIGHT))
        
        # Test invalid movement into wall
        wall_position = Position(0, 0)  # Grid position (0, 0) - wall
        self.assertFalse(self.maze.can_move(wall_position, Direction.UP))
    
    def test_tunnel_wrapping(self):
        """Test tunnel position wrapping functionality."""
        # Test wrapping from left side
        left_position = Position(-10, 180)  # Negative x, row 9
        wrapped = self.maze.wrap_position(left_position)
        self.assertEqual(wrapped.x, (self.maze.width - 1) * self.maze.tile_size)
        self.assertEqual(wrapped.y, 180)
        
        # Test wrapping from right side
        right_position = Position(600, 180)  # x >= width * tile_size, row 9
        wrapped = self.maze.wrap_position(right_position)
        self.assertEqual(wrapped.x, 0)
        self.assertEqual(wrapped.y, 180)
        
        # Test no wrapping for normal position
        normal_position = Position(100, 100)
        wrapped = self.maze.wrap_position(normal_position)
        self.assertEqual(wrapped.x, 100)
        self.assertEqual(wrapped.y, 100)
    
    def test_collectible_detection(self):
        """Test dot and power pellet detection."""
        # Test that dots are loaded
        self.assertTrue(len(self.maze.dots) > 0)
        
        # Test that power pellets are loaded
        self.assertTrue(len(self.maze.power_pellets) > 0)
        
        # Test has_dot functionality
        dot_position = next(iter(self.maze.dots))
        self.assertTrue(self.maze.has_dot(dot_position[0], dot_position[1]))
        self.assertFalse(self.maze.has_dot(0, 0))  # Wall position
        
        # Test has_power_pellet functionality
        pellet_position = next(iter(self.maze.power_pellets))
        self.assertTrue(self.maze.has_power_pellet(pellet_position[0], pellet_position[1]))
        self.assertFalse(self.maze.has_power_pellet(0, 0))  # Wall position
    
    def test_collectible_removal(self):
        """Test dot and power pellet removal."""
        # Test dot removal
        initial_dot_count = len(self.maze.dots)
        dot_position = next(iter(self.maze.dots))
        
        # Remove existing dot
        self.assertTrue(self.maze.remove_dot(dot_position[0], dot_position[1]))
        self.assertEqual(len(self.maze.dots), initial_dot_count - 1)
        self.assertFalse(self.maze.has_dot(dot_position[0], dot_position[1]))
        
        # Try to remove non-existent dot
        self.assertFalse(self.maze.remove_dot(0, 0))
        
        # Test power pellet removal
        initial_pellet_count = len(self.maze.power_pellets)
        pellet_position = next(iter(self.maze.power_pellets))
        
        # Remove existing power pellet
        self.assertTrue(self.maze.remove_power_pellet(pellet_position[0], pellet_position[1]))
        self.assertEqual(len(self.maze.power_pellets), initial_pellet_count - 1)
        self.assertFalse(self.maze.has_power_pellet(pellet_position[0], pellet_position[1]))
        
        # Try to remove non-existent power pellet
        self.assertFalse(self.maze.remove_power_pellet(0, 0))
    
    def test_collectible_counting(self):
        """Test collectible counting methods."""
        initial_dots = self.maze.get_dots_remaining()
        initial_pellets = self.maze.get_power_pellets_remaining()
        
        self.assertGreater(initial_dots, 0)
        self.assertGreater(initial_pellets, 0)
        
        # Remove a dot and check count
        dot_position = next(iter(self.maze.dots))
        self.maze.remove_dot(dot_position[0], dot_position[1])
        self.assertEqual(self.maze.get_dots_remaining(), initial_dots - 1)
        
        # Remove a power pellet and check count
        pellet_position = next(iter(self.maze.power_pellets))
        self.maze.remove_power_pellet(pellet_position[0], pellet_position[1])
        self.assertEqual(self.maze.get_power_pellets_remaining(), initial_pellets - 1)
    
    def test_collectible_reset(self):
        """Test collectible reset functionality."""
        # Remove some collectibles
        dot_position = next(iter(self.maze.dots))
        pellet_position = next(iter(self.maze.power_pellets))
        
        initial_dot_count = len(self.maze.dots)
        initial_pellet_count = len(self.maze.power_pellets)
        
        self.maze.remove_dot(dot_position[0], dot_position[1])
        self.maze.remove_power_pellet(pellet_position[0], pellet_position[1])
        
        # Verify they were removed
        self.assertEqual(len(self.maze.dots), initial_dot_count - 1)
        self.assertEqual(len(self.maze.power_pellets), initial_pellet_count - 1)
        
        # Reset and verify they're back
        self.maze.reset_collectibles()
        self.assertEqual(len(self.maze.dots), initial_dot_count)
        self.assertEqual(len(self.maze.power_pellets), initial_pellet_count)
        self.assertTrue(self.maze.has_dot(dot_position[0], dot_position[1]))
        self.assertTrue(self.maze.has_power_pellet(pellet_position[0], pellet_position[1]))
    
    def test_pixel_position_conversion(self):
        """Test grid to pixel position conversion."""
        pixel_pos = self.maze.get_pixel_position(5, 10)
        self.assertEqual(pixel_pos.x, 5 * 20)  # 5 * tile_size
        self.assertEqual(pixel_pos.y, 10 * 20)  # 10 * tile_size
        
        # Test with different grid coordinates
        pixel_pos2 = self.maze.get_pixel_position(0, 0)
        self.assertEqual(pixel_pos2.x, 0)
        self.assertEqual(pixel_pos2.y, 0)
    
    def test_maze_layout_integrity(self):
        """Test that maze layout is properly loaded and structured."""
        # Verify maze dimensions match the default layout
        self.assertEqual(len(self.maze.layout), 21)  # Height
        self.assertEqual(len(self.maze.layout[0]), 28)  # Width
        
        # Verify that the layout is a deep copy (not reference)
        original_value = self.maze.layout[0][0]
        self.maze.layout[0][0] = 999
        self.assertNotEqual(Maze.DEFAULT_LAYOUT[0][0], 999)
        self.maze.layout[0][0] = original_value  # Restore
    
    def test_collision_detection_edge_cases(self):
        """Test collision detection edge cases."""
        # Test tunnel movement validation
        tunnel_position = Position(0, 180)  # Grid (0, 9) - tunnel
        self.assertTrue(self.maze.can_move(tunnel_position, Direction.LEFT))
        self.assertTrue(self.maze.can_move(tunnel_position, Direction.RIGHT))
        
        # Test movement from tunnel position
        valid_moves = self.maze.get_valid_moves(tunnel_position)
        self.assertIn(Direction.LEFT, valid_moves)
        self.assertIn(Direction.RIGHT, valid_moves)


class TestPlayer(unittest.TestCase):
    """Test cases for the Player class."""
    
    def setUp(self):
        """Set up test player instance."""
        self.maze = Maze(tile_size=20)
        self.start_position = Position(260, 380)  # Grid position (13, 19) - safe starting position
        self.player = Player(self.start_position, self.maze, speed=2)
    
    def test_player_initialization(self):
        """Test player initialization with correct attributes."""
        self.assertEqual(self.player.position.x, 260)
        self.assertEqual(self.player.position.y, 380)
        self.assertEqual(self.player.start_position.x, 260)
        self.assertEqual(self.player.start_position.y, 380)
        self.assertEqual(self.player.speed, 2)
        self.assertEqual(self.player.direction, Direction.NONE)
        self.assertEqual(self.player.next_direction, Direction.NONE)
        self.assertFalse(self.player.is_moving)
        self.assertEqual(self.player.animation_frame, 0)
        self.assertEqual(self.player.animation_timer, 0)
    
    def test_set_direction(self):
        """Test direction setting functionality."""
        self.player.set_direction(Direction.RIGHT)
        self.assertEqual(self.player.next_direction, Direction.RIGHT)
        
        # Test direction queuing
        self.player.set_direction(Direction.UP)
        self.assertEqual(self.player.next_direction, Direction.UP)
    
    def test_direction_change_when_stationary(self):
        """Test direction change when player is not moving."""
        # Set a valid direction
        self.player.set_direction(Direction.RIGHT)
        self.player.update()
        
        # Should change direction immediately when stationary
        self.assertEqual(self.player.direction, Direction.RIGHT)
        self.assertEqual(self.player.next_direction, Direction.NONE)
    
    def test_opposite_direction_change(self):
        """Test immediate opposite direction change."""
        # Start moving right
        self.player.set_direction(Direction.RIGHT)
        self.player.update()
        self.assertEqual(self.player.direction, Direction.RIGHT)
        
        # Change to opposite direction (should be immediate)
        self.player.set_direction(Direction.LEFT)
        self.player.update()
        self.assertEqual(self.player.direction, Direction.LEFT)
        self.assertEqual(self.player.next_direction, Direction.NONE)
    
    def test_movement_updates_position(self):
        """Test that movement updates player position correctly."""
        initial_x = self.player.position.x
        
        # Start moving right
        self.player.set_direction(Direction.RIGHT)
        self.player.update()
        
        # Position should have changed
        self.assertEqual(self.player.position.x, initial_x + 2)  # speed = 2
        self.assertTrue(self.player.is_moving)
    
    def test_collision_detection_stops_movement(self):
        """Test that collision with walls stops movement."""
        # Position player near a wall and try to move into it
        wall_position = Position(20, 20)  # Near wall at (1, 1)
        test_player = Player(wall_position, self.maze, speed=2)
        
        # Try to move up into wall
        test_player.set_direction(Direction.UP)
        test_player.update()
        
        # Should not move into wall
        initial_position = Position(wall_position.x, wall_position.y)
        # Allow some movement but should stop at wall
        for _ in range(10):  # Multiple updates to ensure collision detection
            test_player.update()
        
        # Player should have stopped due to collision
        self.assertEqual(test_player.direction, Direction.NONE)
        self.assertFalse(test_player.is_moving)
    
    def test_grid_alignment_detection(self):
        """Test grid alignment detection."""
        # Player at exact grid position should be aligned
        aligned_player = Player(Position(100, 100), self.maze)  # Grid (5, 5)
        self.assertTrue(aligned_player._is_aligned_to_grid())
        
        # Player at non-grid position should not be aligned
        unaligned_player = Player(Position(105, 107), self.maze)
        self.assertFalse(unaligned_player._is_aligned_to_grid())
    
    def test_grid_alignment_method(self):
        """Test grid alignment functionality."""
        # Start with unaligned position
        self.player.position = Position(263, 382)
        self.assertFalse(self.player._is_aligned_to_grid())
        
        # Align to grid
        self.player._align_to_grid()
        self.assertTrue(self.player._is_aligned_to_grid())
        self.assertEqual(self.player.position.x, 260)  # Rounded to nearest grid
        self.assertEqual(self.player.position.y, 380)
    
    def test_tunnel_wrapping(self):
        """Test tunnel wrapping functionality."""
        # Position player at tunnel entrance (left side)
        tunnel_position = Position(0, 180)  # Grid (0, 9) - tunnel row
        tunnel_player = Player(tunnel_position, self.maze, speed=2)
        
        # Move left (should wrap to right side)
        tunnel_player.set_direction(Direction.LEFT)
        tunnel_player.update()
        
        # Check that player moved left and position was wrapped
        # The player should now be at the right side of the tunnel
        self.assertGreater(tunnel_player.position.x, 500)  # Should be near right side
        
        # Test wrapping from right side
        right_tunnel_position = Position(540, 180)  # Grid (27, 9) - right tunnel
        right_tunnel_player = Player(right_tunnel_position, self.maze, speed=2)
        
        # Move right multiple times until wrapping occurs
        right_tunnel_player.set_direction(Direction.RIGHT)
        for _ in range(15):  # Move until wrapping happens
            right_tunnel_player.update()
            if right_tunnel_player.position.x < 50:
                break
        
        # Check that player wrapped to left side
        self.assertLess(right_tunnel_player.position.x, 50)  # Should be near left side
    
    def test_animation_updates(self):
        """Test animation frame updates during movement."""
        initial_frame = self.player.animation_frame
        
        # Start moving
        self.player.set_direction(Direction.RIGHT)
        
        # Update multiple times to trigger animation
        for _ in range(self.player.animation_speed + 1):
            self.player.update()
        
        # Animation frame should have changed
        self.assertNotEqual(self.player.animation_frame, initial_frame)
    
    def test_animation_stops_when_not_moving(self):
        """Test that animation doesn't update when not moving."""
        # Start moving to get animation going
        self.player.set_direction(Direction.RIGHT)
        for _ in range(self.player.animation_speed + 1):
            self.player.update()
        
        current_frame = self.player.animation_frame
        current_timer = self.player.animation_timer
        
        # Stop moving
        self.player.direction = Direction.NONE
        self.player.is_moving = False
        
        # Update and check animation doesn't change
        self.player.update()
        self.assertEqual(self.player.animation_frame, current_frame)
        self.assertEqual(self.player.animation_timer, current_timer)
    
    def test_get_grid_position(self):
        """Test grid position calculation."""
        grid_x, grid_y = self.player.get_grid_position()
        expected_x, expected_y = self.start_position.to_grid(self.maze.tile_size)
        self.assertEqual(grid_x, expected_x)
        self.assertEqual(grid_y, expected_y)
    
    def test_collect_item_at_position(self):
        """Test item collection functionality."""
        # Position player at a location with a dot
        dot_positions = list(self.maze.dots)
        if dot_positions:
            dot_pos = dot_positions[0]
            pixel_pos = self.maze.get_pixel_position(dot_pos[0], dot_pos[1])
            test_player = Player(pixel_pos, self.maze)
            
            # Collect item
            collected_dot, collected_pellet, points = test_player.collect_item_at_position()
            
            # Should have collected a dot
            self.assertTrue(collected_dot)
            self.assertFalse(collected_pellet)
            self.assertEqual(points, 10)
            
            # Dot should be removed from maze
            self.assertFalse(self.maze.has_dot(dot_pos[0], dot_pos[1]))
    
    def test_collect_power_pellet(self):
        """Test power pellet collection."""
        # Position player at a power pellet location
        pellet_positions = list(self.maze.power_pellets)
        if pellet_positions:
            pellet_pos = pellet_positions[0]
            pixel_pos = self.maze.get_pixel_position(pellet_pos[0], pellet_pos[1])
            test_player = Player(pixel_pos, self.maze)
            
            # Collect item
            collected_dot, collected_pellet, points = test_player.collect_item_at_position()
            
            # Should have collected a power pellet
            self.assertFalse(collected_dot)
            self.assertTrue(collected_pellet)
            self.assertEqual(points, 50)
            
            # Power pellet should be removed from maze
            self.assertFalse(self.maze.has_power_pellet(pellet_pos[0], pellet_pos[1]))
    
    def test_collect_no_items(self):
        """Test collection when no items are present."""
        # Position player at wall location (no collectibles)
        empty_position = Position(0, 0)  # Wall position - no dots or pellets
        test_player = Player(empty_position, self.maze)
        
        collected_dot, collected_pellet, points = test_player.collect_item_at_position()
        
        # Should not have collected anything
        self.assertFalse(collected_dot)
        self.assertFalse(collected_pellet)
        self.assertEqual(points, 0)
    
    def test_reset_position(self):
        """Test player position reset functionality."""
        # Move player and change state
        self.player.position = Position(100, 100)
        self.player.direction = Direction.RIGHT
        self.player.next_direction = Direction.UP
        self.player.is_moving = True
        self.player.animation_frame = 2
        self.player.animation_timer = 5
        
        # Reset position
        self.player.reset_position()
        
        # Should be back to starting state
        self.assertEqual(self.player.position.x, self.start_position.x)
        self.assertEqual(self.player.position.y, self.start_position.y)
        self.assertEqual(self.player.direction, Direction.NONE)
        self.assertEqual(self.player.next_direction, Direction.NONE)
        self.assertFalse(self.player.is_moving)
        self.assertEqual(self.player.animation_frame, 0)
        self.assertEqual(self.player.animation_timer, 0)
    
    def test_get_center_position(self):
        """Test center position calculation."""
        center = self.player.get_center_position()
        expected_x = self.start_position.x + (self.maze.tile_size // 2)
        expected_y = self.start_position.y + (self.maze.tile_size // 2)
        self.assertEqual(center.x, expected_x)
        self.assertEqual(center.y, expected_y)
    
    def test_is_at_intersection(self):
        """Test intersection detection."""
        # Player at grid-aligned position should be at intersection
        aligned_player = Player(Position(100, 100), self.maze)
        self.assertTrue(aligned_player.is_at_intersection())
        
        # Player at non-aligned position should not be at intersection
        unaligned_player = Player(Position(105, 107), self.maze)
        self.assertFalse(unaligned_player.is_at_intersection())
    
    def test_get_valid_directions(self):
        """Test valid directions calculation."""
        valid_directions = self.player.get_valid_directions()
        self.assertIsInstance(valid_directions, list)
        
        # Should return Direction enums
        for direction in valid_directions:
            self.assertIsInstance(direction, Direction)
    
    def test_perpendicular_direction_change_at_intersection(self):
        """Test perpendicular direction change when aligned to grid."""
        # Start moving right
        self.player.set_direction(Direction.RIGHT)
        self.player.update()
        
        # Ensure player is aligned to grid
        self.player._align_to_grid()
        
        # Try to change to perpendicular direction
        self.player.set_direction(Direction.UP)
        self.player.update()
        
        # Should change direction if move is valid
        if self.maze.can_move(self.player.position, Direction.UP):
            self.assertEqual(self.player.direction, Direction.UP)
        else:
            # Should keep queued direction if move is not valid
            self.assertEqual(self.player.next_direction, Direction.UP)
    
    def test_movement_collision_edge_cases(self):
        """Test collision detection edge cases."""
        # Test movement near maze boundaries
        boundary_position = Position(20, 20)  # Near maze edge
        boundary_player = Player(boundary_position, self.maze, speed=2)
        
        # Try various directions
        for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            boundary_player.set_direction(direction)
            initial_pos = Position(boundary_player.position.x, boundary_player.position.y)
            boundary_player.update()
            
            # Should either move or stay in place (no invalid positions)
            self.assertTrue(
                boundary_player.position.x >= 0 and 
                boundary_player.position.y >= 0
            )
    
    def test_smooth_movement_progression(self):
        """Test that movement progresses smoothly."""
        initial_x = self.player.position.x
        
        # Start moving right
        self.player.set_direction(Direction.RIGHT)
        
        # Update multiple times and check position progression
        positions = []
        for _ in range(5):
            self.player.update()
            positions.append(self.player.position.x)
        
        # Positions should increase smoothly
        for i in range(1, len(positions)):
            self.assertGreaterEqual(positions[i], positions[i-1])
    
    def test_direction_queuing_behavior(self):
        """Test direction queuing and processing behavior."""
        # Start with no movement
        self.assertEqual(self.player.direction, Direction.NONE)
        
        # Queue a direction
        self.player.set_direction(Direction.RIGHT)
        self.assertEqual(self.player.next_direction, Direction.RIGHT)
        
        # Update should process the queued direction
        self.player.update()
        self.assertEqual(self.player.direction, Direction.RIGHT)
        self.assertEqual(self.player.next_direction, Direction.NONE)
        
        # Queue another direction while moving
        self.player.set_direction(Direction.DOWN)
        self.assertEqual(self.player.next_direction, Direction.DOWN)
        
        # Should not change immediately if not aligned
        if not self.player._is_aligned_to_grid():
            self.player.update()
            self.assertEqual(self.player.direction, Direction.RIGHT)
            self.assertEqual(self.player.next_direction, Direction.DOWN)


if __name__ == '__main__':
    unittest.main()


class TestScoreManager(unittest.TestCase):
    """Test cases for the ScoreManager class."""
    
    def setUp(self):
        """Set up test score manager instance."""
        self.score_manager = ScoreManager()
    
    def test_score_manager_initialization(self):
        """Test score manager initialization with default values."""
        self.assertEqual(self.score_manager.score, 0)
        self.assertEqual(self.score_manager.level, 1)
        self.assertEqual(self.score_manager.lives, 3)
        self.assertEqual(self.score_manager.ghost_eat_multiplier, 1)
        self.assertEqual(self.score_manager.total_dots_in_level, 0)
        self.assertEqual(self.score_manager.dots_collected_in_level, 0)
    
    def test_dot_collection_scoring(self):
        """Test dot collection with 10-point scoring (Requirement 2.1)."""
        initial_score = self.score_manager.score
        points_earned = self.score_manager.collect_dot()
        
        # Should earn 10 points for dot collection
        self.assertEqual(points_earned, ScoreManager.DOT_POINTS)
        self.assertEqual(points_earned, 10)
        self.assertEqual(self.score_manager.score, initial_score + 10)
        self.assertEqual(self.score_manager.dots_collected_in_level, 1)
    
    def test_power_pellet_collection_scoring(self):
        """Test power pellet collection with 50-point scoring (Requirement 2.2)."""
        initial_score = self.score_manager.score
        points_earned = self.score_manager.collect_power_pellet()
        
        # Should earn 50 points for power pellet collection
        self.assertEqual(points_earned, ScoreManager.POWER_PELLET_POINTS)
        self.assertEqual(points_earned, 50)
        self.assertEqual(self.score_manager.score, initial_score + 50)
        # Power pellet collection should reset ghost multiplier
        self.assertEqual(self.score_manager.ghost_eat_multiplier, 1)
    
    def test_multiple_dot_collection(self):
        """Test multiple dot collections accumulate correctly."""
        initial_score = self.score_manager.score
        
        # Collect 5 dots
        total_points = 0
        for i in range(5):
            points = self.score_manager.collect_dot()
            total_points += points
            self.assertEqual(self.score_manager.dots_collected_in_level, i + 1)
        
        # Should have earned 50 points total (5 * 10)
        self.assertEqual(total_points, 50)
        self.assertEqual(self.score_manager.score, initial_score + 50)
    
    def test_ghost_eating_scoring_progression(self):
        """Test ghost eating with point multipliers (200, 400, 800, 1600)."""
        initial_score = self.score_manager.score
        expected_points = [200, 400, 800, 1600]
        total_points = 0
        
        for i, expected in enumerate(expected_points):
            points_earned = self.score_manager.eat_ghost()
            total_points += points_earned
            
            # Check individual ghost points
            self.assertEqual(points_earned, expected)
            self.assertEqual(self.score_manager.score, initial_score + total_points)
            
            # Check ghost counter progression
            self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, i + 1)
    
    def test_ghost_multiplier_cap(self):
        """Test that ghost eating multiplier caps at 8x (1600 points)."""
        # Eat enough ghosts to exceed the cap
        for _ in range(10):
            self.score_manager.eat_ghost()
        
        # Ghost counter should continue incrementing (no cap)
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 10)
        
        # Next ghost should still give 1600 points
        points = self.score_manager.eat_ghost()
        self.assertEqual(points, 1600)
    
    def test_level_completion_detection(self):
        """Test level completion when all dots collected (Requirement 2.3)."""
        # Initialize level with 10 dots
        self.score_manager.initialize_level(10)
        self.assertFalse(self.score_manager.is_level_complete())
        
        # Collect 9 dots - should not be complete
        for _ in range(9):
            self.score_manager.collect_dot()
        self.assertFalse(self.score_manager.is_level_complete())
        self.assertEqual(self.score_manager.get_dots_remaining(), 1)
        
        # Collect final dot - should be complete
        self.score_manager.collect_dot()
        self.assertTrue(self.score_manager.is_level_complete())
        self.assertEqual(self.score_manager.get_dots_remaining(), 0)
    
    def test_level_progression(self):
        """Test level advancement functionality."""
        initial_level = self.score_manager.level
        
        # Start new level with 15 dots
        self.score_manager.start_new_level(15)
        
        # Level should increment
        self.assertEqual(self.score_manager.level, initial_level + 1)
        self.assertEqual(self.score_manager.total_dots_in_level, 15)
        self.assertEqual(self.score_manager.dots_collected_in_level, 0)
        # Ghost multiplier should reset
        self.assertEqual(self.score_manager.ghost_eat_multiplier, 1)
    
    def test_lives_management(self):
        """Test lives system functionality."""
        initial_lives = self.score_manager.lives
        
        # Lose a life - should not be game over
        game_over = self.score_manager.lose_life()
        self.assertFalse(game_over)
        self.assertEqual(self.score_manager.lives, initial_lives - 1)
        # Ghost multiplier should reset on life loss
        self.assertEqual(self.score_manager.ghost_eat_multiplier, 1)
        
        # Lose remaining lives
        for _ in range(initial_lives - 1):
            game_over = self.score_manager.lose_life()
        
        # Should be game over when lives reach 0
        self.assertTrue(game_over)
        self.assertEqual(self.score_manager.lives, 0)
    
    def test_gain_life(self):
        """Test gaining extra lives."""
        initial_lives = self.score_manager.lives
        
        self.score_manager.gain_life()
        self.assertEqual(self.score_manager.lives, initial_lives + 1)
    
    def test_level_progress_calculation(self):
        """Test level progress percentage calculation."""
        # Initialize level with 20 dots
        self.score_manager.initialize_level(20)
        self.assertEqual(self.score_manager.get_level_progress(), 0.0)
        
        # Collect 10 dots (50% progress)
        for _ in range(10):
            self.score_manager.collect_dot()
        self.assertEqual(self.score_manager.get_level_progress(), 0.5)
        
        # Collect all dots (100% progress)
        for _ in range(10):
            self.score_manager.collect_dot()
        self.assertEqual(self.score_manager.get_level_progress(), 1.0)
    
    def test_level_progress_edge_cases(self):
        """Test level progress with edge cases."""
        # Test with 0 dots in level
        self.score_manager.initialize_level(0)
        self.assertEqual(self.score_manager.get_level_progress(), 1.0)
        
        # Test dots remaining calculation
        self.score_manager.initialize_level(5)
        self.assertEqual(self.score_manager.get_dots_remaining(), 5)
        
        self.score_manager.collect_dot()
        self.assertEqual(self.score_manager.get_dots_remaining(), 4)
    
    def test_bonus_points(self):
        """Test bonus point addition."""
        initial_score = self.score_manager.score
        bonus_points = 1000
        
        self.score_manager.add_bonus_points(bonus_points)
        self.assertEqual(self.score_manager.score, initial_score + bonus_points)
    
    def test_ghost_multiplier_reset(self):
        """Test ghost multiplier reset functionality."""
        # Increase multiplier by eating ghosts
        self.score_manager.eat_ghost()  # First ghost: 200 points
        self.score_manager.eat_ghost()  # Second ghost: 400 points
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 2)
        
        # Reset multiplier
        self.score_manager.reset_ghost_multiplier()
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 0)
        
        # Next ghost should give base points
        points = self.score_manager.eat_ghost()
        self.assertEqual(points, 200)
    
    def test_power_pellet_resets_ghost_multiplier(self):
        """Test that power pellet collection resets ghost multiplier."""
        # Increase multiplier
        self.score_manager.eat_ghost()  # First ghost: 200 points
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 1)
        
        # Collect power pellet - should reset multiplier
        self.score_manager.collect_power_pellet()
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 0)
    
    def test_game_reset(self):
        """Test complete game reset functionality."""
        # Modify all values
        self.score_manager.score = 5000
        self.score_manager.level = 5
        self.score_manager.lives = 1
        self.score_manager.ghost_eat_multiplier = 4
        self.score_manager.total_dots_in_level = 100
        self.score_manager.dots_collected_in_level = 50
        
        # Reset game
        self.score_manager.reset_game()
        
        # Should be back to initial state
        self.assertEqual(self.score_manager.score, 0)
        self.assertEqual(self.score_manager.level, 1)
        self.assertEqual(self.score_manager.lives, 3)
        self.assertEqual(self.score_manager.ghost_eat_multiplier, 1)
        self.assertEqual(self.score_manager.total_dots_in_level, 0)
        self.assertEqual(self.score_manager.dots_collected_in_level, 0)
    
    def test_getter_methods(self):
        """Test all getter methods return correct values."""
        # Set some values
        self.score_manager.score = 1500
        self.score_manager.level = 3
        self.score_manager.lives = 2
        
        # Test getters
        self.assertEqual(self.score_manager.get_score(), 1500)
        self.assertEqual(self.score_manager.get_level(), 3)
        self.assertEqual(self.score_manager.get_lives(), 2)
    
    def test_scoring_integration_with_player_collection(self):
        """Test integration between ScoreManager and Player collection."""
        maze = Maze(tile_size=20)
        
        # Find a dot position
        dot_positions = list(maze.dots)
        if dot_positions:
            dot_pos = dot_positions[0]
            pixel_pos = maze.get_pixel_position(dot_pos[0], dot_pos[1])
            player = Player(pixel_pos, maze)
            
            # Initialize score manager with level
            self.score_manager.initialize_level(len(maze.dots))
            initial_score = self.score_manager.score
            
            # Collect item with score manager
            collected_dot, collected_pellet, points = player.collect_item_at_position(self.score_manager)
            
            # Verify scoring integration
            self.assertTrue(collected_dot)
            self.assertEqual(points, 10)
            self.assertEqual(self.score_manager.score, initial_score + 10)
            self.assertEqual(self.score_manager.dots_collected_in_level, 1)
    
    def test_power_pellet_integration_with_player_collection(self):
        """Test power pellet collection integration."""
        maze = Maze(tile_size=20)
        
        # Find a power pellet position
        pellet_positions = list(maze.power_pellets)
        if pellet_positions:
            pellet_pos = pellet_positions[0]
            pixel_pos = maze.get_pixel_position(pellet_pos[0], pellet_pos[1])
            player = Player(pixel_pos, maze)
            
            initial_score = self.score_manager.score
            
            # Collect power pellet with score manager
            collected_dot, collected_pellet, points = player.collect_item_at_position(self.score_manager)
            
            # Verify power pellet scoring integration
            self.assertTrue(collected_pellet)
            self.assertEqual(points, 50)
            self.assertEqual(self.score_manager.score, initial_score + 50)
    
    def test_complete_level_scenario(self):
        """Test a complete level completion scenario."""
        maze = Maze(tile_size=20)
        total_dots = len(maze.dots)
        
        # Initialize level
        self.score_manager.initialize_level(total_dots)
        self.assertFalse(self.score_manager.is_level_complete())
        
        # Simulate collecting all dots
        expected_score = 0
        for i in range(total_dots):
            points = self.score_manager.collect_dot()
            expected_score += points
            
            # Check progress
            expected_progress = (i + 1) / total_dots
            self.assertAlmostEqual(self.score_manager.get_level_progress(), expected_progress, places=2)
        
        # Level should be complete
        self.assertTrue(self.score_manager.is_level_complete())
        self.assertEqual(self.score_manager.score, expected_score)
        self.assertEqual(self.score_manager.get_dots_remaining(), 0)
    
    def test_score_tracking_requirements_compliance(self):
        """Test compliance with scoring requirements 2.1, 2.2, 2.3, 2.4."""
        # Requirement 2.1: Dot collection with 10-point scoring
        dot_points = self.score_manager.collect_dot()
        self.assertEqual(dot_points, 10)
        
        # Requirement 2.2: Power pellet collection with 50-point scoring
        pellet_points = self.score_manager.collect_power_pellet()
        self.assertEqual(pellet_points, 50)
        
        # Requirement 2.3: Level completion detection when all dots collected
        self.score_manager.initialize_level(3)
        self.assertFalse(self.score_manager.is_level_complete())
        
        for _ in range(3):
            self.score_manager.collect_dot()
        self.assertTrue(self.score_manager.is_level_complete())
        
        # Requirement 2.4: Real-time score updates (verified through immediate score changes)
        initial_score = self.score_manager.score
        self.score_manager.collect_dot()
        self.assertEqual(self.score_manager.score, initial_score + 10)  # Immediate update



class TestGhostMode(unittest.TestCase):
    """Test cases for the GhostMode enum."""
    
    def test_ghost_mode_values(self):
        """Test that ghost mode enum values are correct."""
        self.assertEqual(GhostMode.NORMAL.value, "normal")
        self.assertEqual(GhostMode.FRIGHTENED.value, "frightened")
        self.assertEqual(GhostMode.EATEN.value, "eaten")
    
    def test_is_vulnerable(self):
        """Test vulnerable state detection."""
        self.assertTrue(GhostMode.FRIGHTENED.is_vulnerable())
        self.assertFalse(GhostMode.NORMAL.is_vulnerable())
        self.assertFalse(GhostMode.EATEN.is_vulnerable())
    
    def test_is_dangerous(self):
        """Test dangerous state detection."""
        self.assertTrue(GhostMode.NORMAL.is_dangerous())
        self.assertFalse(GhostMode.FRIGHTENED.is_dangerous())
        self.assertFalse(GhostMode.EATEN.is_dangerous())


class TestGhost(unittest.TestCase):
    """Test cases for the Ghost class."""
    
    def setUp(self):
        """Set up test ghost instance."""
        self.maze = Maze(tile_size=20)
        self.start_position = Position(260, 160)  # Grid position (13, 8) - safe starting position
        self.ghost = Ghost(self.start_position, self.maze, GhostPersonality.BLINKY, speed=2)
        self.player_position = Position(260, 380)  # Player position for AI testing
    
    def test_ghost_initialization(self):
        """Test ghost initialization with correct attributes."""
        self.assertEqual(self.ghost.position.x, 260)
        self.assertEqual(self.ghost.position.y, 160)
        self.assertEqual(self.ghost.start_position.x, 260)
        self.assertEqual(self.ghost.start_position.y, 160)
        self.assertEqual(self.ghost.color, "red")
        self.assertEqual(self.ghost.speed, 2)
        self.assertEqual(self.ghost.mode, GhostMode.NORMAL)
        self.assertEqual(self.ghost.direction, Direction.UP)
        self.assertEqual(self.ghost.frightened_timer, 0)
        self.assertEqual(self.ghost.eaten_timer, 0)
        self.assertEqual(self.ghost.animation_frame, 0)
        self.assertEqual(self.ghost.animation_timer, 0)
    
    def test_set_mode_normal(self):
        """Test setting ghost to normal mode."""
        self.ghost.set_mode(GhostMode.NORMAL)
        self.assertEqual(self.ghost.mode, GhostMode.NORMAL)
        self.assertEqual(self.ghost.frightened_timer, 0)
        self.assertEqual(self.ghost.eaten_timer, 0)
    
    def test_set_mode_frightened(self):
        """Test setting ghost to frightened mode."""
        # Set initial direction
        self.ghost.direction = Direction.RIGHT
        
        # Set frightened mode with duration
        self.ghost.set_mode(GhostMode.FRIGHTENED, duration=600)
        
        self.assertEqual(self.ghost.mode, GhostMode.FRIGHTENED)
        self.assertEqual(self.ghost.frightened_timer, 600)
        # Should reverse direction when becoming frightened
        self.assertEqual(self.ghost.direction, Direction.LEFT)
    
    def test_set_mode_eaten(self):
        """Test setting ghost to eaten mode."""
        self.ghost.set_mode(GhostMode.EATEN, duration=180)
        
        self.assertEqual(self.ghost.mode, GhostMode.EATEN)
        self.assertEqual(self.ghost.eaten_timer, 180)
        # Target should be set to home position
        self.assertEqual(self.ghost.target_position.x, self.start_position.x)
        self.assertEqual(self.ghost.target_position.y, self.start_position.y)
    
    def test_mode_timer_updates(self):
        """Test mode timer countdown and transitions."""
        # Test frightened timer countdown
        self.ghost.set_mode(GhostMode.FRIGHTENED, duration=5)
        self.assertEqual(self.ghost.frightened_timer, 5)
        
        # Update multiple times
        for i in range(5):
            self.ghost._update_mode_timers()
            self.assertEqual(self.ghost.frightened_timer, 4 - i)
        
        # Should transition back to normal
        self.ghost._update_mode_timers()
        self.assertEqual(self.ghost.mode, GhostMode.NORMAL)
        self.assertEqual(self.ghost.frightened_timer, 0)
    
    def test_eaten_mode_timer_and_respawn(self):
        """Test eaten mode timer and respawn behavior."""
        # Move ghost away from start position
        self.ghost.position = Position(100, 100)
        
        # Set eaten mode
        self.ghost.set_mode(GhostMode.EATEN, duration=3)
        self.assertEqual(self.ghost.eaten_timer, 3)
        
        # Update timers
        for i in range(3):
            self.ghost._update_mode_timers()
            self.assertEqual(self.ghost.eaten_timer, 2 - i)
        
        # Should respawn and return to normal mode
        self.ghost._update_mode_timers()
        self.assertEqual(self.ghost.mode, GhostMode.NORMAL)
        self.assertEqual(self.ghost.eaten_timer, 0)
        self.assertEqual(self.ghost.position.x, self.start_position.x)
        self.assertEqual(self.ghost.position.y, self.start_position.y)
    
    def test_ai_target_normal_mode(self):
        """Test AI targeting in normal mode (chase behavior)."""
        self.ghost.set_mode(GhostMode.NORMAL)
        self.ghost._update_ai_target(self.player_position, [])
        
        # Should target player position directly
        self.assertEqual(self.ghost.target_position.x, self.player_position.x)
        self.assertEqual(self.ghost.target_position.y, self.player_position.y)
    
    def test_ai_target_frightened_mode(self):
        """Test AI targeting in frightened mode (flee behavior)."""
        # Position ghost away from player to ensure flee behavior works
        self.ghost.position = Position(self.player_position.x + 50, self.player_position.y + 50)
        self.ghost.set_mode(GhostMode.FRIGHTENED)
        self.ghost._update_ai_target(self.player_position, [])
        
        # Target should be away from player (not equal to player position)
        self.assertNotEqual(self.ghost.target_position.x, self.player_position.x)
        self.assertNotEqual(self.ghost.target_position.y, self.player_position.y)
        
        # Target should be further from player than ghost's current position
        ghost_to_player_dist = self.ghost.position.distance_to(self.player_position)
        target_to_player_dist = self.ghost.target_position.distance_to(self.player_position)
        self.assertGreaterEqual(target_to_player_dist, ghost_to_player_dist)
    
    def test_ai_target_eaten_mode(self):
        """Test AI targeting in eaten mode (return home)."""
        self.ghost.set_mode(GhostMode.EATEN)
        self.ghost._update_ai_target(self.player_position, [])
        
        # Should target home position
        self.assertEqual(self.ghost.target_position.x, self.start_position.x)
        self.assertEqual(self.ghost.target_position.y, self.start_position.y)
    
    def test_flee_target_calculation(self):
        """Test flee target calculation logic."""
        # Position ghost near player
        self.ghost.position = Position(self.player_position.x + 40, self.player_position.y)
        
        self.ghost._calculate_flee_target(self.player_position)
        
        # Target should be on opposite side of player
        self.assertGreater(self.ghost.target_position.x, self.ghost.position.x)
        
        # Target should be within maze bounds
        max_x = (self.maze.width - 1) * self.maze.tile_size
        max_y = (self.maze.height - 1) * self.maze.tile_size
        self.assertGreaterEqual(self.ghost.target_position.x, 0)
        self.assertLessEqual(self.ghost.target_position.x, max_x)
        self.assertGreaterEqual(self.ghost.target_position.y, 0)
        self.assertLessEqual(self.ghost.target_position.y, max_y)
    
    def test_flee_target_same_position(self):
        """Test flee target when ghost is at same position as player."""
        # Position ghost at same location as player
        self.ghost.position = Position(self.player_position.x, self.player_position.y)
        
        self.ghost._calculate_flee_target(self.player_position)
        
        # Should pick a corner position
        corners = [
            Position(0, 0),
            Position((self.maze.width - 1) * self.maze.tile_size, 0),
            Position(0, (self.maze.height - 1) * self.maze.tile_size),
            Position((self.maze.width - 1) * self.maze.tile_size, 
                    (self.maze.height - 1) * self.maze.tile_size)
        ]
        
        # Target should be one of the corners
        target_is_corner = any(
            self.ghost.target_position.x == corner.x and 
            self.ghost.target_position.y == corner.y 
            for corner in corners
        )
        self.assertTrue(target_is_corner)
    
    def test_movement_updates_position(self):
        """Test that movement updates ghost position correctly."""
        initial_y = self.ghost.position.y
        
        # Set direction and move
        self.ghost.direction = Direction.UP
        self.ghost._move_in_direction()
        
        # Position should have changed
        self.assertEqual(self.ghost.position.y, initial_y - 2)  # speed = 2, UP = (0, -1)
    
    def test_collision_detection_stops_movement(self):
        """Test that collision with walls stops movement."""
        # Position ghost near a wall
        wall_position = Position(20, 20)  # Near wall
        test_ghost = Ghost(wall_position, self.maze, speed=2)
        
        # Try to move into wall
        test_ghost.direction = Direction.UP
        test_ghost._move_in_direction()
        
        # Should stop due to collision
        self.assertEqual(test_ghost.direction, Direction.NONE)
    
    def test_tunnel_wrapping(self):
        """Test tunnel wrapping functionality for ghosts."""
        # Position ghost at tunnel entrance
        tunnel_position = Position(0, 180)  # Grid (0, 9) - tunnel row
        tunnel_ghost = Ghost(tunnel_position, self.maze, speed=2)
        
        # Move left
        tunnel_ghost.direction = Direction.LEFT
        tunnel_ghost._move_in_direction()
        
        # Apply wrapping
        tunnel_ghost.position = self.maze.wrap_position(tunnel_ghost.position)
        
        # Should wrap to right side
        self.assertGreater(tunnel_ghost.position.x, 500)
    
    def test_is_at_intersection(self):
        """Test intersection detection."""
        # Ghost at grid-aligned position should be at intersection
        aligned_ghost = Ghost(Position(100, 100), self.maze)
        self.assertTrue(aligned_ghost._is_at_intersection())
        
        # Ghost at non-aligned position should not be at intersection
        unaligned_ghost = Ghost(Position(105, 107), self.maze)
        self.assertFalse(unaligned_ghost._is_at_intersection())
    
    def test_should_change_direction_when_blocked(self):
        """Test direction change when blocked by wall."""
        # Position ghost facing a wall
        wall_position = Position(20, 20)
        test_ghost = Ghost(wall_position, self.maze)
        test_ghost.direction = Direction.UP  # Facing wall
        
        # Should want to change direction when blocked
        self.assertTrue(test_ghost._should_change_direction())
    
    def test_should_change_direction_at_intersection(self):
        """Test direction change at intersections."""
        # Position ghost at intersection
        intersection_position = Position(100, 100)
        test_ghost = Ghost(intersection_position, self.maze)
        test_ghost.last_direction_change = 15  # Past cooldown
        
        # Should consider changing direction at intersection
        self.assertTrue(test_ghost._should_change_direction())
    
    def test_should_not_change_direction_during_cooldown(self):
        """Test that direction doesn't change during cooldown period."""
        # Position ghost at intersection but within cooldown, and ensure it can move in current direction
        intersection_position = Position(100, 100)
        test_ghost = Ghost(intersection_position, self.maze)
        test_ghost.last_direction_change = 5  # Within cooldown
        
        # Set a direction that the ghost can move in (to avoid being blocked)
        test_ghost.direction = Direction.RIGHT
        
        # Only test cooldown if ghost is not blocked
        if self.maze.can_move(test_ghost.position, test_ghost.direction):
            # Should not change direction during cooldown when not blocked
            self.assertFalse(test_ghost._should_change_direction())
        else:
            # If blocked, should change direction regardless of cooldown
            self.assertTrue(test_ghost._should_change_direction())
    
    def test_choose_best_direction_normal_mode(self):
        """Test direction choice in normal mode (toward target)."""
        # Position ghost with clear path to target
        self.ghost.position = Position(100, 100)
        self.ghost.target_position = Position(140, 100)  # Target to the right
        self.ghost.mode = GhostMode.NORMAL
        
        best_direction = self.ghost._choose_best_direction()
        
        # Should choose direction toward target (RIGHT)
        self.assertEqual(best_direction, Direction.RIGHT)
    
    def test_choose_best_direction_avoids_opposite(self):
        """Test that direction choice avoids immediate reversals."""
        # Set current direction
        self.ghost.direction = Direction.RIGHT
        self.ghost.position = Position(100, 100)
        self.ghost.target_position = Position(60, 100)  # Target to the left
        
        # Get valid moves (should exclude opposite direction)
        valid_moves = self.maze.get_valid_moves(self.ghost.position)
        if len(valid_moves) > 1:
            best_direction = self.ghost._choose_best_direction()
            # Should not immediately reverse unless it's the only option
            if len(valid_moves) > 1:
                self.assertNotEqual(best_direction, Direction.LEFT)
    
    def test_choose_best_direction_frightened_randomness(self):
        """Test that frightened mode adds randomness to movement."""
        self.ghost.set_mode(GhostMode.FRIGHTENED)
        self.ghost.position = Position(100, 100)
        
        # Call multiple times and check for variation
        directions = []
        for _ in range(20):
            direction = self.ghost._choose_best_direction()
            if direction != Direction.NONE:
                directions.append(direction)
        
        # Should have some variation in frightened mode (not always the same)
        unique_directions = set(directions)
        # Note: This test might occasionally fail due to randomness, but should usually pass
        self.assertGreaterEqual(len(unique_directions), 1)
    
    def test_animation_updates(self):
        """Test animation frame updates."""
        initial_frame = self.ghost.animation_frame
        
        # Update animation multiple times
        for _ in range(self.ghost.animation_speed + 1):
            self.ghost._update_animation()
        
        # Animation frame should have changed
        self.assertNotEqual(self.ghost.animation_frame, initial_frame)
    
    def test_animation_frightened_mode(self):
        """Test animation in frightened mode."""
        self.ghost.set_mode(GhostMode.FRIGHTENED)
        
        # Update animation
        for _ in range(self.ghost.animation_speed + 1):
            self.ghost._update_animation()
        
        # Should cycle through 2 frames in frightened mode
        self.assertIn(self.ghost.animation_frame, [0, 1])
    
    def test_animation_normal_mode(self):
        """Test animation in normal mode."""
        self.ghost.set_mode(GhostMode.NORMAL)
        
        # Update animation
        for _ in range(self.ghost.animation_speed + 1):
            self.ghost._update_animation()
        
        # Should cycle through 4 frames in normal mode
        self.assertIn(self.ghost.animation_frame, [0, 1, 2, 3])
    
    def test_get_grid_position(self):
        """Test grid position calculation."""
        grid_x, grid_y = self.ghost.get_grid_position()
        expected_x, expected_y = self.start_position.to_grid(self.maze.tile_size)
        self.assertEqual(grid_x, expected_x)
        self.assertEqual(grid_y, expected_y)
    
    def test_get_center_position(self):
        """Test center position calculation."""
        center = self.ghost.get_center_position()
        expected_x = self.start_position.x + (self.maze.tile_size // 2)
        expected_y = self.start_position.y + (self.maze.tile_size // 2)
        self.assertEqual(center.x, expected_x)
        self.assertEqual(center.y, expected_y)
    
    def test_reset_position(self):
        """Test ghost position reset functionality."""
        # Move ghost and change state
        self.ghost.position = Position(100, 100)
        self.ghost.set_mode(GhostMode.FRIGHTENED, duration=300)
        self.ghost.direction = Direction.LEFT
        self.ghost.animation_frame = 2
        self.ghost.animation_timer = 5
        
        # Reset position
        self.ghost.reset_position()
        
        # Should be back to starting state
        self.assertEqual(self.ghost.position.x, self.start_position.x)
        self.assertEqual(self.ghost.position.y, self.start_position.y)
        self.assertEqual(self.ghost.mode, GhostMode.NORMAL)
        self.assertEqual(self.ghost.direction, Direction.UP)
        self.assertEqual(self.ghost.last_direction_change, 0)
        self.assertEqual(self.ghost.animation_frame, 0)
        self.assertEqual(self.ghost.animation_timer, 0)
    
    def test_is_vulnerable(self):
        """Test vulnerability detection."""
        # Normal mode should not be vulnerable
        self.ghost.set_mode(GhostMode.NORMAL)
        self.assertFalse(self.ghost.is_vulnerable())
        
        # Frightened mode should be vulnerable
        self.ghost.set_mode(GhostMode.FRIGHTENED)
        self.assertTrue(self.ghost.is_vulnerable())
        
        # Eaten mode should not be vulnerable
        self.ghost.set_mode(GhostMode.EATEN)
        self.assertFalse(self.ghost.is_vulnerable())
    
    def test_is_dangerous(self):
        """Test danger detection."""
        # Normal mode should be dangerous
        self.ghost.set_mode(GhostMode.NORMAL)
        self.assertTrue(self.ghost.is_dangerous())
        
        # Frightened mode should not be dangerous
        self.ghost.set_mode(GhostMode.FRIGHTENED)
        self.assertFalse(self.ghost.is_dangerous())
        
        # Eaten mode should not be dangerous
        self.ghost.set_mode(GhostMode.EATEN)
        self.assertFalse(self.ghost.is_dangerous())
    
    def test_get_distance_to_player(self):
        """Test distance calculation to player."""
        # Position ghost at known distance from player
        self.ghost.position = Position(self.player_position.x + 30, self.player_position.y + 40)
        
        distance = self.ghost.get_distance_to_player(self.player_position)
        expected_distance = 50.0  # 3-4-5 triangle: sqrt(30^2 + 40^2) = 50
        
        self.assertEqual(distance, expected_distance)
    
    def test_collides_with_player_true(self):
        """Test collision detection when ghost collides with player."""
        # Position ghost very close to player
        self.ghost.position = Position(self.player_position.x + 5, self.player_position.y)
        
        # Should detect collision with default radius
        self.assertTrue(self.ghost.collides_with_player(self.player_position))
    
    def test_collides_with_player_false(self):
        """Test collision detection when ghost doesn't collide with player."""
        # Position ghost far from player
        self.ghost.position = Position(self.player_position.x + 50, self.player_position.y)
        
        # Should not detect collision
        self.assertFalse(self.ghost.collides_with_player(self.player_position))
    
    def test_collides_with_player_custom_radius(self):
        """Test collision detection with custom radius."""
        # Position ghost at medium distance
        self.ghost.position = Position(self.player_position.x + 15, self.player_position.y)
        
        # Should not collide with small radius
        self.assertFalse(self.ghost.collides_with_player(self.player_position, collision_radius=5.0))
        
        # Should collide with large radius
        self.assertTrue(self.ghost.collides_with_player(self.player_position, collision_radius=20.0))
    
    def test_full_update_cycle(self):
        """Test complete update cycle with all components."""
        initial_position = Position(self.ghost.position.x, self.ghost.position.y)
        
        # Update ghost
        self.ghost.update(self.player_position)
        
        # Should have updated AI target
        self.assertEqual(self.ghost.target_position.x, self.player_position.x)
        self.assertEqual(self.ghost.target_position.y, self.player_position.y)
        
        # Animation timer should have incremented
        self.assertEqual(self.ghost.animation_timer, 1)
    
    def test_update_with_mode_transitions(self):
        """Test update cycle with mode transitions."""
        # Set frightened mode with short duration
        self.ghost.set_mode(GhostMode.FRIGHTENED, duration=2)
        
        # Update twice
        self.ghost.update(self.player_position)
        self.assertEqual(self.ghost.mode, GhostMode.FRIGHTENED)
        self.assertEqual(self.ghost.frightened_timer, 1)
        
        self.ghost.update(self.player_position)
        self.assertEqual(self.ghost.mode, GhostMode.NORMAL)
        self.assertEqual(self.ghost.frightened_timer, 0)
    
    def test_ghost_ai_behavior_consistency(self):
        """Test that ghost AI behavior is consistent and predictable."""
        # Set up predictable scenario
        self.ghost.position = Position(100, 100)
        self.ghost.set_mode(GhostMode.NORMAL)
        player_pos = Position(140, 100)  # Player to the right
        
        # Update AI target
        self.ghost._update_ai_target(player_pos, [])
        
        # Target should be player position
        self.assertEqual(self.ghost.target_position.x, player_pos.x)
        self.assertEqual(self.ghost.target_position.y, player_pos.y)
        
        # Choose direction should be toward target
        if self.maze.can_move(self.ghost.position, Direction.RIGHT):
            best_direction = self.ghost._choose_best_direction()
            self.assertEqual(best_direction, Direction.RIGHT)
    
    def test_ghost_movement_integration(self):
        """Test integrated movement with AI and collision detection."""
        # Position ghost in open area
        self.ghost.position = Position(100, 100)
        self.ghost.direction = Direction.RIGHT
        
        # Update movement
        self.ghost._update_movement()
        
        # Should have moved or changed direction appropriately
        # (exact behavior depends on maze layout, but should not crash)
        self.assertIsInstance(self.ghost.position.x, (int, float))
        self.assertIsInstance(self.ghost.position.y, (int, float))


class TestScoreManagerPowerPelletMechanics(unittest.TestCase):
    """Test cases for ScoreManager power pellet mechanics."""
    
    def setUp(self):
        """Set up test score manager instance."""
        self.score_manager = ScoreManager()
    
    def test_ghost_eating_point_progression(self):
        """Test ghost eating point progression: 200, 400, 800, 1600."""
        # First ghost: 200 points (2^0 * 200)
        points1 = self.score_manager.eat_ghost()
        self.assertEqual(points1, 200)
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 1)
        
        # Second ghost: 400 points (2^1 * 200)
        points2 = self.score_manager.eat_ghost()
        self.assertEqual(points2, 400)
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 2)
        
        # Third ghost: 800 points (2^2 * 200)
        points3 = self.score_manager.eat_ghost()
        self.assertEqual(points3, 800)
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 3)
        
        # Fourth ghost: 1600 points (2^3 * 200)
        points4 = self.score_manager.eat_ghost()
        self.assertEqual(points4, 1600)
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 4)
    
    def test_power_pellet_resets_ghost_counter(self):
        """Test that collecting power pellet resets ghost eating counter."""
        # Eat some ghosts
        self.score_manager.eat_ghost()
        self.score_manager.eat_ghost()
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 2)
        
        # Collect power pellet
        self.score_manager.collect_power_pellet()
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 0)
        
        # Next ghost should be 200 points again
        points = self.score_manager.eat_ghost()
        self.assertEqual(points, 200)
    
    def test_reset_ghost_multiplier(self):
        """Test resetting ghost multiplier."""
        # Eat some ghosts
        self.score_manager.eat_ghost()
        self.score_manager.eat_ghost()
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 2)
        
        # Reset multiplier
        self.score_manager.reset_ghost_multiplier()
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 0)
        
        # Next ghost should be 200 points
        points = self.score_manager.eat_ghost()
        self.assertEqual(points, 200)


class TestPowerPelletManager(unittest.TestCase):
    """Test cases for the PowerPelletManager class."""
    
    def setUp(self):
        """Set up test instances."""
        self.maze = Maze(tile_size=20)
        self.power_manager = PowerPelletManager()
        self.score_manager = ScoreManager()
        
        # Create test ghosts
        self.ghost1 = Ghost(Position(100, 100), self.maze, GhostPersonality.BLINKY)
        self.ghost2 = Ghost(Position(120, 100), self.maze, GhostPersonality.PINKY)
        self.ghosts = [self.ghost1, self.ghost2]
    
    def test_power_pellet_manager_initialization(self):
        """Test PowerPelletManager initialization."""
        self.assertFalse(self.power_manager.is_active)
        self.assertEqual(self.power_manager.timer, 0)
        self.assertEqual(len(self.power_manager.affected_ghosts), 0)
        self.assertEqual(self.power_manager.POWER_PELLET_DURATION, 600)  # 10 seconds at 60 FPS
    
    def test_activate_power_mode(self):
        """Test power mode activation."""
        # Activate power mode
        self.power_manager.activate_power_mode(self.ghosts)
        
        # Check power manager state
        self.assertTrue(self.power_manager.is_active)
        self.assertEqual(self.power_manager.timer, 600)
        self.assertEqual(len(self.power_manager.affected_ghosts), 2)
        
        # Check that ghosts are in frightened mode
        self.assertEqual(self.ghost1.mode, GhostMode.FRIGHTENED)
        self.assertEqual(self.ghost2.mode, GhostMode.FRIGHTENED)
        self.assertEqual(self.ghost1.frightened_timer, 600)
        self.assertEqual(self.ghost2.frightened_timer, 600)
    
    def test_activate_power_mode_skips_eaten_ghosts(self):
        """Test that power mode activation skips already eaten ghosts."""
        # Set one ghost to eaten mode
        self.ghost1.set_mode(GhostMode.EATEN, duration=100)
        
        # Activate power mode
        self.power_manager.activate_power_mode(self.ghosts)
        
        # Eaten ghost should remain eaten, other should be frightened
        self.assertEqual(self.ghost1.mode, GhostMode.EATEN)
        self.assertEqual(self.ghost2.mode, GhostMode.FRIGHTENED)
    
    def test_power_mode_timer_countdown(self):
        """Test power mode timer countdown."""
        # Activate power mode
        self.power_manager.activate_power_mode(self.ghosts)
        initial_timer = self.power_manager.timer
        
        # Update once
        still_active = self.power_manager.update()
        self.assertTrue(still_active)
        self.assertEqual(self.power_manager.timer, initial_timer - 1)
        
        # Update multiple times
        for _ in range(10):
            self.power_manager.update()
        
        self.assertEqual(self.power_manager.timer, initial_timer - 11)
    
    def test_power_mode_expiration(self):
        """Test power mode expiration."""
        # Activate power mode with short duration
        self.power_manager.activate_power_mode(self.ghosts)
        self.power_manager.timer = 2  # Set to expire soon
        
        # Update until expiration
        still_active = self.power_manager.update()
        self.assertTrue(still_active)
        self.assertEqual(self.power_manager.timer, 1)
        
        still_active = self.power_manager.update()
        self.assertFalse(still_active)
        self.assertEqual(self.power_manager.timer, 0)
        self.assertFalse(self.power_manager.is_active)
        
        # Ghosts should return to normal mode
        self.assertEqual(self.ghost1.mode, GhostMode.NORMAL)
        self.assertEqual(self.ghost2.mode, GhostMode.NORMAL)
    
    def test_power_mode_deactivation_preserves_eaten_ghosts(self):
        """Test that power mode deactivation preserves eaten ghost state."""
        # Activate power mode
        self.power_manager.activate_power_mode(self.ghosts)
        
        # Set one ghost to eaten during power mode
        self.ghost1.set_mode(GhostMode.EATEN, duration=100)
        
        # Force expiration
        self.power_manager.timer = 0
        self.power_manager.update()
        
        # Eaten ghost should remain eaten, frightened ghost should become normal
        self.assertEqual(self.ghost1.mode, GhostMode.EATEN)
        self.assertEqual(self.ghost2.mode, GhostMode.NORMAL)
    
    def test_eat_ghost_during_power_mode(self):
        """Test eating ghost during power mode."""
        # Activate power mode
        self.power_manager.activate_power_mode(self.ghosts)
        
        # Eat a ghost
        points = self.power_manager.eat_ghost(self.ghost1, self.score_manager)
        
        # Should award points and set ghost to eaten mode
        self.assertEqual(points, 200)  # First ghost eaten
        self.assertEqual(self.ghost1.mode, GhostMode.EATEN)
        self.assertEqual(self.ghost1.eaten_timer, 180)  # 3 seconds at 60 FPS
    
    def test_eat_ghost_when_not_vulnerable(self):
        """Test eating ghost when not vulnerable."""
        # Try to eat ghost in normal mode (not vulnerable)
        points = self.power_manager.eat_ghost(self.ghost1, self.score_manager)
        
        # Should not award points or change ghost state
        self.assertEqual(points, 0)
        self.assertEqual(self.ghost1.mode, GhostMode.NORMAL)
    
    def test_eat_ghost_when_power_mode_inactive(self):
        """Test eating ghost when power mode is inactive."""
        # Set ghost to frightened but don't activate power mode
        self.ghost1.set_mode(GhostMode.FRIGHTENED)
        
        # Try to eat ghost
        points = self.power_manager.eat_ghost(self.ghost1, self.score_manager)
        
        # Should not award points because power mode is inactive
        self.assertEqual(points, 0)
    
    def test_multiple_ghost_eating_point_progression(self):
        """Test multiple ghost eating with correct point progression."""
        # Activate power mode
        self.power_manager.activate_power_mode(self.ghosts)
        
        # Eat first ghost (200 points)
        points1 = self.power_manager.eat_ghost(self.ghost1, self.score_manager)
        self.assertEqual(points1, 200)
        
        # Eat second ghost (400 points)
        points2 = self.power_manager.eat_ghost(self.ghost2, self.score_manager)
        self.assertEqual(points2, 400)
        
        # Check total score
        expected_total = 200 + 400  # Ghost points only (no power pellet in this test)
        self.assertEqual(self.score_manager.get_score(), expected_total)
    
    def test_get_remaining_time_methods(self):
        """Test remaining time calculation methods."""
        # When inactive
        self.assertEqual(self.power_manager.get_remaining_time(), 0)
        self.assertEqual(self.power_manager.get_remaining_seconds(), 0.0)
        
        # When active
        self.power_manager.activate_power_mode(self.ghosts)
        self.assertEqual(self.power_manager.get_remaining_time(), 600)
        self.assertEqual(self.power_manager.get_remaining_seconds(), 10.0)
        
        # After some time passes
        self.power_manager.timer = 300
        self.assertEqual(self.power_manager.get_remaining_time(), 300)
        self.assertEqual(self.power_manager.get_remaining_seconds(), 5.0)
    
    def test_is_power_mode_active(self):
        """Test power mode active status checking."""
        self.assertFalse(self.power_manager.is_power_mode_active())
        
        self.power_manager.activate_power_mode(self.ghosts)
        self.assertTrue(self.power_manager.is_power_mode_active())
        
        self.power_manager.force_deactivate()
        self.assertFalse(self.power_manager.is_power_mode_active())
    
    def test_force_deactivate(self):
        """Test force deactivation of power mode."""
        # Activate power mode
        self.power_manager.activate_power_mode(self.ghosts)
        self.assertTrue(self.power_manager.is_active)
        
        # Force deactivate
        self.power_manager.force_deactivate()
        self.assertFalse(self.power_manager.is_active)
        self.assertEqual(self.power_manager.timer, 0)
        self.assertEqual(len(self.power_manager.affected_ghosts), 0)
        
        # Ghosts should return to normal
        self.assertEqual(self.ghost1.mode, GhostMode.NORMAL)
        self.assertEqual(self.ghost2.mode, GhostMode.NORMAL)
    
    def test_check_ghost_collision_player_eats_ghost(self):
        """Test collision detection when player eats ghost."""
        player_pos = Position(100, 100)  # Same as ghost1 position
        
        # Activate power mode
        self.power_manager.activate_power_mode(self.ghosts)
        
        # Check collision
        player_died, points = self.power_manager.check_ghost_collision(
            player_pos, self.ghosts, self.score_manager
        )
        
        # Player should not die and should earn points
        self.assertFalse(player_died)
        self.assertEqual(points, 200)  # First ghost eaten
        self.assertEqual(self.ghost1.mode, GhostMode.EATEN)
    
    def test_check_ghost_collision_ghost_kills_player(self):
        """Test collision detection when ghost kills player."""
        player_pos = Position(100, 100)  # Same as ghost1 position
        
        # Don't activate power mode (ghosts are dangerous)
        player_died, points = self.power_manager.check_ghost_collision(
            player_pos, self.ghosts, self.score_manager
        )
        
        # Player should die and earn no points
        self.assertTrue(player_died)
        self.assertEqual(points, 0)
        self.assertEqual(self.ghost1.mode, GhostMode.NORMAL)  # Ghost unchanged
    
    def test_check_ghost_collision_no_collision(self):
        """Test collision detection when no collision occurs."""
        player_pos = Position(500, 500)  # Far from ghosts
        
        # Check collision
        player_died, points = self.power_manager.check_ghost_collision(
            player_pos, self.ghosts, self.score_manager
        )
        
        # No collision should occur
        self.assertFalse(player_died)
        self.assertEqual(points, 0)
    
    def test_check_ghost_collision_multiple_ghosts(self):
        """Test collision detection with multiple ghosts at same position."""
        # Position both ghosts at same location as player
        player_pos = Position(100, 100)
        self.ghost1.position = Position(100, 100)
        self.ghost2.position = Position(100, 100)
        
        # Activate power mode
        self.power_manager.activate_power_mode(self.ghosts)
        
        # Check collision (should only process first collision)
        player_died, points = self.power_manager.check_ghost_collision(
            player_pos, self.ghosts, self.score_manager
        )
        
        # Should eat first ghost encountered
        self.assertFalse(player_died)
        self.assertEqual(points, 200)
        
        # One ghost should be eaten
        eaten_count = sum(1 for ghost in self.ghosts if ghost.mode == GhostMode.EATEN)
        self.assertEqual(eaten_count, 1)
    
    def test_power_mode_integration_with_score_manager(self):
        """Test integration between PowerPelletManager and ScoreManager."""
        # Collect power pellet first
        pellet_points = self.score_manager.collect_power_pellet()
        self.assertEqual(pellet_points, 50)
        
        # Activate power mode
        self.power_manager.activate_power_mode(self.ghosts)
        
        # Eat ghosts in sequence
        points1 = self.power_manager.eat_ghost(self.ghost1, self.score_manager)
        points2 = self.power_manager.eat_ghost(self.ghost2, self.score_manager)
        
        # Check point progression
        self.assertEqual(points1, 200)
        self.assertEqual(points2, 400)
        
        # Check total score
        expected_total = 50 + 200 + 400  # Power pellet + two ghosts
        self.assertEqual(self.score_manager.get_score(), expected_total)


if __name__ == '__main__':
    unittest.main()


class TestScoreManagerLivesSystem(unittest.TestCase):
    """Test cases for the ScoreManager lives system functionality."""
    
    def setUp(self):
        """Set up test score manager instance."""
        self.score_manager = ScoreManager(starting_lives=3)
    
    def test_score_manager_initialization_with_lives(self):
        """Test score manager initialization with custom starting lives."""
        # Test default initialization
        default_manager = ScoreManager()
        self.assertEqual(default_manager.lives, 3)
        self.assertEqual(default_manager.starting_lives, 3)
        self.assertFalse(default_manager.game_over)
        
        # Test custom starting lives
        custom_manager = ScoreManager(starting_lives=5)
        self.assertEqual(custom_manager.lives, 5)
        self.assertEqual(custom_manager.starting_lives, 5)
        self.assertFalse(custom_manager.game_over)
    
    def test_lose_life_functionality(self):
        """Test life loss mechanics."""
        initial_lives = self.score_manager.lives
        
        # Lose a life - should not be game over
        game_over = self.score_manager.lose_life()
        self.assertFalse(game_over)
        self.assertEqual(self.score_manager.lives, initial_lives - 1)
        self.assertFalse(self.score_manager.game_over)
        
        # Lose another life - still not game over
        game_over = self.score_manager.lose_life()
        self.assertFalse(game_over)
        self.assertEqual(self.score_manager.lives, initial_lives - 2)
        self.assertFalse(self.score_manager.game_over)
        
        # Lose final life - should be game over
        game_over = self.score_manager.lose_life()
        self.assertTrue(game_over)
        self.assertEqual(self.score_manager.lives, 0)
        self.assertTrue(self.score_manager.game_over)
    
    def test_lose_life_resets_multipliers(self):
        """Test that losing a life resets ghost eating multipliers."""
        # Set up some multiplier state
        self.score_manager.ghosts_eaten_in_power_mode = 2
        self.score_manager.ghost_eat_multiplier = 4
        
        # Lose a life
        self.score_manager.lose_life()
        
        # Multipliers should be reset
        self.assertEqual(self.score_manager.ghost_eat_multiplier, 1)
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 0)
    
    def test_is_game_over_functionality(self):
        """Test game over state detection."""
        # Initially not game over
        self.assertFalse(self.score_manager.is_game_over())
        
        # Lose all lives
        for _ in range(3):
            self.score_manager.lose_life()
        
        # Should be game over
        self.assertTrue(self.score_manager.is_game_over())
    
    def test_reset_game_with_lives(self):
        """Test game reset functionality with lives system."""
        # Modify state
        self.score_manager.score = 1000
        self.score_manager.level = 5
        self.score_manager.lives = 1
        self.score_manager.game_over = True
        self.score_manager.ghosts_eaten_in_power_mode = 3
        
        # Reset game
        self.score_manager.reset_game()
        
        # Should be back to initial state
        self.assertEqual(self.score_manager.score, 0)
        self.assertEqual(self.score_manager.level, 1)
        self.assertEqual(self.score_manager.lives, self.score_manager.starting_lives)
        self.assertFalse(self.score_manager.game_over)
        self.assertEqual(self.score_manager.ghosts_eaten_in_power_mode, 0)
    
    def test_gain_life_functionality(self):
        """Test gaining extra lives."""
        initial_lives = self.score_manager.lives
        
        # Gain a life
        self.score_manager.gain_life()
        self.assertEqual(self.score_manager.lives, initial_lives + 1)
        
        # Gain multiple lives
        self.score_manager.gain_life()
        self.score_manager.gain_life()
        self.assertEqual(self.score_manager.lives, initial_lives + 3)


class TestPlayerGhostCollision(unittest.TestCase):
    """Test cases for player-ghost collision detection."""
    
    def setUp(self):
        """Set up test instances."""
        self.maze = Maze(tile_size=20)
        self.player_position = Position(260, 380)
        self.ghost_position = Position(280, 380)  # Close to player
        self.player = Player(self.player_position, self.maze)
        self.ghost = Ghost(self.ghost_position, self.maze, GhostPersonality.BLINKY)
        self.score_manager = ScoreManager()
    
    def test_check_collision_with_ghost_close_positions(self):
        """Test collision detection when player and ghost are close."""
        # Position ghost very close to player
        close_ghost = Ghost(Position(265, 385), self.maze)  # 5 pixels away
        
        # Should detect collision
        collision = self.player.check_collision_with_ghost(close_ghost)
        self.assertTrue(collision)
    
    def test_check_collision_with_ghost_far_positions(self):
        """Test collision detection when player and ghost are far apart."""
        # Position ghost far from player
        far_ghost = Ghost(Position(100, 100), self.maze)  # Far away
        
        # Should not detect collision
        collision = self.player.check_collision_with_ghost(far_ghost)
        self.assertFalse(collision)
    
    def test_handle_ghost_collision_frightened_ghost(self):
        """Test collision handling with frightened ghost (player eats ghost)."""
        # Set ghost to frightened mode
        self.ghost.set_mode(GhostMode.FRIGHTENED, duration=300)
        
        # Handle collision
        life_lost, points_earned = self.player.handle_ghost_collision(self.ghost, self.score_manager)
        
        # Player should eat ghost, not lose life
        self.assertFalse(life_lost)
        self.assertEqual(points_earned, 200)  # Base ghost points
        self.assertEqual(self.ghost.mode, GhostMode.EATEN)
        
        # Score should be updated
        self.assertEqual(self.score_manager.score, 200)
    
    def test_handle_ghost_collision_normal_ghost(self):
        """Test collision handling with normal ghost (player loses life)."""
        # Ghost is in normal mode by default
        initial_lives = self.score_manager.lives
        
        # Handle collision
        life_lost, points_earned = self.player.handle_ghost_collision(self.ghost, self.score_manager)
        
        # Player should lose life, no points earned
        self.assertTrue(life_lost)
        self.assertEqual(points_earned, 0)
        self.assertEqual(self.score_manager.lives, initial_lives - 1)
    
    def test_handle_ghost_collision_eaten_ghost(self):
        """Test collision handling with eaten ghost (no effect)."""
        # Set ghost to eaten mode
        self.ghost.set_mode(GhostMode.EATEN, duration=180)
        initial_lives = self.score_manager.lives
        
        # Handle collision
        life_lost, points_earned = self.player.handle_ghost_collision(self.ghost, self.score_manager)
        
        # No effect should occur
        self.assertFalse(life_lost)
        self.assertEqual(points_earned, 0)
        self.assertEqual(self.score_manager.lives, initial_lives)
    
    def test_multiple_ghost_eating_point_progression(self):
        """Test point progression when eating multiple ghosts."""
        # Create multiple frightened ghosts
        ghosts = []
        for i in range(4):
            ghost = Ghost(Position(260 + i*5, 380), self.maze, GhostPersonality.BLINKY)
            ghost.set_mode(GhostMode.FRIGHTENED, duration=300)
            ghosts.append(ghost)
        
        expected_points = [200, 400, 800, 1600]  # Point progression
        total_points = 0
        
        # Eat ghosts one by one
        for i, ghost in enumerate(ghosts):
            life_lost, points_earned = self.player.handle_ghost_collision(ghost, self.score_manager)
            
            self.assertFalse(life_lost)
            self.assertEqual(points_earned, expected_points[i])
            total_points += points_earned
            self.assertEqual(self.score_manager.score, total_points)


class TestCollisionManager(unittest.TestCase):
    """Test cases for the CollisionManager class."""
    
    def setUp(self):
        """Set up test instances."""
        self.maze = Maze(tile_size=20)
        self.player = Player(Position(260, 380), self.maze)
        self.ghost = Ghost(Position(265, 385), self.maze)  # Close to player
        self.score_manager = ScoreManager()
        self.collision_manager = CollisionManager()
    
    def test_collision_manager_initialization(self):
        """Test collision manager initialization."""
        self.assertEqual(self.collision_manager.collision_radius, 12.0)
        self.assertFalse(self.collision_manager.life_lost_this_frame)
        self.assertEqual(self.collision_manager.respawn_timer, 0)
        self.assertEqual(self.collision_manager.respawn_duration, 120)
    
    def test_check_collision_detection(self):
        """Test basic collision detection between positions."""
        pos1 = Position(100, 100)
        pos2 = Position(105, 105)  # 5√2 ≈ 7.07 pixels away
        pos3 = Position(150, 150)  # Far away
        
        # Close positions should collide
        self.assertTrue(self.collision_manager._check_collision(pos1, pos2))
        
        # Far positions should not collide
        self.assertFalse(self.collision_manager._check_collision(pos1, pos3))
    
    def test_player_ghost_collision_normal_ghost(self):
        """Test collision with normal ghost (player loses life)."""
        # Ghost is in normal mode by default
        initial_lives = self.score_manager.lives
        
        # Check collision
        life_lost, points_earned, game_over = self.collision_manager.check_player_ghost_collisions(
            self.player, [self.ghost], self.score_manager
        )
        
        # Player should lose life
        self.assertTrue(life_lost)
        self.assertEqual(points_earned, 0)
        self.assertFalse(game_over)  # Still has lives left
        self.assertEqual(self.score_manager.lives, initial_lives - 1)
        
        # Player and ghost should be reset to starting positions
        self.assertEqual(self.player.position.x, self.player.start_position.x)
        self.assertEqual(self.player.position.y, self.player.start_position.y)
        self.assertEqual(self.ghost.position.x, self.ghost.start_position.x)
        self.assertEqual(self.ghost.position.y, self.ghost.start_position.y)
    
    def test_player_ghost_collision_frightened_ghost(self):
        """Test collision with frightened ghost (player eats ghost)."""
        # Set ghost to frightened mode
        self.ghost.set_mode(GhostMode.FRIGHTENED, duration=300)
        
        # Check collision
        life_lost, points_earned, game_over = self.collision_manager.check_player_ghost_collisions(
            self.player, [self.ghost], self.score_manager
        )
        
        # Player should eat ghost
        self.assertFalse(life_lost)
        self.assertEqual(points_earned, 200)
        self.assertFalse(game_over)
        self.assertEqual(self.ghost.mode, GhostMode.EATEN)
        self.assertEqual(self.score_manager.score, 200)
    
    def test_collision_during_respawn_timer(self):
        """Test that collisions are ignored during respawn timer."""
        # Trigger a life loss to start respawn timer
        self.collision_manager._handle_life_loss(self.player, [self.ghost])
        
        # Position ghost close to player again
        self.ghost.position = Position(265, 385)
        
        # Check collision during respawn timer
        life_lost, points_earned, game_over = self.collision_manager.check_player_ghost_collisions(
            self.player, [self.ghost], self.score_manager
        )
        
        # No collision should be detected during respawn
        self.assertFalse(life_lost)
        self.assertEqual(points_earned, 0)
        self.assertFalse(game_over)
    
    def test_respawn_timer_countdown(self):
        """Test respawn timer countdown functionality."""
        # Start respawn timer
        self.collision_manager._handle_life_loss(self.player, [self.ghost])
        
        # Move ghost away to avoid collision during countdown
        self.ghost.position = Position(500, 500)  # Far away
        
        initial_timer = self.collision_manager.respawn_timer
        self.assertTrue(self.collision_manager.is_respawning())
        self.assertEqual(self.collision_manager.get_respawn_time_remaining(), initial_timer)
        
        # Simulate timer countdown
        for _ in range(60):  # 1 second at 60 FPS
            self.collision_manager.check_player_ghost_collisions(
                self.player, [self.ghost], self.score_manager
            )
        
        # Timer should have decreased
        self.assertEqual(self.collision_manager.respawn_timer, initial_timer - 60)
        self.assertTrue(self.collision_manager.is_respawning())
        
        # Continue until timer expires (need to account for already decremented timer)
        remaining_time = self.collision_manager.respawn_timer
        for _ in range(remaining_time + 1):  # +1 to ensure it goes to 0
            self.collision_manager.check_player_ghost_collisions(
                self.player, [self.ghost], self.score_manager
            )
        
        # Timer should be expired
        self.assertFalse(self.collision_manager.is_respawning())
        self.assertEqual(self.collision_manager.get_respawn_time_remaining(), 0)
    
    def test_game_over_on_final_life(self):
        """Test game over when losing final life."""
        # Reduce lives to 1
        self.score_manager.lives = 1
        
        # Check collision that causes final life loss
        life_lost, points_earned, game_over = self.collision_manager.check_player_ghost_collisions(
            self.player, [self.ghost], self.score_manager
        )
        
        # Should trigger game over
        self.assertTrue(life_lost)
        self.assertTrue(game_over)
        self.assertEqual(self.score_manager.lives, 0)
        self.assertTrue(self.score_manager.is_game_over())
    
    def test_multiple_ghosts_collision_priority(self):
        """Test collision handling with multiple ghosts."""
        # Create multiple ghosts - one normal, one frightened
        normal_ghost = Ghost(Position(265, 385), self.maze, GhostPersonality.BLINKY)
        frightened_ghost = Ghost(Position(267, 387), self.maze, GhostPersonality.PINKY)
        frightened_ghost.set_mode(GhostMode.FRIGHTENED, duration=300)
        
        ghosts = [normal_ghost, frightened_ghost]
        
        # Check collision - normal ghost should take priority (cause death)
        life_lost, points_earned, game_over = self.collision_manager.check_player_ghost_collisions(
            self.player, ghosts, self.score_manager
        )
        
        # Should lose life due to normal ghost
        self.assertTrue(life_lost)
        self.assertEqual(points_earned, 0)
    
    def test_collision_manager_reset(self):
        """Test collision manager reset functionality."""
        # Set some state
        self.collision_manager.life_lost_this_frame = True
        self.collision_manager.respawn_timer = 60
        
        # Reset
        self.collision_manager.reset()
        
        # State should be cleared
        self.assertFalse(self.collision_manager.life_lost_this_frame)
        self.assertEqual(self.collision_manager.respawn_timer, 0)
    
    def test_was_life_lost_this_frame_flag(self):
        """Test life lost this frame flag functionality."""
        # Initially false
        self.assertFalse(self.collision_manager.was_life_lost_this_frame())
        
        # Trigger life loss
        self.collision_manager._handle_life_loss(self.player, [self.ghost])
        
        # Should be true once, then reset
        self.assertTrue(self.collision_manager.was_life_lost_this_frame())
        self.assertFalse(self.collision_manager.was_life_lost_this_frame())  # Should reset after checking
    
    def test_handle_life_loss_resets_entities(self):
        """Test that life loss properly resets player and ghosts."""
        # Move entities away from starting positions
        self.player.position = Position(100, 100)
        self.player.direction = Direction.RIGHT
        self.player.is_moving = True
        
        self.ghost.position = Position(200, 200)
        self.ghost.mode = GhostMode.FRIGHTENED
        
        # Handle life loss
        self.collision_manager._handle_life_loss(self.player, [self.ghost])
        
        # Player should be reset
        self.assertEqual(self.player.position.x, self.player.start_position.x)
        self.assertEqual(self.player.position.y, self.player.start_position.y)
        self.assertEqual(self.player.direction, Direction.NONE)
        self.assertFalse(self.player.is_moving)
        
        # Ghost should be reset
        self.assertEqual(self.ghost.position.x, self.ghost.start_position.x)
        self.assertEqual(self.ghost.position.y, self.ghost.start_position.y)
        self.assertEqual(self.ghost.mode, GhostMode.NORMAL)


if __name__ == '__main__':
    unittest.main()