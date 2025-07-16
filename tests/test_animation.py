"""
Unit tests for the animation system.
"""

import unittest
import pygame
from unittest.mock import Mock, patch

from pacman_game.animation import (
    Animation, AnimationFrame, SpriteAnimation, FlashAnimation, 
    SmoothMoveAnimation, AnimationManager, SpriteRenderer, AnimationType
)
from pacman_game.models import Direction, GhostMode


class TestAnimationFrame(unittest.TestCase):
    """Test cases for AnimationFrame dataclass."""
    
    def test_animation_frame_creation(self):
        """Test creating an animation frame."""
        frame = AnimationFrame(duration=10, data="test_data")
        self.assertEqual(frame.duration, 10)
        self.assertEqual(frame.data, "test_data")
    
    def test_animation_frame_with_different_data_types(self):
        """Test animation frame with various data types."""
        # Test with integer data
        frame1 = AnimationFrame(5, 42)
        self.assertEqual(frame1.data, 42)
        
        # Test with tuple data
        frame2 = AnimationFrame(8, (255, 0, 0))
        self.assertEqual(frame2.data, (255, 0, 0))
        
        # Test with dict data
        frame3 = AnimationFrame(12, {"x": 10, "y": 20})
        self.assertEqual(frame3.data, {"x": 10, "y": 20})


class TestAnimation(unittest.TestCase):
    """Test cases for base Animation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.frames = [
            AnimationFrame(10, "frame1"),
            AnimationFrame(15, "frame2"),
            AnimationFrame(8, "frame3")
        ]
        self.animation = Animation(self.frames, loop=True)
    
    def test_animation_initialization(self):
        """Test animation initialization."""
        self.assertEqual(len(self.animation.frames), 3)
        self.assertTrue(self.animation.loop)
        self.assertEqual(self.animation.current_frame_index, 0)
        self.assertEqual(self.animation.frame_timer, 0)
        self.assertFalse(self.animation.finished)
        self.assertFalse(self.animation.paused)
    
    def test_get_current_frame(self):
        """Test getting current animation frame."""
        current_frame = self.animation.get_current_frame()
        self.assertEqual(current_frame.data, "frame1")
        self.assertEqual(current_frame.duration, 10)
    
    def test_animation_update_timing(self):
        """Test animation frame timing and progression."""
        # Should stay on first frame for 10 updates
        for i in range(9):
            self.animation.update()
            self.assertEqual(self.animation.current_frame_index, 0)
            self.assertEqual(self.animation.frame_timer, i + 1)
        
        # On 10th update, should advance to next frame
        self.animation.update()
        self.assertEqual(self.animation.current_frame_index, 1)
        self.assertEqual(self.animation.frame_timer, 0)
        
        # Test second frame duration (15 frames)
        for i in range(14):
            self.animation.update()
        self.assertEqual(self.animation.current_frame_index, 1)
        
        self.animation.update()
        self.assertEqual(self.animation.current_frame_index, 2)
    
    def test_animation_looping(self):
        """Test animation looping behavior."""
        # Advance through all frames
        for _ in range(10):  # First frame
            self.animation.update()
        for _ in range(15):  # Second frame
            self.animation.update()
        for _ in range(8):   # Third frame
            self.animation.update()
        
        # Should loop back to first frame
        self.assertEqual(self.animation.current_frame_index, 0)
        self.assertFalse(self.animation.finished)
    
    def test_animation_no_loop(self):
        """Test animation without looping."""
        no_loop_animation = Animation(self.frames, loop=False)
        
        # Advance through all frames
        for _ in range(10 + 15 + 8):
            no_loop_animation.update()
        
        # Should stay on last frame and be marked as finished
        self.assertEqual(no_loop_animation.current_frame_index, 2)
        self.assertTrue(no_loop_animation.finished)
    
    def test_animation_pause_resume(self):
        """Test pausing and resuming animation."""
        # Update a few times
        for _ in range(5):
            self.animation.update()
        
        initial_timer = self.animation.frame_timer
        
        # Pause animation
        self.animation.pause()
        self.assertTrue(self.animation.paused)
        
        # Updates should not advance timer when paused
        for _ in range(3):
            self.animation.update()
        self.assertEqual(self.animation.frame_timer, initial_timer)
        
        # Resume animation
        self.animation.resume()
        self.assertFalse(self.animation.paused)
        
        # Updates should advance timer again
        self.animation.update()
        self.assertEqual(self.animation.frame_timer, initial_timer + 1)
    
    def test_animation_reset(self):
        """Test resetting animation to beginning."""
        # Advance animation
        for _ in range(20):
            self.animation.update()
        
        # Reset animation
        self.animation.reset()
        
        self.assertEqual(self.animation.current_frame_index, 0)
        self.assertEqual(self.animation.frame_timer, 0)
        self.assertFalse(self.animation.finished)
    
    def test_empty_animation(self):
        """Test animation with no frames."""
        empty_animation = Animation([], loop=True)
        
        # Should handle empty frames gracefully
        empty_animation.update()
        self.assertIsNone(empty_animation.get_current_frame())


class TestSpriteAnimation(unittest.TestCase):
    """Test cases for SpriteAnimation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sprite_indices = [0, 1, 2, 1]
        self.sprite_animation = SpriteAnimation(self.sprite_indices, frame_duration=8)
    
    def test_sprite_animation_initialization(self):
        """Test sprite animation initialization."""
        self.assertEqual(len(self.sprite_animation.frames), 4)
        self.assertTrue(self.sprite_animation.loop)
        
        # Check that frames were created correctly
        for i, frame in enumerate(self.sprite_animation.frames):
            self.assertEqual(frame.duration, 8)
            self.assertEqual(frame.data, self.sprite_indices[i])
    
    def test_get_current_sprite_index(self):
        """Test getting current sprite index."""
        # Should start with first sprite
        self.assertEqual(self.sprite_animation.get_current_sprite_index(), 0)
        
        # Advance to next frame
        for _ in range(8):
            self.sprite_animation.update()
        self.assertEqual(self.sprite_animation.get_current_sprite_index(), 1)
        
        # Advance to third frame
        for _ in range(8):
            self.sprite_animation.update()
        self.assertEqual(self.sprite_animation.get_current_sprite_index(), 2)
    
    def test_sprite_animation_cycling(self):
        """Test sprite animation cycling through indices."""
        expected_sequence = [0, 1, 2, 1, 0, 1, 2, 1]  # Two full cycles
        
        for expected_index in expected_sequence:
            self.assertEqual(self.sprite_animation.get_current_sprite_index(), expected_index)
            # Advance one full frame
            for _ in range(8):
                self.sprite_animation.update()


class TestFlashAnimation(unittest.TestCase):
    """Test cases for FlashAnimation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.flash_animation = FlashAnimation(self.colors, flash_duration=10)
    
    def test_flash_animation_initialization(self):
        """Test flash animation initialization."""
        self.assertEqual(len(self.flash_animation.frames), 3)
        self.assertTrue(self.flash_animation.loop)
        
        # Check that frames were created correctly
        for i, frame in enumerate(self.flash_animation.frames):
            self.assertEqual(frame.duration, 10)
            self.assertEqual(frame.data, self.colors[i])
    
    def test_get_current_color(self):
        """Test getting current flash color."""
        # Should start with first color
        self.assertEqual(self.flash_animation.get_current_color(), (255, 0, 0))
        
        # Advance to next color
        for _ in range(10):
            self.flash_animation.update()
        self.assertEqual(self.flash_animation.get_current_color(), (0, 255, 0))
        
        # Advance to third color
        for _ in range(10):
            self.flash_animation.update()
        self.assertEqual(self.flash_animation.get_current_color(), (0, 0, 255))
    
    def test_flash_animation_cycling(self):
        """Test flash animation cycling through colors."""
        expected_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 0)]
        
        for expected_color in expected_colors:
            self.assertEqual(self.flash_animation.get_current_color(), expected_color)
            # Advance one full frame
            for _ in range(10):
                self.flash_animation.update()


class TestSmoothMoveAnimation(unittest.TestCase):
    """Test cases for SmoothMoveAnimation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.start_pos = (0.0, 0.0)
        self.end_pos = (100.0, 50.0)
        self.move_animation = SmoothMoveAnimation(
            self.start_pos, self.end_pos, duration=20, easing="linear"
        )
    
    def test_smooth_move_initialization(self):
        """Test smooth move animation initialization."""
        self.assertEqual(self.move_animation.start_pos, (0.0, 0.0))
        self.assertEqual(self.move_animation.end_pos, (100.0, 50.0))
        self.assertEqual(self.move_animation.easing, "linear")
        self.assertFalse(self.move_animation.loop)
    
    def test_linear_interpolation(self):
        """Test linear position interpolation."""
        # At start
        self.assertEqual(self.move_animation.get_current_position(), (0.0, 0.0))
        
        # At 25% progress (5 frames out of 20)
        for _ in range(5):
            self.move_animation.update()
        pos = self.move_animation.get_current_position()
        self.assertAlmostEqual(pos[0], 25.0, places=1)
        self.assertAlmostEqual(pos[1], 12.5, places=1)
        
        # At 50% progress (10 frames out of 20)
        for _ in range(5):
            self.move_animation.update()
        pos = self.move_animation.get_current_position()
        self.assertAlmostEqual(pos[0], 50.0, places=1)
        self.assertAlmostEqual(pos[1], 25.0, places=1)
        
        # At end (20 frames)
        for _ in range(10):
            self.move_animation.update()
        pos = self.move_animation.get_current_position()
        self.assertEqual(pos, (100.0, 50.0))
    
    def test_easing_functions(self):
        """Test different easing functions."""
        # Test ease_in
        ease_in_anim = SmoothMoveAnimation((0, 0), (100, 100), 20, "ease_in")
        for _ in range(10):  # 50% progress
            ease_in_anim.update()
        pos = ease_in_anim.get_current_position()
        # Ease in should be slower at start, so less than 50% at 50% time
        self.assertLess(pos[0], 50.0)
        
        # Test ease_out
        ease_out_anim = SmoothMoveAnimation((0, 0), (100, 100), 20, "ease_out")
        for _ in range(10):  # 50% progress
            ease_out_anim.update()
        pos = ease_out_anim.get_current_position()
        # Ease out should be faster at start, so more than 50% at 50% time
        self.assertGreater(pos[0], 50.0)
    
    def test_finished_animation(self):
        """Test animation when finished."""
        # Complete the animation
        for _ in range(25):  # More than duration
            self.move_animation.update()
        
        # Should return end position even after completion
        self.assertEqual(self.move_animation.get_current_position(), (100.0, 50.0))
        self.assertTrue(self.move_animation.is_finished())


class TestAnimationManager(unittest.TestCase):
    """Test cases for AnimationManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = AnimationManager()
    
    def test_animation_manager_initialization(self):
        """Test animation manager initialization."""
        self.assertIsInstance(self.manager.animations, dict)
        self.assertIsInstance(self.manager.entity_animations, dict)
        self.assertIsInstance(self.manager.player_animations, dict)
        self.assertIsInstance(self.manager.ghost_animations, dict)
        
        # Check that default animations are set up
        self.assertIn(Direction.RIGHT, self.manager.player_animations)
        self.assertIn(Direction.LEFT, self.manager.player_animations)
        self.assertIn(Direction.UP, self.manager.player_animations)
        self.assertIn(Direction.DOWN, self.manager.player_animations)
        self.assertIn(Direction.NONE, self.manager.player_animations)
        
        self.assertIn(GhostMode.NORMAL, self.manager.ghost_animations)
        self.assertIn(GhostMode.FRIGHTENED, self.manager.ghost_animations)
        self.assertIn(GhostMode.EATEN, self.manager.ghost_animations)
    
    def test_add_and_get_animation(self):
        """Test adding and retrieving entity animations."""
        test_animation = SpriteAnimation([0, 1, 2], frame_duration=5)
        
        # Add animation for entity
        self.manager.add_animation("player1", "walk", test_animation)
        
        # Retrieve animation
        retrieved = self.manager.get_animation("player1", "walk")
        self.assertEqual(retrieved, test_animation)
        
        # Test non-existent animation
        self.assertIsNone(self.manager.get_animation("player1", "nonexistent"))
        self.assertIsNone(self.manager.get_animation("nonexistent", "walk"))
    
    def test_get_player_animation(self):
        """Test getting player animations for different directions."""
        # Test valid directions
        right_anim = self.manager.get_player_animation(Direction.RIGHT)
        self.assertIsInstance(right_anim, SpriteAnimation)
        
        left_anim = self.manager.get_player_animation(Direction.LEFT)
        self.assertIsInstance(left_anim, SpriteAnimation)
        
        # Test that different directions return different animations
        self.assertNotEqual(right_anim, left_anim)
    
    def test_get_ghost_animation(self):
        """Test getting ghost animations for different modes."""
        # Test valid modes
        normal_anim = self.manager.get_ghost_animation(GhostMode.NORMAL)
        self.assertIsInstance(normal_anim, SpriteAnimation)
        
        frightened_anim = self.manager.get_ghost_animation(GhostMode.FRIGHTENED)
        self.assertIsInstance(frightened_anim, SpriteAnimation)
        
        # Test that different modes return different animations
        self.assertNotEqual(normal_anim, frightened_anim)
    
    def test_get_power_pellet_animation(self):
        """Test getting power pellet flash animation."""
        flash_anim = self.manager.get_power_pellet_animation()
        self.assertIsInstance(flash_anim, FlashAnimation)
    
    def test_update_all_animations(self):
        """Test updating all managed animations."""
        # Add some test animations
        test_anim1 = SpriteAnimation([0, 1], frame_duration=5)
        test_anim2 = SpriteAnimation([2, 3], frame_duration=3)
        
        self.manager.add_animation("entity1", "anim1", test_anim1)
        self.manager.add_animation("entity2", "anim2", test_anim2)
        
        # Update all animations
        self.manager.update_all()
        
        # Verify that animations were updated (frame timers should advance)
        # This is a basic test - in practice, we'd need to check internal state
        self.assertIsNotNone(test_anim1.get_current_frame())
        self.assertIsNotNone(test_anim2.get_current_frame())
    
    def test_reset_all_animations(self):
        """Test resetting all animations."""
        # Advance some animations
        for _ in range(10):
            self.manager.update_all()
        
        # Reset all animations
        self.manager.reset_all_animations()
        
        # Check that player animations are reset
        for animation in self.manager.player_animations.values():
            self.assertEqual(animation.current_frame_index, 0)
            self.assertEqual(animation.frame_timer, 0)
            self.assertFalse(animation.finished)
    
    def test_pause_resume_all_animations(self):
        """Test pausing and resuming all animations."""
        # Pause all animations
        self.manager.pause_all_animations()
        
        # Check that default animations are paused
        for animation in self.manager.player_animations.values():
            self.assertTrue(animation.paused)
        
        # Resume all animations
        self.manager.resume_all_animations()
        
        # Check that animations are resumed
        for animation in self.manager.player_animations.values():
            self.assertFalse(animation.paused)


class TestSpriteRenderer(unittest.TestCase):
    """Test cases for SpriteRenderer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame for testing
        pygame.init()
        self.renderer = SpriteRenderer(tile_size=20)
    
    def tearDown(self):
        """Clean up after tests."""
        self.renderer.cleanup()
        pygame.quit()
    
    def test_sprite_renderer_initialization(self):
        """Test sprite renderer initialization."""
        self.assertEqual(self.renderer.tile_size, 20)
        self.assertIsInstance(self.renderer.sprite_cache, dict)
        
        # Check that basic sprites were created
        self.assertGreater(len(self.renderer.sprite_cache), 0)
    
    def test_get_sprite(self):
        """Test getting sprites from cache."""
        # Test getting existing sprite
        sprite = self.renderer.get_sprite("player_0")
        self.assertIsInstance(sprite, pygame.Surface)
        
        # Test getting non-existent sprite
        self.assertIsNone(self.renderer.get_sprite("nonexistent"))
    
    def test_render_animated_sprite(self):
        """Test rendering animated sprites."""
        # Create test surface and animation
        test_surface = pygame.Surface((100, 100))
        test_animation = SpriteAnimation([0, 1, 2], frame_duration=5)
        
        # Test that the method runs without error
        try:
            self.renderer.render_animated_sprite(
                test_surface, (10, 20), "player", test_animation
            )
            # If we get here, the method executed successfully
            success = True
        except Exception as e:
            success = False
            print(f"render_animated_sprite failed: {e}")
        
        self.assertTrue(success, "render_animated_sprite should execute without error")
    
    @patch('pygame.draw.circle')
    def test_render_flashing_sprite(self, mock_circle):
        """Test rendering flashing sprites."""
        # Create test surface and animation
        test_surface = pygame.Surface((100, 100))
        flash_animation = FlashAnimation([(255, 0, 0), (0, 255, 0)], flash_duration=10)
        
        # Render flashing sprite
        self.renderer.render_flashing_sprite(
            test_surface, (30, 40), (255, 255, 255), flash_animation, radius=8
        )
        
        # Verify that circle drawing was called
        mock_circle.assert_called_once()
        
        # Check that the correct color was used
        call_args = mock_circle.call_args
        self.assertEqual(call_args[0][1], (255, 0, 0))  # First color in animation
    
    def test_sprite_cache_management(self):
        """Test sprite cache management."""
        initial_cache_size = len(self.renderer.sprite_cache)
        
        # Cache should have been populated during initialization
        self.assertGreater(initial_cache_size, 0)
        
        # Cleanup should clear cache
        self.renderer.cleanup()
        self.assertEqual(len(self.renderer.sprite_cache), 0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)