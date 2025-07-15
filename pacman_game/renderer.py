"""
Basic rendering system for the Pacman game using Pygame.
"""

import pygame
from typing import List, Tuple, Optional
from .models import Position, Maze, Player, Ghost, ScoreManager
from .config import GameConfig


class Renderer:
    """Handles all visual rendering for the Pacman game."""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 900, tile_size: int = 20):
        """Initialize the renderer with Pygame surface management.
        
        Args:
            screen_width: Width of the game screen in pixels
            screen_height: Height of the game screen in pixels
            tile_size: Size of each maze tile in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size
        
        # Initialize Pygame display
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Pacman Game")
        
        # Initialize font for UI text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Color constants
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.PINK = (255, 184, 255)
        self.CYAN = (0, 255, 255)
        self.ORANGE = (255, 184, 82)
        self.GRAY = (128, 128, 128)
        
        # Ghost colors mapping
        self.ghost_colors = {
            "red": self.RED,
            "pink": self.PINK,
            "cyan": self.CYAN,
            "orange": self.ORANGE
        }
    
    def clear_screen(self) -> None:
        """Clear the screen with black background."""
        self.screen.fill(self.BLACK)
    
    def render_maze(self, maze: Maze) -> None:
        """Render the maze walls and paths.
        
        Args:
            maze: Maze instance to render
        """
        for y in range(maze.height):
            for x in range(maze.width):
                pixel_x = x * self.tile_size
                pixel_y = y * self.tile_size
                
                cell_value = maze.layout[y][x]
                
                if cell_value == 1:  # Wall
                    # Draw wall as blue rectangle
                    pygame.draw.rect(
                        self.screen, 
                        self.BLUE,
                        (pixel_x, pixel_y, self.tile_size, self.tile_size)
                    )
                elif cell_value == 0 or cell_value == 2 or cell_value == 3 or cell_value == 4:  # Path, dot, power pellet, tunnel
                    # Draw path as black (already cleared)
                    pass
    
    def render_collectibles(self, maze: Maze) -> None:
        """Render dots and power pellets.
        
        Args:
            maze: Maze instance containing collectibles
        """
        # Render dots
        for grid_x, grid_y in maze.dots:
            pixel_x = grid_x * self.tile_size + self.tile_size // 2
            pixel_y = grid_y * self.tile_size + self.tile_size // 2
            
            # Draw small white circle for dot
            pygame.draw.circle(
                self.screen,
                self.WHITE,
                (pixel_x, pixel_y),
                2
            )
        
        # Render power pellets
        for grid_x, grid_y in maze.power_pellets:
            pixel_x = grid_x * self.tile_size + self.tile_size // 2
            pixel_y = grid_y * self.tile_size + self.tile_size // 2
            
            # Draw larger white circle for power pellet
            pygame.draw.circle(
                self.screen,
                self.WHITE,
                (pixel_x, pixel_y),
                6
            )
    
    def render_player(self, player: Player) -> None:
        """Render the player (Pacman) with basic shape.
        
        Args:
            player: Player instance to render
        """
        # Calculate center position
        center_x = int(player.position.x + self.tile_size // 2)
        center_y = int(player.position.y + self.tile_size // 2)
        radius = self.tile_size // 3
        
        # Draw yellow circle for Pacman
        pygame.draw.circle(
            self.screen,
            self.YELLOW,
            (center_x, center_y),
            radius
        )
        
        # Add simple mouth animation based on direction and animation frame
        if player.is_moving and player.animation_frame < 2:
            mouth_size = 30  # degrees
            start_angle = 0
            
            # Adjust mouth direction based on movement direction
            if player.direction.dx > 0:  # Moving right
                start_angle = -mouth_size // 2
            elif player.direction.dx < 0:  # Moving left
                start_angle = 180 - mouth_size // 2
            elif player.direction.dy < 0:  # Moving up
                start_angle = 270 - mouth_size // 2
            elif player.direction.dy > 0:  # Moving down
                start_angle = 90 - mouth_size // 2
            
            # Draw mouth as a pie slice (triangle)
            if start_angle != 0:
                mouth_points = [
                    (center_x, center_y),
                    (center_x + radius, center_y),
                    (center_x + radius * 0.7, center_y + radius * 0.7)
                ]
                pygame.draw.polygon(self.screen, self.BLACK, mouth_points)
    
    def render_ghost(self, ghost: Ghost) -> None:
        """Render a ghost with appropriate color and visual state.
        
        Args:
            ghost: Ghost instance to render
        """
        # Calculate center position
        center_x = int(ghost.position.x + self.tile_size // 2)
        center_y = int(ghost.position.y + self.tile_size // 2)
        radius = self.tile_size // 3
        
        # Determine ghost color based on mode
        if ghost.mode.is_vulnerable():  # Frightened mode
            color = self.GRAY
        elif ghost.mode == ghost.mode.EATEN:
            color = self.WHITE
        else:
            # Use ghost's assigned color
            color = self.ghost_colors.get(ghost.color, self.RED)
        
        # Draw ghost body as circle
        pygame.draw.circle(
            self.screen,
            color,
            (center_x, center_y),
            radius
        )
        
        # Add simple eyes for identification
        eye_size = 2
        eye_offset = radius // 3
        
        # Left eye
        pygame.draw.circle(
            self.screen,
            self.WHITE if ghost.mode != ghost.mode.EATEN else self.BLACK,
            (center_x - eye_offset, center_y - eye_offset // 2),
            eye_size
        )
        
        # Right eye
        pygame.draw.circle(
            self.screen,
            self.WHITE if ghost.mode != ghost.mode.EATEN else self.BLACK,
            (center_x + eye_offset, center_y - eye_offset // 2),
            eye_size
        )
        
        # Add visual indicator for frightened mode
        if ghost.mode.is_vulnerable():
            # Draw wavy bottom edge to indicate frightened state
            bottom_y = center_y + radius
            for i in range(-radius, radius, 4):
                wave_y = bottom_y + (2 if i % 8 < 4 else -2)
                pygame.draw.circle(
                    self.screen,
                    color,
                    (center_x + i, wave_y),
                    2
                )
    
    def render_ghosts(self, ghosts: List[Ghost]) -> None:
        """Render all ghosts in the game.
        
        Args:
            ghosts: List of Ghost instances to render
        """
        for ghost in ghosts:
            self.render_ghost(ghost)
    
    def render_ui(self, score_manager: ScoreManager) -> None:
        """Render UI elements including score, lives, and level.
        
        Args:
            score_manager: ScoreManager instance with current game state
        """
        # Render score
        score_text = self.font.render(f"Score: {score_manager.get_score()}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Render lives
        lives_text = self.font.render(f"Lives: {score_manager.get_lives()}", True, self.WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        # Render level
        level_text = self.font.render(f"Level: {score_manager.get_level()}", True, self.WHITE)
        self.screen.blit(level_text, (10, 90))
        
        # Render dots remaining (optional debug info)
        dots_remaining = score_manager.get_dots_remaining()
        if dots_remaining > 0:
            dots_text = self.small_font.render(f"Dots: {dots_remaining}", True, self.WHITE)
            self.screen.blit(dots_text, (10, 130))
    
    def render_game_over_screen(self, final_score: int) -> None:
        """Render game over screen with final score.
        
        Args:
            final_score: Final score to display
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(self.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, self.RED)
        text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        # Final score
        score_text = self.font.render(f"Final Score: {final_score}", True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(score_text, score_rect)
        
        # Restart instruction
        restart_text = self.small_font.render("Press R to restart or Q to quit", True, self.WHITE)
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def render_start_screen(self) -> None:
        """Render the start/menu screen."""
        # Clear screen
        self.clear_screen()
        
        # Title
        title_text = self.font.render("PACMAN", True, self.YELLOW)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        start_text = self.font.render("Press SPACE to start", True, self.WHITE)
        start_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(start_text, start_rect)
        
        # Controls
        controls_text = self.small_font.render("Use arrow keys to move", True, self.WHITE)
        controls_rect = controls_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        self.screen.blit(controls_text, controls_rect)
    
    def render_pause_screen(self) -> None:
        """Render pause screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(self.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        pause_text = self.font.render("PAUSED", True, self.WHITE)
        pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(pause_text, pause_rect)
        
        # Resume instruction
        resume_text = self.small_font.render("Press P to resume", True, self.WHITE)
        resume_rect = resume_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 40))
        self.screen.blit(resume_text, resume_rect)
    
    def update_display(self) -> None:
        """Update the display to show all rendered content."""
        pygame.display.flip()
    
    def get_screen_surface(self) -> pygame.Surface:
        """Get the main screen surface for advanced rendering.
        
        Returns:
            Pygame Surface object representing the screen
        """
        return self.screen
    
    def cleanup(self) -> None:
        """Clean up Pygame resources."""
        pygame.quit()