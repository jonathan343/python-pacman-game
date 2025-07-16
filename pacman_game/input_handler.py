"""
Input handling system for the Pacman game.
Processes keyboard input and translates to game actions.
"""

import pygame
from typing import Dict, Set, Optional, Callable
from enum import Enum

from .config import Direction, GameState


class InputAction(Enum):
    """Enumeration of possible input actions."""
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    PAUSE = "pause"
    QUIT = "quit"
    RESTART = "restart"


class InputHandler:
    """Handles keyboard input processing for different game states."""
    
    def __init__(self):
        """Initialize the input handler with default key mappings."""
        # Key mappings for different actions
        self.key_mappings: Dict[int, InputAction] = {
            # Arrow keys for movement
            pygame.K_UP: InputAction.MOVE_UP,
            pygame.K_DOWN: InputAction.MOVE_DOWN,
            pygame.K_LEFT: InputAction.MOVE_LEFT,
            pygame.K_RIGHT: InputAction.MOVE_RIGHT,
            
            # WASD alternative movement
            pygame.K_w: InputAction.MOVE_UP,
            pygame.K_s: InputAction.MOVE_DOWN,
            pygame.K_a: InputAction.MOVE_LEFT,
            pygame.K_d: InputAction.MOVE_RIGHT,
            
            # Menu and game control
            pygame.K_RETURN: InputAction.CONFIRM,
            pygame.K_SPACE: InputAction.CONFIRM,
            pygame.K_ESCAPE: InputAction.CANCEL,
            pygame.K_p: InputAction.PAUSE,
            pygame.K_q: InputAction.QUIT,
            pygame.K_r: InputAction.RESTART,
        }
        
        # Direction mappings for easy lookup
        self.direction_mappings: Dict[InputAction, Direction] = {
            InputAction.MOVE_UP: Direction.UP,
            InputAction.MOVE_DOWN: Direction.DOWN,
            InputAction.MOVE_LEFT: Direction.LEFT,
            InputAction.MOVE_RIGHT: Direction.RIGHT,
        }
        
        # Track pressed keys for continuous input
        self.pressed_keys: Set[int] = set()
        self.just_pressed_keys: Set[int] = set()
        self.just_released_keys: Set[int] = set()
        
        # Input callbacks for different game states
        self.input_callbacks: Dict[GameState, Callable] = {}
        
        # Key repeat handling
        self.key_repeat_delay = 200  # milliseconds
        self.key_repeat_interval = 50  # milliseconds
        self.last_key_times: Dict[int, int] = {}
    
    def register_callback(self, game_state: GameState, callback: Callable) -> None:
        """Register a callback function for a specific game state.
        
        Args:
            game_state: Game state to register callback for
            callback: Function to call when input is received
        """
        self.input_callbacks[game_state] = callback
    
    def update(self, events: list, current_state: GameState) -> None:
        """Update input state and process events.
        
        Args:
            events: List of pygame events
            current_state: Current game state
        """
        self._update_key_states(events)
        self._process_input(current_state)
    
    def _update_key_states(self, events: list) -> None:
        """Update the state of pressed keys based on events.
        
        Args:
            events: List of pygame events
        """
        self.just_pressed_keys.clear()
        self.just_released_keys.clear()
        
        current_time = pygame.time.get_ticks()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.pressed_keys.add(event.key)
                self.just_pressed_keys.add(event.key)
                self.last_key_times[event.key] = current_time
            elif event.type == pygame.KEYUP:
                self.pressed_keys.discard(event.key)
                self.just_released_keys.add(event.key)
                self.last_key_times.pop(event.key, None)
    
    def _process_input(self, current_state: GameState) -> None:
        """Process input based on current game state.
        
        Args:
            current_state: Current game state
        """
        if current_state in self.input_callbacks:
            self.input_callbacks[current_state](self)
    
    def is_action_pressed(self, action: InputAction) -> bool:
        """Check if an action key is currently pressed.
        
        Args:
            action: Input action to check
            
        Returns:
            True if action key is pressed, False otherwise
        """
        for key, mapped_action in self.key_mappings.items():
            if mapped_action == action and key in self.pressed_keys:
                return True
        return False
    
    def is_action_just_pressed(self, action: InputAction) -> bool:
        """Check if an action key was just pressed this frame.
        
        Args:
            action: Input action to check
            
        Returns:
            True if action key was just pressed, False otherwise
        """
        for key, mapped_action in self.key_mappings.items():
            if mapped_action == action and key in self.just_pressed_keys:
                return True
        return False
    
    def is_action_just_released(self, action: InputAction) -> bool:
        """Check if an action key was just released this frame.
        
        Args:
            action: Input action to check
            
        Returns:
            True if action key was just released, False otherwise
        """
        for key, mapped_action in self.key_mappings.items():
            if mapped_action == action and key in self.just_released_keys:
                return True
        return False
    
    def get_movement_direction(self) -> Direction:
        """Get the current movement direction based on pressed keys.
        
        Returns:
            Direction enum based on currently pressed movement keys
        """
        # Check for movement actions in priority order
        movement_actions = [
            InputAction.MOVE_UP,
            InputAction.MOVE_DOWN,
            InputAction.MOVE_LEFT,
            InputAction.MOVE_RIGHT
        ]
        
        for action in movement_actions:
            if self.is_action_pressed(action):
                return self.direction_mappings[action]
        
        return Direction.NONE
    
    def get_just_pressed_direction(self) -> Direction:
        """Get the direction that was just pressed this frame.
        
        Returns:
            Direction enum for the key that was just pressed
        """
        movement_actions = [
            InputAction.MOVE_UP,
            InputAction.MOVE_DOWN,
            InputAction.MOVE_LEFT,
            InputAction.MOVE_RIGHT
        ]
        
        for action in movement_actions:
            if self.is_action_just_pressed(action):
                return self.direction_mappings[action]
        
        return Direction.NONE
    
    def handle_menu_input(self) -> Optional[str]:
        """Handle input for menu navigation.
        
        Returns:
            String representing menu action, or None if no action
        """
        if self.is_action_just_pressed(InputAction.CONFIRM):
            return "confirm"
        elif self.is_action_just_pressed(InputAction.CANCEL):
            return "cancel"
        elif self.is_action_just_pressed(InputAction.QUIT):
            return "quit"
        elif self.is_action_just_pressed(InputAction.MOVE_UP):
            return "up"
        elif self.is_action_just_pressed(InputAction.MOVE_DOWN):
            return "down"
        
        return None
    
    def handle_game_input(self) -> Dict[str, any]:
        """Handle input during active gameplay.
        
        Returns:
            Dictionary containing input state information
        """
        input_state = {
            "movement_direction": self.get_movement_direction(),
            "new_direction": self.get_just_pressed_direction(),
            "pause_pressed": self.is_action_just_pressed(InputAction.PAUSE),
            "quit_pressed": self.is_action_just_pressed(InputAction.QUIT),
        }
        
        return input_state
    
    def handle_game_over_input(self) -> Optional[str]:
        """Handle input for game over screen.
        
        Returns:
            String representing game over action, or None if no action
        """
        if self.is_action_just_pressed(InputAction.RESTART):
            return "restart"
        elif self.is_action_just_pressed(InputAction.CONFIRM):
            return "restart"  # Enter also restarts
        elif self.is_action_just_pressed(InputAction.QUIT):
            return "quit"
        elif self.is_action_just_pressed(InputAction.CANCEL):
            return "menu"  # ESC goes back to menu
        
        return None
    
    def handle_pause_input(self) -> Optional[str]:
        """Handle input for pause screen.
        
        Returns:
            String representing pause action, or None if no action
        """
        if self.is_action_just_pressed(InputAction.PAUSE):
            return "resume"
        elif self.is_action_just_pressed(InputAction.CONFIRM):
            return "resume"
        elif self.is_action_just_pressed(InputAction.CANCEL):
            return "resume"
        elif self.is_action_just_pressed(InputAction.QUIT):
            return "quit"
        
        return None
    
    def is_quit_requested(self) -> bool:
        """Check if quit was requested.
        
        Returns:
            True if quit key was pressed, False otherwise
        """
        return self.is_action_just_pressed(InputAction.QUIT)
    
    def is_restart_requested(self) -> bool:
        """Check if restart was requested.
        
        Returns:
            True if restart key was pressed, False otherwise
        """
        return self.is_action_just_pressed(InputAction.RESTART)
    
    def is_pause_requested(self) -> bool:
        """Check if pause was requested.
        
        Returns:
            True if pause key was pressed, False otherwise
        """
        return self.is_action_just_pressed(InputAction.PAUSE)
    
    def clear_input_state(self) -> None:
        """Clear all input state (useful for state transitions)."""
        self.pressed_keys.clear()
        self.just_pressed_keys.clear()
        self.just_released_keys.clear()
        self.last_key_times.clear()
    
    def set_key_mapping(self, key: int, action: InputAction) -> None:
        """Set a custom key mapping.
        
        Args:
            key: Pygame key constant
            action: Input action to map to
        """
        self.key_mappings[key] = action
    
    def remove_key_mapping(self, key: int) -> None:
        """Remove a key mapping.
        
        Args:
            key: Pygame key constant to remove
        """
        self.key_mappings.pop(key, None)
    
    def get_key_for_action(self, action: InputAction) -> Optional[int]:
        """Get the first key mapped to an action.
        
        Args:
            action: Input action to find key for
            
        Returns:
            Pygame key constant, or None if not found
        """
        for key, mapped_action in self.key_mappings.items():
            if mapped_action == action:
                return key
        return None
    
    def get_all_keys_for_action(self, action: InputAction) -> list:
        """Get all keys mapped to an action.
        
        Args:
            action: Input action to find keys for
            
        Returns:
            List of pygame key constants
        """
        keys = []
        for key, mapped_action in self.key_mappings.items():
            if mapped_action == action:
                keys.append(key)
        return keys