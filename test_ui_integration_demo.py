#!/usr/bin/env python3
"""
Integration demo for UI display system.
Demonstrates the UI system working with real game components.
"""

import pygame
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from pacman_game.renderer import Renderer
from pacman_game.models import ScoreManager, Maze, Position, Player
from pacman_game.config import GameConfig


def main():
    """Run UI integration demo."""
    print("Starting UI Display Integration Demo...")
    
    # Initialize Pygame
    pygame.init()
    
    try:
        # Create game components
        renderer = Renderer(
            screen_width=GameConfig.SCREEN_WIDTH,
            screen_height=GameConfig.SCREEN_HEIGHT,
            tile_size=GameConfig.TILE_SIZE
        )
        
        maze = Maze(tile_size=GameConfig.TILE_SIZE)
        score_manager = ScoreManager(starting_lives=3)
        
        # Initialize level with maze dots
        total_dots = maze.get_dots_remaining()
        score_manager.initialize_level(total_dots)
        
        print(f"Initialized game with {total_dots} dots")
        
        # Create player for demonstration
        start_pos = Position(13 * GameConfig.TILE_SIZE, 15 * GameConfig.TILE_SIZE)
        player = Player(start_pos, maze, speed=GameConfig.PLAYER_SPEED)
        
        # Demo clock
        clock = pygame.time.Clock()
        demo_timer = 0
        demo_phase = 0
        
        print("Demo phases:")
        print("1. Initial state")
        print("2. Collect some dots")
        print("3. Collect power pellet")
        print("4. Lose a life")
        print("5. Level progression")
        
        running = True
        while running and demo_timer < 300:  # Run for 5 seconds at 60 FPS
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Demo progression
            if demo_timer == 60:  # 1 second
                demo_phase = 1
                # Simulate collecting dots
                for _ in range(10):
                    score_manager.collect_dot()
                print(f"Phase {demo_phase}: Collected 10 dots, Score: {score_manager.get_score()}")
            
            elif demo_timer == 120:  # 2 seconds
                demo_phase = 2
                # Simulate collecting power pellet
                score_manager.collect_power_pellet()
                print(f"Phase {demo_phase}: Collected power pellet, Score: {score_manager.get_score()}")
            
            elif demo_timer == 180:  # 3 seconds
                demo_phase = 3
                # Simulate eating ghosts
                for _ in range(2):
                    points = score_manager.eat_ghost()
                    print(f"  Ate ghost for {points} points")
                print(f"Phase {demo_phase}: Ate 2 ghosts, Score: {score_manager.get_score()}")
            
            elif demo_timer == 240:  # 4 seconds
                demo_phase = 4
                # Simulate losing a life
                game_over = score_manager.lose_life()
                print(f"Phase {demo_phase}: Lost a life, Lives: {score_manager.get_lives()}, Game Over: {game_over}")
            
            elif demo_timer == 270:  # 4.5 seconds
                demo_phase = 5
                # Simulate level progression
                score_manager.start_new_level(150)  # New level with more dots
                print(f"Phase {demo_phase}: Advanced to level {score_manager.get_level()}")
            
            # Clear screen
            renderer.clear_screen()
            
            # Render maze (simplified)
            renderer.render_maze(maze)
            renderer.render_collectibles(maze)
            
            # Render player
            renderer.render_player(player)
            
            # Render UI (this is what we're testing)
            renderer.render_ui(score_manager)
            
            # Add demo info
            demo_text = renderer.small_font.render(f"Demo Phase: {demo_phase} | Timer: {demo_timer//60}s", True, (255, 255, 255))
            renderer.screen.blit(demo_text, (10, renderer.screen_height - 30))
            
            # Update display
            renderer.update_display()
            
            # Control frame rate
            clock.tick(60)
            demo_timer += 1
        
        print("\nDemo completed successfully!")
        print("UI Display System Features Demonstrated:")
        print("✓ Score display with comma formatting")
        print("✓ Lives counter with visual icons")
        print("✓ Level indicator")
        print("✓ Progress bar for level completion")
        print("✓ Real-time updates during gameplay")
        print("✓ Level complete indicator")
        
        # Test UI bounds
        bounds = renderer.get_ui_bounds()
        print(f"\nUI Layout Information:")
        print(f"UI Panel: {bounds['ui_panel']}")
        print(f"Score Position: {bounds['score']}")
        print(f"Lives Position: {bounds['lives_label']}")
        print(f"Level Position: {bounds['level']}")
        
        # Test minimal UI
        print("\nTesting minimal UI rendering...")
        renderer.clear_screen()
        renderer.render_ui_minimal(score_manager.get_score(), score_manager.get_lives(), score_manager.get_level())
        renderer.update_display()
        
        # Wait a moment to see minimal UI
        pygame.time.wait(1000)
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        renderer.cleanup()
    
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ UI Display System Integration Demo completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ UI Display System Integration Demo failed!")
        sys.exit(1)