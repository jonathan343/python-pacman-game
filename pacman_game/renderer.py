"""
Basic rendering system for the Pacman game using Pygame.
"""

import pygame
from typing import List, Tuple, Optional
from .models import Position, Maze, Player, Ghost, ScoreManager
from .config import GameConfig
from .animation import AnimationManager, SpriteRenderer


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
        
        # Initialize animation system
        self.animation_manager = AnimationManager()
        self.sprite_renderer = SpriteRenderer(tile_size)
        
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
        """Render dots and power pellets with animations.
        
        Args:
            maze: Maze instance containing collectibles
        """
        # Render dots (static)
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
        
        # Render power pellets with flashing animation
        flash_animation = self.animation_manager.get_power_pellet_animation()
        for grid_x, grid_y in maze.power_pellets:
            pixel_x = grid_x * self.tile_size
            pixel_y = grid_y * self.tile_size
            
            # Use flashing animation for power pellets
            self.sprite_renderer.render_flashing_sprite(
                self.screen,
                (pixel_x, pixel_y),
                self.WHITE,
                flash_animation,
                radius=6
            )
    
    def render_player(self, player: Player) -> None:
        """Render the player (Pacman) with sprite animation.
        
        Args:
            player: Player instance to render
        """
        # Get the appropriate animation for current direction
        current_direction = player.direction if player.is_moving else player.direction.NONE
        player_animation = self.animation_manager.get_player_animation(current_direction)
        
        # Calculate position for sprite rendering
        sprite_x = int(player.position.x)
        sprite_y = int(player.position.y)
        
        # Try to render with sprite animation first
        sprite_key = f"player_{current_direction.name.lower()}"
        sprite = self.sprite_renderer.get_sprite(f"{sprite_key}_{player_animation.get_current_sprite_index()}")
        
        if sprite:
            self.screen.blit(sprite, (sprite_x, sprite_y))
        else:
            # Fallback to basic circle rendering with improved mouth animation
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
            
            # Enhanced mouth animation based on sprite animation frame
            if player.is_moving:
                frame_index = player_animation.get_current_sprite_index()
                mouth_opening = 0.3 + (frame_index * 0.2)  # Variable mouth opening
                
                # Calculate mouth direction based on movement
                mouth_angle = 0
                if player.direction.dx > 0:  # Moving right
                    mouth_angle = 0
                elif player.direction.dx < 0:  # Moving left
                    mouth_angle = 180
                elif player.direction.dy < 0:  # Moving up
                    mouth_angle = 270
                elif player.direction.dy > 0:  # Moving down
                    mouth_angle = 90
                
                # Draw animated mouth
                if frame_index > 0:  # Only show mouth when not in closed frame
                    mouth_size = int(radius * mouth_opening)
                    mouth_points = self._calculate_mouth_points(
                        center_x, center_y, radius, mouth_angle, mouth_size
                    )
                    if mouth_points:
                        pygame.draw.polygon(self.screen, self.BLACK, mouth_points)
    
    def _calculate_mouth_points(self, center_x: int, center_y: int, radius: int, 
                              angle: float, mouth_size: int) -> List[Tuple[int, int]]:
        """Calculate points for Pacman's mouth based on direction and size.
        
        Args:
            center_x: Center X coordinate
            center_y: Center Y coordinate
            radius: Pacman radius
            angle: Mouth direction angle in degrees
            mouth_size: Size of the mouth opening
            
        Returns:
            List of points for mouth polygon
        """
        import math
        
        # Convert angle to radians
        angle_rad = math.radians(angle)
        
        # Calculate mouth points
        mouth_points = [(center_x, center_y)]
        
        # Add points for mouth opening
        for i in range(-mouth_size, mouth_size + 1, mouth_size // 2):
            point_angle = angle_rad + math.radians(i)
            point_x = center_x + int(radius * math.cos(point_angle))
            point_y = center_y + int(radius * math.sin(point_angle))
            mouth_points.append((point_x, point_y))
        
        return mouth_points
    
    def render_ghost(self, ghost: Ghost) -> None:
        """Render a ghost with sprite animation and visual state indicators.
        
        Args:
            ghost: Ghost instance to render
        """
        # Get the appropriate animation for current ghost mode
        ghost_animation = self.animation_manager.get_ghost_animation(ghost.mode)
        
        # Calculate position for sprite rendering
        sprite_x = int(ghost.position.x)
        sprite_y = int(ghost.position.y)
        
        # Map ghost color to index for sprite lookup
        color_index = {"red": 0, "pink": 1, "cyan": 2, "orange": 3}.get(ghost.color, 0)
        
        # Try to render with sprite animation first
        sprite_key = f"ghost_{color_index}_{ghost.mode.value}"
        sprite = self.sprite_renderer.get_sprite(sprite_key)
        
        if sprite:
            self.screen.blit(sprite, (sprite_x, sprite_y))
        else:
            # Fallback to enhanced circle rendering with animations
            center_x = int(ghost.position.x + self.tile_size // 2)
            center_y = int(ghost.position.y + self.tile_size // 2)
            radius = self.tile_size // 3
            
            # Determine ghost color based on mode with animation effects
            if ghost.mode.is_vulnerable():  # Frightened mode
                # Animate between blue and white for frightened effect
                frame_index = ghost_animation.get_current_sprite_index()
                color = self.BLUE if frame_index == 0 else (128, 128, 255)  # Light blue
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
            
            # Add animated eyes for identification
            eye_size = 2
            eye_offset = radius // 3
            
            # Animate eye blinking for normal ghosts
            frame_index = ghost_animation.get_current_sprite_index()
            eye_open = frame_index == 0 or ghost.mode != ghost.mode.NORMAL
            
            if eye_open:
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
            else:
                # Draw closed eyes as lines
                pygame.draw.line(
                    self.screen,
                    self.BLACK,
                    (center_x - eye_offset - 1, center_y - eye_offset // 2),
                    (center_x - eye_offset + 1, center_y - eye_offset // 2),
                    1
                )
                pygame.draw.line(
                    self.screen,
                    self.BLACK,
                    (center_x + eye_offset - 1, center_y - eye_offset // 2),
                    (center_x + eye_offset + 1, center_y - eye_offset // 2),
                    1
                )
            
            # Add animated visual indicator for frightened mode
            if ghost.mode.is_vulnerable():
                # Animated wavy bottom edge to indicate frightened state
                bottom_y = center_y + radius
                wave_offset = frame_index * 2  # Animate the wave
                for i in range(-radius, radius, 3):
                    wave_y = bottom_y + (2 if (i + wave_offset) % 6 < 3 else -2)
                    pygame.draw.circle(
                        self.screen,
                        color,
                        (center_x + i, wave_y),
                        1
                    )
    
    def render_ghosts(self, ghosts: List[Ghost]) -> None:
        """Render all ghosts in the game.
        
        Args:
            ghosts: List of Ghost instances to render
        """
        for ghost in ghosts:
            self.render_ghost(ghost)
    
    def render_ui(self, score_manager: ScoreManager) -> None:
        """Render UI elements including score, lives, and level with real-time updates.
        
        Args:
            score_manager: ScoreManager instance with current game state
        """
        # Create UI background panel for better visibility
        ui_panel_height = 150
        ui_panel = pygame.Surface((self.screen_width, ui_panel_height))
        ui_panel.set_alpha(200)  # Semi-transparent
        ui_panel.fill((20, 20, 40))  # Dark blue background
        self.screen.blit(ui_panel, (0, self.screen_height - ui_panel_height))
        
        # Calculate UI positions at bottom of screen
        ui_y_base = self.screen_height - ui_panel_height + 10
        
        # Render score with formatting
        score_value = score_manager.get_score()
        score_text = self.font.render(f"SCORE: {score_value:,}", True, self.YELLOW)
        self.screen.blit(score_text, (20, ui_y_base))
        
        # Render lives with visual indicators
        lives_count = score_manager.get_lives()
        lives_label = self.font.render("LIVES:", True, self.WHITE)
        self.screen.blit(lives_label, (20, ui_y_base + 40))
        
        # Draw life icons as small Pacman symbols
        for i in range(lives_count):
            life_x = 120 + (i * 30)
            life_y = ui_y_base + 45
            pygame.draw.circle(self.screen, self.YELLOW, (life_x, life_y), 8)
            # Add simple mouth to life icon
            pygame.draw.polygon(self.screen, (20, 20, 40), [
                (life_x, life_y),
                (life_x + 6, life_y - 3),
                (life_x + 6, life_y + 3)
            ])
        
        # Render level indicator
        level_value = score_manager.get_level()
        level_text = self.font.render(f"LEVEL: {level_value}", True, self.CYAN)
        self.screen.blit(level_text, (20, ui_y_base + 80))
        
        # Render progress information
        dots_remaining = score_manager.get_dots_remaining()
        progress = score_manager.get_level_progress()
        
        # Always show progress information
        if dots_remaining > 0:
            dots_text = self.small_font.render(f"Dots Remaining: {dots_remaining}", True, self.WHITE)
        else:
            dots_text = self.small_font.render("Level Complete!", True, self.YELLOW)
        self.screen.blit(dots_text, (300, ui_y_base + 10))
        
        # Always draw progress bar for level completion
        bar_width = 200
        bar_height = 10
        bar_x = 300
        bar_y = ui_y_base + 35
        
        # Background bar
        pygame.draw.rect(self.screen, self.GRAY, (bar_x, bar_y, bar_width, bar_height))
        # Progress fill
        fill_width = int(bar_width * progress)
        progress_color = self.YELLOW if dots_remaining > 0 else (0, 255, 0)  # Green when complete
        pygame.draw.rect(self.screen, progress_color, (bar_x, bar_y, fill_width, bar_height))
        # Border
        pygame.draw.rect(self.screen, self.WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # High score display (if available)
        if hasattr(score_manager, 'high_score') and score_manager.high_score > 0:
            high_score_text = self.small_font.render(f"HIGH: {score_manager.high_score:,}", True, self.WHITE)
            self.screen.blit(high_score_text, (500, ui_y_base + 10))
    
    def render_ui_minimal(self, score: int, lives: int, level: int) -> None:
        """Render minimal UI elements for testing purposes.
        
        Args:
            score: Current score value
            lives: Current lives count
            level: Current level number
        """
        # Simple top-aligned UI for testing
        score_text = self.font.render(f"Score: {score}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        lives_text = self.font.render(f"Lives: {lives}", True, self.WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        level_text = self.font.render(f"Level: {level}", True, self.WHITE)
        self.screen.blit(level_text, (10, 90))
    
    def get_ui_bounds(self) -> dict:
        """Get the bounds of UI elements for testing and layout purposes.
        
        Returns:
            Dictionary containing UI element positions and dimensions
        """
        ui_panel_height = 150
        ui_y_base = self.screen_height - ui_panel_height + 10
        
        return {
            'ui_panel': {
                'x': 0,
                'y': self.screen_height - ui_panel_height,
                'width': self.screen_width,
                'height': ui_panel_height
            },
            'score': {'x': 20, 'y': ui_y_base},
            'lives_label': {'x': 20, 'y': ui_y_base + 40},
            'lives_icons': {'x': 120, 'y': ui_y_base + 45},
            'level': {'x': 20, 'y': ui_y_base + 80},
            'progress_info': {'x': 300, 'y': ui_y_base + 10},
            'progress_bar': {'x': 300, 'y': ui_y_base + 35, 'width': 200, 'height': 10}
        }
    
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
    
    def update_animations(self) -> None:
        """Update all animations managed by the renderer."""
        self.animation_manager.update_all()
    
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
        """Clean up Pygame resources and animation system."""
        self.sprite_renderer.cleanup()
        pygame.quit()