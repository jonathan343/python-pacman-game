"""
Unit tests for enhanced ghost AI behaviors.
"""
import unittest
from unittest.mock import Mock, patch
from pacman_game.models import (
    Ghost, GhostPersonality, GhostMode, Position, Direction, Maze, Player
)


class TestEnhancedGhostAI(unittest.TestCase):
    """Test cases for enhanced ghost AI behaviors."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.maze = Maze(tile_size=20)
        self.start_position = Position(260, 200)  # Center of maze
        self.house_position = Position(260, 180)  # Ghost house position
        
        # Create ghosts with different personalities
        self.blinky = Ghost(
            self.start_position, self.maze, 
            GhostPersonality.BLINKY, speed=2
        )
        self.pinky = Ghost(
            self.start_position, self.maze,
            GhostPersonality.PINKY, speed=2, 
            ghost_house_position=self.house_position
        )
        self.inky = Ghost(
            self.start_position, self.maze,
            GhostPersonality.INKY, speed=2,
            ghost_house_position=self.house_position
        )
        self.sue = Ghost(
            self.start_position, self.maze,
            GhostPersonality.SUE, speed=2,
            ghost_house_position=self.house_position
        )
        
        self.player_position = Position(100, 100)
    
    def test_ghost_personality_colors(self):
        """Test that each ghost personality has the correct color."""
        self.assertEqual(self.blinky.color, "red")
        self.assertEqual(self.pinky.color, "pink")
        self.assertEqual(self.inky.color, "cyan")
        self.assertEqual(self.sue.color, "orange")
    
    def test_ghost_mode_properties(self):
        """Test ghost mode vulnerability and danger properties."""
        # Test vulnerable modes
        self.assertTrue(GhostMode.FRIGHTENED.is_vulnerable())
        self.assertFalse(GhostMode.NORMAL.is_vulnerable())
        self.assertFalse(GhostMode.EATEN.is_vulnerable())
        self.assertFalse(GhostMode.SCATTER.is_vulnerable())
        
        # Test dangerous modes
        self.assertTrue(GhostMode.NORMAL.is_dangerous())
        self.assertTrue(GhostMode.SCATTER.is_dangerous())
        self.assertFalse(GhostMode.FRIGHTENED.is_dangerous())
        self.assertFalse(GhostMode.EATEN.is_dangerous())
        self.assertFalse(GhostMode.IN_HOUSE.is_dangerous())
    
    def test_blinky_chase_behavior(self):
        """Test Blinky's direct chase AI behavior."""
        self.blinky.set_mode(GhostMode.NORMAL)
        self.blinky._calculate_chase_target(self.player_position, [])
        
        # Blinky should target player position directly
        self.assertEqual(self.blinky.target_position.x, self.player_position.x)
        self.assertEqual(self.blinky.target_position.y, self.player_position.y)
    
    def test_pinky_ambush_behavior(self):
        """Test Pinky's ambush AI behavior."""
        self.pinky.set_mode(GhostMode.NORMAL)
        self.pinky._calculate_chase_target(self.player_position, [])
        
        # Pinky should target ahead of player (4 tiles up in this case)
        expected_y = (self.player_position.to_grid(20)[1] - 4) * 20
        expected_y = max(0, min(expected_y, (self.maze.height - 1) * 20))
        
        self.assertEqual(self.pinky.target_position.x, self.player_position.x)
        self.assertEqual(self.pinky.target_position.y, expected_y)
    
    def test_inky_flanking_behavior(self):
        """Test Inky's complex flanking AI behavior."""
        # Create Blinky for Inky's AI calculation
        other_ghosts = [self.blinky]
        self.blinky.position = Position(200, 150)
        
        self.inky.set_mode(GhostMode.NORMAL)
        self.inky._calculate_chase_target(self.player_position, other_ghosts)
        
        # Inky's target should be calculated based on Blinky's position
        # and a point ahead of the player
        self.assertIsInstance(self.inky.target_position, Position)
        # Target should be different from direct player position
        self.assertNotEqual(self.inky.target_position.x, self.player_position.x)
    
    def test_inky_fallback_without_blinky(self):
        """Test Inky's fallback behavior when Blinky is not available."""
        other_ghosts = [self.pinky, self.sue]  # No Blinky
        
        self.inky.set_mode(GhostMode.NORMAL)
        self.inky._calculate_chase_target(self.player_position, other_ghosts)
        
        # Should fallback to direct chase
        self.assertEqual(self.inky.target_position.x, self.player_position.x)
        self.assertEqual(self.inky.target_position.y, self.player_position.y)
    
    def test_sue_patrol_behavior_far(self):
        """Test Sue's patrol behavior when far from player."""
        # Position Sue far from player (more than 8 tiles)
        self.sue.position = Position(400, 400)
        
        self.sue.set_mode(GhostMode.NORMAL)
        self.sue._calculate_chase_target(self.player_position, [])
        
        # Should chase when far from player
        self.assertEqual(self.sue.target_position.x, self.player_position.x)
        self.assertEqual(self.sue.target_position.y, self.player_position.y)
    
    def test_sue_patrol_behavior_close(self):
        """Test Sue's patrol behavior when close to player."""
        # Position Sue close to player (less than 8 tiles)
        self.sue.position = Position(120, 120)
        
        self.sue.set_mode(GhostMode.NORMAL)
        self.sue._calculate_chase_target(self.player_position, [])
        
        # Should scatter to corner when close to player
        expected_target = self.sue.scatter_targets[GhostPersonality.SUE]
        self.assertEqual(self.sue.target_position.x, expected_target.x)
        self.assertEqual(self.sue.target_position.y, expected_target.y)
    
    def test_scatter_mode_targeting(self):
        """Test scatter mode targeting for all ghost personalities."""
        ghosts = [self.blinky, self.pinky, self.inky, self.sue]
        
        for ghost in ghosts:
            ghost.set_mode(GhostMode.SCATTER)
            ghost._calculate_scatter_target()
            
            # Each ghost should target their assigned corner
            expected_target = ghost.scatter_targets[ghost.personality]
            self.assertEqual(ghost.target_position.x, expected_target.x)
            self.assertEqual(ghost.target_position.y, expected_target.y)
    
    def test_frightened_mode_flee_behavior(self):
        """Test frightened mode flee behavior."""
        self.blinky.set_mode(GhostMode.FRIGHTENED, duration=600)
        self.blinky.position = Position(150, 150)
        
        self.blinky._calculate_flee_target(self.player_position)
        
        # Target should be away from player
        distance_to_player = self.player_position.distance_to(self.blinky.target_position)
        distance_ghost_to_player = self.player_position.distance_to(self.blinky.position)
        
        # Flee target should generally be farther from player than ghost's current position
        self.assertGreater(distance_to_player, distance_ghost_to_player * 0.5)
    
    def test_house_exit_delays(self):
        """Test ghost house exit delays for different personalities."""
        # Test exit delays
        self.assertEqual(self.blinky._get_house_exit_delay(), 0)  # Immediate
        self.assertEqual(self.pinky._get_house_exit_delay(), 0)   # Immediate
        self.assertEqual(self.inky._get_house_exit_delay(), 180)  # 3 seconds
        self.assertEqual(self.sue._get_house_exit_delay(), 360)   # 6 seconds
    
    def test_dot_threshold_for_exit(self):
        """Test dot thresholds for ghost house exit."""
        self.assertEqual(self.blinky._get_dot_threshold_for_exit(), 0)   # Immediate
        self.assertEqual(self.pinky._get_dot_threshold_for_exit(), 0)    # Immediate
        self.assertEqual(self.inky._get_dot_threshold_for_exit(), 30)    # 30 dots
        self.assertEqual(self.sue._get_dot_threshold_for_exit(), 60)     # 60 dots
    
    def test_house_mechanics_exit_timing(self):
        """Test ghost house exit timing mechanics."""
        # Set Inky to be in house
        self.inky.set_mode(GhostMode.IN_HOUSE)
        self.assertEqual(self.inky.mode, GhostMode.IN_HOUSE)
        
        # Test exit based on dots eaten
        self.inky._update_house_mechanics(dots_eaten=35)  # Above threshold of 30
        self.assertEqual(self.inky.mode, GhostMode.EXITING_HOUSE)
        
        # Test exit based on timer
        self.sue.set_mode(GhostMode.IN_HOUSE)
        self.sue.house_exit_timer = 0  # Timer expired
        self.sue._update_house_mechanics(dots_eaten=0)  # Below threshold
        self.assertEqual(self.sue.mode, GhostMode.EXITING_HOUSE)
    
    def test_house_patrol_behavior(self):
        """Test ghost patrol behavior inside the house."""
        self.inky.set_mode(GhostMode.IN_HOUSE)
        self.inky.position = Position(self.house_position.x, self.house_position.y - 20)
        
        self.inky._calculate_house_patrol_target()
        
        # Should target the opposite end of the house
        expected_y = self.house_position.y + 20  # Bottom of house
        self.assertEqual(self.inky.target_position.x, self.house_position.x)
        self.assertEqual(self.inky.target_position.y, expected_y)
    
    def test_global_mode_timer_sequence(self):
        """Test global mode timer and scatter/chase sequence."""
        self.blinky.set_mode(GhostMode.NORMAL)
        self.blinky.global_mode_timer = 0
        self.blinky.current_mode_index = 0
        
        # Simulate time passing to trigger first scatter mode
        for _ in range(420):  # First scatter duration
            self.blinky._update_global_mode_timer()
        
        # Should have moved to next mode in sequence
        self.assertEqual(self.blinky.current_mode_index, 1)
    
    def test_mode_transitions_on_eaten(self):
        """Test proper mode transitions when ghost is eaten."""
        self.blinky.set_mode(GhostMode.EATEN, duration=180)
        
        self.assertEqual(self.blinky.mode, GhostMode.EATEN)
        self.assertEqual(self.blinky.eaten_timer, 180)
        
        # Target should be set to ghost house
        self.assertEqual(self.blinky.target_position.x, self.blinky.ghost_house_position.x)
        self.assertEqual(self.blinky.target_position.y, self.blinky.ghost_house_position.y)
    
    def test_mode_transitions_on_frightened(self):
        """Test proper mode transitions when ghost becomes frightened."""
        original_direction = self.blinky.direction
        self.blinky.direction = Direction.UP
        
        self.blinky.set_mode(GhostMode.FRIGHTENED, duration=600)
        
        self.assertEqual(self.blinky.mode, GhostMode.FRIGHTENED)
        self.assertEqual(self.blinky.frightened_timer, 600)
        # Direction should be reversed
        self.assertEqual(self.blinky.direction, Direction.DOWN)
    
    def test_respawn_after_eaten(self):
        """Test ghost respawn mechanics after being eaten."""
        self.blinky.set_mode(GhostMode.EATEN, duration=1)  # Very short duration
        
        # Update to trigger respawn
        self.blinky._update_mode_timers()
        
        # Should return to normal mode
        self.assertEqual(self.blinky.mode, GhostMode.NORMAL)
        self.assertEqual(self.blinky.eaten_timer, 0)
    
    def test_frightened_timer_expiration(self):
        """Test frightened mode timer expiration."""
        self.blinky.set_mode(GhostMode.FRIGHTENED, duration=1)  # Very short duration
        
        # Update to trigger mode change
        self.blinky._update_mode_timers()
        
        # Should return to normal mode
        self.assertEqual(self.blinky.mode, GhostMode.NORMAL)
        self.assertEqual(self.blinky.frightened_timer, 0)
    
    def test_direction_choice_avoids_reversal(self):
        """Test that ghosts avoid immediate direction reversals."""
        self.blinky.position = Position(100, 100)
        self.blinky.direction = Direction.UP  # Moving UP
        self.blinky.target_position = Position(50, 100)  # Target to the left
        
        # Mock valid moves to include opposite direction
        with patch.object(self.maze, 'get_valid_moves') as mock_moves:
            mock_moves.return_value = [Direction.LEFT, Direction.DOWN, Direction.UP]
            
            direction = self.blinky._choose_best_direction()
            
            # Should choose LEFT (toward target) and avoid DOWN (opposite of UP)
            # DOWN should be removed from consideration, leaving LEFT as best choice
            self.assertEqual(direction, Direction.LEFT)
    
    def test_frightened_random_movement(self):
        """Test that frightened ghosts have some random movement."""
        self.blinky.set_mode(GhostMode.FRIGHTENED)
        self.blinky.position = Position(100, 100)
        
        # Mock random to always return True for random movement
        with patch('random.random', return_value=0.2):  # 20% < 30% threshold
            with patch.object(self.maze, 'get_valid_moves') as mock_moves:
                mock_moves.return_value = [Direction.LEFT, Direction.RIGHT]
                
                with patch('random.choice', return_value=Direction.RIGHT) as mock_choice:
                    direction = self.blinky._choose_best_direction()
                    
                    # Should use random choice
                    mock_choice.assert_called_once()
                    self.assertEqual(direction, Direction.RIGHT)
    
    def test_update_method_integration(self):
        """Test the main update method integrates all AI components."""
        player_pos = Position(200, 200)
        other_ghosts = [self.pinky, self.inky, self.sue]
        
        # Test normal update
        self.blinky.update(player_pos, other_ghosts, dots_eaten=10)
        
        # Should have updated target position
        self.assertIsInstance(self.blinky.target_position, Position)
        
        # Animation timer should advance
        old_timer = self.blinky.animation_timer
        self.blinky.update(player_pos, other_ghosts, dots_eaten=10)
        self.assertGreaterEqual(self.blinky.animation_timer, old_timer)


if __name__ == '__main__':
    unittest.main()