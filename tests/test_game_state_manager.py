"""
Unit tests for the GameStateManager class.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pacman_game.game_state_manager import GameStateManager
from pacman_game.models import GameState
from pacman_game.config import GameConfig


class TestGameStateManager(unittest.TestCase):
    """Test cases for GameStateManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize pygame for testing
        pygame.init()
        pygame.font.init()
        
        # Create mock screen and config
        self.mock_screen = Mock()
        self.config = GameConfig()
        
        # Create GameStateManager instance
        self.state_manager = GameStateManager(self.mock_screen, self.config)
    
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
    
    def test_initial_state(self):
        """Test that GameStateManager initializes with correct default state."""
        self.assertEqual(self.state_manager.get_current_state(), GameState.MENU)
        self.assertEqual(self.state_manager.get_previous_state(), GameState.MENU)
        self.assertTrue(self.state_manager.is_in_menu())
        self.assertFalse(self.state_manager.is_playing())
        self.assertFalse(self.state_manager.is_game_over())
        self.assertFalse(self.state_manager.is_paused())
    
    def test_state_transitions(self):
        """Test state transitions work correctly."""
        # Test transition from MENU to PLAYING
        self.state_manager.set_state(GameState.PLAYING)
        self.assertEqual(self.state_manager.get_current_state(), GameState.PLAYING)
        self.assertEqual(self.state_manager.get_previous_state(), GameState.MENU)
        self.assertTrue(self.state_manager.is_playing())
        self.assertFalse(self.state_manager.is_in_menu())
        
        # Test transition from PLAYING to GAME_OVER
        self.state_manager.set_state(GameState.GAME_OVER)
        self.assertEqual(self.state_manager.get_current_state(), GameState.GAME_OVER)
        self.assertEqual(self.state_manager.get_previous_state(), GameState.PLAYING)
        self.assertTrue(self.state_manager.is_game_over())
        self.assertFalse(self.state_manager.is_playing())
        
        # Test transition from GAME_OVER to MENU
        self.state_manager.set_state(GameState.MENU)
        self.assertEqual(self.state_manager.get_current_state(), GameState.MENU)
        self.assertEqual(self.state_manager.get_previous_state(), GameState.GAME_OVER)
        self.assertTrue(self.state_manager.is_in_menu())
        self.assertFalse(self.state_manager.is_game_over())
    
    def test_pause_functionality(self):
        """Test pause state transitions."""
        # Start in playing state
        self.state_manager.set_state(GameState.PLAYING)
        
        # Transition to paused
        self.state_manager.set_state(GameState.PAUSED)
        self.assertEqual(self.state_manager.get_current_state(), GameState.PAUSED)
        self.assertEqual(self.state_manager.get_previous_state(), GameState.PLAYING)
        self.assertTrue(self.state_manager.is_paused())
        self.assertFalse(self.state_manager.is_playing())
        
        # Return to playing
        self.state_manager.set_state(GameState.PLAYING)
        self.assertEqual(self.state_manager.get_current_state(), GameState.PLAYING)
        self.assertEqual(self.state_manager.get_previous_state(), GameState.PAUSED)
        self.assertTrue(self.state_manager.is_playing())
        self.assertFalse(self.state_manager.is_paused())
    
    def test_game_over_data(self):
        """Test setting and retrieving game over data."""
        final_score = 1500
        final_level = 3
        
        self.state_manager.set_game_over_data(final_score, final_level)
        self.assertEqual(self.state_manager.final_score, final_score)
        self.assertEqual(self.state_manager.final_level, final_level)
    
    def test_menu_input_navigation(self):
        """Test menu navigation input handling."""
        # Start in menu state
        self.state_manager.set_state(GameState.MENU)
        initial_selection = self.state_manager.menu_selection
        
        # Test UP key navigation
        up_event = Mock()
        up_event.type = pygame.KEYDOWN
        up_event.key = pygame.K_UP
        self.state_manager.handle_input(up_event)
        
        # Should wrap around to last option
        expected_selection = (initial_selection - 1) % len(self.state_manager.menu_options)
        self.assertEqual(self.state_manager.menu_selection, expected_selection)
        
        # Test DOWN key navigation
        down_event = Mock()
        down_event.type = pygame.KEYDOWN
        down_event.key = pygame.K_DOWN
        self.state_manager.handle_input(down_event)
        
        # Should move to next option
        expected_selection = (expected_selection + 1) % len(self.state_manager.menu_options)
        self.assertEqual(self.state_manager.menu_selection, expected_selection)
    
    def test_menu_selection_execution(self):
        """Test menu option execution."""
        # Set up callbacks
        start_callback = Mock()
        quit_callback = Mock()
        self.state_manager.set_callbacks(
            on_start_game=start_callback,
            on_quit_game=quit_callback
        )
        
        # Test "Start Game" selection
        self.state_manager.menu_selection = 0  # "Start Game"
        enter_event = Mock()
        enter_event.type = pygame.KEYDOWN
        enter_event.key = pygame.K_RETURN
        
        self.state_manager.handle_input(enter_event)
        
        # Should transition to PLAYING state and call start callback
        self.assertEqual(self.state_manager.get_current_state(), GameState.PLAYING)
        start_callback.assert_called_once()
        
        # Reset to menu for next test
        self.state_manager.set_state(GameState.MENU)
        
        # Test "Quit" selection
        self.state_manager.menu_selection = 1  # "Quit"
        self.state_manager.handle_input(enter_event)
        
        # Should call quit callback
        quit_callback.assert_called_once()
    
    def test_game_over_input_navigation(self):
        """Test game over screen navigation."""
        # Start in game over state
        self.state_manager.set_state(GameState.GAME_OVER)
        initial_selection = self.state_manager.game_over_selection
        
        # Test UP key navigation
        up_event = Mock()
        up_event.type = pygame.KEYDOWN
        up_event.key = pygame.K_UP
        self.state_manager.handle_input(up_event)
        
        # Should wrap around to last option
        expected_selection = (initial_selection - 1) % len(self.state_manager.game_over_options)
        self.assertEqual(self.state_manager.game_over_selection, expected_selection)
        
        # Test DOWN key navigation
        down_event = Mock()
        down_event.type = pygame.KEYDOWN
        down_event.key = pygame.K_DOWN
        self.state_manager.handle_input(down_event)
        
        # Should move to next option
        expected_selection = (expected_selection + 1) % len(self.state_manager.game_over_options)
        self.assertEqual(self.state_manager.game_over_selection, expected_selection)
    
    def test_game_over_selection_execution(self):
        """Test game over option execution."""
        # Set up callbacks
        restart_callback = Mock()
        quit_callback = Mock()
        self.state_manager.set_callbacks(
            on_restart_game=restart_callback,
            on_quit_game=quit_callback
        )
        
        # Start in game over state
        self.state_manager.set_state(GameState.GAME_OVER)
        
        # Test "Restart" selection
        self.state_manager.game_over_selection = 0  # "Restart"
        enter_event = Mock()
        enter_event.type = pygame.KEYDOWN
        enter_event.key = pygame.K_RETURN
        
        self.state_manager.handle_input(enter_event)
        
        # Should transition to PLAYING state and call restart callback
        self.assertEqual(self.state_manager.get_current_state(), GameState.PLAYING)
        restart_callback.assert_called_once()
        
        # Reset to game over for next test
        self.state_manager.set_state(GameState.GAME_OVER)
        
        # Test "Main Menu" selection
        self.state_manager.game_over_selection = 1  # "Main Menu"
        self.state_manager.handle_input(enter_event)
        
        # Should transition to MENU state
        self.assertEqual(self.state_manager.get_current_state(), GameState.MENU)
        
        # Reset to game over for next test
        self.state_manager.set_state(GameState.GAME_OVER)
        
        # Test "Quit" selection
        self.state_manager.game_over_selection = 2  # "Quit"
        self.state_manager.handle_input(enter_event)
        
        # Should call quit callback
        quit_callback.assert_called_once()
    
    def test_pause_input_handling(self):
        """Test pause functionality input handling."""
        # Start in playing state
        self.state_manager.set_state(GameState.PLAYING)
        
        # Test pause key (ESC)
        esc_event = Mock()
        esc_event.type = pygame.KEYDOWN
        esc_event.key = pygame.K_ESCAPE
        
        self.state_manager.handle_input(esc_event)
        self.assertEqual(self.state_manager.get_current_state(), GameState.PAUSED)
        
        # Test resume key (ESC again)
        self.state_manager.handle_input(esc_event)
        self.assertEqual(self.state_manager.get_current_state(), GameState.PLAYING)
        
        # Test pause with P key
        self.state_manager.set_state(GameState.PLAYING)
        p_event = Mock()
        p_event.type = pygame.KEYDOWN
        p_event.key = pygame.K_p
        
        self.state_manager.handle_input(p_event)
        self.assertEqual(self.state_manager.get_current_state(), GameState.PAUSED)
        
        # Test return to menu from pause
        m_event = Mock()
        m_event.type = pygame.KEYDOWN
        m_event.key = pygame.K_m
        
        self.state_manager.handle_input(m_event)
        self.assertEqual(self.state_manager.get_current_state(), GameState.MENU)
    
    def test_callback_setting(self):
        """Test setting callback functions."""
        start_callback = Mock()
        restart_callback = Mock()
        quit_callback = Mock()
        
        self.state_manager.set_callbacks(
            on_start_game=start_callback,
            on_restart_game=restart_callback,
            on_quit_game=quit_callback
        )
        
        self.assertEqual(self.state_manager.on_start_game, start_callback)
        self.assertEqual(self.state_manager.on_restart_game, restart_callback)
        self.assertEqual(self.state_manager.on_quit_game, quit_callback)
    
    def test_state_query_methods(self):
        """Test state query helper methods."""
        # Test can_handle_game_input
        self.state_manager.set_state(GameState.PLAYING)
        self.assertTrue(self.state_manager.can_handle_game_input())
        
        self.state_manager.set_state(GameState.MENU)
        self.assertFalse(self.state_manager.can_handle_game_input())
        
        # Test should_update_game
        self.state_manager.set_state(GameState.PLAYING)
        self.assertTrue(self.state_manager.should_update_game())
        
        self.state_manager.set_state(GameState.PAUSED)
        self.assertFalse(self.state_manager.should_update_game())
        
        # Test should_render_game
        self.state_manager.set_state(GameState.PLAYING)
        self.assertTrue(self.state_manager.should_render_game())
        
        self.state_manager.set_state(GameState.PAUSED)
        self.assertTrue(self.state_manager.should_render_game())
        
        self.state_manager.set_state(GameState.MENU)
        self.assertFalse(self.state_manager.should_render_game())
    
    def test_no_state_change_on_same_state(self):
        """Test that setting the same state doesn't trigger state change logic."""
        initial_state = self.state_manager.get_current_state()
        initial_previous = self.state_manager.get_previous_state()
        
        # Set the same state
        self.state_manager.set_state(initial_state)
        
        # Should remain unchanged
        self.assertEqual(self.state_manager.get_current_state(), initial_state)
        self.assertEqual(self.state_manager.get_previous_state(), initial_previous)
    
    @patch('pygame.font.Font')
    def test_render_methods_called(self, mock_font):
        """Test that render methods are called without errors."""
        # Mock font rendering
        mock_font_instance = Mock()
        mock_font.return_value = mock_font_instance
        mock_surface = Mock()
        mock_surface.get_rect.return_value = Mock()
        mock_font_instance.render.return_value = mock_surface
        
        # Test menu rendering
        self.state_manager.set_state(GameState.MENU)
        self.state_manager.render()
        
        # Test game over rendering
        self.state_manager.set_state(GameState.GAME_OVER)
        self.state_manager.set_game_over_data(1000, 2)
        self.state_manager.render()
        
        # Test paused rendering
        self.state_manager.set_state(GameState.PAUSED)
        self.state_manager.render()
        
        # Verify screen.blit was called (indicating rendering occurred)
        self.assertTrue(self.mock_screen.blit.called)


if __name__ == '__main__':
    unittest.main()