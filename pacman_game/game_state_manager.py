"""
Game state management module for handling different game states and transitions.
"""

import pygame
from typing import Optional, Callable
from .models import GameState
from .config import GameConfig


class GameStateManager:
    """Manages game state transitions and screen rendering for different states."""
    
    def __init__(self, screen: pygame.Surface, config: GameConfig):
        """Initialize the game state manager.
        
        Args:
            screen: Pygame screen surface for rendering
            config: Game configuration instance
        """
        self.screen = screen
        self.config = config
        self.current_state = GameState.MENU
        self.previous_state = GameState.MENU
        
        # Font for text rendering
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # State-specific data
        self.final_score = 0
        self.final_level = 1
        
        # Menu selection
        self.menu_selection = 0
        self.menu_options = ["Start Game", "Quit"]
        
        # Game over menu selection
        self.game_over_selection = 0
        self.game_over_options = ["Restart", "Main Menu", "Quit"]
        
        # State change callbacks
        self.on_start_game: Optional[Callable] = None
        self.on_restart_game: Optional[Callable] = None
        self.on_quit_game: Optional[Callable] = None
    
    def set_state(self, new_state: GameState) -> None:
        """Change to a new game state.
        
        Args:
            new_state: The new state to transition to
        """
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self._on_state_enter(new_state)
    
    def get_current_state(self) -> GameState:
        """Get the current game state.
        
        Returns:
            Current GameState enum value
        """
        return self.current_state
    
    def get_previous_state(self) -> GameState:
        """Get the previous game state.
        
        Returns:
            Previous GameState enum value
        """
        return self.previous_state
    
    def is_in_menu(self) -> bool:
        """Check if currently in menu state.
        
        Returns:
            True if in menu state, False otherwise
        """
        return self.current_state == GameState.MENU
    
    def is_playing(self) -> bool:
        """Check if currently in playing state.
        
        Returns:
            True if in playing state, False otherwise
        """
        return self.current_state == GameState.PLAYING
    
    def is_game_over(self) -> bool:
        """Check if currently in game over state.
        
        Returns:
            True if in game over state, False otherwise
        """
        return self.current_state == GameState.GAME_OVER
    
    def is_paused(self) -> bool:
        """Check if currently in paused state.
        
        Returns:
            True if in paused state, False otherwise
        """
        return self.current_state == GameState.PAUSED
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle input events based on current state.
        
        Args:
            event: Pygame event to handle
        """
        if self.current_state == GameState.MENU:
            self._handle_menu_input(event)
        elif self.current_state == GameState.GAME_OVER:
            self._handle_game_over_input(event)
        elif self.current_state == GameState.PLAYING:
            self._handle_playing_input(event)
        elif self.current_state == GameState.PAUSED:
            self._handle_paused_input(event)
    
    def render(self) -> None:
        """Render the current state screen."""
        if self.current_state == GameState.MENU:
            self._render_menu()
        elif self.current_state == GameState.GAME_OVER:
            self._render_game_over()
        elif self.current_state == GameState.PAUSED:
            self._render_paused()
        # Note: PLAYING state rendering is handled by the main game renderer
    
    def set_game_over_data(self, final_score: int, final_level: int) -> None:
        """Set the final score and level for game over screen.
        
        Args:
            final_score: Final score achieved
            final_level: Final level reached
        """
        self.final_score = final_score
        self.final_level = final_level
    
    def _on_state_enter(self, state: GameState) -> None:
        """Handle state entry logic.
        
        Args:
            state: The state being entered
        """
        if state == GameState.MENU:
            self.menu_selection = 0
        elif state == GameState.GAME_OVER:
            self.game_over_selection = 0
    
    def _handle_menu_input(self, event: pygame.event.Event) -> None:
        """Handle input for menu state.
        
        Args:
            event: Pygame event to handle
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._execute_menu_selection()
    
    def _handle_game_over_input(self, event: pygame.event.Event) -> None:
        """Handle input for game over state.
        
        Args:
            event: Pygame event to handle
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.game_over_selection = (self.game_over_selection - 1) % len(self.game_over_options)
            elif event.key == pygame.K_DOWN:
                self.game_over_selection = (self.game_over_selection + 1) % len(self.game_over_options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._execute_game_over_selection()
    
    def _handle_playing_input(self, event: pygame.event.Event) -> None:
        """Handle input for playing state.
        
        Args:
            event: Pygame event to handle
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                self.set_state(GameState.PAUSED)
    
    def _handle_paused_input(self, event: pygame.event.Event) -> None:
        """Handle input for paused state.
        
        Args:
            event: Pygame event to handle
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                self.set_state(GameState.PLAYING)
            elif event.key == pygame.K_m:
                self.set_state(GameState.MENU)
    
    def _execute_menu_selection(self) -> None:
        """Execute the selected menu option."""
        selected_option = self.menu_options[self.menu_selection]
        
        if selected_option == "Start Game":
            self.set_state(GameState.PLAYING)
            if self.on_start_game:
                self.on_start_game()
        elif selected_option == "Quit":
            if self.on_quit_game:
                self.on_quit_game()
    
    def _execute_game_over_selection(self) -> None:
        """Execute the selected game over option."""
        selected_option = self.game_over_options[self.game_over_selection]
        
        if selected_option == "Restart":
            self.set_state(GameState.PLAYING)
            if self.on_restart_game:
                self.on_restart_game()
        elif selected_option == "Main Menu":
            self.set_state(GameState.MENU)
        elif selected_option == "Quit":
            if self.on_quit_game:
                self.on_quit_game()
    
    def _render_menu(self) -> None:
        """Render the main menu screen."""
        self.screen.fill(self.config.BLACK)
        
        # Title
        title_text = self.font_large.render("PYTHON PACMAN", True, self.config.YELLOW)
        title_rect = title_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Menu options
        for i, option in enumerate(self.menu_options):
            color = self.config.YELLOW if i == self.menu_selection else self.config.WHITE
            option_text = self.font_medium.render(option, True, color)
            option_rect = option_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 350 + i * 50))
            self.screen.blit(option_text, option_rect)
        
        # Instructions
        instructions = [
            "Use UP/DOWN arrows to navigate",
            "Press ENTER or SPACE to select"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_text = self.font_small.render(instruction, True, self.config.WHITE)
            instruction_rect = instruction_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 500 + i * 30))
            self.screen.blit(instruction_text, instruction_rect)
    
    def _render_game_over(self) -> None:
        """Render the game over screen."""
        self.screen.fill(self.config.BLACK)
        
        # Game Over title
        game_over_text = self.font_large.render("GAME OVER", True, self.config.RED)
        game_over_rect = game_over_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 150))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score and level
        score_text = self.font_medium.render(f"Final Score: {self.final_score}", True, self.config.WHITE)
        score_rect = score_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 220))
        self.screen.blit(score_text, score_rect)
        
        level_text = self.font_medium.render(f"Level Reached: {self.final_level}", True, self.config.WHITE)
        level_rect = level_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 260))
        self.screen.blit(level_text, level_rect)
        
        # Menu options
        for i, option in enumerate(self.game_over_options):
            color = self.config.YELLOW if i == self.game_over_selection else self.config.WHITE
            option_text = self.font_medium.render(option, True, color)
            option_rect = option_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 350 + i * 50))
            self.screen.blit(option_text, option_rect)
        
        # Instructions
        instructions = [
            "Use UP/DOWN arrows to navigate",
            "Press ENTER or SPACE to select"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_text = self.font_small.render(instruction, True, self.config.WHITE)
            instruction_rect = instruction_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, 550 + i * 30))
            self.screen.blit(instruction_text, instruction_rect)
    
    def _render_paused(self) -> None:
        """Render the paused screen overlay."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(self.config.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        paused_text = self.font_large.render("PAUSED", True, self.config.YELLOW)
        paused_rect = paused_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(paused_text, paused_rect)
        
        # Instructions
        instructions = [
            "Press P or ESC to resume",
            "Press M for main menu"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_text = self.font_small.render(instruction, True, self.config.WHITE)
            instruction_rect = instruction_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2 + 20 + i * 30))
            self.screen.blit(instruction_text, instruction_rect)
    
    def set_callbacks(self, 
                     on_start_game: Optional[Callable] = None,
                     on_restart_game: Optional[Callable] = None,
                     on_quit_game: Optional[Callable] = None) -> None:
        """Set callback functions for state transitions.
        
        Args:
            on_start_game: Callback for starting a new game
            on_restart_game: Callback for restarting the game
            on_quit_game: Callback for quitting the game
        """
        self.on_start_game = on_start_game
        self.on_restart_game = on_restart_game
        self.on_quit_game = on_quit_game
    
    def can_handle_game_input(self) -> bool:
        """Check if the current state allows game input.
        
        Returns:
            True if game input should be processed, False otherwise
        """
        return self.current_state == GameState.PLAYING
    
    def should_update_game(self) -> bool:
        """Check if the game logic should be updated.
        
        Returns:
            True if game should update, False otherwise
        """
        return self.current_state == GameState.PLAYING
    
    def should_render_game(self) -> bool:
        """Check if the game should be rendered.
        
        Returns:
            True if game should be rendered, False otherwise
        """
        return self.current_state in (GameState.PLAYING, GameState.PAUSED)