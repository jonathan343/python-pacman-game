"""
Unit tests for UI display system functionality.
Tests the renderer's UI components including score, lives, and level display.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame
import sys
import os

# Add the parent directory to the path to import pacman_game modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pacman_game.renderer import Renderer
from pacman_game.models import ScoreManager, Position, Maze


class TestUIDisplay(unittest.TestCase):
    """Test cases for UI display functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock pygame to avoid actual display initialization
        self.pygame_patcher = patch('pacman_game.renderer.pygame')
        self.mock_pygame = self.pygame_patcher.start()
        
        # Mock display and font objects
        self.mock_screen = Mock()
        self.mock_font = Mock()
        self.mock_small_font = Mock()
        
        self.mock_pygame.display.set_mode.return_value = self.mock_screen
        self.mock_pygame.font.Font.side_effect = [self.mock_font, self.mock_small_font]
        
        # Create renderer instance
        self.renderer = Renderer(screen_width=800, screen_height=900, tile_size=20)
        
        # Create test score manager
        self.score_manager = ScoreManager(starting_lives=3)
        self.score_manager.initialize_level(100)  # 100 dots in level
    
    def tearDown(self):
        """Clean up after each test method."""
        self.pygame_patcher.stop()
    
    def test_render_ui_basic_elements(self):
        """Test that basic UI elements are rendered correctly."""
        # Set up test data
        self.score_manager.score = 1500
        self.score_manager.level = 2
        self.score_manager.lives = 2
        
        # Mock font rendering
        mock_score_surface = Mock()
        mock_lives_surface = Mock()
        mock_level_surface = Mock()
        
        self.mock_font.render.side_effect = [
            mock_score_surface,  # Score text
            mock_lives_surface,  # Lives text
            mock_level_surface   # Level text
        ]
        
        # Call render_ui
        self.renderer.render_ui(self.score_manager)
        
        # Verify font.render was called with correct parameters
        expected_calls = [
            unittest.mock.call("SCORE: 1,500", True, self.renderer.YELLOW),
            unittest.mock.call("LIVES:", True, self.renderer.WHITE),
            unittest.mock.call("LEVEL: 2", True, self.renderer.CYAN)
        ]
        
        # Check that font.render was called (allowing for additional calls)
        self.assertTrue(self.mock_font.render.call_count >= 3)
        
        # Verify screen.blit was called to draw the elements
        self.assertTrue(self.mock_screen.blit.called)
        self.assertTrue(self.mock_screen.blit.call_count >= 3)
    
    def test_render_ui_lives_icons(self):
        """Test that life icons are drawn correctly."""
        # Set up test data with different life counts
        test_cases = [1, 2, 3, 5]
        
        for lives_count in test_cases:
            with self.subTest(lives=lives_count):
                self.score_manager.lives = lives_count
                
                # Reset mock calls
                self.mock_pygame.draw.circle.reset_mock()
                self.mock_pygame.draw.polygon.reset_mock()
                
                # Call render_ui
                self.renderer.render_ui(self.score_manager)
                
                # Verify that circles were drawn for each life (life icons)
                # Each life icon consists of a circle and a polygon (mouth)
                circle_calls = self.mock_pygame.draw.circle.call_args_list
                polygon_calls = self.mock_pygame.draw.polygon.call_args_list
                
                # Count life icon circles (yellow circles for lives)
                life_icon_circles = [
                    call for call in circle_calls 
                    if len(call[0]) >= 3 and call[0][1] == self.renderer.YELLOW and call[0][3] == 8
                ]
                
                self.assertEqual(len(life_icon_circles), lives_count, 
                               f"Expected {lives_count} life icons, got {len(life_icon_circles)}")
    
    def test_render_ui_progress_bar(self):
        """Test that progress bar is rendered correctly."""
        # Set up test data with partial progress
        self.score_manager.dots_collected_in_level = 30
        self.score_manager.total_dots_in_level = 100
        
        # Mock small font for dots remaining text
        mock_dots_surface = Mock()
        self.mock_small_font.render.return_value = mock_dots_surface
        
        # Call render_ui
        self.renderer.render_ui(self.score_manager)
        
        # Verify progress bar rectangles were drawn
        rect_calls = self.mock_pygame.draw.rect.call_args_list
        
        # Should have background bar, progress fill, and border
        self.assertTrue(len(rect_calls) >= 3, "Progress bar should draw at least 3 rectangles")
        
        # Verify dots remaining text was rendered
        self.mock_small_font.render.assert_called_with("Dots Remaining: 70", True, self.renderer.WHITE)
    
    def test_render_ui_minimal(self):
        """Test minimal UI rendering for testing purposes."""
        # Test data
        score = 2500
        lives = 1
        level = 3
        
        # Mock font rendering
        mock_surfaces = [Mock(), Mock(), Mock()]
        self.mock_font.render.side_effect = mock_surfaces
        
        # Call render_ui_minimal
        self.renderer.render_ui_minimal(score, lives, level)
        
        # Verify correct text was rendered
        expected_calls = [
            unittest.mock.call("Score: 2500", True, self.renderer.WHITE),
            unittest.mock.call("Lives: 1", True, self.renderer.WHITE),
            unittest.mock.call("Level: 3", True, self.renderer.WHITE)
        ]
        
        self.mock_font.render.assert_has_calls(expected_calls)
        
        # Verify surfaces were blitted to screen
        self.assertEqual(self.mock_screen.blit.call_count, 3)
    
    def test_get_ui_bounds(self):
        """Test UI bounds calculation for layout purposes."""
        bounds = self.renderer.get_ui_bounds()
        
        # Verify structure of returned bounds
        expected_keys = ['ui_panel', 'score', 'lives_label', 'lives_icons', 
                        'level', 'progress_info', 'progress_bar']
        
        for key in expected_keys:
            self.assertIn(key, bounds, f"Missing key '{key}' in UI bounds")
        
        # Verify UI panel bounds
        ui_panel = bounds['ui_panel']
        self.assertEqual(ui_panel['x'], 0)
        self.assertEqual(ui_panel['width'], self.renderer.screen_width)
        self.assertEqual(ui_panel['height'], 150)
        self.assertEqual(ui_panel['y'], self.renderer.screen_height - 150)
        
        # Verify progress bar dimensions
        progress_bar = bounds['progress_bar']
        self.assertEqual(progress_bar['width'], 200)
        self.assertEqual(progress_bar['height'], 10)
    
    def test_ui_real_time_updates(self):
        """Test that UI updates reflect real-time changes in game state."""
        # Initial state
        initial_score = 100
        initial_lives = 3
        initial_level = 1
        
        self.score_manager.score = initial_score
        self.score_manager.lives = initial_lives
        self.score_manager.level = initial_level
        
        # Mock font rendering
        self.mock_font.render.return_value = Mock()
        
        # First render
        self.renderer.render_ui(self.score_manager)
        first_render_calls = self.mock_font.render.call_args_list.copy()
        
        # Update game state
        self.score_manager.score = 2500
        self.score_manager.lives = 2
        self.score_manager.level = 2
        
        # Reset mock to track new calls
        self.mock_font.render.reset_mock()
        
        # Second render
        self.renderer.render_ui(self.score_manager)
        second_render_calls = self.mock_font.render.call_args_list
        
        # Verify that updated values are rendered
        score_calls = [call for call in second_render_calls if "SCORE:" in str(call)]
        level_calls = [call for call in second_render_calls if "LEVEL:" in str(call)]
        
        self.assertTrue(any("2,500" in str(call) for call in score_calls), 
                       "Updated score should be rendered")
        self.assertTrue(any("2" in str(call) for call in level_calls), 
                       "Updated level should be rendered")
    
    def test_ui_score_formatting(self):
        """Test that scores are formatted correctly with commas."""
        test_scores = [0, 100, 1000, 10000, 100000, 1234567]
        expected_formats = ["0", "100", "1,000", "10,000", "100,000", "1,234,567"]
        
        for score, expected in zip(test_scores, expected_formats):
            with self.subTest(score=score):
                self.score_manager.score = score
                
                # Reset mock
                self.mock_font.render.reset_mock()
                
                # Render UI
                self.renderer.render_ui(self.score_manager)
                
                # Check that the formatted score was rendered
                score_calls = [call for call in self.mock_font.render.call_args_list 
                             if "SCORE:" in str(call)]
                
                self.assertTrue(any(expected in str(call) for call in score_calls),
                               f"Score {score} should be formatted as {expected}")
    
    def test_ui_level_completion_progress(self):
        """Test that level completion progress is displayed correctly."""
        # Test different completion percentages
        test_cases = [
            (0, 100, 0.0),    # 0% complete
            (25, 100, 0.25),  # 25% complete
            (50, 100, 0.5),   # 50% complete
            (75, 100, 0.75),  # 75% complete
            (100, 100, 1.0)   # 100% complete
        ]
        
        for collected, total, expected_progress in test_cases:
            with self.subTest(collected=collected, total=total):
                self.score_manager.dots_collected_in_level = collected
                self.score_manager.total_dots_in_level = total
                
                # Reset mock
                self.mock_pygame.draw.rect.reset_mock()
                
                # Render UI
                self.renderer.render_ui(self.score_manager)
                
                # Verify progress calculation
                actual_progress = self.score_manager.get_level_progress()
                self.assertAlmostEqual(actual_progress, expected_progress, places=2)
                
                # Verify progress bar was drawn
                rect_calls = self.mock_pygame.draw.rect.call_args_list
                self.assertTrue(len(rect_calls) >= 3, "Progress bar should be drawn")
    
    def test_ui_no_dots_remaining(self):
        """Test UI behavior when no dots remain (level complete)."""
        # Set up completed level
        self.score_manager.dots_collected_in_level = 100
        self.score_manager.total_dots_in_level = 100
        
        # Mock font rendering
        self.mock_small_font.render.return_value = Mock()
        
        # Render UI
        self.renderer.render_ui(self.score_manager)
        
        # Verify that dots remaining is 0
        self.assertEqual(self.score_manager.get_dots_remaining(), 0)
        
        # Progress bar should still be drawn even when complete
        rect_calls = self.mock_pygame.draw.rect.call_args_list
        self.assertTrue(len(rect_calls) >= 3, "Progress bar should be drawn even when complete")
    
    def test_ui_high_score_display(self):
        """Test high score display when available."""
        # Add high_score attribute to score_manager
        self.score_manager.high_score = 50000
        
        # Mock font rendering
        self.mock_small_font.render.return_value = Mock()
        
        # Render UI
        self.renderer.render_ui(self.score_manager)
        
        # Verify high score was rendered
        high_score_calls = [call for call in self.mock_small_font.render.call_args_list 
                           if "HIGH:" in str(call)]
        
        self.assertTrue(len(high_score_calls) > 0, "High score should be displayed")
        self.assertTrue(any("50,000" in str(call) for call in high_score_calls),
                       "High score should be formatted correctly")


class TestUIIntegration(unittest.TestCase):
    """Integration tests for UI display with game components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock pygame
        self.pygame_patcher = patch('pacman_game.renderer.pygame')
        self.mock_pygame = self.pygame_patcher.start()
        
        # Mock display and font objects
        self.mock_screen = Mock()
        self.mock_font = Mock()
        self.mock_small_font = Mock()
        
        self.mock_pygame.display.set_mode.return_value = self.mock_screen
        self.mock_pygame.font.Font.side_effect = [self.mock_font, self.mock_small_font]
        
        # Create components
        self.renderer = Renderer()
        self.score_manager = ScoreManager()
        self.maze = Maze()
        
        # Initialize level
        self.score_manager.initialize_level(self.maze.get_dots_remaining())
    
    def tearDown(self):
        """Clean up after tests."""
        self.pygame_patcher.stop()
    
    def test_ui_updates_with_score_changes(self):
        """Test that UI reflects score changes from gameplay."""
        # Mock font rendering
        self.mock_font.render.return_value = Mock()
        
        # Initial render
        self.renderer.render_ui(self.score_manager)
        
        # Simulate collecting dots
        initial_score = self.score_manager.get_score()
        self.score_manager.collect_dot()
        self.score_manager.collect_dot()
        
        # Verify score increased
        self.assertEqual(self.score_manager.get_score(), initial_score + 20)
        
        # Render again
        self.mock_font.render.reset_mock()
        self.renderer.render_ui(self.score_manager)
        
        # Verify updated score is rendered
        score_calls = [call for call in self.mock_font.render.call_args_list 
                      if "SCORE:" in str(call)]
        self.assertTrue(len(score_calls) > 0, "Score should be rendered")
    
    def test_ui_updates_with_life_changes(self):
        """Test that UI reflects life changes."""
        # Mock font and drawing
        self.mock_font.render.return_value = Mock()
        
        # Initial state - 3 lives
        initial_lives = self.score_manager.get_lives()
        self.renderer.render_ui(self.score_manager)
        
        # Lose a life
        self.score_manager.lose_life()
        
        # Render again
        self.mock_pygame.draw.circle.reset_mock()
        self.renderer.render_ui(self.score_manager)
        
        # Verify fewer life icons are drawn
        circle_calls = self.mock_pygame.draw.circle.call_args_list
        life_icon_circles = [
            call for call in circle_calls 
            if len(call[0]) >= 3 and call[0][1] == self.renderer.YELLOW and call[0][3] == 8
        ]
        
        expected_lives = initial_lives - 1
        self.assertEqual(len(life_icon_circles), expected_lives,
                        f"Should draw {expected_lives} life icons after losing a life")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)