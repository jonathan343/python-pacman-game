#!/usr/bin/env python3
"""
Demo script to test the animation system functionality.
"""

import pygame
import sys
from pacman_game.animation import AnimationManager, SpriteRenderer, FlashAnimation
from pacman_game.models import Direction, GhostMode


def test_animation_system():
    """Test the animation system with visual feedback."""
    print("Testing Animation System...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Animation System Test")
    clock = pygame.time.Clock()
    
    # Initialize animation system
    animation_manager = AnimationManager()
    sprite_renderer = SpriteRenderer(tile_size=20)
    
    print("✓ Animation system initialized")
    
    # Test player animations
    print("\nTesting Player Animations:")
    for direction in [Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN, Direction.NONE]:
        player_anim = animation_manager.get_player_animation(direction)
        print(f"  ✓ {direction.name}: {len(player_anim.frames)} frames")
    
    # Test ghost animations
    print("\nTesting Ghost Animations:")
    for mode in [GhostMode.NORMAL, GhostMode.FRIGHTENED, GhostMode.EATEN]:
        ghost_anim = animation_manager.get_ghost_animation(mode)
        print(f"  ✓ {mode.name}: {len(ghost_anim.frames)} frames")
    
    # Test power pellet animation
    power_pellet_anim = animation_manager.get_power_pellet_animation()
    print(f"\n✓ Power Pellet Animation: {len(power_pellet_anim.frames)} frames")
    
    # Test sprite rendering
    print("\nTesting Sprite Rendering:")
    sprite_count = len(sprite_renderer.sprite_cache)
    print(f"  ✓ {sprite_count} sprites cached")
    
    # Visual test - run for a few seconds to see animations
    print("\nRunning visual test for 3 seconds...")
    test_duration = 180  # 3 seconds at 60 FPS
    frame_count = 0
    
    try:
        while frame_count < test_duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
            
            # Update animations
            animation_manager.update_all()
            
            # Clear screen
            screen.fill((0, 0, 0))
            
            # Test power pellet flashing
            flash_anim = animation_manager.get_power_pellet_animation()
            sprite_renderer.render_flashing_sprite(
                screen, (50, 50), (255, 255, 255), flash_anim, radius=8
            )
            
            # Test another power pellet at different position
            sprite_renderer.render_flashing_sprite(
                screen, (150, 100), (255, 255, 255), flash_anim, radius=6
            )
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
            frame_count += 1
        
        print("✓ Visual test completed successfully")
        
    except Exception as e:
        print(f"✗ Visual test failed: {e}")
        return False
    
    finally:
        # Cleanup
        sprite_renderer.cleanup()
        pygame.quit()
    
    print("\n✓ All animation system tests passed!")
    return True


def test_animation_timing():
    """Test animation timing and frame progression."""
    print("\nTesting Animation Timing:")
    
    # Create test animation
    from pacman_game.animation import SpriteAnimation
    test_anim = SpriteAnimation([0, 1, 2, 1], frame_duration=5)
    
    # Test frame progression
    expected_sequence = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0]
    actual_sequence = []
    
    for i in range(21):
        actual_sequence.append(test_anim.get_current_sprite_index())
        test_anim.update()
    
    if actual_sequence == expected_sequence:
        print("  ✓ Animation timing is correct")
        return True
    else:
        print(f"  ✗ Animation timing failed")
        print(f"    Expected: {expected_sequence}")
        print(f"    Actual:   {actual_sequence}")
        return False


def test_flash_animation():
    """Test flash animation color cycling."""
    print("\nTesting Flash Animation:")
    
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    flash_anim = FlashAnimation(colors, flash_duration=3)
    
    # Test color progression
    expected_colors = [
        (255, 0, 0), (255, 0, 0), (255, 0, 0),  # Red for 3 frames
        (0, 255, 0), (0, 255, 0), (0, 255, 0),  # Green for 3 frames
        (0, 0, 255), (0, 0, 255), (0, 0, 255),  # Blue for 3 frames
        (255, 0, 0)  # Back to red
    ]
    
    actual_colors = []
    for i in range(10):
        actual_colors.append(flash_anim.get_current_color())
        flash_anim.update()
    
    if actual_colors == expected_colors:
        print("  ✓ Flash animation color cycling is correct")
        return True
    else:
        print(f"  ✗ Flash animation failed")
        print(f"    Expected: {expected_colors}")
        print(f"    Actual:   {actual_colors}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("PACMAN GAME - ANIMATION SYSTEM TEST")
    print("=" * 50)
    
    success = True
    
    # Run tests
    success &= test_animation_system()
    success &= test_animation_timing()
    success &= test_flash_animation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! Animation system is working correctly.")
    else:
        print("❌ SOME TESTS FAILED! Check the output above.")
    print("=" * 50)
    
    sys.exit(0 if success else 1)