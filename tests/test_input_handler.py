"""
Unit tests for the InputHandler class.
"""

import unittest
from unittest.mock import Mock, patch
import pygame

from pacman_game.input_handler import InputHandler, InputAction
from pacman_game.config import Direction, GameState


class TestInputHandler(unittest.TestCase):
    """Test cases for InputHandler class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize pygame for key constants
        pygame.init()
        self.input_handler = InputHandler()
    
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
    
    def test_initialization(self):
        """Test InputHandler initialization."""
        self.assertIsInstance(self.input_handler.key_mappings, dict)
        self.assertIsInstance(self.input_handler.direction_mappings, dict)
        self.assertIsInstance(self.input_handler.pressed_keys, set)
        self.assertIsInstance(self.input_handler.just_pressed_keys, set)
        self.assertIsInstance(self.input_handler.just_released_keys, set)
        
        # Check that default key mappings are set
        self.assertIn(pygame.K_UP, self.input_handler.key_mappings)
        self.assertIn(pygame.K_DOWN, self.input_handler.key_mappings)
        self.assertIn(pygame.K_LEFT, self.input_handler.key_mappings)
        self.assertIn(pygame.K_RIGHT, self.input_handler.key_mappings)
    
    def test_key_mappings(self):
        """Test default key mappings are correct."""
        # Test arrow keys
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_UP], 
            InputAction.MOVE_UP
        )
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_DOWN], 
            InputAction.MOVE_DOWN
        )
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_LEFT], 
            InputAction.MOVE_LEFT
        )
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_RIGHT], 
            InputAction.MOVE_RIGHT
        )
        
        # Test WASD keys
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_w], 
            InputAction.MOVE_UP
        )
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_s], 
            InputAction.MOVE_DOWN
        )
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_a], 
            InputAction.MOVE_LEFT
        )
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_d], 
            InputAction.MOVE_RIGHT
        )
        
        # Test control keys
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_RETURN], 
            InputAction.CONFIRM
        )
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_ESCAPE], 
            InputAction.CANCEL
        )
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_p], 
            InputAction.PAUSE
        )
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_q], 
            InputAction.QUIT
        )
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_r], 
            InputAction.RESTART
        )
    
    def test_direction_mappings(self):
        """Test direction mappings are correct."""
        self.assertEqual(
            self.input_handler.direction_mappings[InputAction.MOVE_UP], 
            Direction.UP
        )
        self.assertEqual(
            self.input_handler.direction_mappings[InputAction.MOVE_DOWN], 
            Direction.DOWN
        )
        self.assertEqual(
            self.input_handler.direction_mappings[InputAction.MOVE_LEFT], 
            Direction.LEFT
        )
        self.assertEqual(
            self.input_handler.direction_mappings[InputAction.MOVE_RIGHT], 
            Direction.RIGHT
        )
    
    def test_register_callback(self):
        """Test callback registration for game states."""
        mock_callback = Mock()
        
        self.input_handler.register_callback(GameState.PLAYING, mock_callback)
        
        self.assertIn(GameState.PLAYING, self.input_handler.input_callbacks)
        self.assertEqual(
            self.input_handler.input_callbacks[GameState.PLAYING], 
            mock_callback
        )
    
    def test_update_key_states_keydown(self):
        """Test key state updates on key down events."""
        # Create mock keydown event
        keydown_event = Mock()
        keydown_event.type = pygame.KEYDOWN
        keydown_event.key = pygame.K_UP
        
        with patch('pygame.time.get_ticks', return_value=1000):
            self.input_handler._update_key_states([keydown_event])
        
        self.assertIn(pygame.K_UP, self.input_handler.pressed_keys)
        self.assertIn(pygame.K_UP, self.input_handler.just_pressed_keys)
        self.assertIn(pygame.K_UP, self.input_handler.last_key_times)
    
    def test_update_key_states_keyup(self):
        """Test key state updates on key up events."""
        # First press the key
        self.input_handler.pressed_keys.add(pygame.K_UP)
        self.input_handler.last_key_times[pygame.K_UP] = 1000
        
        # Create mock keyup event
        keyup_event = Mock()
        keyup_event.type = pygame.KEYUP
        keyup_event.key = pygame.K_UP
        
        self.input_handler._update_key_states([keyup_event])
        
        self.assertNotIn(pygame.K_UP, self.input_handler.pressed_keys)
        self.assertIn(pygame.K_UP, self.input_handler.just_released_keys)
        self.assertNotIn(pygame.K_UP, self.input_handler.last_key_times)
    
    def test_is_action_pressed(self):
        """Test checking if an action is currently pressed."""
        # Add key to pressed keys
        self.input_handler.pressed_keys.add(pygame.K_UP)
        
        self.assertTrue(self.input_handler.is_action_pressed(InputAction.MOVE_UP))
        self.assertFalse(self.input_handler.is_action_pressed(InputAction.MOVE_DOWN))
    
    def test_is_action_just_pressed(self):
        """Test checking if an action was just pressed."""
        # Add key to just pressed keys
        self.input_handler.just_pressed_keys.add(pygame.K_UP)
        
        self.assertTrue(self.input_handler.is_action_just_pressed(InputAction.MOVE_UP))
        self.assertFalse(self.input_handler.is_action_just_pressed(InputAction.MOVE_DOWN))
    
    def test_is_action_just_released(self):
        """Test checking if an action was just released."""
        # Add key to just released keys
        self.input_handler.just_released_keys.add(pygame.K_UP)
        
        self.assertTrue(self.input_handler.is_action_just_released(InputAction.MOVE_UP))
        self.assertFalse(self.input_handler.is_action_just_released(InputAction.MOVE_DOWN))
    
    def test_get_movement_direction(self):
        """Test getting movement direction from pressed keys."""
        # Test no keys pressed
        self.assertEqual(self.input_handler.get_movement_direction(), Direction.NONE)
        
        # Test single direction
        self.input_handler.pressed_keys.add(pygame.K_UP)
        self.assertEqual(self.input_handler.get_movement_direction(), Direction.UP)
        
        # Test multiple directions (should return first in priority order)
        self.input_handler.pressed_keys.add(pygame.K_DOWN)
        self.assertEqual(self.input_handler.get_movement_direction(), Direction.UP)
        
        # Test WASD keys
        self.input_handler.pressed_keys.clear()
        self.input_handler.pressed_keys.add(pygame.K_w)
        self.assertEqual(self.input_handler.get_movement_direction(), Direction.UP)
    
    def test_get_just_pressed_direction(self):
        """Test getting direction that was just pressed."""
        # Test no keys just pressed
        self.assertEqual(self.input_handler.get_just_pressed_direction(), Direction.NONE)
        
        # Test single direction just pressed
        self.input_handler.just_pressed_keys.add(pygame.K_LEFT)
        self.assertEqual(self.input_handler.get_just_pressed_direction(), Direction.LEFT)
        
        # Test multiple directions just pressed (should return first in priority)
        self.input_handler.just_pressed_keys.add(pygame.K_UP)
        self.assertEqual(self.input_handler.get_just_pressed_direction(), Direction.UP)
    
    def test_handle_menu_input(self):
        """Test menu input handling."""
        # Test confirm action
        self.input_handler.just_pressed_keys.add(pygame.K_RETURN)
        self.assertEqual(self.input_handler.handle_menu_input(), "confirm")
        
        # Test cancel action
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_ESCAPE)
        self.assertEqual(self.input_handler.handle_menu_input(), "cancel")
        
        # Test quit action
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_q)
        self.assertEqual(self.input_handler.handle_menu_input(), "quit")
        
        # Test navigation
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_UP)
        self.assertEqual(self.input_handler.handle_menu_input(), "up")
        
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_DOWN)
        self.assertEqual(self.input_handler.handle_menu_input(), "down")
        
        # Test no input
        self.input_handler.just_pressed_keys.clear()
        self.assertIsNone(self.input_handler.handle_menu_input())
    
    def test_handle_game_input(self):
        """Test game input handling."""
        # Set up some input state
        self.input_handler.pressed_keys.add(pygame.K_RIGHT)
        self.input_handler.just_pressed_keys.add(pygame.K_UP)
        self.input_handler.just_pressed_keys.add(pygame.K_p)
        
        input_state = self.input_handler.handle_game_input()
        
        self.assertEqual(input_state["movement_direction"], Direction.RIGHT)
        self.assertEqual(input_state["new_direction"], Direction.UP)
        self.assertTrue(input_state["pause_pressed"])
        self.assertFalse(input_state["quit_pressed"])
    
    def test_handle_game_over_input(self):
        """Test game over input handling."""
        # Test restart with R key
        self.input_handler.just_pressed_keys.add(pygame.K_r)
        self.assertEqual(self.input_handler.handle_game_over_input(), "restart")
        
        # Test restart with Enter key
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_RETURN)
        self.assertEqual(self.input_handler.handle_game_over_input(), "restart")
        
        # Test quit
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_q)
        self.assertEqual(self.input_handler.handle_game_over_input(), "quit")
        
        # Test menu (ESC)
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_ESCAPE)
        self.assertEqual(self.input_handler.handle_game_over_input(), "menu")
        
        # Test no input
        self.input_handler.just_pressed_keys.clear()
        self.assertIsNone(self.input_handler.handle_game_over_input())
    
    def test_handle_pause_input(self):
        """Test pause input handling."""
        # Test resume with pause key
        self.input_handler.just_pressed_keys.add(pygame.K_p)
        self.assertEqual(self.input_handler.handle_pause_input(), "resume")
        
        # Test resume with Enter
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_RETURN)
        self.assertEqual(self.input_handler.handle_pause_input(), "resume")
        
        # Test resume with ESC
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_ESCAPE)
        self.assertEqual(self.input_handler.handle_pause_input(), "resume")
        
        # Test quit
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_q)
        self.assertEqual(self.input_handler.handle_pause_input(), "quit")
        
        # Test no input
        self.input_handler.just_pressed_keys.clear()
        self.assertIsNone(self.input_handler.handle_pause_input())
    
    def test_convenience_methods(self):
        """Test convenience methods for common input checks."""
        # Test quit requested
        self.input_handler.just_pressed_keys.add(pygame.K_q)
        self.assertTrue(self.input_handler.is_quit_requested())
        
        # Test restart requested
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_r)
        self.assertTrue(self.input_handler.is_restart_requested())
        
        # Test pause requested
        self.input_handler.just_pressed_keys.clear()
        self.input_handler.just_pressed_keys.add(pygame.K_p)
        self.assertTrue(self.input_handler.is_pause_requested())
        
        # Test all false when no keys pressed
        self.input_handler.just_pressed_keys.clear()
        self.assertFalse(self.input_handler.is_quit_requested())
        self.assertFalse(self.input_handler.is_restart_requested())
        self.assertFalse(self.input_handler.is_pause_requested())
    
    def test_clear_input_state(self):
        """Test clearing input state."""
        # Set up some input state
        self.input_handler.pressed_keys.add(pygame.K_UP)
        self.input_handler.just_pressed_keys.add(pygame.K_DOWN)
        self.input_handler.just_released_keys.add(pygame.K_LEFT)
        self.input_handler.last_key_times[pygame.K_UP] = 1000
        
        self.input_handler.clear_input_state()
        
        self.assertEqual(len(self.input_handler.pressed_keys), 0)
        self.assertEqual(len(self.input_handler.just_pressed_keys), 0)
        self.assertEqual(len(self.input_handler.just_released_keys), 0)
        self.assertEqual(len(self.input_handler.last_key_times), 0)
    
    def test_custom_key_mapping(self):
        """Test setting and removing custom key mappings."""
        # Test setting custom mapping
        self.input_handler.set_key_mapping(pygame.K_SPACE, InputAction.MOVE_UP)
        self.assertEqual(
            self.input_handler.key_mappings[pygame.K_SPACE], 
            InputAction.MOVE_UP
        )
        
        # Test removing mapping
        self.input_handler.remove_key_mapping(pygame.K_SPACE)
        self.assertNotIn(pygame.K_SPACE, self.input_handler.key_mappings)
    
    def test_get_key_for_action(self):
        """Test getting key for a specific action."""
        # Test getting existing mapping
        key = self.input_handler.get_key_for_action(InputAction.MOVE_UP)
        self.assertIn(key, [pygame.K_UP, pygame.K_w])  # Either arrow or WASD
        
        # Test getting non-existent mapping
        # First remove all MOVE_UP mappings
        keys_to_remove = []
        for k, action in self.input_handler.key_mappings.items():
            if action == InputAction.MOVE_UP:
                keys_to_remove.append(k)
        
        for k in keys_to_remove:
            del self.input_handler.key_mappings[k]
        
        key = self.input_handler.get_key_for_action(InputAction.MOVE_UP)
        self.assertIsNone(key)
    
    def test_get_all_keys_for_action(self):
        """Test getting all keys for a specific action."""
        keys = self.input_handler.get_all_keys_for_action(InputAction.MOVE_UP)
        self.assertIn(pygame.K_UP, keys)
        self.assertIn(pygame.K_w, keys)
        self.assertEqual(len(keys), 2)  # Should have both arrow and WASD
        
        # Test action with no keys
        keys = self.input_handler.get_all_keys_for_action(InputAction.CONFIRM)
        self.assertGreaterEqual(len(keys), 1)  # Should have at least Enter
    
    def test_update_with_callback(self):
        """Test update method with registered callback."""
        mock_callback = Mock()
        self.input_handler.register_callback(GameState.PLAYING, mock_callback)
        
        # Create mock events
        events = []
        
        self.input_handler.update(events, GameState.PLAYING)
        
        # Callback should be called with the input handler
        mock_callback.assert_called_once_with(self.input_handler)
    
    def test_multiple_key_events(self):
        """Test handling multiple key events in one update."""
        keydown_up = Mock()
        keydown_up.type = pygame.KEYDOWN
        keydown_up.key = pygame.K_UP
        
        keydown_down = Mock()
        keydown_down.type = pygame.KEYDOWN
        keydown_down.key = pygame.K_DOWN
        
        keyup_left = Mock()
        keyup_left.type = pygame.KEYUP
        keyup_left.key = pygame.K_LEFT
        
        # Pre-add left key to pressed keys
        self.input_handler.pressed_keys.add(pygame.K_LEFT)
        
        with patch('pygame.time.get_ticks', return_value=1000):
            self.input_handler._update_key_states([keydown_up, keydown_down, keyup_left])
        
        # Check all events were processed
        self.assertIn(pygame.K_UP, self.input_handler.pressed_keys)
        self.assertIn(pygame.K_DOWN, self.input_handler.pressed_keys)
        self.assertNotIn(pygame.K_LEFT, self.input_handler.pressed_keys)
        
        self.assertIn(pygame.K_UP, self.input_handler.just_pressed_keys)
        self.assertIn(pygame.K_DOWN, self.input_handler.just_pressed_keys)
        self.assertIn(pygame.K_LEFT, self.input_handler.just_released_keys)


if __name__ == '__main__':
    unittest.main()