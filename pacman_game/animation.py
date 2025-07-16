"""
Animation system for the Pacman game.
Handles sprite animations, visual effects, and smooth character movement.
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass

from .models import Direction, GhostMode


class AnimationType(Enum):
    """Types of animations supported by the system."""
    SPRITE_CYCLE = "sprite_cycle"
    FLASH = "flash"
    SMOOTH_MOVE = "smooth_move"
    ROTATION = "rotation"
    SCALE = "scale"


@dataclass
class AnimationFrame:
    """Represents a single frame in an animation sequence."""
    duration: int  # Duration in game frames
    data: Any  # Frame-specific data (sprite index, color, position, etc.)


class Animation:
    """Base animation class that handles timing and frame progression."""
    
    def __init__(self, frames: List[AnimationFrame], loop: bool = True):
        """Initialize animation with frames.
        
        Args:
            frames: List of animation frames
            loop: Whether animation should loop when finished
        """
        self.frames = frames
        self.loop = loop
        self.current_frame_index = 0
        self.frame_timer = 0
        self.finished = False
        self.paused = False
    
    def update(self) -> None:
        """Update animation timing and advance frames."""
        if self.finished or self.paused or not self.frames:
            return
        
        self.frame_timer += 1
        current_frame = self.frames[self.current_frame_index]
        
        if self.frame_timer >= current_frame.duration:
            self.frame_timer = 0
            self.current_frame_index += 1
            
            if self.current_frame_index >= len(self.frames):
                if self.loop:
                    self.current_frame_index = 0
                else:
                    self.current_frame_index = len(self.frames) - 1
                    self.finished = True
    
    def get_current_frame(self) -> Optional[AnimationFrame]:
        """Get the current animation frame.
        
        Returns:
            Current AnimationFrame or None if no frames
        """
        if not self.frames or self.current_frame_index >= len(self.frames):
            return None
        return self.frames[self.current_frame_index]
    
    def reset(self) -> None:
        """Reset animation to the beginning."""
        self.current_frame_index = 0
        self.frame_timer = 0
        self.finished = False
    
    def pause(self) -> None:
        """Pause the animation."""
        self.paused = True
    
    def resume(self) -> None:
        """Resume the animation."""
        self.paused = False
    
    def is_finished(self) -> bool:
        """Check if animation is finished.
        
        Returns:
            True if animation is finished and not looping
        """
        return self.finished


class SpriteAnimation(Animation):
    """Animation specifically for sprite cycling."""
    
    def __init__(self, sprite_indices: List[int], frame_duration: int = 8, loop: bool = True):
        """Initialize sprite animation.
        
        Args:
            sprite_indices: List of sprite indices to cycle through
            frame_duration: Duration of each frame in game frames
            loop: Whether animation should loop
        """
        frames = [AnimationFrame(frame_duration, sprite_idx) for sprite_idx in sprite_indices]
        super().__init__(frames, loop)
    
    def get_current_sprite_index(self) -> int:
        """Get the current sprite index.
        
        Returns:
            Current sprite index, or 0 if no frames
        """
        frame = self.get_current_frame()
        return frame.data if frame else 0


class FlashAnimation(Animation):
    """Animation for flashing effects (like power pellets)."""
    
    def __init__(self, colors: List[Tuple[int, int, int]], flash_duration: int = 15):
        """Initialize flash animation.
        
        Args:
            colors: List of colors to cycle through
            flash_duration: Duration of each color in game frames
        """
        frames = [AnimationFrame(flash_duration, color) for color in colors]
        super().__init__(frames, loop=True)
    
    def get_current_color(self) -> Tuple[int, int, int]:
        """Get the current flash color.
        
        Returns:
            Current color as RGB tuple
        """
        frame = self.get_current_frame()
        return frame.data if frame else (255, 255, 255)


class SmoothMoveAnimation(Animation):
    """Animation for smooth movement between positions."""
    
    def __init__(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], 
                 duration: int = 20, easing: str = "linear"):
        """Initialize smooth movement animation.
        
        Args:
            start_pos: Starting position (x, y)
            end_pos: Ending position (x, y)
            duration: Total duration in game frames
            easing: Easing function type ("linear", "ease_in", "ease_out", "ease_in_out")
        """
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.easing = easing
        
        # Create single frame with full duration
        frames = [AnimationFrame(duration, {"start": start_pos, "end": end_pos})]
        super().__init__(frames, loop=False)
    
    def get_current_position(self) -> Tuple[float, float]:
        """Get the current interpolated position.
        
        Returns:
            Current position as (x, y) tuple
        """
        if self.finished:
            return self.end_pos
        
        if not self.frames:
            return self.start_pos
        
        # Calculate progress (0.0 to 1.0)
        total_duration = self.frames[0].duration
        progress = self.frame_timer / total_duration if total_duration > 0 else 1.0
        progress = min(1.0, progress)
        
        # Apply easing
        eased_progress = self._apply_easing(progress)
        
        # Interpolate position
        start_x, start_y = self.start_pos
        end_x, end_y = self.end_pos
        
        current_x = start_x + (end_x - start_x) * eased_progress
        current_y = start_y + (end_y - start_y) * eased_progress
        
        return (current_x, current_y)
    
    def _apply_easing(self, t: float) -> float:
        """Apply easing function to progress value.
        
        Args:
            t: Progress value (0.0 to 1.0)
            
        Returns:
            Eased progress value
        """
        if self.easing == "ease_in":
            return t * t
        elif self.easing == "ease_out":
            return 1 - (1 - t) * (1 - t)
        elif self.easing == "ease_in_out":
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        else:  # linear
            return t


class AnimationManager:
    """Manages all animations for game entities."""
    
    def __init__(self):
        """Initialize the animation manager."""
        self.animations: Dict[str, Animation] = {}
        self.entity_animations: Dict[str, Dict[str, Animation]] = {}
        
        # Pre-defined animation configurations
        self._setup_default_animations()
    
    def _setup_default_animations(self) -> None:
        """Set up default animation configurations."""
        # Player (Pacman) animations for each direction
        self.player_animations = {
            Direction.RIGHT: SpriteAnimation([0, 1, 2, 1], frame_duration=6),
            Direction.LEFT: SpriteAnimation([3, 4, 5, 4], frame_duration=6),
            Direction.UP: SpriteAnimation([6, 7, 8, 7], frame_duration=6),
            Direction.DOWN: SpriteAnimation([9, 10, 11, 10], frame_duration=6),
            Direction.NONE: SpriteAnimation([0], frame_duration=60)  # Idle frame
        }
        
        # Ghost animations for different modes
        self.ghost_animations = {
            GhostMode.NORMAL: SpriteAnimation([0, 1], frame_duration=15),
            GhostMode.FRIGHTENED: SpriteAnimation([2, 3], frame_duration=10),
            GhostMode.EATEN: SpriteAnimation([4], frame_duration=60)  # Static frame
        }
        
        # Power pellet flash animation
        self.power_pellet_flash = FlashAnimation([
            (255, 255, 255),  # White
            (255, 255, 0),    # Yellow
            (255, 200, 0),    # Orange
            (255, 255, 0)     # Yellow
        ], flash_duration=12)
    
    def add_animation(self, entity_id: str, animation_name: str, animation: Animation) -> None:
        """Add an animation for a specific entity.
        
        Args:
            entity_id: Unique identifier for the entity
            animation_name: Name of the animation
            animation: Animation instance
        """
        if entity_id not in self.entity_animations:
            self.entity_animations[entity_id] = {}
        self.entity_animations[entity_id][animation_name] = animation
    
    def get_animation(self, entity_id: str, animation_name: str) -> Optional[Animation]:
        """Get an animation for a specific entity.
        
        Args:
            entity_id: Entity identifier
            animation_name: Animation name
            
        Returns:
            Animation instance or None if not found
        """
        if entity_id in self.entity_animations:
            return self.entity_animations[entity_id].get(animation_name)
        return None
    
    def update_all(self) -> None:
        """Update all managed animations."""
        # Update global animations
        for animation in self.animations.values():
            animation.update()
        
        # Update entity-specific animations
        for entity_animations in self.entity_animations.values():
            for animation in entity_animations.values():
                animation.update()
        
        # Update default animations
        for animation in self.player_animations.values():
            animation.update()
        
        for animation in self.ghost_animations.values():
            animation.update()
        
        self.power_pellet_flash.update()
    
    def get_player_animation(self, direction: Direction) -> SpriteAnimation:
        """Get player animation for a specific direction.
        
        Args:
            direction: Movement direction
            
        Returns:
            SpriteAnimation for the direction
        """
        return self.player_animations.get(direction, self.player_animations[Direction.NONE])
    
    def get_ghost_animation(self, mode: GhostMode) -> SpriteAnimation:
        """Get ghost animation for a specific mode.
        
        Args:
            mode: Ghost mode
            
        Returns:
            SpriteAnimation for the mode
        """
        return self.ghost_animations.get(mode, self.ghost_animations[GhostMode.NORMAL])
    
    def get_power_pellet_animation(self) -> FlashAnimation:
        """Get the power pellet flash animation.
        
        Returns:
            FlashAnimation for power pellets
        """
        return self.power_pellet_flash
    
    def reset_all_animations(self) -> None:
        """Reset all animations to their starting state."""
        for animation in self.animations.values():
            animation.reset()
        
        for entity_animations in self.entity_animations.values():
            for animation in entity_animations.values():
                animation.reset()
        
        for animation in self.player_animations.values():
            animation.reset()
        
        for animation in self.ghost_animations.values():
            animation.reset()
        
        self.power_pellet_flash.reset()
    
    def pause_all_animations(self) -> None:
        """Pause all animations."""
        for animation in self.animations.values():
            animation.pause()
        
        for entity_animations in self.entity_animations.values():
            for animation in entity_animations.values():
                animation.pause()
        
        # Pause default animations
        for animation in self.player_animations.values():
            animation.pause()
        
        for animation in self.ghost_animations.values():
            animation.pause()
        
        self.power_pellet_flash.pause()
    
    def resume_all_animations(self) -> None:
        """Resume all animations."""
        for animation in self.animations.values():
            animation.resume()
        
        for entity_animations in self.entity_animations.values():
            for animation in entity_animations.values():
                animation.resume()
        
        # Resume default animations
        for animation in self.player_animations.values():
            animation.resume()
        
        for animation in self.ghost_animations.values():
            animation.resume()
        
        self.power_pellet_flash.resume()


class SpriteRenderer:
    """Handles rendering of animated sprites."""
    
    def __init__(self, tile_size: int = 20):
        """Initialize sprite renderer.
        
        Args:
            tile_size: Size of game tiles in pixels
        """
        self.tile_size = tile_size
        self.sprite_cache: Dict[str, pygame.Surface] = {}
        
        # Create basic sprite surfaces (placeholder implementation)
        self._create_basic_sprites()
    
    def _create_basic_sprites(self) -> None:
        """Create basic sprite surfaces for entities."""
        # Player sprites (Pacman) - different mouth positions and directions
        player_sprites = []
        
        # Right-facing sprites (0-2)
        for i in range(3):
            sprite = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            pygame.draw.circle(sprite, (255, 255, 0), 
                             (self.tile_size // 2, self.tile_size // 2), 
                             self.tile_size // 3)
            
            # Add mouth based on animation frame
            if i > 0:
                mouth_angle = 30 * i  # Varying mouth opening
                center = (self.tile_size // 2, self.tile_size // 2)
                radius = self.tile_size // 3
                
                # Create mouth triangle
                mouth_points = [
                    center,
                    (center[0] + radius, center[1] - mouth_angle // 2),
                    (center[0] + radius, center[1] + mouth_angle // 2)
                ]
                pygame.draw.polygon(sprite, (0, 0, 0), mouth_points)
            
            player_sprites.append(sprite)
        
        # Store player sprites
        for i, sprite in enumerate(player_sprites):
            self.sprite_cache[f"player_{i}"] = sprite
        
        # Create rotated versions for other directions
        for direction, base_angle in [(Direction.LEFT, 180), (Direction.UP, 270), (Direction.DOWN, 90)]:
            for i in range(3):
                original = player_sprites[i]
                rotated = pygame.transform.rotate(original, base_angle)
                key = f"player_{direction.name.lower()}_{i}"
                self.sprite_cache[key] = rotated
        
        # Ghost sprites
        ghost_colors = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)]
        ghost_modes = ["normal", "frightened", "eaten"]
        
        for color_idx, color in enumerate(ghost_colors):
            for mode_idx, mode in enumerate(ghost_modes):
                sprite = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                
                if mode == "frightened":
                    # Blue/gray for frightened ghosts
                    ghost_color = (0, 0, 255) if mode_idx % 2 == 0 else (128, 128, 128)
                elif mode == "eaten":
                    # White outline for eaten ghosts
                    ghost_color = (255, 255, 255)
                else:
                    ghost_color = color
                
                # Draw ghost body
                center = (self.tile_size // 2, self.tile_size // 2)
                radius = self.tile_size // 3
                pygame.draw.circle(sprite, ghost_color, center, radius)
                
                # Add eyes
                eye_color = (255, 255, 255) if mode != "eaten" else (0, 0, 0)
                eye_size = 2
                pygame.draw.circle(sprite, eye_color, 
                                 (center[0] - radius // 2, center[1] - radius // 3), eye_size)
                pygame.draw.circle(sprite, eye_color, 
                                 (center[0] + radius // 2, center[1] - radius // 3), eye_size)
                
                key = f"ghost_{color_idx}_{mode}"
                self.sprite_cache[key] = sprite
    
    def get_sprite(self, sprite_key: str) -> Optional[pygame.Surface]:
        """Get a sprite surface by key.
        
        Args:
            sprite_key: Key identifying the sprite
            
        Returns:
            Pygame Surface or None if not found
        """
        return self.sprite_cache.get(sprite_key)
    
    def render_animated_sprite(self, surface: pygame.Surface, position: Tuple[int, int], 
                             sprite_key: str, animation: SpriteAnimation) -> None:
        """Render an animated sprite to a surface.
        
        Args:
            surface: Target surface to render to
            position: Position to render at (x, y)
            sprite_key: Base sprite key
            animation: Animation providing current frame
        """
        frame_index = animation.get_current_sprite_index()
        full_key = f"{sprite_key}_{frame_index}"
        sprite = self.get_sprite(full_key)
        
        if sprite:
            surface.blit(sprite, position)
    
    def render_flashing_sprite(self, surface: pygame.Surface, position: Tuple[int, int],
                             base_color: Tuple[int, int, int], flash_animation: FlashAnimation,
                             radius: int = 6) -> None:
        """Render a flashing sprite (like power pellets).
        
        Args:
            surface: Target surface to render to
            position: Position to render at (x, y)
            base_color: Base color when not flashing
            flash_animation: Flash animation providing current color
            radius: Radius of the sprite
        """
        current_color = flash_animation.get_current_color()
        center_x = position[0] + self.tile_size // 2
        center_y = position[1] + self.tile_size // 2
        
        pygame.draw.circle(surface, current_color, (center_x, center_y), radius)
    
    def cleanup(self) -> None:
        """Clean up sprite resources."""
        self.sprite_cache.clear()